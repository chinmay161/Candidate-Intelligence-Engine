from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.concern_detector import ConcernDetector


class ConcernDetectorTests(unittest.TestCase):
    def test_detects_penalties_and_missing_requirements(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("RISKY", fit=0.2, penalty=0.9, notice_score=0.2)
        match = CandidateScorer().score(analysis, candidate)

        concerns = ConcernDetector().detect(analysis, match, candidate)
        descriptions = " ".join(concern.description for concern in concerns)

        self.assertIn("suspicious-profile risk", descriptions)
        self.assertIn("missing required JD requirement", descriptions)
        self.assertTrue(all(concern.supporting_evidence for concern in concerns))

    def test_detects_honeypot_candidate_from_penalties(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("HONEYPOT", fit=0.9, penalty=1.0)
        match = CandidateScorer().score(analysis, candidate)

        concerns = ConcernDetector().detect(analysis, match, candidate)

        self.assertIn("honeypot_score", {concern.category for concern in concerns})


if __name__ == "__main__":
    unittest.main()
