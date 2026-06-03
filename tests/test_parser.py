from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from candidate_processor.parser import CandidateParser


class CandidateParserTests(unittest.TestCase):
    def test_parser_loads_sample_json_array(self) -> None:
        parser = CandidateParser()
        candidates = parser.parse_json_array(Path("data/sample_candidates.json"))

        self.assertEqual(len(candidates), 50)
        self.assertEqual(candidates[0].candidate_id, "CAND_0000001")
        self.assertGreaterEqual(candidates[0].profile.years_of_experience, 0)

    def test_parser_streams_jsonl_and_skips_malformed(self) -> None:
        payload = json.loads(Path("data/candidates.jsonl").read_text(encoding="utf-8").splitlines()[0])
        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidates.jsonl"
            path.write_text(json.dumps(payload) + "\n" + "{bad json}\n", encoding="utf-8")

            parser = CandidateParser()
            candidates = list(parser.stream_jsonl(path))

        self.assertEqual(len(candidates), 1)
        self.assertEqual(parser.malformed_records, 1)


if __name__ == "__main__":
    unittest.main()
