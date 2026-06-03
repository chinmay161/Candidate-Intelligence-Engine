"""Schema validation and conversion into candidate dataclasses."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import date
from typing import Any, TypeVar

from candidate_processor.constants import (
    CANDIDATE_ID_PATTERN,
    COMPANY_SIZE_BUCKETS,
    EDUCATION_TIERS,
    LANGUAGE_PROFICIENCY_ORDER,
    SKILL_PROFICIENCY_ORDER,
    WORK_MODES,
)
from candidate_processor.models import (
    Candidate,
    CareerHistory,
    Certification,
    Education,
    Language,
    Profile,
    RedrobSignals,
    SalaryRange,
    Skill,
)

T = TypeVar("T")


class CandidateValidationError(ValueError):
    """Raised when a candidate record violates the published schema."""


def parse_candidate(data: Mapping[str, Any]) -> Candidate:
    """Validate and convert a raw mapping into a typed Candidate."""

    candidate_id = _string(data, "candidate_id")
    if re.fullmatch(CANDIDATE_ID_PATTERN, candidate_id) is None:
        raise CandidateValidationError(f"Invalid candidate_id: {candidate_id!r}")

    profile = _profile(_mapping(data, "profile"))
    career_history = tuple(_career_history(item) for item in _list(data, "career_history", 1, 10))
    education = tuple(_education(item) for item in _list(data, "education", 0, 5))
    skills = tuple(_skill(item) for item in _list(data, "skills", 0, None))
    certifications = tuple(_certification(item) for item in _optional_list(data, "certifications"))
    languages = tuple(_language(item) for item in _optional_list(data, "languages"))
    redrob_signals = _redrob_signals(_mapping(data, "redrob_signals"))

    return Candidate(
        candidate_id=candidate_id,
        profile=profile,
        career_history=career_history,
        education=education,
        skills=skills,
        certifications=certifications,
        languages=languages,
        redrob_signals=redrob_signals,
        raw=dict(data),
    )


def _profile(data: Mapping[str, Any]) -> Profile:
    yoe = _number(data, "years_of_experience", minimum=0, maximum=50)
    company_size = _enum(_string(data, "current_company_size"), COMPANY_SIZE_BUCKETS, "current_company_size")
    return Profile(
        anonymized_name=_string(data, "anonymized_name"),
        headline=_string(data, "headline"),
        summary=_string(data, "summary"),
        location=_string(data, "location"),
        country=_string(data, "country"),
        years_of_experience=yoe,
        current_title=_string(data, "current_title"),
        current_company=_string(data, "current_company"),
        current_company_size=company_size,
        current_industry=_string(data, "current_industry"),
    )


def _career_history(data: Any) -> CareerHistory:
    if not isinstance(data, Mapping):
        raise CandidateValidationError("career_history item must be an object")
    return CareerHistory(
        company=_string(data, "company"),
        title=_string(data, "title"),
        start_date=_date(data, "start_date"),
        end_date=_date_or_none(data, "end_date"),
        duration_months=_integer(data, "duration_months", minimum=0),
        is_current=_boolean(data, "is_current"),
        industry=_string(data, "industry"),
        company_size=_enum(_string(data, "company_size"), COMPANY_SIZE_BUCKETS, "company_size"),
        description=_string(data, "description"),
    )


def _education(data: Any) -> Education:
    if not isinstance(data, Mapping):
        raise CandidateValidationError("education item must be an object")
    return Education(
        institution=_string(data, "institution"),
        degree=_string(data, "degree"),
        field_of_study=_string(data, "field_of_study"),
        start_year=_integer(data, "start_year", minimum=1970, maximum=2030),
        end_year=_integer(data, "end_year", minimum=1970, maximum=2035),
        grade=_optional_string(data, "grade"),
        tier=_enum(str(data.get("tier", "unknown")), EDUCATION_TIERS, "tier"),
    )


def _skill(data: Any) -> Skill:
    if not isinstance(data, Mapping):
        raise CandidateValidationError("skill item must be an object")
    return Skill(
        name=_string(data, "name"),
        proficiency=_enum(_string(data, "proficiency"), tuple(SKILL_PROFICIENCY_ORDER), "proficiency"),
        endorsements=_integer(data, "endorsements", minimum=0),
        duration_months=_integer(data, "duration_months", minimum=0, default=0),
    )


def _certification(data: Any) -> Certification:
    if not isinstance(data, Mapping):
        raise CandidateValidationError("certification item must be an object")
    return Certification(
        name=_string(data, "name"),
        issuer=_string(data, "issuer"),
        year=_integer(data, "year"),
    )


def _language(data: Any) -> Language:
    if not isinstance(data, Mapping):
        raise CandidateValidationError("language item must be an object")
    return Language(
        language=_string(data, "language"),
        proficiency=_enum(_string(data, "proficiency"), tuple(LANGUAGE_PROFICIENCY_ORDER), "language proficiency"),
    )


def _redrob_signals(data: Mapping[str, Any]) -> RedrobSignals:
    salary = _mapping(data, "expected_salary_range_inr_lpa")
    assessments = _mapping(data, "skill_assessment_scores")
    assessment_scores = {
        str(name): _validate_number(score, f"skill_assessment_scores.{name}", minimum=0, maximum=100)
        for name, score in assessments.items()
    }
    salary_range = SalaryRange(
        min=_number(salary, "min", minimum=0),
        max=_number(salary, "max", minimum=0),
    )
    return RedrobSignals(
        profile_completeness_score=_number(data, "profile_completeness_score", minimum=0, maximum=100),
        signup_date=_date(data, "signup_date"),
        last_active_date=_date(data, "last_active_date"),
        open_to_work_flag=_boolean(data, "open_to_work_flag"),
        profile_views_received_30d=_integer(data, "profile_views_received_30d", minimum=0),
        applications_submitted_30d=_integer(data, "applications_submitted_30d", minimum=0),
        recruiter_response_rate=_number(data, "recruiter_response_rate", minimum=0, maximum=1),
        avg_response_time_hours=_number(data, "avg_response_time_hours", minimum=0),
        skill_assessment_scores=assessment_scores,
        connection_count=_integer(data, "connection_count", minimum=0),
        endorsements_received=_integer(data, "endorsements_received", minimum=0),
        notice_period_days=_integer(data, "notice_period_days", minimum=0, maximum=180),
        expected_salary_range_inr_lpa=salary_range,
        preferred_work_mode=_enum(_string(data, "preferred_work_mode"), WORK_MODES, "preferred_work_mode"),
        willing_to_relocate=_boolean(data, "willing_to_relocate"),
        github_activity_score=_number(data, "github_activity_score", minimum=-1, maximum=100),
        search_appearance_30d=_integer(data, "search_appearance_30d", minimum=0),
        saved_by_recruiters_30d=_integer(data, "saved_by_recruiters_30d", minimum=0),
        interview_completion_rate=_number(data, "interview_completion_rate", minimum=0, maximum=1),
        offer_acceptance_rate=_number(data, "offer_acceptance_rate", minimum=-1, maximum=1),
        verified_email=_boolean(data, "verified_email"),
        verified_phone=_boolean(data, "verified_phone"),
        linkedin_connected=_boolean(data, "linkedin_connected"),
    )


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = data.get(key)
    if not isinstance(value, Mapping):
        raise CandidateValidationError(f"{key} must be an object")
    return value


def _list(data: Mapping[str, Any], key: str, min_items: int, max_items: int | None) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise CandidateValidationError(f"{key} must be a list")
    if len(value) < min_items:
        raise CandidateValidationError(f"{key} must contain at least {min_items} items")
    if max_items is not None and len(value) > max_items:
        raise CandidateValidationError(f"{key} must contain at most {max_items} items")
    return value


def _optional_list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise CandidateValidationError(f"{key} must be a list")
    return value


def _string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise CandidateValidationError(f"{key} must be a string")
    return value


def _optional_string(data: Mapping[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise CandidateValidationError(f"{key} must be a string or null")
    return value


def _integer(
    data: Mapping[str, Any], key: str, minimum: int | None = None, maximum: int | None = None, default: int | None = None
) -> int:
    if key not in data and default is not None:
        return default
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise CandidateValidationError(f"{key} must be an integer")
    if minimum is not None and value < minimum:
        raise CandidateValidationError(f"{key} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise CandidateValidationError(f"{key} must be <= {maximum}")
    return value


def _number(data: Mapping[str, Any], key: str, minimum: float | None = None, maximum: float | None = None) -> float:
    return _validate_number(data.get(key), key, minimum, maximum)


def _validate_number(value: Any, label: str, minimum: float | None = None, maximum: float | None = None) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise CandidateValidationError(f"{label} must be a number")
    number = float(value)
    if minimum is not None and number < minimum:
        raise CandidateValidationError(f"{label} must be >= {minimum}")
    if maximum is not None and number > maximum:
        raise CandidateValidationError(f"{label} must be <= {maximum}")
    return number


def _boolean(data: Mapping[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise CandidateValidationError(f"{key} must be a boolean")
    return value


def _date(data: Mapping[str, Any], key: str) -> date:
    value = data.get(key)
    if not isinstance(value, str):
        raise CandidateValidationError(f"{key} must be an ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CandidateValidationError(f"{key} must be an ISO date string") from exc


def _date_or_none(data: Mapping[str, Any], key: str) -> date | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise CandidateValidationError(f"{key} must be an ISO date string or null")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CandidateValidationError(f"{key} must be an ISO date string or null") from exc


def _enum(value: str, allowed: tuple[str, ...], label: str) -> str:
    if value not in allowed:
        raise CandidateValidationError(f"{label} must be one of {allowed}")
    return value
