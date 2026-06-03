"""Final score assembly from semantic, feature, and penalty scores."""

from __future__ import annotations

from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY
from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis
from ranking.contribution_tracker import ContributionTracker, feature_group
from ranking.match_models import ScoringBreakdown


class ScoreCalculator:
    """Combine ranking signals into one bounded candidate score."""

    def __init__(self) -> None:
        self.penalty_features = {
            definition.name
            for definition in DEFAULT_FEATURE_REGISTRY.list_all()
            if definition.is_penalty
        }

    def calculate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        *,
        semantic_score: float,
        feature_match_score: float,
        penalty_score: float,
        tracker: ContributionTracker | None = None,
    ) -> ScoringBreakdown:
        tracker = tracker or ContributionTracker()
        weighted_feature_score, group_scores = self._weighted_feature_score(analysis, candidate)
        tracker.extend_weighted_features(
            analysis,
            candidate,
            normalizer=self._normalize_feature,
            penalty_features=self.penalty_features,
        )

        tracker.add(
            feature="semantic_alignment",
            group="semantic",
            weight=0.30,
            raw_value=semantic_score,
            contribution=semantic_score * 0.30,
            reason="Composite semantic alignment",
        )
        tracker.add(
            feature="requirement_match_score",
            group="requirement",
            weight=0.50,
            raw_value=feature_match_score,
            contribution=feature_match_score * 0.50,
            reason="Structured JD requirement coverage",
        )
        tracker.add(
            feature="weighted_candidate_feature_score",
            group="feature",
            weight=0.20,
            raw_value=weighted_feature_score,
            contribution=weighted_feature_score * 0.20,
            reason="JD-weighted candidate feature score",
        )
        tracker.add(
            feature="penalty_score",
            group="penalty",
            weight=1.0,
            raw_value=penalty_score,
            contribution=-penalty_score,
            reason="Bounded ranking penalty deduction",
        )

        raw_score = clamp(semantic_score * 0.30 + feature_match_score * 0.50 + weighted_feature_score * 0.20)
        final_score = clamp(raw_score - penalty_score)
        return ScoringBreakdown(
            semantic_score=round(semantic_score, 6),
            feature_match_score=round(feature_match_score, 6),
            weighted_feature_score=round(weighted_feature_score, 6),
            penalty_score=round(penalty_score, 6),
            raw_score=round(raw_score, 6),
            final_score=round(final_score, 6),
            group_scores=group_scores,
        )

    def _weighted_feature_score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> tuple[float, dict[str, float]]:
        total_weight = 0.0
        weighted_total = 0.0
        group_scores: dict[str, float] = {}
        for group, weights in analysis.feature_weights.by_group.items():
            group_weight = 0.0
            group_total = 0.0
            values = feature_group(candidate, group)
            for feature, weight in weights.items():
                if weight <= 0 or feature in self.penalty_features:
                    continue
                normalized = self._normalize_feature(feature, float(values.get(feature, 0.0)))
                group_total += normalized * weight
                group_weight += weight
            if group_weight > 0:
                group_scores[group] = round(clamp(group_total / group_weight), 6)
                weighted_total += group_total
                total_weight += group_weight
            else:
                group_scores[group] = 0.0
        return (clamp(weighted_total / total_weight) if total_weight else 0.0), group_scores

    def _normalize_feature(self, feature: str, value: float) -> float:
        if feature.endswith("_count"):
            return clamp(value / 5.0)
        if feature.endswith("_months"):
            return clamp(value / 60.0)
        if feature.endswith("_years_proxy") or feature.endswith("_exposure"):
            return clamp(value / 6.0)
        if feature == "availability_multiplier":
            return clamp((value - 0.75) / 0.50)
        if feature == "contactability_multiplier":
            return clamp((value - 0.85) / 0.30)
        return clamp(value)
