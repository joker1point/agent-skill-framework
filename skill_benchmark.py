from __future__ import annotations
import json
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple
from datetime import datetime
from skill_evals import SkillEvals, EvalCase, EvalResult


class AgentExecutor(Protocol):
    def execute(self, prompt: str, skill_name: Optional[str] = None) -> Tuple[str, int, float]:
        ...


@dataclass
class MockAgentExecutor:
    skill_enhancement_factor: float = 1.5

    def execute(self, prompt: str, skill_name: Optional[str] = None) -> Tuple[str, int, float]:
        base_response = f"Processing request: {prompt[:60]}..."
        if skill_name:
            enhanced_content = f"\n\n[Skill: {skill_name}] Enhanced output with comprehensive details and proper formatting."
            response = base_response + enhanced_content
        else:
            response = base_response + "\n\nBasic response without skill enhancement."

        token_count = len(response) * 4
        duration = len(response) * 0.05

        return response, token_count, duration


@dataclass
class RunMetrics:
    total_tokens: int = 0
    duration_ms: int = 0
    total_duration_seconds: float = 0.0


@dataclass
class BenchmarkResult:
    eval_name: str
    eval_id: int
    passed: bool
    assertion_results: List[EvalResult]
    metrics: Optional[RunMetrics] = None
    config_name: str = "with_skill"
    raw_output: str = ""


@dataclass
class BenchmarkConfig:
    name: str
    skill_name: Optional[str] = None
    baseline: bool = False


@dataclass
class BenchmarkSummary:
    skill_name: str
    run_date: datetime
    total_evals: int
    configs: List[str]
    results: Dict[str, List[BenchmarkResult]]
    pass_rates: Dict[str, float]
    avg_tokens: Dict[str, float]
    avg_duration: Dict[str, float]
    delta_pass_rate: Optional[float] = None


class SkillBenchmark:
    def __init__(
        self,
        skills_dir: Path,
        workspace_dir: Optional[Path] = None,
        executor: Optional[AgentExecutor] = None
    ):
        self.skills_dir = skills_dir
        self.workspace_dir = workspace_dir or skills_dir.parent / "skill-workspace"
        self.evals = SkillEvals(skills_dir)
        self.executor = executor or MockAgentExecutor()

    def run_benchmark(
        self,
        skill_name: str,
        configs: List[BenchmarkConfig],
        iteration: int = 1,
        previous_workspace: Optional[Path] = None
    ) -> BenchmarkSummary:
        evals = self.evals.load_evals(skill_name)
        if not evals:
            raise ValueError(f"No evaluations found for skill: {skill_name}")

        iteration_dir = self.workspace_dir / skill_name / f"iteration-{iteration}"
        iteration_dir.mkdir(parents=True, exist_ok=True)

        all_results: Dict[str, List[BenchmarkResult]] = {}

        for config in configs:
            config_dir = iteration_dir / config.name
            config_dir.mkdir(parents=True, exist_ok=True)

            results = []
            for eval_case in evals:
                eval_dir = config_dir / eval_case.name
                eval_dir.mkdir(parents=True, exist_ok=True)

                output, tokens, duration = self._execute_eval(eval_case, config)

                assertions = self.evals.evaluate_output(eval_case, output)
                passed = all(r.passed for r in assertions)

                metrics = RunMetrics(
                    total_tokens=tokens,
                    duration_ms=int(duration * 1000),
                    total_duration_seconds=duration
                )

                result = BenchmarkResult(
                    eval_name=eval_case.name,
                    eval_id=eval_case.id,
                    passed=passed,
                    assertion_results=assertions,
                    metrics=metrics,
                    config_name=config.name,
                    raw_output=output
                )
                results.append(result)

                self._save_eval_result(eval_dir, eval_case, output, assertions, metrics)

            all_results[config.name] = results

        summary = self._aggregate_results(skill_name, configs, all_results)
        self._save_benchmark_summary(iteration_dir, summary)

        return summary

    def _execute_eval(self, eval_case: EvalCase, config: BenchmarkConfig) -> Tuple[str, int, float]:
        if config.baseline:
            return self.executor.execute(eval_case.prompt, skill_name=None)
        return self.executor.execute(eval_case.prompt, skill_name=config.skill_name)

    def _save_eval_result(
        self,
        eval_dir: Path,
        eval_case: EvalCase,
        output: str,
        assertions: List[EvalResult],
        metrics: RunMetrics
    ):
        with open(eval_dir / "output.txt", "w", encoding="utf-8") as f:
            f.write(output)

        with open(eval_dir / "timing.json", "w", encoding="utf-8") as f:
            json.dump({
                "total_tokens": metrics.total_tokens,
                "duration_ms": metrics.duration_ms,
                "total_duration_seconds": metrics.total_duration_seconds
            }, f, indent=2)

        with open(eval_dir / "grading.json", "w", encoding="utf-8") as f:
            json.dump({
                "eval_name": eval_case.name,
                "eval_id": eval_case.id,
                "assertions": [{
                    "text": r.assertion_name,
                    "passed": r.passed,
                    "evidence": r.evidence
                } for r in assertions]
            }, f, indent=2)

        with open(eval_dir / "eval_metadata.json", "w", encoding="utf-8") as f:
            json.dump({
                "eval_id": eval_case.id,
                "eval_name": eval_case.name,
                "prompt": eval_case.prompt,
                "assertions": [{
                    "name": r.assertion_name,
                    "passed": r.passed
                } for r in assertions]
            }, f, indent=2)

    def _aggregate_results(
        self,
        skill_name: str,
        configs: List[BenchmarkConfig],
        results: Dict[str, List[BenchmarkResult]]
    ) -> BenchmarkSummary:
        pass_rates: Dict[str, float] = {}
        avg_tokens: Dict[str, float] = {}
        avg_duration: Dict[str, float] = {}

        for config in configs:
            config_results = results.get(config.name, [])
            if config_results:
                pass_count = sum(1 for r in config_results if r.passed)
                pass_rates[config.name] = (pass_count / len(config_results)) * 100

                tokens = [r.metrics.total_tokens for r in config_results if r.metrics]
                avg_tokens[config.name] = statistics.mean(tokens) if tokens else 0

                durations = [r.metrics.duration_ms for r in config_results if r.metrics]
                avg_duration[config.name] = statistics.mean(durations) if durations else 0

        delta = None
        if len(configs) >= 2:
            main = pass_rates.get(configs[0].name, 0)
            baseline = pass_rates.get(configs[1].name, 0)
            delta = main - baseline

        return BenchmarkSummary(
            skill_name=skill_name,
            run_date=datetime.now(),
            total_evals=len(results.get(configs[0].name, [])),
            configs=[c.name for c in configs],
            results=results,
            pass_rates=pass_rates,
            avg_tokens=avg_tokens,
            avg_duration=avg_duration,
            delta_pass_rate=delta
        )

    def _save_benchmark_summary(self, iteration_dir: Path, summary: BenchmarkSummary):
        benchmark_data = {
            "skill_name": summary.skill_name,
            "run_date": summary.run_date.isoformat(),
            "total_evals": summary.total_evals,
            "configs": summary.configs,
            "pass_rates": summary.pass_rates,
            "avg_tokens": summary.avg_tokens,
            "avg_duration_ms": summary.avg_duration,
            "delta_pass_rate": summary.delta_pass_rate,
            "results": {}
        }

        for config_name, config_results in summary.results.items():
            benchmark_data["results"][config_name] = [{
                "eval_name": r.eval_name,
                "eval_id": r.eval_id,
                "passed": r.passed,
                "assertions": [{
                    "name": a.assertion_name,
                    "passed": a.passed,
                    "evidence": a.evidence
                } for a in r.assertion_results]
            } for r in config_results]

        with open(iteration_dir / "benchmark.json", "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, indent=2, ensure_ascii=False)

        markdown = self._generate_markdown_report(summary)
        with open(iteration_dir / "benchmark.md", "w", encoding="utf-8") as f:
            f.write(markdown)

    def _generate_markdown_report(self, summary: BenchmarkSummary) -> str:
        lines = [
            f"# Benchmark Report: {summary.skill_name}",
            f"",
            f"**Run Date:** {summary.run_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Evaluations:** {summary.total_evals}",
            f"",
            f"## Summary",
            f""
        ]

        lines.append("| Configuration | Pass Rate | Avg Tokens | Avg Duration |")
        lines.append("|--------------|-----------|------------|--------------|")
        for config in summary.configs:
            lines.append(f"| {config} | {summary.pass_rates.get(config, 0):.1f}% | {summary.avg_tokens.get(config, 0):.0f} | {summary.avg_duration.get(config, 0):.0f}ms |")

        if summary.delta_pass_rate is not None:
            lines.append(f"")
            lines.append(f"**Delta (Skill vs Baseline):** {summary.delta_pass_rate:+.1f}%")

        lines.append("")
        lines.append("## Detailed Results")
        lines.append("")

        for config_name, config_results in summary.results.items():
            lines.append(f"### {config_name}")
            lines.append("")
            lines.append("| Eval | Passed | Assertions |")
            lines.append("|------|--------|------------|")
            for r in config_results:
                passed_count = sum(1 for a in r.assertion_results if a.passed)
                total_count = len(r.assertion_results)
                lines.append(f"| {r.eval_name} | {'✓' if r.passed else '✗'} | {passed_count}/{total_count} |")

            lines.append("")

        return "\n".join(lines)

    def compare_iterations(self, skill_name: str, iteration_a: int, iteration_b: int) -> Dict[str, Any]:
        dir_a = self.workspace_dir / skill_name / f"iteration-{iteration_a}"
        dir_b = self.workspace_dir / skill_name / f"iteration-{iteration_b}"

        if not dir_a.exists() or not dir_b.exists():
            return {"error": "One or both iteration directories not found"}

        try:
            with open(dir_a / "benchmark.json", "r", encoding="utf-8") as f:
                data_a = json.load(f)
            with open(dir_b / "benchmark.json", "r", encoding="utf-8") as f:
                data_b = json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"error": "Failed to read benchmark files"}

        comparison = {
            "skill_name": skill_name,
            "iteration_a": iteration_a,
            "iteration_b": iteration_b,
            "pass_rate_change": {},
            "token_change": {},
            "duration_change": {}
        }

        for config in data_a.get("configs", []):
            rate_a = data_a["pass_rates"].get(config, 0)
            rate_b = data_b["pass_rates"].get(config, 0)
            comparison["pass_rate_change"][config] = {
                "iteration_a": rate_a,
                "iteration_b": rate_b,
                "delta": rate_b - rate_a
            }

            tokens_a = data_a["avg_tokens"].get(config, 0)
            tokens_b = data_b["avg_tokens"].get(config, 0)
            comparison["token_change"][config] = {
                "iteration_a": tokens_a,
                "iteration_b": tokens_b,
                "delta": tokens_b - tokens_a
            }

            duration_a = data_a["avg_duration_ms"].get(config, 0)
            duration_b = data_b["avg_duration_ms"].get(config, 0)
            comparison["duration_change"][config] = {
                "iteration_a": duration_a,
                "iteration_b": duration_b,
                "delta": duration_b - duration_a
            }

        return comparison

    def list_iterations(self, skill_name: str) -> List[int]:
        skill_workspace = self.workspace_dir / skill_name
        if not skill_workspace.exists():
            return []
        iterations = []
        for item in skill_workspace.iterdir():
            if item.is_dir() and item.name.startswith("iteration-"):
                try:
                    iterations.append(int(item.name.split("-")[1]))
                except ValueError:
                    pass
        return sorted(iterations)

    def run_ab_test(
        self,
        skill_name: str,
        skill_version_a: str,
        skill_version_b: str,
        iteration: int = 1
    ) -> BenchmarkSummary:
        configs = [
            BenchmarkConfig(name="version_a", skill_name=skill_version_a),
            BenchmarkConfig(name="version_b", skill_name=skill_version_b)
        ]
        return self.run_benchmark(skill_name, configs, iteration)