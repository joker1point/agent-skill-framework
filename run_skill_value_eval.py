#!/usr/bin/env python3
"""技能价值与自主路由评估（v2 实验）—— 见 PLAN-skill-value-eval.md。

用法：
  python run_skill_value_eval.py create-evals        # 写入 3 个新技能的 evals.json（幂等）
  python run_skill_value_eval.py precheck            # 零成本：断言 token 预检 + 泄题检查
  python run_skill_value_eval.py run <skill>         # 跑一个技能（见 MANIFEST）
  python run_skill_value_eval.py summary             # 读盘汇总（不调 API）

纪律（PLAN §3 / §4）：
  · 断言 token 必须先过预检，才允许跑批；
  · 含 error 的批次整体作废，重跑；
  · 预期没中 → 先修断言 / 换题，再谈结论。

复用（不复制）：run_agentic_eval.build_executor（凭据 + 退避）、
SkillEvals / SkillBenchmark / BenchmarkConfig / AgenticExecutor。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
SKILLS_DIR = BASE_DIR / "skills"
WORKSPACE_DIR = BASE_DIR / "skill-workspace"

# skill -> iteration 号（新技能从 1 起；weather 已到 iteration-6，对照跑在 7）
MANIFEST = {"preset-navigator": 1, "skills-manager": 1, "code-tools": 1, "weather": 7}
NEW_SKILLS = ("preset-navigator", "skills-manager", "code-tools")

# ---------------------------------------------------------------- 用例定义（唯一来源）
# create-evals 会把它们写入 skills/<name>/evals/evals.json；
# 断言钉的都是"模型不可能凭空知道"的私有 token（PLAN §1）。
CASES: dict[str, list[dict]] = {
    "preset-navigator": [
        {
            "id": 1,
            "name": "pn-db-file",
            "prompt": "我要直接读数据库统计技能数量，这些技能和 Preset 的数据存在哪个文件里？用什么工具查？",
            "expected_output": "给出 ~/.skills-manager/skills-manager.db 路径与 sqlite3 查询方式",
            "assertions": [
                {"type": "contains", "name": "has_db_file", "substring": "skills-manager.db"},
                {"type": "regex", "name": "has_sqlite_or_sql", "pattern": "sqlite3|SELECT"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
        {
            "id": 2,
            "name": "pn-active-scenario",
            "prompt": "我想知道现在激活的是哪个 Preset，用 Python 查的话要看哪张表、怎么查？",
            "expected_output": "说明查 active_scenario 表（key='current'）",
            "assertions": [
                {"type": "contains", "name": "has_active_scenario", "substring": "active_scenario"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
        {
            "id": 3,
            "name": "pn-scenario-skills",
            "prompt": "给定一个技能名，想知道它属于哪些 Preset，SQL 怎么写？",
            "expected_output": "说明用 scenario_skills 关联表 JOIN",
            "assertions": [
                {"type": "contains", "name": "has_scenario_skills", "substring": "scenario_skills"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
    ],
    "skills-manager": [
        {
            "id": 1,
            "name": "sm-central-dir",
            "prompt": "这些 AI 编码工具的 skills 想集中到一处管理，默认的中央库目录在哪？",
            "expected_output": "给出 ~/.skills-manager/skills/ 中央库路径",
            "assertions": [
                {"type": "contains", "name": "has_central_dir", "substring": ".skills-manager"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
        {
            "id": 2,
            "name": "sm-preset-add",
            "prompt": "把一个技能加进某个 Preset，命令行怎么写？",
            "expected_output": "给出 skills-manager-cli presets add-skill <preset> <skill>",
            "assertions": [
                # 2026-09-29 首跑修正：contains_all["presets","add-skill"] 被通用答案蒙中
                # （编造的 dify 命令里含 "add-skill"）→ 改为钉工具名 + 命令形态
                {"type": "contains", "name": "has_cli_name", "substring": "skills-manager-cli"},
                {"type": "regex", "name": "has_preset_add_skill", "pattern": "presets\\s+add-skill"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
    ],
    "code-tools": [
        {
            "id": 1,
            "name": "ct-review-graph",
            "prompt": "我要做 PR 审查、想要一张专做代码审查的图谱，用这组工具里的哪个？",
            "expected_output": "推荐 code-review-graph（专做代码审查 / PR 把关）",
            "assertions": [
                {"type": "contains", "name": "has_review_graph", "substring": "code-review-graph"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
        {
            "id": 2,
            "name": "ct-memory-mcp",
            "prompt": "团队要共享代码库记忆、还要语义检索，用这组工具里的哪个？",
            "expected_output": "推荐 codebase-memory-mcp（团队共享 + 语义检索）",
            "assertions": [
                {"type": "contains", "name": "has_memory_mcp", "substring": "codebase-memory-mcp"},
                {"type": "length", "name": "min_length", "min_length": 10},
            ],
        },
    ],
}


# ---------------------------------------------------------------- tools
def skill_body(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


def _assertion_tokens(assertion: dict) -> list[str]:
    kind = assertion.get("type", "contains")
    if kind == "contains":
        return [assertion["substring"]]
    if kind == "contains_all":
        return list(assertion["substrings"])
    if kind == "regex":
        return [assertion["pattern"]]
    return []


def _token_in_text(kind: str, assertion: dict, text: str) -> bool:
    lower = text.lower()
    if kind == "contains":
        return assertion["substring"].lower() in lower
    if kind == "contains_all":
        return all(s.lower() in lower for s in assertion["substrings"])
    if kind == "regex":
        return bool(re.search(assertion["pattern"], text, re.IGNORECASE))
    return True  # length 等不参与 token 预检


# ---------------------------------------------------------------- create-evals
def cmd_create_evals() -> int:
    from skill_evals import SkillEvals

    evals = SkillEvals(SKILLS_DIR)
    for name in NEW_SKILLS:
        ok = evals.create_eval_file(name, CASES[name])
        path = SKILLS_DIR / name / "evals" / "evals.json"
        print(f"[create-evals] {name}: {'已写入' if ok else '写入失败'} -> {path}")
    return 0


# ---------------------------------------------------------------- precheck
def cmd_precheck() -> int:
    print("=" * 76)
    print("断言预检（零成本）：token 必须在技能正文中命中；且不得出现在问题里（防泄题）")
    print("=" * 76)
    failures = 0
    for name in NEW_SKILLS:
        body = skill_body(name)
        print(f"\n[{name}] SKILL.md {len(body)} 字符")
        for case in CASES[name]:
            prompt_lower = case["prompt"].lower()
            marks = []
            for assertion in case["assertions"]:
                kind = assertion.get("type", "contains")
                if kind == "length":
                    continue
                hit = _token_in_text(kind, assertion, body)
                tokens = _assertion_tokens(assertion)
                leak = any(t.lower() in prompt_lower for t in tokens)
                flags = "✓" if hit and not leak else "✗"
                if not hit or leak:
                    failures += 1
                detail = "/".join(tokens)
                why = ("正文未命中" if not hit else "") + (" 问题泄题" if leak else "")
                marks.append(f"{flags} {assertion['name']}: {detail}{'  ← ' + why if why else ''}")
            print(f"  {case['name']}")
            for m in marks:
                print(f"      {m}")
    # weather：沿用现有用例，不改动，只确认存在
    wev = SKILLS_DIR / "weather" / "evals" / "evals.json"
    if wev.exists():
        data = json.loads(wev.read_text(encoding="utf-8"))
        names = [e.get("name") for e in data.get("evals", [])]
        print(f"\n[weather] 沿用现有用例（{len(names)} 条，不改动）: {', '.join(names)}")
    else:
        print("\n[weather] 缺少 evals.json —— 需要先跑 setup_weather_evals")
        failures += 1
    print(f"\n预检结果：{'全部通过' if failures == 0 else f'{failures} 项未通过'}")
    return 0 if failures == 0 else 1


# ---------------------------------------------------------------- run
def cmd_run(skill: str) -> int:
    from run_agentic_eval import build_executor
    from skill_benchmark import BenchmarkConfig, SkillBenchmark
    from skill_evals import SkillEvals

    if skill not in MANIFEST:
        print(f"未知技能：{skill}（可选：{', '.join(MANIFEST)}）")
        return 2
    iteration = MANIFEST[skill]
    cases = SkillEvals(SKILLS_DIR).load_evals(skill)
    if not cases:
        print(f"{skill} 没有用例文件；先跑 create-evals（weather 用现有文件）")
        return 2

    configs = [
        BenchmarkConfig(name="agentic", skill_name=skill, agentic=True),
        BenchmarkConfig(name="with_skill", skill_name=skill),
    ]
    if skill != "weather":
        # 固定注入臂：模拟"没有人工路由"时的静态注入（PLAN §2 实验二）
        configs.append(BenchmarkConfig(name="with_skill_weather", skill_name="weather"))
    configs.append(BenchmarkConfig(name="without_skill", baseline=True))

    executor = build_executor()
    executor.log = False  # 控制台保持简洁；全过程落盘到 skill-workspace
    print(f"模型: {executor.model}")
    print(f"技能: {skill} | iteration-{iteration} | 用例 {len(cases)} 条 | "
          f"臂: {' / '.join(c.name for c in configs)}")
    print("跑批中……（每条约 3–15s；限流会自动退避）")

    benchmark = SkillBenchmark(SKILLS_DIR, WORKSPACE_DIR, executor=executor)
    summary = benchmark.run_benchmark(skill, configs, iteration=iteration)
    _print_summary(skill, iteration, summary)
    return 0


def _print_summary(skill: str, iteration: int, summary) -> None:
    print()
    print("=" * 76)
    print(f"{skill} · iteration-{iteration} · 对比汇总")
    print("=" * 76)
    print(f"{'配置':<20}{'通过率':>8}{'均Tokens':>10}{'均耗时':>10}{'均轮数':>8}{'均工具调用':>10}")
    for name in summary.configs:
        print(f"{name:<20}"
              f"{summary.pass_rates.get(name, 0):>7.1f}%"
              f"{summary.avg_tokens.get(name, 0):>10.0f}"
              f"{summary.avg_duration.get(name, 0):>8.0f}ms"
              f"{summary.avg_iterations.get(name, 0):>8.1f}"
              f"{summary.avg_tool_calls.get(name, 0):>10.1f}")

    errors = 0
    print("\n停止原因分布:")
    for name in summary.configs:
        counts = summary.stop_reason_counts.get(name) or {}
        errors += counts.get("error", 0)
        detail = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items())) or "-"
        print(f"  {name}: {detail}")

    routed, total = 0, 0
    print("\nagentic 路由明细（loaded_skills，应为被考技能）:")
    for result in summary.results.get("agentic", []):
        metrics = result.metrics
        loaded = list(metrics.loaded_skills) if metrics and metrics.loaded_skills else []
        hit = skill in loaded
        routed += hit
        total += 1
        print(f"  {result.eval_name}: loaded=[{', '.join(loaded) or '（未加载）'}] "
              f"steps={metrics.iterations if metrics else 0} "
              f"stop={metrics.stop_reason if metrics else '-'} "
              f"passed={result.passed} 路由{'✓' if hit else '✗'}")
    print(f"路由命中: {routed}/{total}")

    if errors:
        print(f"\n[!] 本批出现 {errors} 个 error —— 按纪律整批作废，需重跑")
    else:
        print("\n[OK] 本批无 error")
    print(f"\n报告: {WORKSPACE_DIR / skill / f'iteration-{iteration}' / 'benchmark.md'}")


# ---------------------------------------------------------------- summary（读盘）
def cmd_summary() -> int:
    print("=" * 76)
    print("v2 实验汇总（读盘，零 API）")
    print("=" * 76)
    for skill, iteration in MANIFEST.items():
        iter_dir = WORKSPACE_DIR / skill / f"iteration-{iteration}"
        bench = iter_dir / "benchmark.json"
        if not bench.exists():
            print(f"\n[{skill} · iteration-{iteration}] 未跑")
            continue
        data = json.loads(bench.read_text(encoding="utf-8"))
        configs = data.get("configs", [])
        print(f"\n[{skill} · iteration-{iteration}] {data.get('total_evals', 0)} 用例")
        for name in configs:
            rate = data.get("pass_rates", {}).get(name, 0)
            tokens = data.get("avg_tokens", {}).get(name, 0)
            stops = (data.get("stop_reason_counts", {}) or {}).get(name, {}) or {}
            err = stops.get("error", 0)
            print(f"  {name:<20}{rate:>7.1f}%  均 {tokens:>6.0f} tok"
                  + (f"  [!] error×{err}" if err else ""))
        agentic_dir = iter_dir / "agentic"
        hits, total = 0, 0
        if agentic_dir.exists():
            for case_dir in sorted(p for p in agentic_dir.iterdir() if p.is_dir()):
                timing = case_dir / "timing.json"
                if not timing.exists():
                    continue
                loaded = json.loads(timing.read_text(encoding="utf-8")).get("loaded_skills", [])
                total += 1
                hits += skill in loaded
            print(f"  路由命中: {hits}/{total}")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="技能价值与自主路由评估（v2）")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("create-evals")
    sub.add_parser("precheck")
    p_run = sub.add_parser("run")
    p_run.add_argument("skill", choices=list(MANIFEST))
    sub.add_parser("summary")
    args = parser.parse_args()

    if args.cmd == "create-evals":
        return cmd_create_evals()
    if args.cmd == "precheck":
        return cmd_precheck()
    if args.cmd == "run":
        return cmd_run(args.skill)
    if args.cmd == "summary":
        return cmd_summary()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
