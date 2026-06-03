"""Generates an evaluation report from the pipeline run."""

import json
from pathlib import Path
from typing import Sequence

from reasoning.reasoning_models import CandidateRecommendation
from submission.submission_models import SubmissionFile


class ReportGenerator:
    """Calculates metrics and outputs the evaluation report."""

    @staticmethod
    def generate(
        submission: SubmissionFile,
        all_recommendations: Sequence[CandidateRecommendation],
        output_path: str | Path,
    ) -> None:
        """
        Generate evaluation metrics based on submission and raw recommendations.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        total_candidates_ranked = submission.metadata.total_candidates_processed
        top_k_selected = len(submission.rows)

        # Reasoning metrics
        reasonings = [row.reasoning for row in submission.rows]
        unique_reasonings = len(set(reasonings))
        reasoning_uniqueness_score = unique_reasonings / max(1, len(reasonings))

        avg_reasoning_len = sum(len(r.split()) for r in reasonings) / max(1, len(reasonings))

        # We approximate evidence utilization by seeing how much evidence the top K recommendations used
        # We need to map candidate_id back to recommendations to fetch evidence
        top_recs_map = {
            rec.candidate_id: rec
            for rec in all_recommendations
            if any(r.candidate_id == rec.candidate_id for r in submission.rows)
        }

        total_evidence_top_k = sum(len(rec.evidence) for rec in top_recs_map.values())
        avg_evidence_utilization = total_evidence_top_k / max(1, len(top_recs_map))

        # Quality metrics
        scores = [row.score for row in submission.rows]
        avg_score = sum(scores) / max(1, len(scores))

        sorted_scores = sorted(scores)
        score_distribution = {
            "min": sorted_scores[0] if scores else 0.0,
            "max": sorted_scores[-1] if scores else 0.0,
            "median": sorted_scores[len(sorted_scores) // 2] if scores else 0.0,
        }

        confidences = [rec.confidence for rec in top_recs_map.values()]
        avg_confidence = sum(confidences) / max(1, len(confidences))

        penalties = [len(rec.concerns) for rec in top_recs_map.values()]
        avg_penalty_frequency = sum(penalties) / max(1, len(penalties))

        report = {
            "ranking_metrics": {
                "total_candidates_ranked": total_candidates_ranked,
                "top_k_selected": top_k_selected,
            },
            "reasoning_metrics": {
                "reasoning_uniqueness_score": reasoning_uniqueness_score,
                "evidence_utilization_rate": avg_evidence_utilization,
                "average_reasoning_length": avg_reasoning_len,
            },
            "quality_metrics": {
                "average_score": avg_score,
                "score_distribution": score_distribution,
                "average_confidence": avg_confidence,
                "penalty_frequency": avg_penalty_frequency,
            },
            "system_metrics": {
                "pipeline_runtime": submission.metadata.pipeline_runtime_seconds,
                "memory_usage_estimate": submission.metadata.memory_usage_mb,
            },
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
