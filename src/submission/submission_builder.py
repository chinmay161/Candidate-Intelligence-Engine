"""Converts pipeline output into a structured submission file."""

from typing import Sequence

from reasoning.reasoning_models import CandidateRecommendation
from submission.submission_models import SubmissionFile, SubmissionMetadata, SubmissionRow


class SubmissionBuilder:
    """Builds a deterministic SubmissionFile from candidate recommendations."""

    @staticmethod
    def build(
        recommendations: Sequence[CandidateRecommendation],
        top_k: int = 100,
        total_candidates_processed: int = 0,
        pipeline_runtime_seconds: float = 0.0,
        memory_usage_mb: float | None = None,
    ) -> SubmissionFile:
        """
        Convert recommendations into a SubmissionFile.
        
        Rules:
        - Exactly top_k rows (if enough candidates)
        - Rank starts at 1 and is unique
        - Scores sorted descending
        - Deterministic ordering (breaks ties by candidate_id)
        """
        # Sort by score descending, then by candidate_id for stable deterministic ordering
        sorted_recs = sorted(
            recommendations,
            key=lambda x: (-x.score, x.candidate_id)
        )

        # Take top K
        top_recs = sorted_recs[:top_k]

        rows = []
        for i, rec in enumerate(top_recs):
            rank = i + 1
            rows.append(
                SubmissionRow(
                    candidate_id=rec.candidate_id,
                    rank=rank,
                    score=rec.score,
                    reasoning=rec.reasoning,
                )
            )

        metadata = SubmissionMetadata(
            total_candidates_processed=max(total_candidates_processed, len(recommendations)),
            top_k=top_k,
            pipeline_runtime_seconds=pipeline_runtime_seconds,
            memory_usage_mb=memory_usage_mb,
        )

        return SubmissionFile(rows=tuple(rows), metadata=metadata)
