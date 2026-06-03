from __future__ import annotations

import unittest

from ranking.feature_matcher import FeatureMatcher
from ranking_fixtures import candidate_record, retrieval_jd


class FeatureMatcherTests(unittest.TestCase):
    def test_matches_required_skills_experience_and_location(self) -> None:
        result = FeatureMatcher().match(retrieval_jd(), candidate_record())

        self.assertGreater(result.match_score, 0.70)
        self.assertIn("required_skill:semantic_search", result.matched_requirements)
        self.assertIn("required_skill:python", result.matched_requirements)
        self.assertTrue(any(item.startswith("experience:") for item in result.matched_requirements))
        self.assertFalse(any(item.startswith("required_skill:") for item in result.missing_requirements))

    def test_marks_missing_required_skills_for_low_fit_candidate(self) -> None:
        result = FeatureMatcher().match(retrieval_jd(), candidate_record(fit=0.15))

        self.assertLess(result.match_score, 0.45)
        self.assertTrue(any(item.startswith("required_skill:") for item in result.missing_requirements))


if __name__ == "__main__":
    unittest.main()
