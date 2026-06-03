"""Build final recruiter-facing candidate recommendations."""

from __future__ import annotations

from ranking.match_models import CandidateMatch
from reasoning.reasoning_models import CandidateRecommendation, ReasoningResult


class RecommendationBuilder:
    """Convert match and reasoning output into a ranked recommendation."""

    def build(
        self,
        *,
        rank: int,
        match: CandidateMatch,
        reasoning: ReasoningResult,
    ) -> CandidateRecommendation:
        return CandidateRecommendation(
            candidate_id=match.candidate_id,
            rank=rank,
            score=match.score,
            reasoning=reasoning.reasoning,
            confidence=reasoning.confidence,
            strengths=reasoning.strengths,
            concerns=reasoning.concerns,
            evidence=reasoning.evidence,
        )

    def build_many(
        self,
        ranked_matches: tuple[CandidateMatch, ...],
        reasoning_by_candidate: dict[str, ReasoningResult],
    ) -> tuple[CandidateRecommendation, ...]:
        recommendations: list[CandidateRecommendation] = []
        for index, match in enumerate(ranked_matches, start=1):
            recommendations.append(
                self.build(
                    rank=index,
                    match=match,
                    reasoning=reasoning_by_candidate[match.candidate_id],
                )
            )
        return tuple(recommendations)
