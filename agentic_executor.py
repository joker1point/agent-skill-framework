"""真 agentic loop 执行器：技能通过 load_skill 工具自主加载。

与 RealAgentExecutor（技能正文静态注入 + 单次调用）的差异：
- 系统提示只给技能清单（渐进式加载 Level 1：name + description），技能正文不在上下文里
- 模型自主决定是否加载技能、加载哪个（load_skill 工具调用）
- 多轮 tool-use loop，受 max_iterations / token 预算 / 墙钟超时约束
- 每轮产出完整轨迹（AgentTrace）：轮数、工具调用序列、token 分解、停止原因

保留 execute()（静态注入单次调用）以便同一执行器内做三方对比：
  without_skill（无技能） vs with_skill（静态注入） vs agentic（自主加载）

实测前提（2026-09-28 探测，见 _probe_tools.py）：
- agnes-3.0-flash / agnes-2.5-flash 支持 tools / tool 回灌 / tool_choice=required
- agnes-2.5-flash 同一轮可能产生重复并行 tool_calls（协议要求逐个回灌 tool 消息）
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from load_skill_tool import LoadSkillTool
from skills_loader import SkillsLoader

RETRYABLE_STATUS = (429, 500, 502, 503, 504)


@dataclass
class RetryPolicy:
    """瞬时错误的指数退避重试（错误分类对齐 agent-fault-tolerance-design）。

    - 可重试（瞬时）：429 / 5xx / 超时 / 连接错误
    - 不重试（确定性）：400 / 401 / 403 / 404 等——重试无意义，直接失败
    - 退避带随机抖动，避免多请求同步重试形成二次拥塞
    """

    max_retries: int = 3
    base_delay: float = 2.0
    max_delay: float = 30.0
    jitter: float = 0.5

    def is_retryable(self, error: Exception) -> bool:
        if isinstance(
            error,
            (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError),
        ):
            return True
        if isinstance(error, APIStatusError):
            return getattr(error, "status_code", None) in RETRYABLE_STATUS
        return False

    def delay_for(self, attempt: int) -> float:
        raw = min(self.max_delay, self.base_delay * (2 ** attempt))
        return raw * (1 + random.uniform(-self.jitter, self.jitter))


@dataclass
class ToolCallRecord:
    """单次工具调用记录。"""

    iteration: int
    tool_name: str
    arguments: str
    ok: bool
    result_chars: int = 0
    error: str = ""
    deduped: bool = False  # 命中只读工具的重复调用短路（省 token，行为仍计入统计）

    @property
    def skill_name(self) -> str:
        try:
            return (json.loads(self.arguments) or {}).get("skill_name", "")
        except (json.JSONDecodeError, TypeError):
            return ""


@dataclass
class AgentTrace:
    """单次执行的完整轨迹（loop 与静态模式共用）。"""

    stop_reason: str = "unknown"  # final_answer/max_iterations/budget_exceeded/timeout/error/static/fallback_static
    iterations: int = 0
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    loaded_skills: List[str] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration: float = 0.0
    retries: int = 0
    error: str = ""

    @property
    def loaded_skills_unique(self) -> List[str]:
        seen: List[str] = []
        for s in self.loaded_skills:
            if s and s not in seen:
                seen.append(s)
        return seen

    @property
    def redundant_loads(self) -> int:
        """重复加载次数（同一技能被加载 >1 次）。"""
        return len(self.loaded_skills) - len(self.loaded_skills_unique)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stop_reason": self.stop_reason,
            "iterations": self.iterations,
            "tool_calls": [asdict(tc) | {"skill_name": tc.skill_name} for tc in self.tool_calls],
            "loaded_skills": self.loaded_skills_unique,
            "redundant_loads": self.redundant_loads,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "duration_ms": int(self.duration * 1000),
            "retries": self.retries,
            "error": self.error,
        }


class ToolRegistry:
    """工具注册表：OpenAI tools schema 生成 + 调用分派 + 错误兜底。

    工具对象契约（见 load_skill_tool.LoadSkillTool）：
      name / description / parameters(JSON Schema) / execute(**kwargs) -> str
    """

    def __init__(self, tools: List[Any]):
        self._tools: Dict[str, Any] = {t.name: t for t in tools}

    def openai_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def get(self, tool_name: str) -> Any:
        return self._tools.get(tool_name)

    def is_read_only(self, tool_name: str) -> bool:
        """只读工具（内置 read_only=True）的完全重复调用可安全短路。"""
        return bool(getattr(self._tools.get(tool_name), "read_only", False))

    def execute(self, tool_name: str, arguments: str) -> Tuple[str, bool, str]:
        """执行工具调用，返回 (回灌文本, 是否成功, 错误信息)。

        失败也必须返回文本：协议要求每个 tool_call_id 都有对应的 tool 消息，
        否则下一次请求会被 API 拒绝。
        """
        tool = self._tools.get(tool_name)
        if tool is None:
            err = f"unknown tool '{tool_name}'"
            return f"Error: {err}. Available: {', '.join(self._tools)}", False, err

        if arguments:
            try:
                kwargs = json.loads(arguments)
            except json.JSONDecodeError as e:
                err = f"invalid JSON arguments: {e}"
                return f"Error: {err}", False, err
        else:
            kwargs = {}

        if not isinstance(kwargs, dict):
            err = f"arguments must be an object, got {type(kwargs).__name__}"
            return f"Error: {err}", False, err

        try:
            result = tool.execute(**kwargs)
            return str(result), True, ""
        except Exception as e:  # 工具异常不得中断 loop
            err = f"{type(e).__name__}: {e}"
            return f"Error: tool '{tool_name}' failed: {err}", False, err


class AgenticExecutor:
    """技能自主加载的真 agentic loop 执行器。

    两种模式共用一个实例，保证 with_skill / agentic 配置在同一模型同参数下对比：
    - execute(prompt, skill_name)          静态注入技能正文 + 单次调用
    - execute_agentic(prompt, allowed)     loop：技能清单入 prompt，模型自选加载
    """

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "https://apihub.agnes-ai.com/v1",
        model: str = "agnes-3.0-flash",
        skills_dir: Optional[Path] = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        max_iterations: int = 6,
        max_total_tokens: int = 30000,
        total_time_budget: float = 300.0,
        timeout: float = 90.0,
        retry_policy: Optional[RetryPolicy] = None,
        client: Optional[Any] = None,
        log: bool = True,
    ):
        self.model = model
        self.skills_dir = Path(skills_dir) if skills_dir else Path(__file__).parent / "skills"
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.max_total_tokens = max_total_tokens
        self.total_time_budget = total_time_budget
        self.timeout = timeout
        self.log = log
        self.retry_policy = retry_policy or RetryPolicy()
        self.client = client or OpenAI(api_key=api_key, base_url=base_url)

        self.loader = SkillsLoader(self.skills_dir)
        self.registry = ToolRegistry([LoadSkillTool(self.loader)])
        self.last_trace = AgentTrace()

    # ------------------------------------------------------------------ 静态模式

    def _build_static_system_prompt(self, skill_name: Optional[str] = None) -> str:
        base_prompt = "你是一个有帮助的 AI 助手。请根据用户的问题给出准确、简洁的回答。"
        if skill_name and skill_name in self.loader.skills:
            skill_body = self.loader.skills[skill_name]["body"]
            return (
                f"{base_prompt}\n\n=== 已加载技能: {skill_name} ===\n"
                f"{skill_body}\n=== 技能结束 ===\n请在回答时参考以上技能知识。"
            )
        return base_prompt

    def execute(
        self, prompt: str, skill_name: Optional[str] = None
    ) -> Tuple[str, int, float]:
        """静态注入 + 单次调用（与 RealAgentExecutor 行为等价，供对比配置使用）。"""
        trace = AgentTrace(stop_reason="static")
        self.last_trace = trace
        start = time.time()

        try:
            response = self._create_completion(
                trace=trace,
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_static_system_prompt(skill_name)},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout,
            )
            output = response.choices[0].message.content or ""
            if response.usage:
                trace.prompt_tokens = response.usage.prompt_tokens or 0
                trace.completion_tokens = response.usage.completion_tokens or 0
                trace.total_tokens = response.usage.total_tokens or 0
        except Exception as e:
            output = f"[API调用失败] {type(e).__name__}: {e}"
            trace.stop_reason = "error"
            trace.error = f"{type(e).__name__}: {e}"

        trace.iterations = 1
        trace.duration = time.time() - start
        return output, trace.total_tokens or len(output) * 4, trace.duration

    # ------------------------------------------------------------------ agentic 模式

    def _build_agentic_system_prompt(self, skills_summary: str) -> str:
        return (
            "你是一个有帮助的 AI 助手，可以调用 load_skill 工具加载技能知识。\n\n"
            "工作方式：\n"
            "1. 先判断用户问题是否属于某个技能的领域；属于则调用 load_skill 加载该技能，再作答。\n"
            "2. 每个技能只需加载一次——已加载过的技能内容就在对话里，直接使用，不要重复加载。\n"
            "3. 问题与所有技能都无关时，不要调用工具，直接回答。\n"
            "4. 拿到所需技能后，基于技能内容给出准确、简洁的答案。\n\n"
            f"可用技能清单：\n{skills_summary}\n"
        )

    def execute_agentic(
        self, prompt: str, allowed_skills: Optional[List[str]] = None
    ) -> Tuple[str, int, float]:
        """跑一轮 agentic loop，返回 (output, total_tokens, duration)。

        轨迹写入 self.last_trace。用尽预算仍未产出正文时会追加一次
        「无工具收尾调用」，避免评估拿到空输出（降级路径）。
        """
        trace = AgentTrace()
        self.last_trace = trace
        start = time.time()

        allowed = set(allowed_skills) if allowed_skills else None
        summary = self._skills_summary(allowed)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._build_agentic_system_prompt(summary)},
            {"role": "user", "content": prompt},
        ]
        tools_schema = self._tools_schema(allowed)
        seen_calls: set = set()

        output = ""
        used_tokens = 0

        for iteration in range(1, self.max_iterations + 1):
            trace.iterations = iteration
            try:
                response = self._chat(messages, tools_schema, step=iteration, trace=trace)
            except Exception as e:
                trace.stop_reason = "error"
                trace.error = f"{type(e).__name__}: {e}"
                output = output or f"[API调用失败] {trace.error}"
                break

            self._accumulate_usage(trace, response)
            used_tokens = trace.prompt_tokens + trace.completion_tokens
            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", None) or []

            if not tool_calls:
                output = message.content or output
                trace.stop_reason = "final_answer"
                break

            messages.append(message)
            for call in tool_calls:
                result, ok, err, deduped = self._dispatch_tool(call, seen_calls)
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result}
                )
                record = ToolCallRecord(
                    iteration=iteration,
                    tool_name=call.function.name,
                    arguments=call.function.arguments or "",
                    ok=ok,
                    result_chars=len(result),
                    error=err,
                    deduped=deduped,
                )
                trace.tool_calls.append(record)
                if ok and record.skill_name:
                    trace.loaded_skills.append(record.skill_name)

            if used_tokens >= self.max_total_tokens:
                trace.stop_reason = "budget_exceeded"
                break
            if time.time() - start >= self.total_time_budget:
                trace.stop_reason = "timeout"
                break
        else:
            trace.stop_reason = "max_iterations"

        # 降级收尾：loop 用尽但没产出正文时，禁用工具再要一次最终答案
        if not output and trace.stop_reason in ("max_iterations", "budget_exceeded", "timeout"):
            messages.append(
                {
                    "role": "user",
                    "content": "请基于已获得的信息直接作答，不要再调用工具。",
                }
            )
            try:
                response = self._chat(messages, tools=None, trace=trace)
                self._accumulate_usage(trace, response)
                output = response.choices[0].message.content or ""
                trace.stop_reason = f"{trace.stop_reason}+forced_final"
            except Exception as e:
                trace.error = f"forced_final failed: {type(e).__name__}: {e}"
                output = output or f"[API调用失败] {trace.error}"

        trace.duration = time.time() - start
        trace.total_tokens = trace.prompt_tokens + trace.completion_tokens
        return output, trace.total_tokens or len(output) * 4, trace.duration

    # ------------------------------------------------------------------ 内部工具

    def _skills_summary(self, allowed: Optional[set]) -> str:
        exclude = None
        if allowed is not None:
            exclude = set(self.loader.skills) - allowed
        summary = self.loader.build_skills_summary(exclude=exclude)
        return summary or "（本环境没有可用技能，请直接回答）"

    def _tools_schema(self, allowed: Optional[set]) -> List[Dict[str, Any]]:
        """工具 schema；限定技能集时，在 description 里写明可选范围。"""
        schema = self.registry.openai_schema()
        if allowed is not None:
            names = ", ".join(sorted(allowed))
            for item in schema:
                item["function"]["description"] += f"（可选值：{names}）"
        return schema

    def _dispatch_tool(self, call: Any, seen_calls: set) -> Tuple[str, bool, str, bool]:
        """执行工具调用，返回 (回灌文本, 是否成功, 错误, 是否短路)。

        只读工具的**完全重复调用**（同工具 + 同规范化参数）走短路：协议要求每个
        tool_call_id 都要有 tool 消息，但没必要重发全文——实测 agnes-3.0-flash
        会重复加载同一技能，白烧一轮 token。短路不影响行为统计：「想重复几次」
        仍记入 trace，供评估观测。
        """
        name = call.function.name
        arguments = call.function.arguments or ""
        call_key = (name, self._canonical_args(arguments))

        if self.registry.is_read_only(name) and call_key in seen_calls:
            notice = (
                f"重复调用提示：{name} 已用相同参数调用过，结果见前面的工具消息，"
                f"请直接使用已有内容作答，不要重复调用。"
            )
            return notice, True, "", True

        result, ok, err = self.registry.execute(name, arguments)
        seen_calls.add(call_key)
        return result, ok, err, False

    @staticmethod
    def _canonical_args(arguments: str) -> str:
        """规范化参数串（键排序），用于稳定的重复调用判定。"""
        if not arguments:
            return "{}"
        try:
            return json.dumps(json.loads(arguments), sort_keys=True, ensure_ascii=False)
        except json.JSONDecodeError:
            return arguments

    def _create_completion(self, trace: Optional[AgentTrace] = None, **kwargs):
        """带指数退避的模型调用（瞬时错误重试；确定性错误直接抛出）。"""
        policy = self.retry_policy
        attempt = 0
        while True:
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as error:  # noqa: BLE001 - 必须按错误类型分流
                if attempt >= policy.max_retries or not policy.is_retryable(error):
                    raise
                delay = policy.delay_for(attempt)
                attempt += 1
                if trace is not None:
                    trace.retries += 1
                if self.log:
                    print(f"    [retry {attempt}/{policy.max_retries}] "
                          f"{type(error).__name__} -> 等 {delay:.1f}s 重试")
                time.sleep(delay)

    def _chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        step: Optional[int] = None,
        trace: Optional[AgentTrace] = None,
    ):
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if self.log:
            n_tools = len(tools) if tools else 0
            label = f"step={step}" if step else "final"
            print(f"    [agent] {label} messages={len(messages)} tools={n_tools} -> {self.model}")
        return self._create_completion(trace=trace, **kwargs)

    @staticmethod
    def _accumulate_usage(trace: AgentTrace, response: Any) -> None:
        usage = getattr(response, "usage", None)
        if not usage:
            return
        trace.prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
        trace.completion_tokens += getattr(usage, "completion_tokens", 0) or 0


def create_agentic_executor(skills_dir: Optional[Path] = None, **overrides) -> AgenticExecutor:
    """按环境变量创建 agentic 执行器（缺省 agnes-3.0-flash，2026-09-28 探测可用）。"""
    import os

    params = dict(
        api_key=os.environ.get("AGNES_API_KEY", ""),
        base_url=os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        model=os.environ.get("AGNES_MODEL", "agnes-3.0-flash"),
        skills_dir=skills_dir,
    )
    params.update(overrides)
    return AgenticExecutor(**params)
