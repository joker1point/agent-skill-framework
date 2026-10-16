"""AgenticExecutor loop 逻辑测试（mock client，不消耗真实 API）。

覆盖：正常 loop / 并行 tool_calls / 重复加载 / 工具错误不中断 /
轮数用尽强制收尾 / 预算超限 / API 异常 / 静态模式兼容 / 技能白名单。

运行：
  python test_agentic_executor.py        # 无 pytest 直接跑
  pytest test_agentic_executor.py -q     # pytest
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

from agentic_executor import AgenticExecutor, AgentTrace

sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- mock 基础设施

def make_tool_call(call_id: str, name: str, arguments: str) -> SimpleNamespace:
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))


def make_response(content=None, tool_calls=None, prompt_tokens=10, completion_tokens=5):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    choice = SimpleNamespace(
        message=message, finish_reason="tool_calls" if tool_calls else "stop"
    )
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
    return SimpleNamespace(choices=[choice], usage=usage)


class FakeClient:
    """按脚本逐次返回响应；脚本元素为 Exception 时抛出。"""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        if not self.script:
            raise AssertionError("FakeClient: 脚本已用尽，说明发生了预期外的额外调用")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def setup_skills(root: Path) -> Path:
    skills_dir = root / "skills"
    specs = {
        "weather": ("查询天气", "# 天气技能\n用 wttr.in 查询天气。"),
        "github": ("GitHub 操作", "# GitHub 技能\n用 gh 命令操作仓库。"),
    }
    for name, (desc, body) in specs.items():
        d = skills_dir / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {desc}\ntags: {name}\n---\n\n{body}\n",
            encoding="utf-8",
        )
    return skills_dir


def make_executor(script, **kwargs) -> tuple[AgenticExecutor, FakeClient, tempfile.TemporaryDirectory]:
    tmp = tempfile.TemporaryDirectory()
    skills_dir = setup_skills(Path(tmp.name))
    client = FakeClient(script)
    executor = AgenticExecutor(
        model="fake-model",
        skills_dir=skills_dir,
        client=client,
        log=False,
        **kwargs,
    )
    return executor, client, tmp


# ---------------------------------------------------------------- 用例

def test_normal_loop():
    """单轮工具调用 -> 回灌 -> 最终答案。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(content="北京今天晴，18°C"),
    ])
    output, tokens, duration = executor.execute_agentic("北京天气怎么样")

    assert output == "北京今天晴，18°C", output
    t = executor.last_trace
    assert t.stop_reason == "final_answer", t.stop_reason
    assert t.iterations == 2, t.iterations
    assert t.loaded_skills == ["weather"], t.loaded_skills
    assert t.tool_calls[0].ok is True

    # 第二次请求必须包含 tool 消息且 tool_call_id 对齐
    msgs = client.requests[1]["messages"]
    tool_msgs = [m for m in msgs if isinstance(m, dict) and m.get("role") == "tool"]
    assert len(tool_msgs) == 1 and tool_msgs[0]["tool_call_id"] == "c1"
    assert "<skill name=\"weather\">" in tool_msgs[0]["content"]

    # 系统提示是技能清单（Level 1），不含技能正文
    system = client.requests[0]["messages"][0]["content"]
    assert "weather" in system and "wttr.in" not in system
    tmp.cleanup()
    print("  [ok] test_normal_loop")


def test_parallel_tool_calls():
    """同一轮多个 tool_calls（agnes-2.5-flash 行为）必须逐个回灌。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[
            make_tool_call("c1", "load_skill", '{"skill_name": "weather"}'),
            make_tool_call("c2", "load_skill", '{"skill_name": "github"}'),
        ]),
        make_response(content="两个技能都用上了"),
    ])
    output, _, _ = executor.execute_agentic("查天气并看 GitHub 趋势")

    assert output == "两个技能都用上了"
    msgs = client.requests[1]["messages"]
    tool_msgs = [m for m in msgs if isinstance(m, dict) and m.get("role") == "tool"]
    assert len(tool_msgs) == 2, len(tool_msgs)
    assert {m["tool_call_id"] for m in tool_msgs} == {"c1", "c2"}
    assert executor.last_trace.loaded_skills_unique == ["weather", "github"]
    tmp.cleanup()
    print("  [ok] test_parallel_tool_calls")


def test_redundant_load_tracked():
    """重复加载同一技能会被计入 redundant_loads。"""
    executor, _, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(tool_calls=[make_tool_call("c2", "load_skill", '{"skill_name": "weather"}')]),
        make_response(content="答案"),
    ])
    executor.execute_agentic("北京天气")
    t = executor.last_trace
    assert t.loaded_skills_unique == ["weather"]
    assert t.redundant_loads == 1, t.redundant_loads
    tmp.cleanup()
    print("  [ok] test_redundant_load_tracked")


def test_repeated_readonly_call_short_circuits():
    """只读工具重复调用短路：不重发全文，但行为仍计入 trace。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(tool_calls=[make_tool_call("c2", "load_skill", '{"skill_name": "weather"}')]),
        make_response(content="答案"),
    ])
    executor.execute_agentic("北京天气")

    msgs = client.requests[2]["messages"]
    tool_msgs = [m for m in msgs if isinstance(m, dict) and m.get("role") == "tool"]
    assert len(tool_msgs) == 2, len(tool_msgs)
    assert '<skill name="weather">' in tool_msgs[0]["content"]
    assert "重复调用提示" in tool_msgs[1]["content"], tool_msgs[1]["content"]
    assert len(tool_msgs[1]["content"]) < 200, "短路提示必须是轻量文本"

    t = executor.last_trace
    assert t.redundant_loads == 1, t.redundant_loads
    assert t.tool_calls[1].deduped is True
    assert t.tool_calls[0].deduped is False
    tmp.cleanup()
    print("  [ok] test_repeated_readonly_call_short_circuits")


def test_different_args_not_short_circuited():
    """参数不同的调用不算重复，必须正常执行。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(tool_calls=[make_tool_call("c2", "load_skill", '{"skill_name": "github"}')]),
        make_response(content="答案"),
    ])
    executor.execute_agentic("问题")

    assert all(not r.deduped for r in executor.last_trace.tool_calls)
    tool_msgs = [m for m in client.requests[2]["messages"]
                 if isinstance(m, dict) and m.get("role") == "tool"]
    assert "github" in tool_msgs[1]["content"]
    tmp.cleanup()
    print("  [ok] test_different_args_not_short_circuited")


def test_canonical_args_stable():
    """重复判定用的参数规范化：格式差异不影响等价性。"""
    canonical = AgenticExecutor._canonical_args
    assert canonical('{"skill_name": "weather"}') == canonical('{"skill_name":"weather"}')
    assert canonical("") == "{}"
    assert canonical("not-json") == "not-json"
    print("  [ok] test_canonical_args_stable")


def test_tool_error_does_not_break_loop():
    """未知工具 / 非法参数：错误回灌，loop 继续并给出答案。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[
            make_tool_call("c1", "no_such_tool", "{}"),
            make_tool_call("c2", "load_skill", "not-json"),
        ]),
        make_response(content="降级后的答案"),
    ])
    output, _, _ = executor.execute_agentic("随便问问")

    assert output == "降级后的答案"
    t = executor.last_trace
    assert t.tool_calls[0].ok is False and "unknown tool" in t.tool_calls[0].error
    assert t.tool_calls[1].ok is False and "invalid JSON" in t.tool_calls[1].error
    tool_msgs = [m for m in client.requests[1]["messages"]
                 if isinstance(m, dict) and m.get("role") == "tool"]
    assert len(tool_msgs) == 2 and all("Error:" in m["content"] for m in tool_msgs)
    assert t.loaded_skills == []
    tmp.cleanup()
    print("  [ok] test_tool_error_does_not_break_loop")


def test_max_iterations_forced_final():
    """轮数用尽且无正文时追加无工具收尾调用。"""
    executor, client, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(tool_calls=[make_tool_call("c2", "load_skill", '{"skill_name": "github"}')]),
        make_response(content="收尾答案"),
    ], max_iterations=2)
    output, _, _ = executor.execute_agentic("问题")

    assert output == "收尾答案", output
    t = executor.last_trace
    assert t.stop_reason == "max_iterations+forced_final", t.stop_reason
    assert t.iterations == 2
    final_req = client.requests[-1]
    assert "tools" not in final_req, "收尾调用必须禁用工具"
    tmp.cleanup()
    print("  [ok] test_max_iterations_forced_final")


def test_budget_exceeded():
    """token 预算超限时停止并进入收尾。"""
    executor, _, tmp = make_executor([
        make_response(
            tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')],
            prompt_tokens=1000, completion_tokens=100,
        ),
        make_response(content="预算内收尾"),
    ], max_total_tokens=500)
    output, _, _ = executor.execute_agentic("问题")

    assert output == "预算内收尾"
    assert "budget_exceeded" in executor.last_trace.stop_reason, executor.last_trace.stop_reason
    tmp.cleanup()
    print("  [ok] test_budget_exceeded")


class _FastRetryPolicy:
    """测试用：零延迟重试，把 RuntimeError 视为瞬时错误。"""

    max_retries = 2
    base_delay = 0.0
    max_delay = 0.0
    jitter = 0.0

    def is_retryable(self, error):
        return isinstance(error, RuntimeError)

    def delay_for(self, attempt):
        return 0.0


def test_retry_then_success():
    """瞬时错误退避后恢复：trace.retries 如实记录重试次数。"""
    executor, client, tmp = make_executor([
        RuntimeError("transient-1"),
        RuntimeError("transient-2"),
        make_response(content="重试后成功"),
    ])
    executor.retry_policy = _FastRetryPolicy()
    output, _, _ = executor.execute_agentic("问题")

    assert output == "重试后成功", output
    assert executor.last_trace.retries == 2, executor.last_trace.retries
    assert len(client.requests) == 3
    tmp.cleanup()
    print("  [ok] test_retry_then_success")


def test_retry_exhausted_reports_error():
    """重试耗尽后如实报错，不掩盖失败。"""
    executor, _, tmp = make_executor([
        RuntimeError("t1"), RuntimeError("t2"), RuntimeError("t3"),
    ])
    executor.retry_policy = _FastRetryPolicy()
    output, _, _ = executor.execute_agentic("问题")

    assert "API调用失败" in output and "t3" in output
    assert executor.last_trace.stop_reason == "error"
    assert executor.last_trace.retries == 2, executor.last_trace.retries
    tmp.cleanup()
    print("  [ok] test_retry_exhausted_reports_error")


def test_retry_policy_classification():
    """错误分类：超时可重试、普通异常不可重试。"""
    import httpx
    from openai import APITimeoutError

    from agentic_executor import RetryPolicy

    policy = RetryPolicy()
    timeout_error = APITimeoutError(request=httpx.Request("POST", "http://example.invalid"))
    assert policy.is_retryable(timeout_error) is True
    assert policy.is_retryable(ValueError("确定性错误")) is False
    assert policy.delay_for(0) > 0
    print("  [ok] test_retry_policy_classification")


def test_api_error_reported():
    """API 异常：返回错误文本、stop_reason=error，不抛异常。"""
    executor, _, tmp = make_executor([RuntimeError("boom")])
    output, _, _ = executor.execute_agentic("问题")

    assert "API调用失败" in output and "boom" in output
    assert executor.last_trace.stop_reason == "error"
    tmp.cleanup()
    print("  [ok] test_api_error_reported")


def test_static_mode_still_works():
    """静态模式（execute）保持单次调用语义，供三方对比使用。"""
    executor, client, tmp = make_executor([make_response(content="静态答案")])
    output, tokens, duration = executor.execute("问题", skill_name="weather")

    assert output == "静态答案"
    assert executor.last_trace.stop_reason == "static"
    assert executor.last_trace.iterations == 1
    system = client.requests[0]["messages"][0]["content"]
    assert "wttr.in" in system, "静态模式必须注入技能正文"
    assert "tools" not in client.requests[0]
    tmp.cleanup()
    print("  [ok] test_static_mode_still_works")


def test_allowed_skills_filter():
    """技能白名单：清单与工具描述只含允许项。"""
    executor, client, tmp = make_executor([
        make_response(content="回答"),
    ])
    executor.execute_agentic("问题", allowed_skills=["weather"])

    req = client.requests[0]
    system = req["messages"][0]["content"]
    assert "weather" in system and "github" not in system, system
    tool_desc = req["tools"][0]["function"]["description"]
    assert "weather" in tool_desc, tool_desc
    tmp.cleanup()
    print("  [ok] test_allowed_skills_filter")


def test_trace_to_dict_serializable():
    """trace 序列化：可直接写入 JSON 报告。"""
    import json as _json
    executor, _, tmp = make_executor([
        make_response(tool_calls=[make_tool_call("c1", "load_skill", '{"skill_name": "weather"}')]),
        make_response(content="答案"),
    ])
    executor.execute_agentic("问题")
    data = executor.last_trace.to_dict()
    text = _json.dumps(data, ensure_ascii=False)
    assert data["stop_reason"] == "final_answer"
    assert data["loaded_skills"] == ["weather"]
    assert "tool_calls" in data and len(data["tool_calls"]) == 1
    assert '"skill_name": "weather"' in text
    tmp.cleanup()
    print("  [ok] test_trace_to_dict_serializable")


ALL_TESTS = [
    test_normal_loop,
    test_parallel_tool_calls,
    test_redundant_load_tracked,
    test_repeated_readonly_call_short_circuits,
    test_different_args_not_short_circuited,
    test_canonical_args_stable,
    test_tool_error_does_not_break_loop,
    test_retry_then_success,
    test_retry_exhausted_reports_error,
    test_retry_policy_classification,
    test_max_iterations_forced_final,
    test_budget_exceeded,
    test_api_error_reported,
    test_static_mode_still_works,
    test_allowed_skills_filter,
    test_trace_to_dict_serializable,
]


if __name__ == "__main__":
    print("=" * 60)
    print("AgenticExecutor 测试（mock client）")
    print("=" * 60)
    failures = []
    for fn in ALL_TESTS:
        try:
            fn()
        except AssertionError as e:
            failures.append((fn.__name__, e))
            print(f"  [FAIL] {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures.append((fn.__name__, e))
            print(f"  [ERROR] {fn.__name__}: {type(e).__name__}: {e}")

    print("-" * 60)
    if failures:
        print(f"✗ {len(failures)}/{len(ALL_TESTS)} 个用例失败")
        sys.exit(1)
    print(f"✓ 全部 {len(ALL_TESTS)} 个用例通过")
