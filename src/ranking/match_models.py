"""Serializable models emitted by the candidate ranking engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class FeatureContribution:
    """One weighted score component used for ranking explainability."""

    feature: str
    group: str
    weight: float
    raw_value: float
    contribution: float
    reason: str = ""
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FeatureContribution":
        return cls(
            feature=str(data["feature"]),
            group=str(data["group"]),
            weight=float(data["weight"]),
            raw_value=float(data["raw_value"]),
            contribution=float(data["contribution"]),
            reason=str(data.get("reason", "")),
            evidence=tuple(str(item) for item in data.get("evidence", ())),
        )


@dataclass(frozen=True, slots=True)
class MatchPenalty:
    """A ranking deduction with machine-readable severity."""

    reason: str
    severity: str
    value: float
    feature: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchPenalty":
        return cls(
            reason=str(data["reason"]),
            severity=str(data["severity"]),
            value=float(data["value"]),
            feature=str(data.get("feature", "")),
        )


@dataclass(frozen=True, slots=True)
class ScoringBreakdown:
    """Score internals for downstream debugging and reasoning generation."""

    semantic_score: float
    feature_match_score: float
    weighted_feature_score: float
    penalty_score: float
    raw_score: float
    final_score: float
    group_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_score": self.semantic_score,
            "feature_match_score": self.feature_match_score,
            "weighted_feature_score": self.weighted_feature_score,
            "penalty_score": self.penalty_score,
            "raw_score": self.raw_score,
            "final_score": self.final_score,
            "group_scores": dict(self.group_scores),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScoringBreakdown":
        return cls(
            semantic_score=float(data["semantic_score"]),
            feature_match_score=float(data["feature_match_score"]),
            weighted_feature_score=float(data["weighted_feature_score"]),
            penalty_score=float(data["penalty_score"]),
            raw_score=float(data["raw_score"]),
            final_score=float(data["final_score"]),
            group_scores={str(name): float(value) for name, value in data.get("group_scores", {}).items()},
        )


@dataclass(frozen=True, slots=True)
class CandidateMatch:
    """Score output for one candidate against one job description."""

    candidate_id: str
    score: float
    confidence: float
    feature_contributions: tuple[FeatureContribution, ...]
    matched_requirements: tuple[str, ...]
    penalties: tuple[MatchPenalty, ...]
    missing_requirements: tuple[str, ...] = ()
    scoring_breakdown: ScoringBreakdown | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "score": self.score,
            "confidence": self.confidence,
            "feature_contributions": [item.to_dict() for item in self.feature_contributions],
            "matched_requirements": list(self.matched_requirements),
            "missing_requirements": list(self.missing_requirements),
            "penalties": [item.to_dict() for item in self.penalties],
            "scoring_breakdown": self.scoring_breakdown.to_dict() if self.scoring_breakdown else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateMatch":
        breakdown = data.get("scoring_breakdown")
        return cls(
            candidate_id=str(data["candidate_id"]),
            score=float(data["score"]),
            confidence=float(data["confidence"]),
            feature_contributions=tuple(FeatureContribution.from_dict(item) for item in data.get("feature_contributions", ())),
            matched_requirements=tuple(str(item) for item in data.get("matched_requirements", ())),
            missing_requirements=tuple(str(item) for item in data.get("missing_requirements", ())),
            penalties=tuple(MatchPenalty.from_dict(item) for item in data.get("penalties", ())),
            scoring_breakdown=ScoringBreakdown.from_dict(breakdown) if isinstance(breakdown, dict) else None,
        )


@dataclass(frozen=True, slots=True)
class RankingResult:
    """Ranked candidate matches for one JD."""

    matches: tuple[CandidateMatch, ...]
    total_candidates: int
    selected_count: int
    normalized: bool = True
    method: str = "minmax"

    def to_dict(self) -> dict[str, Any]:
        return {
            "matches": [match.to_dict() for match in self.matches],
            "total_candidates": self.total_candidates,
            "selected_count": self.selected_count,
            "normalized": self.normalized,
            "method": self.method,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RankingResult":
        return cls(
            matches=tuple(CandidateMatch.from_dict(item) for item in data.get("matches", ())),
            total_candidates=int(data["total_candidates"]),
            selected_count=int(data["selected_count"]),
            normalized=bool(data.get("normalized", True)),
            method=str(data.get("method", "minmax")),
        )
