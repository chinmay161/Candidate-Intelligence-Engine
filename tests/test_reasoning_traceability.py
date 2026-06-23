from __future__ import annotations

import unittest

from candidate_processor.models import CandidateFeatureRecord
from ranking.candidate_scorer import CandidateScorer
from ranking.match_models import CandidateMatch
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.reasoning_generator import ReasoningGenerator
from reasoning.reasoning_models import ReasoningResult


def _get_candidate_feature_value(candidate: CandidateFeatureRecord, feature: str) -> tuple[float | int | None, bool]:
    for group in ("semantic", "experience", "skill", "behavioral", "career", "education", "logistics", "anomaly"):
        features = getattr(candidate, f"{group}_features")
        if feature in features:
            return features[feature], True
    return None, False


class ReasoningTraceabilityTests(unittest.TestCase):
    def verify_traceability(
        self,
        match: CandidateMatch,
        candidate: CandidateFeatureRecord,
        result: ReasoningResult,
    ) -> None:
        # 1. Verify that all evidence items match candidate data or match data
        for ev in result.evidence:
            if ev.source == "candidate_match":
                if ev.feature == "matched_requirements":
                    matched_required = sum(
                        1 for item in match.matched_requirements if item.startswith("required_skill:")
                    )
                    self.assertEqual(ev.raw_value, matched_required)
                elif "missing" in ev.feature:
                    importance = "required" if "required" in ev.feature else "preferred"
                    missing = [item for item in match.missing_requirements if item.startswith(f"{importance}_skill:")]
                    self.assertEqual(ev.raw_value, len(missing))
            else:
                val, found = _get_candidate_feature_value(candidate, ev.feature)
                self.assertTrue(found, f"Evidence feature '{ev.feature}' not found in candidate record")
                self.assertAlmostEqual(val, ev.raw_value, places=5)

                # Snippets check
                raw_snippets = candidate.evidence.get(ev.feature)
                for snippet in ev.snippets:
                    self.assertIn(snippet, raw_snippets)

        import re
        sentences = [s.strip() for s in re.split(r'\.(?!\d)', result.reasoning.replace("?", ".")) if s.strip()]

        for sentence in sentences:
            mapped = False

            # Fallback check
            if any(
                term in sentence.lower()
                for term in [
                    "limited evidence-backed strengths",
                    "minimal evidence-backed strengths",
                    "ranking output indicates limited positive evidence",
                ]
            ):
                mapped = True
                continue

            # Availability/Behavioral check
            if any(
                term in sentence.lower()
                for term in [
                    "available", "active", "engagement", "responsiveness", "responsive", "platform", "notice", "behavioral"
                ]
            ):
                mapped = True
                continue

            # Concerns check
            if any(sentence.startswith(prefix) for prefix in ["Potential concern:", "Area for review:", "Note:"]):
                mapped = True
                continue

            # Strength / Experience / JD Alignment / Closings
            if any(
                term in sentence.lower()
                for term in [
                    "experience", "background", "match", "alignment", "fit", "skills", "infrastructure", 
                    "profile", "recommend", "priority", "tradeoff", "gap", "ramping", "engineering",
                    "retrieval", "systems", "coding", "history", "ramp", "demand", "familiarity",
                    "capability", "capabilities"
                ]
            ):
                mapped = True
                continue

            self.assertTrue(
                mapped,
                f"Sentence '{sentence}' could not be traced back to candidate strengths/concerns/availability/fallback",
            )

    def test_traceability_strong_candidate(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record()
        match = CandidateScorer().score(analysis, candidate)
        result = ReasoningGenerator().generate(analysis, match, candidate)
        self.verify_traceability(match, candidate, result)

    def test_traceability_weak_candidate(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("WEAK", fit=0.15)
        match = CandidateScorer().score(analysis, candidate)
        result = ReasoningGenerator().generate(analysis, match, candidate)
        self.verify_traceability(match, candidate, result)

    def test_traceability_candidate_with_penalties(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("PENALTY", penalty=1.0)
        match = CandidateScorer().score(analysis, candidate)
        result = ReasoningGenerator().generate(analysis, match, candidate)
        self.verify_traceability(match, candidate, result)

    def test_traceability_only_availability(self) -> None:
        analysis = retrieval_jd()
        # Set other features below thresholds but availability high
        candidate = candidate_record("AVAIL", fit=0.1)
        # Manually force availability features
        candidate.behavioral_features["availability_multiplier"] = 1.2
        candidate.evidence.by_feature["availability_multiplier"] = ["active and open to work"]

        match = CandidateScorer().score(analysis, candidate)
        result = ReasoningGenerator().generate(analysis, match, candidate)
        self.verify_traceability(match, candidate, result)

    def test_traceability_no_strengths(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("NO_STRENGTHS", fit=0.0)
        # Clear evidence snippets to prevent any positive evidence selection
        candidate.evidence.by_feature.clear()

        match = CandidateScorer().score(analysis, candidate)
        result = ReasoningGenerator().generate(analysis, match, candidate)
        self.verify_traceability(match, candidate, result)


if __name__ == "__main__":
    unittest.main()
