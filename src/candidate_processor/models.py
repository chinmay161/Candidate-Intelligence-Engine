"""Typed dataclasses for candidates, evidence, and extracted features."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True, slots=True)
class Profile:
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float
    current_title: str
    current_company: str
    current_company_size: str
    current_industry: str


@dataclass(frozen=True, slots=True)
class CareerHistory:
    company: str
    title: str
    start_date: date
    end_date: date | None
    duration_months: int
    is_current: bool
    industry: str
    company_size: str
    description: str


@dataclass(frozen=True, slots=True)
class Education:
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: str | None = None
    tier: str = "unknown"


@dataclass(frozen=True, slots=True)
class Skill:
    name: str
    proficiency: str
    endorsements: int
    duration_months: int = 0


@dataclass(frozen=True, slots=True)
class Certification:
    name: str
    issuer: str
    year: int


@dataclass(frozen=True, slots=True)
class Language:
    language: str
    proficiency: str


@dataclass(frozen=True, slots=True)
class SalaryRange:
    min: float
    max: float


@dataclass(frozen=True, slots=True)
class RedrobSignals:
    profile_completeness_score: float
    signup_date: date
    last_active_date: date
    open_to_work_flag: bool
    profile_views_received_30d: int
    applications_submitted_30d: int
    recruiter_response_rate: float
    avg_response_time_hours: float
    skill_assessment_scores: dict[str, float]
    connection_count: int
    endorsements_received: int
    notice_period_days: int
    expected_salary_range_inr_lpa: SalaryRange
    preferred_work_mode: str
    willing_to_relocate: bool
    github_activity_score: float
    search_appearance_30d: int
    saved_by_recruiters_30d: int
    interview_completion_rate: float
    offer_acceptance_rate: float
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool


@dataclass(frozen=True, slots=True)
class Candidate:
    candidate_id: str
    profile: Profile
    career_history: tuple[CareerHistory, ...]
    education: tuple[Education, ...]
    skills: tuple[Skill, ...]
    redrob_signals: RedrobSignals
    certifications: tuple[Certification, ...] = ()
    languages: tuple[Language, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict, compare=False, hash=False, repr=False)

    @property
    def career_text(self) -> str:
        return " ".join(
            f"{role.title} {role.company} {role.industry} {role.description}"
            for role in self.career_history
        )

    @property
    def profile_text(self) -> str:
        p = self.profile
        return " ".join(
            [
                p.headline,
                p.summary,
                p.current_title,
                p.current_company,
                p.current_industry,
                p.location,
                p.country,
            ]
        )

    @property
    def skill_text(self) -> str:
        return " ".join(skill.name for skill in self.skills)

    @property
    def full_text(self) -> str:
        return " ".join([self.profile_text, self.career_text, self.skill_text])


@dataclass(frozen=True, slots=True)
class CandidateEvidence:
    candidate_id: str
    by_feature: dict[str, list[str]]

    def get(self, feature_name: str) -> list[str]:
        return self.by_feature.get(feature_name, [])

    def to_dict(self) -> dict[str, list[str]]:
        return self.by_feature


@dataclass(frozen=True, slots=True)
class CandidateFeatureRecord:
    candidate_id: str
    semantic_features: dict[str, float | int]
    experience_features: dict[str, float | int]
    skill_features: dict[str, float | int]
    behavioral_features: dict[str, float | int]
    career_features: dict[str, float | int]
    education_features: dict[str, float | int]
    logistics_features: dict[str, float | int]
    anomaly_features: dict[str, float | int]
    evidence: CandidateEvidence

    def to_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "semantic_features": self.semantic_features,
            "experience_features": self.experience_features,
            "skill_features": self.skill_features,
            "behavioral_features": self.behavioral_features,
            "career_features": self.career_features,
            "education_features": self.education_features,
            "logistics_features": self.logistics_features,
            "anomaly_features": self.anomaly_features,
            "evidence": self.evidence.to_dict(),
        }
