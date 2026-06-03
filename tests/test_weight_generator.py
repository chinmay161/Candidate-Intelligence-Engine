from __future__ import annotations

import unittest

from jd_parser.jd_parser import JDParser
from jd_parser.jd_models import WeightProfile


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
        self.assertAlmostEqual(_weight_sum(weights), 1.0, delta=0.01)
        self.assertGreater(weights["skill"]["retrieval_skill_depth"], 0.03)
        self.assertGreater(weights["skill"]["vector_db_skill_coverage"], 0.03)
        self.assertGreater(weights["semantic"]["ranking_eval_phrase_score"], 0.03)
        self.assertGreater(weights["career"]["services_only_penalty"], 0.02)
        self.assertIn("Required skill", analysis.feature_weights.explanations["retrieval_skill_depth"]["reason"])
        self.assertEqual(
            analysis.feature_weights.explanations["retrieval_skill_depth"]["weight"],
            weights["skill"]["retrieval_skill_depth"],
        )
        self.assertGreater(analysis.confidence, 0.55)

    def test_computer_vision_jd_does_not_overweight_retrieval(self) -> None:
        jd = """
        ML Engineer for computer vision. Required: Python, PyTorch, OpenCV, object detection,
        model deployment, and 4+ years of production ML experience.
        Preferred: Docker and Kubernetes.
        """

        analysis = JDParser().parse(jd, title="Machine Learning Engineer")
        weights = analysis.feature_weights.by_group

        self.assertAlmostEqual(_weight_sum(weights), 1.0, delta=0.01)
        self.assertGreater(weights["experience"]["production_ml_years_proxy"], 0.06)
        self.assertGreater(weights["skill"]["mlops_skill_score"], 0.03)
        self.assertLess(weights["skill"]["retrieval_skill_depth"], 0.01)
        self.assertGreater(weights["skill"]["cv_speech_robotics_dominance_penalty"], 0.06)
        self.assertIn(
            "Required skill: computer vision",
            analysis.feature_weights.explanations["cv_speech_robotics_dominance_penalty"]["reason"],
        )

    def test_weight_profile_normalizes_across_groups(self) -> None:
        profile = WeightProfile(
            by_group={
                "skill": {
                    "retrieval_skill_depth": 1.0,
                    "vector_db_skill_coverage": 0.8,
                },
                "behavioral": {
                    "availability_multiplier": 0.4,
                },
            },
            reasons={"retrieval_skill_depth": "Required skill: retrieval systems"},
        )

        normalized = profile.normalize()

        self.assertAlmostEqual(_weight_sum(normalized.by_group), 1.0, delta=0.01)
        self.assertGreater(
            normalized.by_group["skill"]["retrieval_skill_depth"],
            normalized.by_group["skill"]["vector_db_skill_coverage"],
        )
        self.assertGreater(
            normalized.by_group["skill"]["vector_db_skill_coverage"],
            normalized.by_group["behavioral"]["availability_multiplier"],
        )
        self.assertEqual(
            normalized.explanations["retrieval_skill_depth"]["reason"],
            "Required skill: retrieval systems",
        )


def _weight_sum(weights: dict[str, dict[str, float]]) -> float:
    return sum(weight for group_weights in weights.values() for weight in group_weights.values())


if __name__ == "__main__":
    unittest.main()
