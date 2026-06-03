from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from candidate_processor.text_builder import CandidateTextBuilder
from candidate_processor.validators import parse_candidate


def _payload() -> dict:
    return json.loads(Path("data/sample_candidates.json").read_text(encoding="utf-8"))[0]


class CandidateTextBuilderTests(unittest.TestCase):
    def test_builder_normalizes_whitespace_and_removes_duplicates(self) -> None:
        payload = copy.deepcopy(_payload())
        payload["profile"]["headline"] = "Senior   ML Engineer"
        payload["profile"]["summary"] = "Senior ML Engineer"
        payload["skills"].append({"name": "python", "proficiency": "advanced", "endorsements": 1, "duration_months": 12})
        payload["skills"].append({"name": "Python", "proficiency": "expert", "endorsements": 2, "duration_months": 24})
        candidate = parse_candidate(payload)
        builder = CandidateTextBuilder()

        profile_text = builder.build_profile_text(candidate)
        skill_text = builder.build_skill_text(candidate)
        full_text = builder.build_full_text(candidate)

        self.assertIn("Senior ML Engineer", profile_text)
        self.assertEqual(skill_text.count("Python"), 1)
        self.assertIn(candidate.career_history[0].description[:80], full_text)
        self.assertIs(builder.build_full_text(candidate), full_text)

    def test_core_text_includes_current_context(self) -> None:
        candidate = parse_candidate(_payload())
        core_text = CandidateTextBuilder().build_core_text(candidate)

        self.assertIn(candidate.profile.current_title, core_text)
        self.assertIn(candidate.profile.current_company, core_text)


if __name__ == "__main__":
    unittest.main()
