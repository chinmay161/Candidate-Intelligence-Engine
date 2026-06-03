from __future__ import annotations

import unittest

from jd_parser.negative_signal_detector import NegativeSignalDetector


class NegativeSignalDetectorTests(unittest.TestCase):
    def test_detects_explicit_negative_signals(self) -> None:
        jd = """
        This is not research focused and not purely academic.
        No consulting background or agency experience.
        Must be hands-on and must code, not management only.
        Production experience required, not demo only.
        """

        signals = NegativeSignalDetector().detect(jd)

        self.assertIn("research_only", signals)
        self.assertIn("consulting_only", signals)
        self.assertIn("non_hands_on", signals)
        self.assertIn("framework_demo_only", signals)


if __name__ == "__main__":
    unittest.main()

