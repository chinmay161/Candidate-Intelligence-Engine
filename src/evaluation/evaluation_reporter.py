import json
from pathlib import Path
from typing import Dict, Any


class EvaluationReporter:
    """
    Aggregates all evaluation metrics into a comprehensive final report.
    """

    def generate_report(self, 
                        benchmark_results: Dict[str, Any], 
                        runtime_profile: Dict[str, Any], 
                        memory_profile: Dict[str, Any], 
                        ablation_results: Dict[str, Any],
                        diagnostics: Dict[str, Any],
                        bottleneck_analysis: Dict[str, Any]) -> str:
        
        report = [
            "# Final Evaluation Report",
            "",
            "## Performance",
            f"- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)",
            ""
        ]

        # Runtime Profile Summary
        total_runtime = runtime_profile.get("total_runtime", 0.0)
        report.append("### Runtime Profile")
        for phase, rt in runtime_profile.items():
            if phase != "total_runtime":
                report.append(f"- **{phase}**: {rt:.2f}s")
        report.append(f"- **Total Runtime**: {total_runtime:.2f}s")
        report.append("")

        # Memory Profile Summary
        report.append("### Memory Profile")
        report.append(f"- **Peak Memory**: {memory_profile.get('peak_memory_mb', 0.0):.2f} MB")
        report.append(f"- **Average Memory**: {memory_profile.get('average_memory_mb', 0.0):.2f} MB")
        report.append(f"- **Memory per Candidate**: {memory_profile.get('memory_per_candidate', 0.0):.4f} MB")
        report.append("")

        # Scalability / Benchmarks
        report.append("## Scalability")
        report.append("| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |")
        report.append("|-------|-------------|-------------|----------------------|")
        for scale, metrics in benchmark_results.items():
            report.append(f"| {scale} | {metrics.get('runtime', 0.0)} | {metrics.get('memory', 0.0)} | {metrics.get('throughput', 0.0)} |")
        report.append("")

        # Diagnostics / Explainability / Robustness
        report.append("## Explainability & Robustness")
        score_dist = diagnostics.get("candidate_score_distribution", {})
        report.append(f"- **Score Range**: {score_dist.get('min', 0):.2f} - {score_dist.get('max', 0):.2f}")
        report.append(f"- **Score Variance**: {diagnostics.get('score_variance', 0.0):.4f}")
        report.append(f"- **Duplicate Score Rate**: {diagnostics.get('duplicate_score_rate', 0.0)*100:.2f}%")
        report.append(f"- **Penalty Rate (Honeypot/Anomalies)**: {diagnostics.get('penalty_rate', 0.0)*100:.2f}%")
        report.append("")
        
        # Ablations
        report.append("## Ablation Studies")
        report.append("| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |")
        report.append("|---------------|-------------|------------------|-------------------|")
        for config_name, metrics in ablation_results.items():
            div = metrics.get('candidate_diversity', 0.0)
            rq = metrics.get('reasoning_quality', 'N/A')
            report.append(f"| {config_name} | {metrics.get('runtime', 0.0):.2f} | {div:.2f} | {rq} |")
        report.append("")

        # Optimization Summary
        report.append("## Optimization Summary")
        report.append(f"**Largest Bottleneck**: {bottleneck_analysis.get('largest_runtime_component')} "
                      f"({bottleneck_analysis.get('runtime_percentage')}%)")
        report.append("")
        report.append("### Recommendations")
        report.append("Please refer to `optimization_report.md` for deterministic recommendations to reduce the "
                      "runtime toward the target benchmark without degrading explainability and ranking quality.")

        return "\n".join(report)

    def save_report(self, 
                    benchmark_results: Dict[str, Any], 
                    runtime_profile: Dict[str, Any], 
                    memory_profile: Dict[str, Any], 
                    ablation_results: Dict[str, Any],
                    diagnostics: Dict[str, Any],
                    bottleneck_analysis: Dict[str, Any],
                    output_dir: str = "reports") -> str:
        """Saves the final evaluation report to a markdown file."""
        report_content = self.generate_report(
            benchmark_results, runtime_profile, memory_profile, 
            ablation_results, diagnostics, bottleneck_analysis
        )
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "final_evaluation_report.md"

        with open(output_path, "w") as f:
            f.write(report_content)

        return str(output_path)
