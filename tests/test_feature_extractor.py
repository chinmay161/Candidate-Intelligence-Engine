from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.validators import parse_candidate


def _sample_payload(index: int = 0) -> dict:
    return json.loads(Path("data/sample_candidates.json").read_text(encoding="utf-8"))[index]


class CandidateFeatureExtractorTests(unittest.TestCase):
    def test_feature_extractor_emits_all_requested_groups(self) -> None:
        candidate = parse_candidate(_sample_payload())
        record = CandidateFeatureExtractor().extract(candidate)
        feature_count = sum(
            len(group)
            for group in (
                record.semantic_features,
                record.experience_features,
                record.skill_features,
                record.behavioral_features,
                record.career_features,
                record.education_features,
                record.logistics_features,
                record.anomaly_features,
            )
        )

        self.assertEqual(record.candidate_id, "CAND_0000001")
        self.assertEqual(feature_count, 91)
        self.assertIn("production_ir_evidence_score", record.semantic_features)
        self.assertIn("production_eval_cooccurrence_score", record.semantic_features)
        self.assertIn("query_understanding_score", record.semantic_features)
        self.assertIn("yoe_target_band_score", record.experience_features)
        self.assertIn("hands_on_ml_role_ratio", record.experience_features)
        self.assertIn("python_strength_score", record.skill_features)
        self.assertIn("availability_multiplier", record.behavioral_features)
        self.assertIn("contactability_multiplier", record.behavioral_features)
        self.assertIn("product_company_exposure_months", record.career_features)
        self.assertIn("cs_ai_field_score", record.education_features)
        self.assertIn("preferred_location_score", record.logistics_features)
        self.assertIn("honeypot_score", record.anomaly_features)

    def test_production_retrieval_and_evaluation_features_score_positive(self) -> None:
        payload = _sample_payload()
        payload["career_history"][0]["title"] = "Senior ML Search Engineer"
        payload["career_history"][0]["industry"] = "Software"
        payload["career_history"][0]["description"] = (
            "Built a production semantic retrieval and hybrid BM25+dense ranking system for recruiter search. "
            "Owned Elasticsearch, vector index refresh, NDCG, MRR, online A/B tests, latency monitoring, "
            "and feedback loops from recruiters."
        )
        payload["skills"].extend(
            [
                {"name": "Python", "proficiency": "expert", "endorsements": 20, "duration_months": 72},
                {"name": "Elasticsearch", "proficiency": "advanced", "endorsements": 12, "duration_months": 36},
                {"name": "Learning to Rank", "proficiency": "advanced", "endorsements": 8, "duration_months": 30},
            ]
        )
        candidate = parse_candidate(payload)
        record = CandidateFeatureExtractor().extract(candidate)

        self.assertGreater(record.semantic_features["production_ir_evidence_score"], 0)
        self.assertGreater(record.semantic_features["ranking_eval_phrase_score"], 0)
        self.assertEqual(record.semantic_features["hybrid_search_evidence"], 1)
        self.assertGreater(record.skill_features["python_strength_score"], 0.5)
        self.assertTrue(record.evidence.get("production_ir_evidence_score"))

    def test_anomaly_features_detect_keyword_stuffing_and_impossible_duration(self) -> None:
        payload = copy.deepcopy(_sample_payload(1))
        payload["profile"]["current_title"] = "Marketing Manager"
        payload["profile"]["summary"] = "Marketing manager with 12.5 years of experience and AI keywords."
        payload["skills"].extend(
            [
                {"name": "Pinecone", "proficiency": "expert", "endorsements": 4, "duration_months": 0},
                {"name": "Semantic Search", "proficiency": "expert", "endorsements": 4, "duration_months": 0},
                {"name": "Learning to Rank", "proficiency": "expert", "endorsements": 4, "duration_months": 0},
                {"name": "Embeddings", "proficiency": "expert", "endorsements": 4, "duration_months": 0},
                {"name": "RAG", "proficiency": "expert", "endorsements": 4, "duration_months": 0},
            ]
        )
        candidate = parse_candidate(payload)
        record = CandidateFeatureExtractor().extract(candidate)

        self.assertEqual(record.skill_features["ai_keyword_stuffing_penalty"], 1)
        self.assertGreaterEqual(record.anomaly_features["skill_duration_impossibility_count"], 5)
        self.assertGreater(record.anomaly_features["honeypot_score"], 0)


if __name__ == "__main__":
    unittest.main()
