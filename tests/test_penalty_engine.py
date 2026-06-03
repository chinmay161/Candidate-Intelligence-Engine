from __future__ import annotations

import unittest

from ranking.penalty_engine import PenaltyEngine
from ranking_fixtures import candidate_record, retrieval_jd


class PenaltyEngineTests(unittest.TestCase):
    def test_applies_anomaly_services_and_notice_penalties(self) -> None:
        score, penalties = PenaltyEngine().apply(
            retrieval_jd(),
            candidate_record("RISKY", fit=0.8, penalty=0.9, notice_score=0.2),
        )

        reasons = {penalty.reason for penalty in penalties}
        self.assertGreater(score, 0.10)
        self.assertIn("suspicious-profile risk", reasons)
        self.assertIn("services-only career signal", reasons)
        self.assertIn("90 day notice period", reasons)
        self.assertTrue(all(penalty.value > 0 for penalty in penalties))


if __name__ == "__main__":
    unittest.main()
