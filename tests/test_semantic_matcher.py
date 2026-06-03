from __future__ import annotations

import unittest

from ranking.semantic_matcher import SemanticMatcher
from ranking_fixtures import candidate_record, retrieval_jd


class SemanticMatcherTests(unittest.TestCase):
    def test_retrieval_candidate_scores_above_weak_candidate(self) -> None:
        analysis = retrieval_jd()
        matcher = SemanticMatcher()

        strong = matcher.score(analysis, candidate_record("STRONG", fit=1.0))
        weak = matcher.score(analysis, candidate_record("WEAK", fit=0.2))

        self.assertGreater(strong, 0.70)
        self.assertLess(weak, strong)
        self.assertGreaterEqual(strong, 0.0)
        self.assertLessEqual(strong, 1.0)


if __name__ == "__main__":
    unittest.main()
