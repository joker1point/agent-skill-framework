"""R1：dev-lessons 可检索库效用三臂对照（without / inject / retrieve）。

- without  ：无技能、无工具（executor.execute(prompt) 静态无注入），模型先验基线
- inject   ：把题目对应的 reference 文件全文静态注入 system prompt（oracle：人工已定位对文件）
- retrieve ：真 agentic loop，allowed=[dev-lessons]，工具=[load_skill, read_skill_ref]，
             agent 自主走「SKILL.md 索引 → 读 references」

用法：
    python run_devlessons_eval.py                # 跑三臂
    python run_devlessons_eval.py without,inject   # 只跑两臂（先看基线）
    python run_devlessons_eval.py retrieve         # 只跑检索臂
凭据：本仓库 .env 优先；缺 KEY 时回退读取 CharacterSeed 的 .env（只取 AGNES_API_KEY / AGNES_BASE_URL）。
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.stdout.reconfigure(encoding="utf-8")

from agentic_executor import AgenticExecutor, AgentTrace, RetryPolicy, ToolRegistry
from load_skill_tool import LoadSkillTool
from read_skill_ref import ReadSkillRefTool

HERE = Path(__file__).parent
SKILLS_DIR = HERE / "skills"
DEVLESSONS = "dev-lessons"
EVALS_PATH = SKILLS_DIR / DEVLESSONS / "evals" / "evals.json"
FALLBACK_ENV = Path(os.path.expandvars(r"%USERPROFILE%\Documents\trae_projects\luyan\CharacterSeed\.env"))


def load_credentials() -> None:
    """加载凭据到环境变量（已设置的不覆盖）。"""
    from dotenv import dotenv_values

    local_env = HERE / ".env"
    if local_env.exists():
        for key, value in (dotenv_values(local_env) or {}).items():
            if value and not os.environ.get(key):
                os.environ[key] = value

    if not os.environ.get("AGNES_API_KEY") and FALLBACK_ENV.exists():
        values = dotenv_values(FALLBACK_ENV) or {}
        for key in ("AGNES_API_KEY", "AGNES_BASE_URL"):
            if values.get(key) and not os.environ.get(key):
                os.environ[key] = values[key]


class DevLessonsExecutor(AgenticExecutor):
    """在 agentic loop 中追加 read_skill_ref，复现真实检索链路。"""

    def __init__(self, **kwargs):
        kwargs.setdefault("skills_dir", SKILLS_DIR)
        kwargs.setdefault("api_key", os.environ.get("AGNES_API_KEY", ""))
        kwargs.setdefault(
            "base_url",
            os.environ.get("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1"),
        )
        kwargs.setdefault(
            "retry_policy", RetryPolicy(max_retries=4, base_delay=5.0, max_delay=60.0)
        )
        super().__init__(**kwargs)
        self.registry = ToolRegistry(
            [LoadSkillTool(self.loader), ReadSkillRefTool(self.loader)]
        )

    def execute_injected(self, prompt: str, injected_text: str):
        """静态注入参考资料全文（oracle：人工已定位到正确文件）。"""
        trace = AgentTrace(stop_reason="static")
        self.last_trace = trace
        start = time.time()
        sys_prompt = (
            "你是一个有帮助的 AI 助手。请根据用户的问题给出准确、简洁的回答。\n\n"
            "=== 已检索到的参考资料 ===\n" + injected_text +
            "\n=== 资料结束 ===\n请基于以上资料作答。"
        )
        try:
            resp = self._create_completion(
                trace=trace, model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens, temperature=self.temperature,
                timeout=self.timeout,
            )
            output = resp.choices[0].message.content or ""
            self._accumulate_usage(trace, resp)
        except Exception as e:  # noqa: BLE001
            output = f"[API调用失败] {type(e).__name__}: {e}"
            trace.stop_reason = "error"
            trace.error = f"{type(e).__name__}: {e}"
        trace.iterations = 1
        trace.duration = time.time() - start
        return output, trace.total_tokens or len(output) * 4, trace.duration


def load_cases() -> List[Dict[str, Any]]:
    return json.loads(EVALS_PATH.read_text(encoding="utf-8"))["evals"]


def read_ref(rel: str) -> str:
    p = SKILLS_DIR / DEVLESSONS / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""


def check_assert(output: str, case: Dict[str, Any]) -> bool:
    subs = [a.get("substring", "") for a in case.get("assertions", [])
            if a.get("type") == "contains"]
    if case.get("assert_any"):
        return any(s and s in output for s in subs)
    return all(s and s in output for s in subs)


def main():
    load_credentials()
    if not os.environ.get("AGNES_API_KEY"):
        print("[WARN] 环境变量 AGNES_API_KEY 仍未设置，API 调用将失败。")
    arms = (set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1]
            else {"without", "inject", "retrieve"})
    cases = load_cases()
    ex = DevLessonsExecutor()
    tally = {"without": 0, "inject": 0, "retrieve": 0}
    print(f"模型: {ex.model}  题目数: {len(cases)}  本次臂: {sorted(arms)}\n")

    for case in cases:
        prompt = case["prompt"]
        ref_text = read_ref(case.get("inject_ref", ""))

        out_w = tok_w = dur_w = r_w = None
        out_i = tok_i = dur_i = r_i = None
        out_r = tok_r = dur_r = r_r = None

        if "without" in arms:
            out_w, tok_w, dur_w = ex.execute(prompt)
            r_w = check_assert(out_w, case)
            tally["without"] += int(r_w)
        if "inject" in arms:
            out_i, tok_i, dur_i = ex.execute_injected(prompt, ref_text)
            r_i = check_assert(out_i, case)
            tally["inject"] += int(r_i)
        if "retrieve" in arms:
            out_r, tok_r, dur_r = ex.execute_agentic(prompt, allowed_skills=[DEVLESSONS])
            r_r = check_assert(out_r, case)
            tally["retrieve"] += int(r_r)

        refs_read = [
            (json.loads(t.arguments).get("relative_path", ""))
            for t in ex.last_trace.tool_calls
            if t.tool_name == "read_skill_ref" and t.ok
        ]
        loaded = ex.last_trace.loaded_skills_unique
        stop = ex.last_trace.stop_reason

        print(f"#{case['id']} {case['name']}")
        if "without" in arms:
            print(f"   without : {'✓' if r_w else '✗'} ({tok_w}t,{dur_w:.1f}s)")
        if "inject" in arms:
            print(f"   inject  : {'✓' if r_i else '✗'} ({tok_i}t,{dur_i:.1f}s)")
        if "retrieve" in arms:
            print(f"   retrieve: {'✓' if r_r else '✗'} ({tok_r}t,{dur_r:.1f}s) "
                  f"stop={stop} loaded={loaded} refs_read={refs_read}")
        print()

    n = len(cases)
    print("=" * 52)
    parts = []
    if "without" in arms:
        parts.append(f"without={tally['without']}/{n}")
    if "inject" in arms:
        parts.append(f"inject={tally['inject']}/{n}")
    if "retrieve" in arms:
        parts.append(f"retrieve={tally['retrieve']}/{n}")
    print("通过率  " + "  ".join(parts))
    print(f"模型: {ex.model}")
    print("=" * 52)


if __name__ == "__main__":
    main()
