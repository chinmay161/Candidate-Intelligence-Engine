from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.feature_store import CandidateFeatureStore
from candidate_processor.parser import CandidateParser


class CandidateFeatureStoreTests(unittest.TestCase):
    def test_feature_store_round_trips_csv(self) -> None:
        candidate = CandidateParser().parse_json_array(Path("data/sample_candidates.json"))[0]
        record = CandidateFeatureExtractor().extract(candidate)

        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidate_features.csv"
            store = CandidateFeatureStore()
            store.save_csv([record], path)
            rows = store.load_csv(path)

        self.assertEqual(rows[0]["candidate_id"], record.candidate_id)
        self.assertEqual(
            rows[0]["semantic_features"]["jd_semantic_bm25_score"],
            record.semantic_features["jd_semantic_bm25_score"],
        )
        self.assertIn("redrob_signals", rows[0]["evidence"])


if __name__ == "__main__":
    unittest.main()
