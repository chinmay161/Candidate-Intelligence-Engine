from __future__ import annotations

import unittest
from pathlib import Path

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY, FeatureDefinition, FeatureRegistry
from candidate_processor.parser import CandidateParser


class FeatureRegistryTests(unittest.TestCase):
    def test_default_registry_contains_all_unique_emitted_features(self) -> None:
        candidate = CandidateParser().parse_json_array(Path("data/sample_candidates.json"))[0]
        record = CandidateFeatureExtractor().extract(candidate)
        emitted_names = set()
        for group in (
            record.semantic_features,
            record.experience_features,
            record.skill_features,
            record.behavioral_features,
            record.career_features,
            record.education_features,
            record.logistics_features,
            record.anomaly_features,
        ):
            emitted_names.update(group)

        registered_names = {definition.name for definition in DEFAULT_FEATURE_REGISTRY.list_all()}

        self.assertEqual(registered_names, emitted_names)
        self.assertEqual(len(registered_names), 90)
        self.assertEqual(DEFAULT_FEATURE_REGISTRY.get("production_ir_evidence_score").priority, 5)
        self.assertTrue(DEFAULT_FEATURE_REGISTRY.get("honeypot_score").is_penalty)
        self.assertIn("availability_multiplier", {item.name for item in DEFAULT_FEATURE_REGISTRY.list_by_group("behavioral")})

    def test_registry_validates_duplicate_and_group(self) -> None:
        registry = FeatureRegistry()
        definition = FeatureDefinition(
            name="example_score",
            group="semantic",
            priority=3,
            description="Example score.",
            feature_type="score",
            is_penalty=False,
            requires_evidence=False,
        )

        registry.register(definition)

        with self.assertRaises(ValueError):
            registry.register(definition)
        with self.assertRaises(ValueError):
            FeatureRegistry(
                (
                    FeatureDefinition(
                        name="bad",
                        group="invalid",
                        priority=3,
                        description="Bad group.",
                        feature_type="score",
                        is_penalty=False,
                        requires_evidence=False,
                    ),
                )
            )


if __name__ == "__main__":
    unittest.main()

