"""Serializable recruiter-facing reasoning models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ReasoningEvidence:
    """One traceable piece of evidence used by the reasoning engine."""

    feature: str
    group: str
    description: str
    contribution: float
    raw_value: float
    snippets: tuple[str, ...] = ()
    source: str = "feature_contribution"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["snippets"] = list(self.snippets)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReasoningEvidence":
        return cls(
            feature=str(data["feature"]),
            group=str(data["group"]),
            description=str(data["description"]),
            contribution=float(data["contribution"]),
            raw_value=float(data["raw_value"]),
            snippets=tuple(str(item) for item in data.get("snippets", ())),
            source=str(data.get("source", "feature_contribution")),
        )


@dataclass(frozen=True, slots=True)
class CandidateStrength:
    """A positive, evidence-backed candidate signal."""

    category: str
    description: str
    supporting_evidence: tuple[ReasoningEvidence, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "supporting_evidence": [item.to_dict() for item in self.supporting_evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateStrength":
        return cls(
            category=str(data["category"]),
            description=str(data["description"]),
            supporting_evidence=tuple(
                ReasoningEvidence.from_dict(item) for item in data.get("supporting_evidence", ())
            ),
        )


@dataclass(frozen=True, slots=True)
class CandidateConcern:
    """A negative or missing signal that should be disclosed to recruiters."""

    category: str
    description: str
    supporting_evidence: tuple[ReasoningEvidence, ...]
    severity: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "supporting_evidence": [item.to_dict() for item in self.supporting_evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateConcern":
        return cls(
            category=str(data["category"]),
            description=str(data["description"]),
            severity=str(data.get("severity", "low")),
            supporting_evidence=tuple(
                ReasoningEvidence.from_dict(item) for item in data.get("supporting_evidence", ())
            ),
        )


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """Final explanation and traceability payload for one candidate."""

    candidate_id: str
    reasoning: str
    confidence: float
    evidence: tuple[ReasoningEvidence, ...]
    strengths: tuple[CandidateStrength, ...]
    concerns: tuple[CandidateConcern, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "evidence": [item.to_dict() for item in self.evidence],
            "strengths": [item.to_dict() for item in self.strengths],
            "concerns": [item.to_dict() for item in self.concerns],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReasoningResult":
        return cls(
            candidate_id=str(data["candidate_id"]),
            reasoning=str(data["reasoning"]),
            confidence=float(data["confidence"]),
            evidence=tuple(ReasoningEvidence.from_dict(item) for item in data.get("evidence", ())),
            strengths=tuple(CandidateStrength.from_dict(item) for item in data.get("strengths", ())),
            concerns=tuple(CandidateConcern.from_dict(item) for item in data.get("concerns", ())),
        )


@dataclass(frozen=True, slots=True)
class CandidateRecommendation:
    """Recruiter-facing ranked recommendation for one candidate."""

    candidate_id: str
    rank: int
    score: float
    reasoning: str
    confidence: float
    strengths: tuple[CandidateStrength, ...] = ()
    concerns: tuple[CandidateConcern, ...] = ()
    evidence: tuple[ReasoningEvidence, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "strengths": [item.to_dict() for item in self.strengths],
            "concerns": [item.to_dict() for item in self.concerns],
            "evidence": [item.to_dict() for item in self.evidence],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateRecommendation":
        return cls(
            candidate_id=str(data["candidate_id"]),
            rank=int(data["rank"]),
            score=float(data["score"]),
            reasoning=str(data["reasoning"]),
            confidence=float(data["confidence"]),
            strengths=tuple(CandidateStrength.from_dict(item) for item in data.get("strengths", ())),
            concerns=tuple(CandidateConcern.from_dict(item) for item in data.get("concerns", ())),
            evidence=tuple(ReasoningEvidence.from_dict(item) for item in data.get("evidence", ())),
        )
