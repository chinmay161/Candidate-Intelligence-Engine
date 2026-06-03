"""Penalty application for ranking guardrails and JD negative signals."""

from __future__ import annotations

from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY
from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis
from ranking.match_models import MatchPenalty


class PenaltyEngine:
    """Convert anomaly and negative-fit features into bounded deductions."""

    FEATURE_REASONS: dict[str, str] = {
        "honeypot_score": "suspicious-profile risk",
        "services_only_penalty": "services-only career signal",
        "research_only_phd_penalty": "research-only signal",
        "management_only_recent_penalty": "recent non-hands-on role",
        "framework_demo_penalty_text": "demo-only framework language",
        "job_hop_title_chaser_penalty": "short-tenure title progression risk",
        "nontech_role_penalty": "non-technical current role signal",
        "salary_range_width_penalty": "unusual expected salary range",
        "ai_keyword_stuffing_penalty": "unsupported AI keyword density",
    }

    def __init__(self) -> None:
        self.penalty_features = {
            definition.name
            for definition in DEFAULT_FEATURE_REGISTRY.list_all()
            if definition.is_penalty
        }

    def apply(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> tuple[float, tuple[MatchPenalty, ...]]:
        penalties: list[MatchPenalty] = []
        penalty_score = 0.0

        for feature in sorted(self.penalty_features):
            raw = self._feature_value(candidate, feature)
            normalized = self._normalize_penalty_value(raw)
            if normalized <= 0:
                continue
            weight = self._feature_weight(analysis, feature)
            value = clamp(normalized * (0.035 + weight * 1.35), 0.0, 0.20)
            if value <= 0.005:
                continue
            penalty_score += value
            penalties.append(
                MatchPenalty(
                    reason=self.FEATURE_REASONS.get(feature, feature.replace("_", " ")),
                    severity=self._severity(value),
                    value=round(value, 6),
                    feature=feature,
                )
            )

        inactive = 1.0 - float(candidate.behavioral_features.get("days_since_active_score", 1.0))
        if inactive >= 0.75:
            value = round(clamp(inactive * 0.035), 6)
            penalty_score += value
            penalties.append(MatchPenalty("inactive candidate", self._severity(value), value, "days_since_active_score"))

        notice = 1.0 - max(
            float(candidate.behavioral_features.get("notice_period_score", 1.0)),
            float(candidate.logistics_features.get("notice_buyout_fit", 1.0)),
        )
        if notice >= 0.55:
            value = round(clamp(notice * 0.045), 6)
            penalty_score += value
            penalties.append(MatchPenalty("90 day notice period", self._severity(value), value, "notice_period_score"))

        return round(clamp(penalty_score, 0.0, 0.55), 6), tuple(penalties)

    def _feature_value(self, candidate: CandidateFeatureRecord, feature: str) -> float:
        for group in (
            candidate.semantic_features,
            candidate.experience_features,
            candidate.skill_features,
            candidate.career_features,
            candidate.education_features,
            candidate.logistics_features,
            candidate.anomaly_features,
        ):
            if feature in group:
                return float(group[feature])
        return 0.0

    def _feature_weight(self, analysis: JDAnalysis, feature: str) -> float:
        for weights in analysis.feature_weights.by_group.values():
            if feature in weights:
                return float(weights[feature])
        return 0.0

    def _normalize_penalty_value(self, value: float) -> float:
        if value <= 0:
            return 0.0
        if value > 1.0:
            return clamp(value / 5.0)
        return clamp(value)

    def _severity(self, value: float) -> str:
        if value >= 0.08:
            return "high"
        if value >= 0.035:
            return "medium"
        return "low"
