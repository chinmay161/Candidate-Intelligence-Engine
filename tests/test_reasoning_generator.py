from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.reasoning_generator import ReasoningGenerator
from reasoning.reasoning_models import ReasoningResult


class ReasoningGeneratorTests(unittest.TestCase):
    def test_generates_concise_grounded_reasoning_for_strong_candidate(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record()
        match = CandidateScorer().score(analysis, candidate)

        result = ReasoningGenerator().generate(analysis, match, candidate)
        restored = ReasoningResult.from_dict(result.to_dict())

        self.assertEqual(restored.candidate_id, candidate.candidate_id)
        self.assertTrue(any(w in result.reasoning.lower() for w in ["match", "fit", "background", "candidate"]))
        self.assertIn("retrieval", result.reasoning.lower())
        self.assertNotIn("appears highly qualified", result.reasoning.lower())
        self.assertGreater(result.confidence, 0.55)
        self.assertGreaterEqual(len(result.reasoning.split()), 20)
        self.assertLessEqual(len(result.reasoning.split()), 80)
        self.assertTrue(result.evidence)
        self.assertTrue(result.strengths)

    def test_generates_concerns_for_weak_candidate(self) -> None:
        analysis = retrieval_jd()
        candidate = candidate_record("WEAK", fit=0.15)
        match = CandidateScorer().score(analysis, candidate)

        result = ReasoningGenerator().generate(analysis, match, candidate)

        self.assertTrue(any(prefix in result.reasoning for prefix in ["Potential concern:", "Area for review:", "Note:"]))
        self.assertTrue(result.concerns)
        self.assertLess(result.confidence, 0.75)


if __name__ == "__main__":
    unittest.main()
