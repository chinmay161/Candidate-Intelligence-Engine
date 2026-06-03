from __future__ import annotations

import unittest

from ranking.contribution_tracker import ContributionTracker
from ranking.score_calculator import ScoreCalculator
from ranking_fixtures import candidate_record, retrieval_jd


class ScoreCalculatorTests(unittest.TestCase):
    def test_calculates_breakdown_and_feature_contributions(self) -> None:
        tracker = ContributionTracker()
        breakdown = ScoreCalculator().calculate(
            retrieval_jd(),
            candidate_record(),
            semantic_score=0.8,
            feature_match_score=0.85,
            penalty_score=0.05,
            tracker=tracker,
        )
        contributions = {item.feature: item for item in tracker.as_tuple()}

        self.assertGreater(breakdown.final_score, 0.70)
        self.assertLess(breakdown.final_score, breakdown.raw_score)
        self.assertIn("retrieval_skill_depth", contributions)
        self.assertGreater(contributions["retrieval_skill_depth"].contribution, 0.0)
        self.assertEqual(contributions["penalty_score"].contribution, -0.05)
        self.assertIn("skill", breakdown.group_scores)


if __name__ == "__main__":
    unittest.main()
