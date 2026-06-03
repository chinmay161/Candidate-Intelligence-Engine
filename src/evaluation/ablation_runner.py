import json
import time
from typing import Dict, Any, Callable, List
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AblationConfig:
    name: str
    behavioral_features_enabled: bool = True
    honeypot_detection_enabled: bool = True
    reasoning_layer_enabled: bool = True
    structured_features_enabled: bool = True


class AblationRunner:
    """
    Runs ablation studies on the pipeline by disabling components and measuring impact.
    """

    def __init__(self):
        self.configs = [
            AblationConfig("full_system"),
            AblationConfig("no_behavioral_signals", behavioral_features_enabled=False),
            AblationConfig("no_honeypot_detection", honeypot_detection_enabled=False),
            AblationConfig("no_reasoning_layer", reasoning_layer_enabled=False),
            AblationConfig("semantic_only", structured_features_enabled=False, behavioral_features_enabled=False)
        ]

    def run(self, pipeline_func: Callable[[AblationConfig], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the pipeline function with each ablation configuration.
        The pipeline_func should return a dict containing metrics like:
        - score_distribution (min, max, mean, variance)
        - candidate_diversity (a float metric)
        - runtime (float)
        - reasoning_quality (float or dict)
        """
        results = {}

        for config in self.configs:
            start_time = time.perf_counter()
            pipeline_result = pipeline_func(config)
            runtime = time.perf_counter() - start_time

            results[config.name] = {
                "runtime": pipeline_result.get("runtime", runtime),
                "score_distribution": pipeline_result.get("score_distribution", {}),
                "candidate_diversity": pipeline_result.get("candidate_diversity", 0.0),
                "reasoning_quality": pipeline_result.get("reasoning_quality", {})
            }

        return results

    def save_report(self, results: Dict[str, Any], output_dir: str = "reports/ablations") -> str:
        """Saves the ablation results to a JSON file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "ablation_report.json"

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        return str(output_path)
