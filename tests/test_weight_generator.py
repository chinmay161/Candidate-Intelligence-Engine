from __future__ import annotations

import unittest

from jd_parser.jd_parser import JDParser


class WeightGeneratorTests(unittest.TestCase):
    def test_retrieval_jd_prioritizes_retrieval_features(self) -> None:
        jd = """
        Senior AI Engineer for HR Tech recruitment marketplace.
        Required: 5-9 years, Python, semantic search, embeddings, Pinecone, Elasticsearch,
        hybrid search, learning to rank, NDCG, MRR, production ranking systems.
        Must be hands-on with ownership, startup mindset, and product thinking.
        No consulting background. Not purely academic.
        """

        analysis = JDParser().parse(jd, title="Senior AI Engineer")
        weights = analysis.feature_weights.by_group

        self.assertEqual(analysis.role_family, "AI_ENGINEER")
        self.assertIn("semantic", weights)
        self.assertIn("experience", weights)
        self.assertIn("skill", weights)
        self.assertIn("behavioral", weights)
        self.assertIn("career", weights)
        self.assertIn("education", weights)
        self.assertIn("logistics", weights)
        self.assertIn("anomaly", weights)
        self.assertGreater(weights["skill"]["retrieval_skill_depth"], 0.7)
        self.assertGreater(weights["skill"]["vector_db_skill_coverage"], 0.7)
        self.assertGreater(weights["semantic"]["ranking_eval_phrase_score"], 0.7)
        self.assertGreater(weights["career"]["services_only_penalty"], 0.5)
        self.assertGreater(analysis.confidence, 0.55)

    def test_computer_vision_jd_does_not_overweight_retrieval(self) -> None:
        jd = """
        ML Engineer for computer vision. Required: Python, PyTorch, OpenCV, object detection,
        model deployment, and 4+ years of production ML experience.
        Preferred: Docker and Kubernetes.
        """

        analysis = JDParser().parse(jd, title="Machine Learning Engineer")
        weights = analysis.feature_weights.by_group

        self.assertGreater(weights["experience"]["production_ml_years_proxy"], 0.6)
        self.assertGreater(weights["skill"]["mlops_skill_score"], 0.2)
        self.assertLess(weights["skill"]["retrieval_skill_depth"], 0.2)
        self.assertGreater(weights["skill"]["cv_speech_robotics_dominance_penalty"], 0.2)


if __name__ == "__main__":
    unittest.main()

