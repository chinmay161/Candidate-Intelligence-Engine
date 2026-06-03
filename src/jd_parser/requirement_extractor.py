"""Extract structured requirements from raw job-description text."""

from __future__ import annotations

import re

from candidate_processor.normalizer import TextNormalizer
from jd_parser.dictionaries import BEHAVIORAL_TRAIT_KEYWORDS, INDUSTRY_ALIASES, LOCATION_ALIASES, SENIORITY_TERMS
from jd_parser.jd_models import JobRequirement
from jd_parser.skill_mapper import SkillMapper


class RequirementExtractor:
    """Extract experience, skills, industries, locations, and behavior preferences."""

    _range_pattern = re.compile(r"(?P<min>\d{1,2})\s*(?:-|to)\s*(?P<max>\d{1,2})\s*\+?\s*(?:years|yrs)", re.IGNORECASE)
    _plus_pattern = re.compile(r"(?P<min>\d{1,2})\s*\+?\s*(?:years|yrs)", re.IGNORECASE)

    def __init__(self, skill_mapper: SkillMapper | None = None) -> None:
        self.skill_mapper = skill_mapper or SkillMapper()

    def extract(self, jd_text: str) -> JobRequirement:
        """Extract a typed requirement object from JD text."""

        skill_buckets = self.skill_mapper.extract(jd_text)
        experience_min, experience_max = self._experience_range(jd_text)
        return JobRequirement(
            experience_min=experience_min,
            experience_max=experience_max,
            seniority=self._seniority(jd_text, experience_min),
            required_skills=skill_buckets["required_skills"],
            preferred_skills=skill_buckets["preferred_skills"],
            optional_skills=skill_buckets["optional_skills"],
            industries=self._extract_aliases(jd_text, INDUSTRY_ALIASES),
            locations=self._extract_aliases(jd_text, LOCATION_ALIASES),
            behavioral_preferences=self._extract_aliases(jd_text, BEHAVIORAL_TRAIT_KEYWORDS),
        )

    def _experience_range(self, jd_text: str) -> tuple[int, int]:
        range_match = self._range_pattern.search(jd_text)
        if range_match:
            minimum = int(range_match.group("min"))
            maximum = int(range_match.group("max"))
            return minimum, max(minimum, maximum)
        plus_match = self._plus_pattern.search(jd_text)
        if plus_match:
            minimum = int(plus_match.group("min"))
            return minimum, minimum + 4
        normalized = TextNormalizer.normalize(jd_text)
        if any(term in normalized for term in ("staff", "principal")):
            return 8, 14
        if any(term in normalized for term in ("senior", "lead", "founding")):
            return 5, 10
        return 0, 0

    def _seniority(self, jd_text: str, experience_min: int) -> str:
        normalized = TextNormalizer.normalize(jd_text)
        for seniority, terms in SENIORITY_TERMS.items():
            if any(term in normalized for term in terms):
                return seniority
        if experience_min >= 8:
            return "lead"
        if experience_min >= 5:
            return "senior"
        if experience_min >= 3:
            return "mid"
        if experience_min > 0:
            return "junior"
        return "unspecified"

    def _extract_aliases(self, jd_text: str, aliases: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
        matched: list[str] = []
        for canonical, terms in aliases.items():
            if TextNormalizer.has_any(jd_text, terms):
                matched.append(canonical)
        return tuple(matched)

