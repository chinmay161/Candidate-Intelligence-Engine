"""Skill extraction and canonicalization for job descriptions."""

from __future__ import annotations

from candidate_processor.normalizer import TextNormalizer
from jd_parser.dictionaries import OPTIONAL_MARKERS, PREFERRED_MARKERS, REQUIRED_MARKERS, SKILL_ALIASES
from jd_parser.jd_models import JobSkill


class SkillMapper:
    """Map JD skill mentions into canonical skill categories."""

    def extract(self, jd_text: str) -> dict[str, tuple[JobSkill, ...]]:
        """Extract required, preferred, and optional canonical skills from JD text."""

        buckets: dict[str, dict[str, JobSkill]] = {
            "required_skills": {},
            "preferred_skills": {},
            "optional_skills": {},
        }
        for sentence in TextNormalizer.sentences(jd_text.replace("\n", ". ")):
            importance = self._importance(sentence)
            for alias, (canonical, category) in SKILL_ALIASES.items():
                if not TextNormalizer.has_any(sentence, (alias,)):
                    continue
                skill = JobSkill(
                    name=alias,
                    canonical_name=canonical,
                    category=category,
                    importance=importance,
                    evidence=(sentence[:240],),
                )
                bucket_name = f"{importance}_skills"
                existing = buckets[bucket_name].get(canonical)
                if existing is None:
                    buckets[bucket_name][canonical] = skill
                else:
                    buckets[bucket_name][canonical] = JobSkill(
                        name=existing.name,
                        canonical_name=existing.canonical_name,
                        category=existing.category,
                        importance=existing.importance,
                        evidence=tuple(dict.fromkeys(existing.evidence + skill.evidence)),
                    )
        return {name: tuple(values.values()) for name, values in buckets.items()}

    def canonicalize(self, skill_name: str, importance: str = "required") -> JobSkill | None:
        """Canonicalize one skill mention if it is known."""

        for alias, (canonical, category) in SKILL_ALIASES.items():
            if TextNormalizer.normalize(skill_name) == TextNormalizer.normalize(alias):
                return JobSkill(
                    name=skill_name,
                    canonical_name=canonical,
                    category=category,
                    importance=importance,
                    evidence=(skill_name,),
                )
        return None

    def _importance(self, sentence: str) -> str:
        normalized = TextNormalizer.normalize(sentence)
        if any(marker in normalized for marker in OPTIONAL_MARKERS):
            return "optional"
        if any(marker in normalized for marker in PREFERRED_MARKERS):
            return "preferred"
        if any(marker in normalized for marker in REQUIRED_MARKERS):
            return "required"
        return "required"

