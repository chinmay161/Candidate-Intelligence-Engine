import json
import statistics
from typing import List, Dict, Any
from pathlib import Path


class RankingDiagnostics:
    """
    Computes statistical diagnostics on ranking outcomes.
    """

    def analyze(self, ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates diagnostic metrics based on the ranked candidates output.
        Expects a list of candidate dictionaries which include 'score', 'penalties' (optional),
        and 'confidence' (optional).
        """
        if not ranked_candidates:
            return {}

        scores = [c.get("score", 0.0) for c in ranked_candidates]
        penalties = [1 for c in ranked_candidates if c.get("penalties") or c.get("penalty_applied")]
        confidences = [c.get("confidence", 0.0) for c in ranked_candidates if "confidence" in c]

        score_distribution = {
            "min": min(scores),
            "max": max(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores) if scores else 0.0,
            "variance": statistics.variance(scores) if len(scores) > 1 else 0.0
        }

        unique_scores = set(scores)
        duplicate_score_rate = 1.0 - (len(unique_scores) / len(scores))

        penalty_rate = len(penalties) / len(ranked_candidates)

        confidence_distribution = {}
        if confidences:
            confidence_distribution = {
                "mean": statistics.mean(confidences),
                "median": statistics.median(confidences),
                "min": min(confidences),
                "max": max(confidences)
            }

        return {
            "candidate_score_distribution": score_distribution,
            "score_variance": score_distribution["variance"],
            "duplicate_score_rate": duplicate_score_rate,
            "penalty_rate": penalty_rate,
            "confidence_distribution": confidence_distribution
        }

    def save_diagnostics(self, ranked_candidates: List[Dict[str, Any]], output_dir: str = "reports/diagnostics") -> str:
        """Saves diagnostics to a JSON file."""
        diagnostics = self.analyze(ranked_candidates)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "ranking_diagnostics.json"

        with open(output_path, "w") as f:
            json.dump(diagnostics, f, indent=2)

        return str(output_path)
