"""Confidence estimation for generated explanations."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from ranking.match_models import CandidateMatch
from reasoning.reasoning_models import CandidateConcern, CandidateStrength, ReasoningEvidence


class ReasoningConfidenceEstimator:
    """Estimate how well the final prose is supported by stored evidence."""

    def estimate(
        self,
        match: CandidateMatch,
        candidate: CandidateFeatureRecord,
        evidence: list[ReasoningEvidence],
        strengths: list[CandidateStrength],
        concerns: list[CandidateConcern],
    ) -> float:
        evidence_quality = self._evidence_quality(evidence)
        coverage = min(len(evidence) / 5.0, 1.0)
        feature_support = min(len(strengths) / 4.0, 1.0)
        match_confidence = match.confidence
        anomaly_level = self._anomaly_level(candidate)
        unresolved_concerns = min(len([item for item in concerns if item.severity in {"medium", "high"}]) / 4.0, 1.0)

        confidence = (
            evidence_quality * 0.30
            + coverage * 0.20
            + feature_support * 0.20
            + match_confidence * 0.20
            + (1.0 - anomaly_level) * 0.10
            - unresolved_concerns * 0.12
        )
        return round(self._clamp(confidence), 6)

    def _evidence_quality(self, evidence: list[ReasoningEvidence]) -> float:
        if not evidence:
            return 0.0
        scored = []
        for item in evidence:
            snippet_score = 1.0 if item.snippets else 0.0
            contribution_score = min(abs(item.contribution) / 0.05, 1.0) if item.contribution else min(item.raw_value, 1.0)
            scored.append(snippet_score * 0.65 + contribution_score * 0.35)
        return sum(scored) / len(scored)

    def _anomaly_level(self, candidate: CandidateFeatureRecord) -> float:
        values = [
            float(value)
            for feature, value in candidate.anomaly_features.items()
            if feature != "reasoning_confidence_score" and float(value) > 0
        ]
        if not values:
            return 0.0
        return self._clamp(max(values))

    def _clamp(self, value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(upper, value))
