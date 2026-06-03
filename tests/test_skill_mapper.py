from __future__ import annotations

import unittest

from jd_parser.skill_mapper import SkillMapper


class SkillMapperTests(unittest.TestCase):
    def test_canonicalizes_required_and_preferred_skills(self) -> None:
        jd = """
        Required: Python, Sentence Transformers, BGE, Pinecone, Elasticsearch, and learning to rank.
        Preferred: Qdrant, OpenSearch, NDCG, and MLflow.
        Optional: familiarity with OpenCV.
        """

        skills = SkillMapper().extract(jd)
        required = {skill.canonical_name for skill in skills["required_skills"]}
        preferred = {skill.canonical_name for skill in skills["preferred_skills"]}
        optional = {skill.canonical_name for skill in skills["optional_skills"]}

        self.assertIn("python", required)
        self.assertIn("embeddings", required)
        self.assertIn("vector_database", required)
        self.assertIn("search", required)
        self.assertIn("ranking", required)
        self.assertIn("ranking_evaluation", preferred)
        self.assertIn("mlops", preferred)
        self.assertIn("computer_vision", optional)

    def test_unknown_skill_returns_none(self) -> None:
        self.assertIsNone(SkillMapper().canonicalize("Underwater Basket Weaving"))


if __name__ == "__main__":
    unittest.main()

