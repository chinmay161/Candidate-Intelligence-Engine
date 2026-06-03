"""Deterministic recruiter-facing reasoning templates."""

from __future__ import annotations

from ranking.match_models import CandidateMatch
from reasoning.reasoning_models import CandidateConcern, CandidateStrength


class ReasoningTemplates:
    """Generate concise, factual recruiter-facing language."""

    def render(
        self,
        match: CandidateMatch,
        strengths: list[CandidateStrength],
        concerns: list[CandidateConcern],
    ) -> str:
        sentences: list[str] = []

        if strengths:
            primary = strengths[:3]
            if self._is_strong(match):
                sentences.append(f"Strong match due to {self._join(item.description for item in primary)}.")
            else:
                sentences.append(f"Good fit with demonstrated experience in {self._join(item.description for item in primary)}.")

            secondary = [
                item.description
                for item in strengths[3:5]
                if item.category not in {"availability"}
            ]
            if secondary:
                sentences.append(f"Also demonstrates {self._join(secondary)}.")

            if any(item.category == "availability" for item in strengths):
                sentences.append("Candidate also shows strong recruiter engagement and recent activity.")
        else:
            sentences.append("Limited evidence-backed strengths were available from the ranking output.")

        for concern in concerns[:2]:
            sentences.append(f"Potential concern: {concern.description}.")

        return self._fit_target_length(" ".join(sentences))

    def _is_strong(self, match: CandidateMatch) -> bool:
        return match.score >= 75.0 or 0.75 <= match.score <= 1.0

    def _join(self, values: object) -> str:
        items = [str(item) for item in values if str(item)]
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return f"{', '.join(items[:-1])}, and {items[-1]}"

    def _fit_target_length(self, text: str) -> str:
        words = text.split()
        if len(words) <= 80:
            return text

        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        trimmed: list[str] = []
        total = 0
        for sentence in sentences:
            length = len(sentence.split())
            if trimmed and total + length > 78:
                break
            trimmed.append(sentence)
            total += length
        return ". ".join(trimmed) + "."
