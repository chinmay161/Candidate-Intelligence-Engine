from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.evidence_selector import EvidenceSelector
from reasoning.strength_detector import StrengthDetector


class StrengthDetectorTests(unittest.TestCase):
    def test_detects_only_evidence_backed_strengths(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record()
        match = CandidateScorer().score(analysis, candidate)
        evidence = EvidenceSelector().select(match, candidate)

        strengths = StrengthDetector().detect(analysis, match, candidate, evidence)

        categories = {strength.category for strength in strengths}
        self.assertIn("production", categories)
        self.assertIn("retrieval", categories)
        self.assertIn("availability", categories)
        self.assertTrue(all(strength.supporting_evidence for strength in strengths))

    def test_does_not_invent_strengths_for_low_fit_candidate(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("LOW", fit=0.15)
        match = CandidateScorer().score(analysis, candidate)
        evidence = EvidenceSelector().select(match, candidate)

        strengths = StrengthDetector().detect(analysis, match, candidate, evidence)

        self.assertFalse(any(strength.category == "production" for strength in strengths))
        self.assertFalse(any(strength.category == "retrieval" for strength in strengths))


if __name__ == "__main__":
    unittest.main()
