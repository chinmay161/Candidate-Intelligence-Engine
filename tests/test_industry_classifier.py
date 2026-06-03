from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from candidate_processor.industry_classifier import IndustryClassifier
from candidate_processor.validators import parse_candidate


def _payload() -> dict:
    return json.loads(Path("data/sample_candidates.json").read_text(encoding="utf-8"))[0]


class IndustryClassifierTests(unittest.TestCase):
    def test_classifies_consulting_company_names(self) -> None:
        classification = IndustryClassifier().classify_fields(
            company_names=("TCS",),
            industries=("IT Services",),
            descriptions=("Delivered client implementation and managed services."),
        )

        self.assertIn(classification.primary_industry, {"CONSULTING", "SERVICES"})
        self.assertGreater(classification.confidence, 0.45)
        self.assertTrue(classification.evidence)

    def test_extracts_product_and_services_features(self) -> None:
        payload = copy.deepcopy(_payload())
        payload["career_history"][0]["company"] = "SearchSaaS"
        payload["career_history"][0]["industry"] = "SaaS"
        payload["career_history"][0]["company_size"] = "51-200"
        payload["career_history"][0]["duration_months"] = 24
        payload["career_history"][0]["description"] = "Built product platform features for marketplace users."
        payload["career_history"][1]["company"] = "TCS"
        payload["career_history"][1]["industry"] = "IT Services"
        payload["career_history"][1]["duration_months"] = 24
        payload["career_history"][1]["description"] = "Delivered consulting and managed services for clients."
        candidate = parse_candidate(payload)

        features = IndustryClassifier().extract_features(candidate)

        self.assertGreaterEqual(features["product_company_exposure_months"], 24)
        self.assertEqual(features["services_only_penalty"], 0.0)
        self.assertGreater(features["industry_diversity_score"], 0)
        self.assertGreater(features["startup_exposure_score"], 0)

    def test_services_only_penalty(self) -> None:
        payload = copy.deepcopy(_payload())
        for index, role in enumerate(payload["career_history"]):
            role["company"] = "TCS" if index == 0 else "Infosys"
            role["industry"] = "IT Services"
            role["description"] = "Delivered consulting services and client implementation."
        candidate = parse_candidate(payload)

        features = IndustryClassifier().extract_features(candidate)

        self.assertEqual(features["services_only_penalty"], 1.0)
        self.assertEqual(features["product_company_exposure_months"], 0)


if __name__ == "__main__":
    unittest.main()

