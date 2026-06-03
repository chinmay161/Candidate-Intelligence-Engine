"""Contribution capture for transparent, downstream-safe scoring."""

from __future__ import annotations

from collections.abc import Callable

from candidate_processor.models import CandidateFeatureRecord
from jd_parser.jd_models import JDAnalysis
from ranking.match_models import FeatureContribution


class ContributionTracker:
    """Collect feature weights, raw values, and signed contributions."""

    def __init__(self) -> None:
        self._items: list[FeatureContribution] = []

    def add(
        self,
        *,
        feature: str,
        group: str,
        weight: float,
        raw_value: float,
        contribution: float,
        reason: str = "",
        evidence: tuple[str, ...] = (),
    ) -> None:
        self._items.append(
            FeatureContribution(
                feature=feature,
                group=group,
                weight=round(weight, 6),
                raw_value=round(raw_value, 6),
                contribution=round(contribution, 6),
                reason=reason,
                evidence=evidence,
            )
        )

    def extend_weighted_features(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        *,
        normalizer: Callable[[str, float], float],
        penalty_features: set[str],
    ) -> None:
        """Track every non-zero JD-weighted candidate feature."""

        for group, weights in analysis.feature_weights.by_group.items():
            values = feature_group(candidate, group)
            for feature, weight in weights.items():
                if weight <= 0:
                    continue
                raw = float(values.get(feature, 0.0))
                normalized = float(normalizer(feature, raw))
                sign = -1.0 if feature in penalty_features else 1.0
                self.add(
                    feature=feature,
                    group=group,
                    weight=weight,
                    raw_value=raw,
                    contribution=sign * weight * normalized,
                    reason=analysis.feature_weights.reasons.get(feature, "Baseline feature prior"),
                    evidence=tuple(candidate.evidence.get(feature)),
                )

    def as_tuple(self) -> tuple[FeatureContribution, ...]:
        return tuple(self._items)

    def as_dict(self) -> dict[str, float]:
        return {item.feature: item.contribution for item in self._items}


def feature_group(candidate: CandidateFeatureRecord, group: str) -> dict[str, float | int]:
    groups = {
        "semantic": candidate.semantic_features,
        "experience": candidate.experience_features,
        "skill": candidate.skill_features,
        "behavioral": candidate.behavioral_features,
        "career": candidate.career_features,
        "education": candidate.education_features,
        "logistics": candidate.logistics_features,
        "anomaly": candidate.anomaly_features,
    }
    return groups.get(group, {})
