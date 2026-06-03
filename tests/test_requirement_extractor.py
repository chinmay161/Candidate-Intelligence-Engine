from __future__ import annotations

import unittest

from jd_parser.requirement_extractor import RequirementExtractor


class RequirementExtractorTests(unittest.TestCase):
    def test_extracts_experience_industry_location_and_behavior(self) -> None:
        jd = """
        Senior AI Engineer, Pune or Noida, hybrid.
        Required: 5-9 years building semantic search, vector databases, and Python services.
        We are an HR Tech recruitment marketplace.
        You should have startup mindset, ownership, communication, product thinking, and experimentation.
        """

        requirement = RequirementExtractor().extract(jd)

        self.assertEqual(requirement.experience_min, 5)
        self.assertEqual(requirement.experience_max, 9)
        self.assertEqual(requirement.seniority, "senior")
        self.assertIn("hrtech", requirement.industries)
        self.assertIn("recruitment", requirement.industries)
        self.assertIn("marketplace", requirement.industries)
        self.assertIn("pune", requirement.locations)
        self.assertIn("noida", requirement.locations)
        self.assertIn("hybrid", requirement.locations)
        self.assertIn("ownership", requirement.behavioral_preferences)
        self.assertIn("product_thinking", requirement.behavioral_preferences)

    def test_extracts_plus_years(self) -> None:
        requirement = RequirementExtractor().extract("Need 6+ years of Python and ML experience.")

        self.assertEqual(requirement.experience_min, 6)
        self.assertEqual(requirement.experience_max, 10)


if __name__ == "__main__":
    unittest.main()

