"""Reusable candidate text representations for retrieval and ranking."""

from __future__ import annotations

import re
from functools import lru_cache

from candidate_processor.models import Candidate
from candidate_processor.normalizer import TextNormalizer


class CandidateTextBuilder:
    """Build deterministic text blocks from typed candidate records."""

    _space_pattern = re.compile(r"\s+")

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], str] = {}

    def build_core_text(self, candidate: Candidate) -> str:
        """Build concise text from headline, summary, current title, and current company."""

        return self._cached(
            candidate,
            "core",
            (
                candidate.profile.current_title,
                candidate.profile.headline,
                candidate.profile.summary,
                candidate.profile.current_company,
                candidate.profile.current_industry,
            ),
        )

    def build_profile_text(self, candidate: Candidate) -> str:
        """Build profile text from headline and summary with location context."""

        return self._cached(
            candidate,
            "profile",
            (
                candidate.profile.headline,
                candidate.profile.summary,
                candidate.profile.location,
                candidate.profile.country,
            ),
        )

    def build_experience_text(self, candidate: Candidate) -> str:
        """Build career-history text from role titles, employers, industries, and descriptions."""

        fragments: list[str] = []
        for role in candidate.career_history:
            fragments.extend((role.title, role.company, role.industry, role.description))
        return self._cached(candidate, "experience", tuple(fragments))

    def build_skill_text(self, candidate: Candidate) -> str:
        """Build canonical skill text with duplicate skills removed case-insensitively."""

        fragments = tuple(skill.name for skill in candidate.skills)
        return self._cached(candidate, "skill", fragments, canonicalize=True)

    def build_education_text(self, candidate: Candidate) -> str:
        """Build education text from institutions, degrees, and fields of study."""

        fragments: list[str] = []
        for education in candidate.education:
            fragments.extend((education.institution, education.degree, education.field_of_study, education.tier))
        return self._cached(candidate, "education", tuple(fragments))

    def build_full_text(self, candidate: Candidate) -> str:
        """Build profile, experience, skills, and education text into one deduplicated block."""

        return self._cached(
            candidate,
            "full",
            (
                self.build_profile_text(candidate),
                self.build_experience_text(candidate),
                self.build_skill_text(candidate),
                self.build_education_text(candidate),
            ),
        )

    def clear_cache(self) -> None:
        """Clear per-instance candidate text cache."""

        self._cache.clear()

    def _cached(
        self,
        candidate: Candidate,
        section: str,
        fragments: tuple[str, ...],
        *,
        canonicalize: bool = False,
    ) -> str:
        key = (candidate.candidate_id, section)
        if key not in self._cache:
            if canonicalize:
                self._cache[key] = self._join_unique_canonical(fragments)
            else:
                self._cache[key] = self._join_unique(fragments)
        return self._cache[key]

    @classmethod
    @lru_cache(maxsize=100_000)
    def _join_unique(cls, fragments: tuple[str, ...]) -> str:
        seen: set[str] = set()
        output: list[str] = []
        for fragment in fragments:
            clean = cls._normalize_whitespace(fragment)
            if not clean:
                continue
            key = TextNormalizer.normalize(clean)
            if key in seen:
                continue
            seen.add(key)
            output.append(clean)
        return "\n".join(output)

    @classmethod
    @lru_cache(maxsize=100_000)
    def _join_unique_canonical(cls, fragments: tuple[str, ...]) -> str:
        seen: set[str] = set()
        output: list[str] = []
        for fragment in fragments:
            clean = cls._normalize_whitespace(fragment)
            if not clean:
                continue
            key = TextNormalizer.normalize(clean)
            if key in seen:
                continue
            seen.add(key)
            output.append(" ".join(part.capitalize() for part in key.split()))
        return "\n".join(output)

    @classmethod
    def _normalize_whitespace(cls, value: str) -> str:
        return cls._space_pattern.sub(" ", value).strip()

