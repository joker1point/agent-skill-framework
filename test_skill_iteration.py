from pathlib import Path
from skill_evals import SkillEvals
from skill_benchmark import SkillBenchmark, BenchmarkConfig
from skill_trigger_analyzer import SkillTriggerAnalyzer
from eval_viewer import EvalViewer


def test_evals_system():
    skills_dir = Path(__file__).parent / "skills"
    evals = SkillEvals(skills_dir)

    print("=" * 60)
    print("测试技能评估系统 (SkillEvals)")
    print("=" * 60)

    print("\n1. 创建示例评估文件:")
    sample_evals = [
        {
            "id": 1,
            "name": "weather_inquiry",
            "prompt": "What's the weather like today?",
            "expected_output": "weather information",
            "assertions": [
                {"type": "contains", "name": "contains_weather", "substring": "weather"},
                {"type": "length", "name": "min_length", "min_length": 10}
            ]
        },
        {
            "id": 2,
            "name": "weather_with_location",
            "prompt": "What's the weather in Beijing?",
            "expected_output": "Beijing weather",
            "assertions": [
                {"type": "contains_all", "name": "contains_both", "substrings": ["weather", "Beijing"]}
            ]
        }
    ]
    success = evals.create_eval_file("weather", sample_evals)
    print(f"   创建评估文件: {'✓ 成功' if success else '✗ 失败'}")

    print("\n2. 加载评估:")
    loaded_evals = evals.load_evals("weather")
    print(f"   加载的评估数量: {len(loaded_evals)}")
    for e in loaded_evals:
        print(f"   - {e.name}: {e.prompt[:30]}...")
        print(f"     断言数量: {len(e.assertions)}")

    print("\n3. 执行评估:")
    test_output = "The weather in Beijing today is sunny with 25°C."
    results = evals.evaluate_output(loaded_evals[1], test_output)
    for r in results:
        status = "✓ 通过" if r.passed else "✗ 失败"
        print(f"   {r.assertion_name}: {status}")
        print(f"     证据: {r.evidence}")

    print("\n4. 获取评估摘要:")
    summary = evals.get_eval_summary("weather")
    print(f"   技能名称: {summary['skill_name']}")
    print(f"   评估总数: {summary['total_evals']}")
    print(f"   评估名称: {summary['eval_names']}")
    print(f"   断言总数: {summary['assertion_count']}")

    print("\n5. 列出有评估的技能:")
    skills_with_evals = evals.list_skills_with_evals()
    print(f"   有评估的技能: {skills_with_evals}")


def test_benchmark_system():
    skills_dir = Path(__file__).parent / "skills"
    benchmark = SkillBenchmark(skills_dir)

    print("\n" + "=" * 60)
    print("测试基准测试系统 (SkillBenchmark)")
    print("=" * 60)

    print("\n1. 运行基准测试 (Iteration 1):")
    configs = [
        BenchmarkConfig(name="with_skill"),
        BenchmarkConfig(name="without_skill", baseline=True)
    ]
    try:
        summary = benchmark.run_benchmark("weather", configs, iteration=1)
        print(f"   技能名称: {summary.skill_name}")
        print(f"   评估总数: {summary.total_evals}")
        print(f"   配置: {summary.configs}")
        print(f"   Pass Rates: {summary.pass_rates}")
        print(f"   Delta: {summary.delta_pass_rate:+.1f}%")
    except ValueError as e:
        print(f"   跳过 (无评估): {e}")

    print("\n2. 运行基准测试 (Iteration 2 - 模拟改进后):")
    try:
        summary = benchmark.run_benchmark("weather", configs, iteration=2)
        print(f"   Pass Rates: {summary.pass_rates}")
    except ValueError as e:
        print(f"   跳过: {e}")

    print("\n3. 列出迭代:")
    iterations = benchmark.list_iterations("weather")
    print(f"   迭代列表: {iterations}")

    print("\n4. 比较迭代结果:")
    if len(iterations) >= 2:
        comparison = benchmark.compare_iterations("weather", iterations[-2], iterations[-1])
        if "error" not in comparison:
            for config, change in comparison["pass_rate_change"].items():
                print(f"   {config}: {change['iteration_a']:.1f}% → {change['iteration_b']:.1f}% ({change['delta']:+.1f}%)")


def test_trigger_analyzer():
    skills_dir = Path(__file__).parent / "skills"
    analyzer = SkillTriggerAnalyzer(skills_dir)

    print("\n" + "=" * 60)
    print("测试触发分析器 (SkillTriggerAnalyzer)")
    print("=" * 60)

    sample_prompts = [
        "What's the weather today?",
        "Show me the weather forecast for tomorrow",
        "I want to build a website",
        "Get me the current temperature",
        "Can you help me with GitHub?",
        "Weather in Shanghai please"
    ]

    print("\n1. 分析单个技能触发:")
    try:
        analysis = analyzer.analyze_trigger("weather", sample_prompts)
        print(f"   技能名称: {analysis.skill_name}")
        print(f"   质量分数: {analysis.quality_score}/100")
        print(f"   触发关键词: {analysis.trigger_keywords[:5]}...")
        print(f"   假阳性: {len(analysis.false_positives)}")
        print(f"   假阴性: {len(analysis.false_negatives)}")
        print(f"   建议: {analysis.suggestions[:2]}")
    except ValueError as e:
        print(f"   跳过: {e}")

    print("\n2. 优化描述:")
    try:
        result = analyzer.optimize_description("weather", sample_prompts)
        if "error" not in result:
            print(f"   原始描述: {result['original_description'][:50]}...")
            print(f"   优化描述: {result['optimized_description'][:50]}...")
            print(f"   质量分数: {result['analysis']['quality_score']}")
    except Exception as e:
        print(f"   跳过: {e}")

    print("\n3. 批量分析所有技能:")
    results = analyzer.batch_analyze(sample_prompts)
    print(f"   分析的技能数量: {len(results)}")
    for r in results[:3]:
        print(f"   {r.skill_name}: {r.quality_score}/100")


def test_eval_viewer():
    skills_dir = Path(__file__).parent / "skills"
    workspace_dir = Path(__file__).parent / "skill-workspace"
    viewer = EvalViewer(workspace_dir)

    print("\n" + "=" * 60)
    print("测试评估查看器 (EvalViewer)")
    print("=" * 60)

    print("\n1. 生成HTML报告:")
    try:
        html = viewer.generate_html("weather", 2)
        print(f"   HTML生成成功, 长度: {len(html)} 字符")
    except Exception as e:
        print(f"   跳过: {e}")

    print("\n2. 保存HTML报告:")
    try:
        output_path = viewer.save_html("weather", 2)
        print(f"   HTML已保存到: {output_path}")
    except Exception as e:
        print(f"   跳过: {e}")


if __name__ == "__main__":
    test_evals_system()
    test_benchmark_system()
    test_trigger_analyzer()
    test_eval_viewer()
    print("\n" + "=" * 60)
    print("✓ 所有迭代机制测试完成!")
    print("=" * 60)