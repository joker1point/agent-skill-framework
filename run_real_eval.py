"""端到端真实评估: 使用 Agnes AI API 运行 skill 基准测试。

对比 with_skill vs without_skill 的真实输出, 验证 skill 带来的实际提升。
"""
from __future__ import annotations
import json
from pathlib import Path

from real_agent_executor import create_default_executor
from skill_evals import SkillEvals
from skill_benchmark import SkillBenchmark, BenchmarkConfig
from eval_viewer import EvalViewer


def setup_weather_evals(skills_dir: Path):
    """为 weather skill 创建评估用例 (基于 iteration-3 的发现优化断言)。"""
    evals = SkillEvals(skills_dir)
    sample_evals = [
        {
            "id": 1,
            "name": "weather_query_basic",
            "prompt": "帮我查一下北京今天的天气",
            "expected_output": "包含天气信息的回答",
            "assertions": [
                {"type": "contains", "name": "mentions_weather_or_temp", "substring": "天气"},
                {"type": "regex", "name": "has_temperature", "pattern": "\\d+°?C|温度|度"},
                {"type": "length", "name": "min_length", "min_length": 10}
            ]
        },
        {
            "id": 2,
            "name": "weather_query_location",
            "prompt": "伦敦现在多少度？",
            "expected_output": "包含温度信息",
            "assertions": [
                {"type": "contains_all", "name": "has_temp_and_location", "substrings": ["伦敦", "度"]}
            ]
        },
        {
            "id": 3,
            "name": "weather_format_check",
            "prompt": "如何用命令行查天气？",
            "expected_output": "提到 wttr.in 或 curl 命令",
            "assertions": [
                {"type": "regex", "name": "has_curl_or_wttr", "pattern": "curl|wttr"}
            ]
        }
    ]
    evals.create_eval_file("weather", sample_evals)
    print(f"已创建 weather skill 的评估用例 ({len(sample_evals)} 个)")


def run_real_benchmark():
    skills_dir = Path(__file__).parent / "skills"
    workspace_dir = Path(__file__).parent / "skill-workspace"

    print("=" * 60)
    print("端到端真实评估: 使用 Agnes AI API")
    print("=" * 60)

    print("\n1. 创建真实执行器 (Agnes AI / agnes-1.5-flash):")
    executor = create_default_executor(skills_dir)
    print(f"   模型: {executor.model}")
    print(f"   API: {executor.client.base_url}")

    print("\n2. 设置评估用例 (已优化断言):")
    setup_weather_evals(skills_dir)

    print("\n3. 运行完整基准测试 (Iteration 4 - 真实执行):")
    benchmark = SkillBenchmark(skills_dir, workspace_dir, executor=executor)

    configs = [
        BenchmarkConfig(name="with_skill", skill_name="weather"),
        BenchmarkConfig(name="without_skill", baseline=True)
    ]

    try:
        summary = benchmark.run_benchmark("weather", configs, iteration=4)
        print(f"\n   基准测试完成!")
        print(f"   评估总数: {summary.total_evals}")
        print(f"\n   通过率对比:")
        for config in summary.configs:
            rate = summary.pass_rates.get(config, 0)
            print(f"     {config}: {rate:.1f}%")

        print(f"\n   平均 Token 对比:")
        for config in summary.configs:
            tokens = summary.avg_tokens.get(config, 0)
            print(f"     {config}: {tokens:.0f}")

        print(f"\n   平均耗时对比:")
        for config in summary.configs:
            dur = summary.avg_duration.get(config, 0)
            print(f"     {config}: {dur:.0f}ms")

        if summary.delta_pass_rate is not None:
            print(f"\n   Delta (Skill vs Baseline): {summary.delta_pass_rate:+.1f}%")

    except ValueError as e:
        print(f"   失败: {e}")
        return

    print("\n4. 生成 HTML 报告:")
    viewer = EvalViewer(workspace_dir)
    html_path = viewer.save_html("weather", 4)
    print(f"   报告已保存: {html_path}")

    print("\n5. 显示详细结果:")
    iteration_dir = workspace_dir / "weather" / "iteration-4"
    for config in ["with_skill", "without_skill"]:
        config_dir = iteration_dir / config
        print(f"\n   [{config}]")
        for eval_dir in sorted(config_dir.iterdir()):
            if eval_dir.is_dir():
                output_file = eval_dir / "output.txt"
                grading_file = eval_dir / "grading.json"
                if output_file.exists():
                    output = output_file.read_text(encoding="utf-8")
                    print(f"     {eval_dir.name}:")
                    print(f"       输出: {output[:100]}")
                    if grading_file.exists():
                        grading = json.loads(grading_file.read_text(encoding="utf-8"))
                        for a in grading.get("assertions", []):
                            status = "✓" if a["passed"] else "✗"
                            print(f"       {status} {a['text']}: {a['evidence'][:60]}")

    print("\n6. 对比迭代 (Iteration 3 → 4):")
    comparison = benchmark.compare_iterations("weather", 3, 4)
    if "error" not in comparison:
        for config, change in comparison["pass_rate_change"].items():
            print(f"   {config}: {change['iteration_a']:.1f}% → {change['iteration_b']:.1f}% ({change['delta']:+.1f}%)")

    print("\n" + "=" * 60)
    print("✓ 端到端真实评估完成!")
    print("=" * 60)


if __name__ == "__main__":
    run_real_benchmark()