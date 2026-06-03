from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jd_parser.jd_feature_store import JDFeatureStore
from jd_parser.jd_parser import JDParser


class JDFeatureStoreTests(unittest.TestCase):
    def test_json_round_trip(self) -> None:
        analysis = JDParser().parse(
            "Required: 5+ years, Python, semantic search, Pinecone, NDCG, ownership. Pune hybrid.",
            title="Senior AI Engineer",
        )

        with TemporaryDirectory() as directory:
            path = Path(directory) / "jd_analysis.json"
            store = JDFeatureStore()
            store.save_json(analysis, path)
            loaded = store.load_json(path)

        self.assertEqual(loaded.role_family, analysis.role_family)
        self.assertEqual(loaded.experience_min, analysis.experience_min)
        self.assertEqual(
            loaded.feature_weights.by_group["skill"]["vector_db_skill_coverage"],
            analysis.feature_weights.by_group["skill"]["vector_db_skill_coverage"],
        )
        self.assertEqual(
            loaded.feature_weights.explanations["vector_db_skill_coverage"]["reason"],
            analysis.feature_weights.explanations["vector_db_skill_coverage"]["reason"],
        )

    def test_yaml_round_trip(self) -> None:
        analysis = JDParser().parse("Required: Python and MLflow. Remote role.", title="MLOps Engineer")

        with TemporaryDirectory() as directory:
            path = Path(directory) / "jd_analysis.yaml"
            store = JDFeatureStore()
            store.save_yaml(analysis, path)
            loaded = store.load_yaml(path)

        self.assertEqual(loaded.role_family, analysis.role_family)
        self.assertIn("remote", loaded.locations)
        self.assertIn("weight_explanations", loaded.to_dict())


if __name__ == "__main__":
    unittest.main()
