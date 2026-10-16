"""三方对比评估：agentic（技能自主加载） vs with_skill（静态注入） vs without_skill（对照）。

用法：
  python run_agentic_eval.py smoke       # 单条 agentic 执行，打印完整轨迹
  python run_agentic_eval.py [iteration] # 完整三方对比（默认 iteration 5）

产出：skill-workspace/weather/iteration-N/
  - benchmark.md / benchmark.json       配置级汇总（含 Steps / Tool Calls / Stop Reasons）
  - <config>/<eval>/agent_trace.json    每条用例的 loop 轨迹

凭据：本仓库 .env 优先；缺 KEY 时回退读取 CharacterSeed 的 .env，
只取 AGNES_API_KEY / AGNES_BASE_URL —— 刻意不取 AGNES_MODEL，
因为那个值是 CharacterSeed 生图/视频链路的配置（且已下架）。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
FALLBACK_ENV = Path(r"C:\Users\biren\Documents\trae_projects\luyan\CharacterSeed\.env")
DEFAULT_ITERATION = 5


def load_credentials() -> None:
    """加载凭据到环境变量（已设置的不覆盖）。"""
    from dotenv import dotenv_values

    local_env = BASE_DIR / ".env"
    if local_env.exists():
        for key, value in (dotenv_values(local_env) or {}).items():
            if value and not os.environ.get(key):
                os.environ[key] = value

    if not os.environ.get("AGNES_API_KEY") and FALLBACK_ENV.exists():
        values = dotenv_values(FALLBACK_ENV) or {}
        for key in ("AGNES_API_KEY", "AGNES_BASE_URL"):
            if values.get(key) and not os.environ.get(key):
                os.environ[key] = values[key]


def build_executor():
    load_credentials()
    from agentic_executor import RetryPolicy, create_agentic_executor

    # 免费额度实测会在跑批中途触发 429，用更宽松的退避扛过瞬时限流
    return create_agentic_executor(
        skills_dir=BASE_DIR / "skills",
        retry_policy=RetryPolicy(max_retries=4, base_delay=5.0, max_delay=60.0),
    )


def run_smoke() -> None:
    executor = build_executor()
    print(f"模型: {executor.model}\n")
    output, tokens, duration = executor.execute_agentic("帮我查一下北京今天的天气")
    print("\n输出:", output)
    trace = executor.last_trace.to_dict()
    print("\n轨迹:")
    for key, value in trace.items():
        if key != "tool_calls":
            print(f"  {key}: {value}")
    print("  tool_calls:")
    for call in trace["tool_calls"]:
        print(f"    - iter{call['iteration']} {call['tool_name']}({call['arguments']}) "
              f"ok={call['ok']} chars={call['result_chars']}")


def run_benchmark(iteration: int) -> None:
    from run_real_eval import setup_weather_evals
    from skill_benchmark import BenchmarkConfig, SkillBenchmark

    executor = build_executor()
    setup_weather_evals(BASE_DIR / "skills")

    print(f"模型: {executor.model}")
    print(f"loop 参数: max_iterations={executor.max_iterations} "
          f"max_total_tokens={executor.max_total_tokens}\n")

    benchmark = SkillBenchmark(BASE_DIR / "skills", BASE_DIR / "skill-workspace", executor=executor)
    configs = [
        BenchmarkConfig(name="agentic", skill_name="weather", agentic=True),
        BenchmarkConfig(name="with_skill", skill_name="weather"),
        BenchmarkConfig(name="without_skill", baseline=True),
    ]
    summary = benchmark.run_benchmark("weather", configs, iteration=iteration)

    print("\n" + "=" * 76)
    print(f"iteration-{iteration} 三方对比")
    print("=" * 76)
    print(f"{'配置':<16}{'通过率':>8}{'均Tokens':>10}{'均耗时':>10}{'均轮数':>8}{'均工具调用':>10}")
    for name in summary.configs:
        print(f"{name:<16}"
              f"{summary.pass_rates.get(name, 0):>7.1f}%"
              f"{summary.avg_tokens.get(name, 0):>10.0f}"
              f"{summary.avg_duration.get(name, 0):>8.0f}ms"
              f"{summary.avg_iterations.get(name, 0):>8.1f}"
              f"{summary.avg_tool_calls.get(name, 0):>10.1f}")

    print("\n停止原因分布:")
    for name in summary.configs:
        counts = summary.stop_reason_counts.get(name) or {}
        detail = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items())) or "-"
        print(f"  {name}: {detail}")

    print("\nagentic 技能加载明细:")
    for result in summary.results.get("agentic", []):
        metrics = result.metrics
        loaded = ", ".join(metrics.loaded_skills) if metrics and metrics.loaded_skills else "（未加载）"
        steps = metrics.iterations if metrics else 0
        stop = metrics.stop_reason if metrics else "-"
        print(f"  {result.eval_name}: loaded=[{loaded}] steps={steps} stop={stop} passed={result.passed}")

    agentic = summary.pass_rates.get("agentic", 0)
    static = summary.pass_rates.get("with_skill", 0)
    baseline = summary.pass_rates.get("without_skill", 0)
    print(f"\n差值: agentic-baseline={agentic - baseline:+.1f}pp | "
          f"agentic-static={agentic - static:+.1f}pp | static-baseline={static - baseline:+.1f}pp")
    print(f"\n报告: {BASE_DIR / 'skill-workspace' / 'weather' / f'iteration-{iteration}' / 'benchmark.md'}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "smoke":
        run_smoke()
    else:
        run_benchmark(int(arg) if arg else DEFAULT_ITERATION)
