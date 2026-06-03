from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking.match_models import CandidateMatch
from ranking_fixtures import candidate_record, retrieval_jd


class CandidateScorerTests(unittest.TestCase):
    def test_scores_one_candidate_with_serializable_output(self) -> None:
        match = CandidateScorer().score(retrieval_jd(), candidate_record())
        restored = CandidateMatch.from_dict(match.to_dict())

        self.assertEqual(restored.candidate_id, "CAND_MATCH")
        self.assertGreater(match.score, 0.65)
        self.assertGreater(match.confidence, 0.65)
        self.assertTrue(match.feature_contributions)
        self.assertIn("required_skill:python", match.matched_requirements)
        self.assertIsNotNone(match.scoring_breakdown)


if __name__ == "__main__":
    unittest.main()
