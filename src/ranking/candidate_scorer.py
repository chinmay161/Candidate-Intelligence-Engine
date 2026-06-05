"""Single-candidate orchestration for Phase 4 ranking."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis
from ranking.contribution_tracker import ContributionTracker
from ranking.feature_matcher import FeatureMatcher
from ranking.match_models import CandidateMatch
from ranking.penalty_engine import PenaltyEngine
from ranking.score_calculator import ScoreCalculator
from ranking.semantic_matcher import SemanticMatcher


class CandidateScorer:
    """Score one candidate against one JDAnalysis."""

    def __init__(
        self,
        *,
        semantic_matcher: SemanticMatcher | None = None,
        feature_matcher: FeatureMatcher | None = None,
        penalty_engine: PenaltyEngine | None = None,
        score_calculator: ScoreCalculator | None = None,
    ) -> None:
        self.semantic_matcher = semantic_matcher or SemanticMatcher()
        self.feature_matcher = feature_matcher or FeatureMatcher()
        self.penalty_engine = penalty_engine or PenaltyEngine()
        self.score_calculator = score_calculator or ScoreCalculator()

    def score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> CandidateMatch:
        semantic_score = self.semantic_matcher.score(analysis, candidate)
        feature_match = self.feature_matcher.match(analysis, candidate)
        penalty_score, penalties = self.penalty_engine.apply(analysis, candidate)
        tracker = ContributionTracker()
        breakdown = self.score_calculator.calculate(
            analysis,
            candidate,
            semantic_score=semantic_score,
            feature_match_score=feature_match.match_score,
            penalty_score=penalty_score,
            missing_requirements_count=len(feature_match.missing_requirements),
            tracker=tracker,
        )
        return CandidateMatch(
            candidate_id=candidate.candidate_id,
            score=breakdown.final_score,
            confidence=self._confidence(analysis, candidate, breakdown.final_score, penalty_score),
            feature_contributions=tracker.as_tuple(),
            matched_requirements=feature_match.matched_requirements,
            missing_requirements=feature_match.missing_requirements,
            penalties=penalties,
            scoring_breakdown=breakdown,
        )

    def _confidence(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        final_score: float,
        penalty_score: float,
    ) -> float:
        reasoning_confidence = float(candidate.anomaly_features.get("reasoning_confidence_score", 0.5))
        completeness = float(candidate.behavioral_features.get("profile_completeness_confidence", 0.5))
        evidence_density = min(len(candidate.evidence.by_feature), 10) / 10.0
        confidence = (
            analysis.confidence * 0.35
            + reasoning_confidence * 0.30
            + completeness * 0.15
            + evidence_density * 0.10
            + final_score * 0.10
            - penalty_score * 0.20
        )
        return round(clamp(confidence), 6)
