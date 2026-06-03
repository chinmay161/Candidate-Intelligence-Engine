"""Typed models for job description intelligence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class JobDescription:
    """Raw job description input with optional structured metadata."""

    raw_text: str
    title: str = ""
    company: str = ""
    location_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobDescription":
        return cls(
            raw_text=str(data["raw_text"]),
            title=str(data.get("title", "")),
            company=str(data.get("company", "")),
            location_hint=str(data.get("location_hint", "")),
        )


@dataclass(frozen=True, slots=True)
class JobSkill:
    """Canonical skill mention extracted from a job description."""

    name: str
    canonical_name: str
    category: str
    importance: str
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobSkill":
        return cls(
            name=str(data["name"]),
            canonical_name=str(data["canonical_name"]),
            category=str(data["category"]),
            importance=str(data["importance"]),
            evidence=tuple(str(item) for item in data.get("evidence", ())),
        )


@dataclass(frozen=True, slots=True)
class JobRequirement:
    """Structured requirements extracted from a job description."""

    experience_min: int = 0
    experience_max: int = 0
    seniority: str = "unspecified"
    required_skills: tuple[JobSkill, ...] = ()
    preferred_skills: tuple[JobSkill, ...] = ()
    optional_skills: tuple[JobSkill, ...] = ()
    industries: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    behavioral_preferences: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "seniority": self.seniority,
            "required_skills": [skill.to_dict() for skill in self.required_skills],
            "preferred_skills": [skill.to_dict() for skill in self.preferred_skills],
            "optional_skills": [skill.to_dict() for skill in self.optional_skills],
            "industries": list(self.industries),
            "locations": list(self.locations),
            "behavioral_preferences": list(self.behavioral_preferences),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JobRequirement":
        return cls(
            experience_min=int(data.get("experience_min", 0)),
            experience_max=int(data.get("experience_max", 0)),
            seniority=str(data.get("seniority", "unspecified")),
            required_skills=tuple(JobSkill.from_dict(item) for item in data.get("required_skills", ())),
            preferred_skills=tuple(JobSkill.from_dict(item) for item in data.get("preferred_skills", ())),
            optional_skills=tuple(JobSkill.from_dict(item) for item in data.get("optional_skills", ())),
            industries=tuple(str(item) for item in data.get("industries", ())),
            locations=tuple(str(item) for item in data.get("locations", ())),
            behavioral_preferences=tuple(str(item) for item in data.get("behavioral_preferences", ())),
        )


@dataclass(frozen=True, slots=True)
class RoleClassification:
    """JD role family with confidence and evidence."""

    role_family: str
    confidence: float
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_family": self.role_family,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RoleClassification":
        return cls(
            role_family=str(data["role_family"]),
            confidence=float(data["confidence"]),
            evidence=tuple(str(item) for item in data.get("evidence", ())),
        )


@dataclass(frozen=True, slots=True)
class WeightProfile:
    """Candidate-feature weights grouped by feature group."""

    by_group: dict[str, dict[str, float]] = field(default_factory=dict)
    reasons: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, dict[str, float]]:
        return {group: dict(weights) for group, weights in self.by_group.items()}

    def to_explanation_dict(self) -> dict[str, dict[str, Any]]:
        """Return a flat, feature-keyed explanation map for debugging."""

        return self.explanations

    @property
    def explanations(self) -> dict[str, dict[str, Any]]:
        """Flat feature explanations with the active normalized weight."""

        return {
            feature_name: {
                "weight": weight,
                "reason": self.reasons.get(feature_name, "Baseline feature prior"),
            }
            for weights in self.by_group.values()
            for feature_name, weight in weights.items()
        }

    def normalize(self) -> "WeightProfile":
        """Return a profile whose positive weights sum to one across all groups."""

        total = sum(max(float(weight), 0.0) for weights in self.by_group.values() for weight in weights.values())
        if total <= 0:
            normalized = {
                group: {feature_name: 0.0 for feature_name in weights}
                for group, weights in self.by_group.items()
            }
        else:
            normalized = {
                group: {
                    feature_name: round(max(float(weight), 0.0) / total, 4)
                    for feature_name, weight in weights.items()
                }
                for group, weights in self.by_group.items()
            }
        return WeightProfile(by_group=normalized, reasons=dict(self.reasons))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WeightProfile":
        grouped: dict[str, dict[str, float]] = {}
        reasons: dict[str, str] = {}

        if isinstance(data.get("by_group"), dict):
            nested_data = data.get("by_group", {})
            raw_reasons = data.get("reasons", {})
            if isinstance(raw_reasons, dict):
                reasons.update({str(name): str(reason) for name, reason in raw_reasons.items()})
        else:
            nested_data = data

        for group, weights in nested_data.items():
            if not isinstance(weights, dict):
                continue
            grouped[str(group)] = {}
            for name, value in weights.items():
                feature_name = str(name)
                if isinstance(value, dict):
                    grouped[str(group)][feature_name] = float(value.get("weight", 0.0))
                    if "reason" in value:
                        reasons[feature_name] = str(value["reason"])
                else:
                    grouped[str(group)][feature_name] = float(value)

        return cls(
            by_group=grouped,
            reasons=reasons,
        )


@dataclass(frozen=True, slots=True)
class JDAnalysis:
    """Complete structured analysis of an incoming job description."""

    job_description: JobDescription
    role_classification: RoleClassification
    requirements: JobRequirement
    negative_signals: tuple[str, ...]
    feature_weights: WeightProfile
    confidence: float

    @property
    def role_family(self) -> str:
        return self.role_classification.role_family

    @property
    def required_skills(self) -> tuple[JobSkill, ...]:
        return self.requirements.required_skills

    @property
    def preferred_skills(self) -> tuple[JobSkill, ...]:
        return self.requirements.preferred_skills

    @property
    def optional_skills(self) -> tuple[JobSkill, ...]:
        return self.requirements.optional_skills

    @property
    def experience_min(self) -> int:
        return self.requirements.experience_min

    @property
    def experience_max(self) -> int:
        return self.requirements.experience_max

    @property
    def industries(self) -> tuple[str, ...]:
        return self.requirements.industries

    @property
    def locations(self) -> tuple[str, ...]:
        return self.requirements.locations

    @property
    def behavioral_preferences(self) -> tuple[str, ...]:
        return self.requirements.behavioral_preferences

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_family": self.role_family,
            "required_skills": [skill.to_dict() for skill in self.required_skills],
            "preferred_skills": [skill.to_dict() for skill in self.preferred_skills],
            "optional_skills": [skill.to_dict() for skill in self.optional_skills],
            "negative_signals": list(self.negative_signals),
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "industries": list(self.industries),
            "locations": list(self.locations),
            "behavioral_preferences": list(self.behavioral_preferences),
            "feature_weights": self.feature_weights.to_dict(),
            "weight_explanations": self.feature_weights.to_explanation_dict(),
            "confidence": self.confidence,
            "job_description": self.job_description.to_dict(),
            "role_classification": self.role_classification.to_dict(),
            "requirements": self.requirements.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JDAnalysis":
        requirements_data = data.get("requirements")
        if not isinstance(requirements_data, dict):
            requirements_data = {
                "experience_min": data.get("experience_min", 0),
                "experience_max": data.get("experience_max", 0),
                "required_skills": data.get("required_skills", ()),
                "preferred_skills": data.get("preferred_skills", ()),
                "optional_skills": data.get("optional_skills", ()),
                "industries": data.get("industries", ()),
                "locations": data.get("locations", ()),
                "behavioral_preferences": data.get("behavioral_preferences", ()),
            }
        role_data = data.get("role_classification")
        if not isinstance(role_data, dict):
            role_data = {
                "role_family": data.get("role_family", "UNKNOWN"),
                "confidence": data.get("confidence", 0.0),
                "evidence": (),
            }
        return cls(
            job_description=JobDescription.from_dict(data.get("job_description", {"raw_text": ""})),
            role_classification=RoleClassification.from_dict(role_data),
            requirements=JobRequirement.from_dict(requirements_data),
            negative_signals=tuple(str(item) for item in data.get("negative_signals", ())),
            feature_weights=_weight_profile_from_analysis_data(data),
            confidence=float(data.get("confidence", 0.0)),
        )


def _weight_profile_from_analysis_data(data: dict[str, Any]) -> WeightProfile:
    profile = WeightProfile.from_dict(data.get("feature_weights", {}))
    raw_explanations = data.get("weight_explanations", {})
    if not isinstance(raw_explanations, dict):
        return profile

    reasons = dict(profile.reasons)
    for feature_name, explanation in raw_explanations.items():
        if isinstance(explanation, dict) and "reason" in explanation:
            reasons[str(feature_name)] = str(explanation["reason"])
    return WeightProfile(by_group=profile.by_group, reasons=reasons)
