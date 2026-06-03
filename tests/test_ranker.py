from __future__ import annotations

import unittest

from ranking.ranker import Ranker
from ranking.score_normalizer import ScoreNormalizer
from ranking_fixtures import candidate_record, retrieval_jd


class RankerTests(unittest.TestCase):
    def test_ranks_candidates_stably_and_normalizes_top_k(self) -> None:
        candidates = (
            candidate_record("MID", fit=0.55),
            candidate_record("TOP", fit=1.0),
            candidate_record("LOW", fit=0.2),
            candidate_record("RISKY", fit=0.95, penalty=0.8),
        )

        result = Ranker().rank(retrieval_jd(), candidates, top_k=2)

        self.assertEqual(result.total_candidates, 4)
        self.assertEqual(result.selected_count, 2)
        self.assertEqual(result.matches[0].candidate_id, "TOP")
        self.assertEqual(result.matches[0].score, 100.0)
        self.assertGreaterEqual(result.matches[0].score, result.matches[1].score)

    def test_ranker_can_prerank_before_full_scoring(self) -> None:
        candidates = tuple(candidate_record(f"CAND_{index}", fit=index / 10) for index in range(1, 11))

        result = Ranker().rank(retrieval_jd(), candidates, top_k=2, pre_rank_limit=4)

        self.assertEqual(result.total_candidates, 10)
        self.assertEqual(result.selected_count, 2)
        self.assertEqual(result.matches[0].candidate_id, "CAND_10")

    def test_score_normalizer_supports_zscore_and_softmax(self) -> None:
        raw = Ranker().rank(retrieval_jd(), (candidate_record("A"), candidate_record("B", fit=0.5)), top_k=None)
        zscore = ScoreNormalizer().normalize(raw.matches, method="zscore")
        softmax = ScoreNormalizer().normalize(raw.matches, method="softmax")

        self.assertEqual(len(zscore), 2)
        self.assertAlmostEqual(sum(match.score for match in softmax), 100.0, delta=0.0001)


if __name__ == "__main__":
    unittest.main()
