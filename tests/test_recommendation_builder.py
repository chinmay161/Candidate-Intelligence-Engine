from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.reasoning_generator import ReasoningGenerator
from reasoning.reasoning_models import CandidateRecommendation
from reasoning.recommendation_builder import RecommendationBuilder


class RecommendationBuilderTests(unittest.TestCase):
    def test_builds_serializable_recruiter_recommendation(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record()
        match = CandidateScorer().score(analysis, candidate)
        reasoning = ReasoningGenerator().generate(analysis, match, candidate)

        recommendation = RecommendationBuilder().build(rank=1, match=match, reasoning=reasoning)
        restored = CandidateRecommendation.from_dict(recommendation.to_dict())

        self.assertEqual(restored.candidate_id, candidate.candidate_id)
        self.assertEqual(restored.rank, 1)
        self.assertEqual(restored.score, match.score)
        self.assertEqual(restored.reasoning, reasoning.reasoning)
        self.assertEqual(restored.confidence, reasoning.confidence)
        self.assertTrue(restored.evidence)


if __name__ == "__main__":
    unittest.main()
