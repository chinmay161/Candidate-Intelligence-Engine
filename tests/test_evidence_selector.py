from __future__ import annotations

import unittest

from ranking.candidate_scorer import CandidateScorer
from ranking_fixtures import candidate_record, retrieval_jd
from reasoning.evidence_selector import EvidenceSelector
from reasoning.reasoning_models import ReasoningEvidence


class EvidenceSelectorTests(unittest.TestCase):
    def test_selects_top_five_grounded_priority_evidence_items(self) -> None:
        candidate = candidate_record()
        match = CandidateScorer().score(retrieval_jd(), candidate)

        evidence = EvidenceSelector().select(match, candidate)

        self.assertLessEqual(len(evidence), 5)
        self.assertTrue(all(isinstance(item, ReasoningEvidence) for item in evidence))
        self.assertTrue(all(item.snippets for item in evidence))
        self.assertEqual(evidence[0].feature, "production_ir_evidence_score")
        self.assertIn("retrieval_skill_depth", {item.feature for item in evidence})


if __name__ == "__main__":
    unittest.main()
