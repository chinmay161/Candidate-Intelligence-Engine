from __future__ import annotations

import json
import unittest
from pathlib import Path

from candidate_processor.role_classifier import RoleClassifier
from candidate_processor.validators import parse_candidate


class RoleClassifierTests(unittest.TestCase):
    def test_title_weighting_resists_ai_keyword_stuffing(self) -> None:
        classification = RoleClassifier().classify_texts(
            current_title="Marketing Manager",
            headline="Growth and lifecycle marketing leader",
            summary="Experimented with fine-tuning LLMs, Milvus, vector databases, and RAG demos.",
            career_history=(),
        )

        self.assertEqual(classification.primary_role, "MARKETING")
        self.assertGreaterEqual(classification.confidence, 0.85)
        self.assertTrue(any("current title" in item for item in classification.evidence))

    def test_classifies_ml_candidate_from_sample(self) -> None:
        payload = json.loads(Path("data/sample_candidates.json").read_text(encoding="utf-8"))[0]
        payload["profile"]["current_title"] = "Senior Machine Learning Engineer"
        payload["profile"]["headline"] = "ML engineer building retrieval systems"
        payload["career_history"][0]["title"] = "Machine Learning Engineer"
        payload["career_history"][0]["description"] = "Built production ML services and search ranking systems."
        candidate = parse_candidate(payload)

        classification = RoleClassifier().classify(candidate)

        self.assertIn(classification.primary_role, {"ML_ENGINEER", "AI_ENGINEER"})
        self.assertGreater(classification.confidence, 0.4)
        self.assertTrue(classification.evidence)


if __name__ == "__main__":
    unittest.main()

