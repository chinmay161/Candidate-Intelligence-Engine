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

        # 2. Verify that every sentence in the reasoning matches strengths, concerns, availability, or fallback
        sentences = [s.strip() for s in result.reasoning.replace("?", ".").split(".") if s.strip()]

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
                self.assertEqual(len(result.strengths), 0)
                mapped = True
                continue

            # Availability sentence checks
            if (
                "candidate also shows strong recruiter engagement" in sentence.lower()
                or "active recruiter response and recent platform" in sentence.lower()
                or "engagement metrics show active recruiter responsiveness" in sentence.lower()
                or sentence.lower().startswith("high availability candidate")
                or sentence.lower().startswith("highly active candidate")
                or sentence.lower().startswith("immediately active candidate")
            ):
                self.assertTrue(any(s.category == "availability" for s in result.strengths))
                mapped = True
                continue

            # Concerns check
            if (
                sentence.startswith("Potential concern:")
                or sentence.startswith("Area for review:")
                or sentence.startswith("Note:")
            ):
                matched_concern = None
                for concern in result.concerns:
                    if concern.description.lower() in sentence.lower():
                        matched_concern = concern
                        break
                self.assertIsNotNone(
                    matched_concern,
                    f"Sentence '{sentence}' indicates concern but matches no concern in result",
                )
                for ev in matched_concern.supporting_evidence:
                    if ev.source == "candidate_match" and "missing" in ev.feature:
                        importance = "required" if "required" in ev.feature else "preferred"
                        missing = [item for item in match.missing_requirements if item.startswith(f"{importance}_skill:")]
                        self.assertEqual(ev.raw_value, len(missing))
                    else:
                        val, found = _get_candidate_feature_value(candidate, ev.feature)
                        self.assertTrue(found, f"Concern feature '{ev.feature}' not found in candidate record")
                        self.assertAlmostEqual(val, ev.raw_value, places=5)
                mapped = True
                continue

            # Strengths check
            for strength in result.strengths:
                if strength.category == "availability":
                    continue

                desc = strength.description.lower()
                # Check if the strength description or parts of it are in the sentence
                if desc in sentence.lower() or any(part in sentence.lower() for part in desc.split(", ")):
                    for ev in strength.supporting_evidence:
                        if ev.source == "candidate_match" and ev.feature == "matched_requirements":
                            matched_required = sum(
                                1 for item in match.matched_requirements if item.startswith("required_skill:")
                            )
                            self.assertEqual(ev.raw_value, matched_required)
                        else:
                            val, found = _get_candidate_feature_value(candidate, ev.feature)
                            self.assertTrue(found, f"Strength feature '{ev.feature}' not found in candidate record")
                            self.assertAlmostEqual(val, ev.raw_value, places=5)
                    mapped = True

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
