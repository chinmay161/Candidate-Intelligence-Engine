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

        # Deterministic pattern index based on candidate_id to vary phrasing across candidates
        pattern_index = sum(ord(c) for c in match.candidate_id) % 3

        if strengths:
            non_avail_strengths = [s for s in strengths if s.category != "availability"]
            has_avail = any(s.category == "availability" for s in strengths)
            categories = {s.category for s in strengths}

            # Select template family
            if "production" in categories:
                family = "strong_production_background"
            elif "retrieval" in categories or "evaluation" in categories:
                family = "high_technical_fit"
            elif "availability" in categories and not non_avail_strengths:
                family = "high_availability_candidate"
            elif "availability" in categories:
                family = "high_availability_candidate"
            elif len(strengths) >= 3:
                family = "balanced_candidate"
            elif self._is_strong(match):
                family = "strong_match"
            else:
                family = "balanced_candidate"

            # Render primary sentence
            if family == "high_availability_candidate" and not non_avail_strengths:
                if pattern_index == 0:
                    sentences.append("High availability candidate with strong recruiter engagement and recent activity.")
                elif pattern_index == 1:
                    sentences.append("Highly active candidate showing active recruiter response and recent platform engagement.")
                else:
                    sentences.append("Immediately active candidate exhibiting strong recruiter engagement and recent activity.")
                append_avail_sentence = False
            else:
                primary = non_avail_strengths[:3]
                if not primary:
                    sentences.append("Good fit candidate.")
                else:
                    primary_desc = self._join(item.description for item in primary)
                    if family == "strong_production_background":
                        if pattern_index == 0:
                            sentences.append(f"Strong production background highlighted by {primary_desc}.")
                        elif pattern_index == 1:
                            sentences.append(f"Demonstrates a strong production background in {primary_desc}.")
                        else:
                            sentences.append(f"Proven production track record featuring expertise in {primary_desc}.")
                    elif family == "high_technical_fit":
                        if pattern_index == 0:
                            sentences.append(f"High technical fit demonstrating expertise in {primary_desc}.")
                        elif pattern_index == 1:
                            sentences.append(f"Excellent technical match with strong skills in {primary_desc}.")
                        else:
                            sentences.append(f"Displays strong technical capabilities in {primary_desc}.")
                    elif family == "high_availability_candidate":
                        if pattern_index == 0:
                            sentences.append(f"High availability candidate with key strengths in {primary_desc}.")
                        elif pattern_index == 1:
                            sentences.append(f"Highly active candidate featuring key strengths in {primary_desc}.")
                        else:
                            sentences.append(f"Immediately active candidate showing strong fit in {primary_desc}.")
                    elif family == "strong_match":
                        if pattern_index == 0:
                            sentences.append(f"Strong match due to {primary_desc}.")
                        elif pattern_index == 1:
                            sentences.append(f"Highly recommended candidate, showing strong match due to {primary_desc}.")
                        else:
                            sentences.append(f"Excellent match based on {primary_desc}.")
                    else:  # balanced_candidate / fallback
                        if self._is_strong(match):
                            if pattern_index == 0:
                                sentences.append(f"Well-balanced candidate showing strong fit in {primary_desc}.")
                            elif pattern_index == 1:
                                sentences.append(f"Strong, multi-faceted profile demonstrating depth in {primary_desc}.")
                            else:
                                sentences.append(f"Highly balanced match with key qualifications in {primary_desc}.")
                        else:
                            if pattern_index == 0:
                                sentences.append(f"Balanced candidate profile with solid experience across {primary_desc}.")
                            elif pattern_index == 1:
                                sentences.append(f"Broadly qualified profile with demonstrated experience in {primary_desc}.")
                            else:
                                sentences.append(f"Well-rounded profile showing capabilities across {primary_desc}.")
                append_avail_sentence = has_avail

            # Render secondary strengths
            secondary = [
                item.description
                for item in non_avail_strengths[3:5]
            ]
            if secondary:
                sentences.append(f"Also demonstrates {self._join(secondary)}.")

            if append_avail_sentence:
                if pattern_index == 0:
                    sentences.append("Candidate also shows strong recruiter engagement and recent activity.")
                elif pattern_index == 1:
                    sentences.append("Active recruiter response and recent platform engagement are also demonstrated.")
                else:
                    sentences.append("Engagement metrics show active recruiter responsiveness and recent activity.")
        else:
            if pattern_index == 0:
                sentences.append("Limited evidence-backed strengths were available from the ranking output.")
            elif pattern_index == 1:
                sentences.append("Minimal evidence-backed strengths were identified in the ranking results.")
            else:
                sentences.append("Ranking output indicates limited positive evidence for this profile.")

        for i, concern in enumerate(concerns[:2]):
            concern_index = (pattern_index + i) % 3
            if concern_index == 0:
                sentences.append(f"Potential concern: {concern.description}.")
            elif concern_index == 1:
                sentences.append(f"Area for review: {concern.description}.")
            else:
                sentences.append(f"Note: {concern.description}.")

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
