from __future__ import annotations

import unittest

from jd_parser.role_detector import RoleDetector


class RoleDetectorTests(unittest.TestCase):
    def test_detects_ai_engineer_from_title_and_stack(self) -> None:
        jd = """
        We need a founding engineer to build LLM-assisted retrieval, RAG, embeddings, and vector search.
        Requirements: strong Python, production ranking systems, and hands-on model deployment.
        """

        classification = RoleDetector().detect(title="Senior AI Engineer", jd_text=jd)

        self.assertEqual(classification.role_family, "AI_ENGINEER")
        self.assertGreater(classification.confidence, 0.45)
        self.assertTrue(classification.evidence)

    def test_detects_data_engineer_from_requirements(self) -> None:
        jd = """
        Requirements: data engineer with Spark, Kafka, Airflow, SQL, and warehouse experience.
        You will build reliable ETL pipelines for analytics and ML features.
        """

        classification = RoleDetector().detect(title="Platform Engineer", jd_text=jd)

        self.assertEqual(classification.role_family, "DATA_ENGINEER")
        self.assertGreater(classification.confidence, 0.3)


if __name__ == "__main__":
    unittest.main()

