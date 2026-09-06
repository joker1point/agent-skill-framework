from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
from skill_benchmark import SkillBenchmark


class EvalViewer:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def generate_html(self, skill_name: str, iteration: int) -> str:
        iteration_dir = self.workspace_dir / skill_name / f"iteration-{iteration}"
        
        try:
            with open(iteration_dir / "benchmark.json", "r", encoding="utf-8") as f:
                benchmark_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return "<h1>Error: Could not load benchmark data</h1>"

        configs = benchmark_data.get("configs", [])
        results = benchmark_data.get("results", {})

        html_parts = [
            """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill Eval Viewer - """ + skill_name + """</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #1a1a1a; margin-bottom: 20px; }
        .tabs { display: flex; gap: 8px; margin-bottom: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }
        .tab { padding: 8px 16px; cursor: pointer; border: none; background: transparent; font-size: 14px; color: #666; }
        .tab.active { color: #1a73e8; border-bottom: 2px solid #1a73e8; font-weight: 500; }
        .content { display: none; }
        .content.active { display: block; }
        .summary-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 16px; }
        .metric { text-align: center; padding: 16px; background: #f8f9fa; border-radius: 8px; }
        .metric-label { font-size: 12px; color: #666; margin-bottom: 8px; }
        .metric-value { font-size: 24px; font-weight: 600; color: #1a1a1a; }
        .delta-positive { color: #1a73e8; }
        .delta-negative { color: #d93025; }
        .eval-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .eval-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .eval-name { font-weight: 600; color: #1a1a1a; }
        .eval-status { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .eval-status.passed { background: #e8f5e9; color: #2e7d32; }
        .eval-status.failed { background: #ffebee; color: #c62828; }
        .eval-prompt { background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 14px; color: #333; margin-bottom: 12px; }
        .output-section { margin-bottom: 12px; }
        .output-label { font-size: 12px; color: #666; margin-bottom: 4px; }
        .output-content { background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 14px; color: #333; white-space: pre-wrap; }
        .assertions-list { margin-top: 12px; }
        .assertion-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f8f9fa; border-radius: 4px; margin-bottom: 4px; }
        .assertion-name { font-size: 13px; color: #333; }
        .assertion-passed { color: #2e7d32; }
        .assertion-failed { color: #c62828; }
        .assertion-evidence { font-size: 12px; color: #666; margin-left: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f8f9fa; font-weight: 600; color: #666; font-size: 13px; }
        td { font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Skill Eval Viewer: """ + skill_name + """ (Iteration """ + str(iteration) + """)</h1>
        <div class="tabs">
            <button class="tab active" onclick="switchTab('summary')">Summary</button>
            <button class="tab" onclick="switchTab('detailed')">Detailed Results</button>
            <button class="tab" onclick="switchTab('comparison')">Comparison</button>
        </div>
"""
        ]

        html_parts.append(self._generate_summary_tab(benchmark_data))
        html_parts.append(self._generate_detailed_tab(results, configs))
        html_parts.append(self._generate_comparison_tab(skill_name, iteration))

        html_parts.append("""    </div>
    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }
    </script>
</body>
</html>""")

        return "\n".join(html_parts)

    def _generate_summary_tab(self, benchmark_data: Dict[str, Any]) -> str:
        configs = benchmark_data.get("configs", [])
        pass_rates = benchmark_data.get("pass_rates", {})
        avg_tokens = benchmark_data.get("avg_tokens", {})
        avg_duration = benchmark_data.get("avg_duration_ms", {})
        delta = benchmark_data.get("delta_pass_rate")

        rows = []
        for config in configs:
            rows.append(f"""<tr>
                <td>{config}</td>
                <td>{pass_rates.get(config, 0):.1f}%</td>
                <td>{avg_tokens.get(config, 0):.0f}</td>
                <td>{avg_duration.get(config, 0):.0f}ms</td>
            </tr>""")

        delta_color = "delta-positive" if delta and delta >= 0 else "delta-negative"
        delta_display = f"<span class='{delta_color}'>{delta:+.1f}%</span>" if delta else "N/A"

        return f"""        <div id="summary-tab" class="content active">
            <div class="summary-card">
                <h2>Benchmark Summary</h2>
                <div class="summary-grid">
                    <div class="metric">
                        <div class="metric-label">Total Evaluations</div>
                        <div class="metric-value">{benchmark_data.get('total_evals', 0)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Run Date</div>
                        <div class="metric-value">{benchmark_data.get('run_date', '')[:16]}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Delta (Skill vs Baseline)</div>
                        <div class="metric-value">{delta_display}</div>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr><th>Configuration</th><th>Pass Rate</th><th>Avg Tokens</th><th>Avg Duration</th></tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>"""

    def _generate_detailed_tab(self, results: Dict[str, Any], configs: List[str]) -> str:
        parts = ["        <div id=\"detailed-tab\" class=\"content\">"]

        for config in configs:
            config_results = results.get(config, [])
            parts.append(f"            <h2>{config}</h2>")
            
            for result in config_results:
                status = "passed" if result.get("passed") else "failed"
                assertions = result.get("assertions", [])
                
                assertion_items = []
                for assert_item in assertions:
                    assert_status = "assertion-passed" if assert_item.get("passed") else "assertion-failed"
                    assertion_items.append(f"""<div class="assertion-item">
                        <span class="assertion-name">{assert_item.get("name", "")}</span>
                        <span class="{assert_status}">{assert_item.get("passed") and "✓" or "✗"}</span>
                        <span class="assertion-evidence">{assert_item.get("evidence", "")}</span>
                    </div>""")

                parts.append(f"""            <div class="eval-card">
                <div class="eval-header">
                    <span class="eval-name">{result.get("eval_name", "")}</span>
                    <span class="eval-status {status}">{status.upper()}</span>
                </div>
                <div class="eval-prompt"><strong>Prompt:</strong> {result.get("prompt", "")}</div>
                <div class="assertions-list">
                    {''.join(assertion_items)}
                </div>
            </div>""")

        parts.append("        </div>")
        return "\n".join(parts)

    def _generate_comparison_tab(self, skill_name: str, iteration: int) -> str:
        benchmark = SkillBenchmark(self.workspace_dir.parent / "skills", self.workspace_dir)
        iterations = benchmark.list_iterations(skill_name)
        
        if len(iterations) < 2:
            return """        <div id="comparison-tab" class="content">
            <div class="summary-card">
                <h2>Iteration Comparison</h2>
                <p style="margin-top: 16px; color: #666;">Not enough iterations for comparison. Run at least 2 iterations.</p>
            </div>
        </div>"""

        comparison = benchmark.compare_iterations(skill_name, iterations[-2], iterations[-1])
        
        if "error" in comparison:
            return f"""        <div id="comparison-tab" class="content">
            <div class="summary-card">
                <h2>Iteration Comparison</h2>
                <p style="margin-top: 16px; color: #d93025;">{comparison['error']}</p>
            </div>
        </div>"""

        rows = []
        for config, change in comparison.get("pass_rate_change", {}).items():
            delta_color = "delta-positive" if change.get("delta", 0) >= 0 else "delta-negative"
            rows.append(f"""<tr>
                <td>{config}</td>
                <td>{change.get('iteration_a', 0):.1f}%</td>
                <td>{change.get('iteration_b', 0):.1f}%</td>
                <td><span class='{delta_color}'>{change.get('delta', 0):+.1f}%</span></td>
            </tr>""")

        return f"""        <div id="comparison-tab" class="content">
            <div class="summary-card">
                <h2>Iteration Comparison: {iterations[-2]} → {iterations[-1]}</h2>
                <table>
                    <thead>
                        <tr><th>Configuration</th><th>Iteration {iterations[-2]}</th><th>Iteration {iterations[-1]}</th><th>Delta</th></tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
        </div>"""

    def save_html(self, skill_name: str, iteration: int, output_path: Optional[Path] = None) -> Path:
        html = self.generate_html(skill_name, iteration)
        if output_path is None:
            output_path = self.workspace_dir / skill_name / f"iteration-{iteration}" / "eval-viewer.html"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return output_path