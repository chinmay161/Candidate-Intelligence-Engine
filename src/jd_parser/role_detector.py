"""Weighted role-family detection for job descriptions."""

from __future__ import annotations

from candidate_processor.normalizer import TextNormalizer, clamp
from jd_parser.dictionaries import ROLE_KEYWORDS
from jd_parser.jd_models import RoleClassification


SUPPORTED_ROLES = (
    "AI_ENGINEER",
    "ML_ENGINEER",
    "MLOPS_ENGINEER",
    "DATA_ENGINEER",
    "DATA_SCIENTIST",
    "BACKEND_ENGINEER",
    "SOFTWARE_ENGINEER",
    "PRODUCT_MANAGER",
    "RESEARCHER",
    "UNKNOWN",
)


class RoleDetector:
    """Classify JD role family using title, requirements, responsibilities, and stack."""

    TITLE_WEIGHT = 12.0
    REQUIREMENT_WEIGHT = 4.0
    RESPONSIBILITY_WEIGHT = 2.5
    STACK_WEIGHT = 3.0
    BODY_WEIGHT = 1.0

    REQUIREMENT_MARKERS = ("requirements", "required", "must have", "you have", "qualifications")
    RESPONSIBILITY_MARKERS = ("responsibilities", "what you will do", "you will", "build", "own", "design")
    STACK_MARKERS = ("tech stack", "technology", "tools", "stack", "skills")

    def detect(self, title: str, jd_text: str) -> RoleClassification:
        """Return the most likely role family for the JD."""

        scores = {role: 0.0 for role in SUPPORTED_ROLES if role != "UNKNOWN"}
        evidence: dict[str, list[str]] = {role: [] for role in scores}

        self._score_text(scores, evidence, title, self.TITLE_WEIGHT, "title")
        for line in TextNormalizer.sentences(jd_text.replace("\n", ". ")):
            weight = self._line_weight(line)
            self._score_text(scores, evidence, line, weight, "jd text")

        role, top_score = max(scores.items(), key=lambda item: item[1])
        if top_score <= 0:
            return RoleClassification(role_family="UNKNOWN", confidence=0.0, evidence=())

        ordered = sorted(scores.values(), reverse=True)
        runner_up = ordered[1] if len(ordered) > 1 else 0.0
        confidence = clamp((top_score - runner_up * 0.35) / max(top_score + runner_up, 1.0))
        return RoleClassification(role_family=role, confidence=round(confidence, 4), evidence=tuple(evidence[role][:5]))

    def _line_weight(self, line: str) -> float:
        normalized = TextNormalizer.normalize(line)
        if any(marker in normalized for marker in self.REQUIREMENT_MARKERS):
            return self.REQUIREMENT_WEIGHT
        if any(marker in normalized for marker in self.STACK_MARKERS):
            return self.STACK_WEIGHT
        if any(marker in normalized for marker in self.RESPONSIBILITY_MARKERS):
            return self.RESPONSIBILITY_WEIGHT
        return self.BODY_WEIGHT

    def _score_text(
        self,
        scores: dict[str, float],
        evidence: dict[str, list[str]],
        text: str,
        weight: float,
        source: str,
    ) -> None:
        normalized = TextNormalizer.normalize(text)
        if not normalized:
            return
        for role, terms in ROLE_KEYWORDS.items():
            matched = [term for term in terms if TextNormalizer.has_any(normalized, (term,))]
            if not matched:
                continue
            scores[role] += weight * min(len(matched), 3)
            evidence[role].append(f"{source}: {text[:220]}")
