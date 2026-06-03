from typing import Dict, Any
from pathlib import Path


class OptimizationRecommender:
    """
    Generates deterministic recommendations based on bottleneck analysis.
    """
    
    def generate_recommendations(self, bottleneck_analysis: Dict[str, Any]) -> str:
        """
        Generates markdown report of optimization recommendations.
        """
        largest_component = bottleneck_analysis.get("largest_runtime_component")
        runtime_percentage = bottleneck_analysis.get("runtime_percentage")
        
        report = [
            "# Optimization Recommendations",
            "",
            f"**Largest Bottleneck**: {largest_component} consumes {runtime_percentage}% of total runtime.",
            ""
        ]
        
        report.append("## Targeted Recommendations")
        report.append("")
        
        if largest_component == "feature_extraction_time":
            report.append("Consider:")
            report.append("- Caching (e.g., standardizing text once and reusing)")
            report.append("- Vectorization of operations across candidates")
            report.append("- Compiled regex (using `re.compile` at module level)")
            report.append("- Lazy evaluation of expensive features")
        elif largest_component == "ranking_time":
            report.append("Consider:")
            report.append("- Minimizing unnecessary sorting")
            report.append("- Avoiding repeated score calculations")
            report.append("- Utilizing min/max heaps for Top-K extraction")
        elif largest_component == "reasoning_time":
            report.append("Consider:")
            report.append("- Verifying reasoning only runs for Top-K candidates (not all)")
            report.append("- Pre-computing templates")
        elif largest_component in ["jd_parsing_time", "candidate_parsing_time"]:
            report.append("Consider:")
            report.append("- Avoiding redundant file I/O")
            report.append("- Parallelizing parsing using `multiprocessing` or `ThreadPoolExecutor`")
            report.append("- Using faster JSON/YAML parsing libraries if applicable (e.g., `orjson`)")
        elif largest_component == "submission_time":
            report.append("Consider:")
            report.append("- Reducing excessive serialization (e.g., dataclass to dict overhead)")
            report.append("- Minimizing redundant data copying")
        else:
            report.append("Consider:")
            report.append("- Profiling sub-functions of this component")
            report.append("- Parallelizing independent tasks")
            
        report.append("")
        report.append("## General Recommendations")
        report.append("- Memory: If peak memory is high, consider generator expressions instead of list comprehensions.")
        report.append("- I/O Bound: Use async I/O or batching for external calls.")
        
        return "\n".join(report)

    def save_report(self, bottleneck_analysis: Dict[str, Any], output_dir: str = "reports") -> str:
        """Saves the optimization recommendations to a markdown file."""
        report = self.generate_recommendations(bottleneck_analysis)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "optimization_report.md"
        
        with open(output_path, "w") as f:
            f.write(report)
            
        return str(output_path)
