"""Confidence estimation for parsed job-description intelligence."""

from __future__ import annotations

from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis, JobRequirement, RoleClassification


class ConfidenceEstimator:
    """Estimate certainty from skill coverage, role confidence, completeness, and ambiguity."""

    def estimate_partial(
        self,
        *,
        role_classification: RoleClassification,
        requirements: JobRequirement,
        negative_signals: tuple[str, ...] = (),
    ) -> float:
        """Estimate confidence before the full JDAnalysis object exists."""

        skill_count = (
            len(requirements.required_skills)
            + len(requirements.preferred_skills) * 0.7
            + len(requirements.optional_skills) * 0.3
        )
        skill_coverage = clamp(skill_count / 8.0)
        completeness = sum(
            (
                bool(requirements.experience_min),
                bool(requirements.industries),
                bool(requirements.locations),
                bool(requirements.behavioral_preferences),
            )
        ) / 4.0
        ambiguity_penalty = 0.18 if role_classification.role_family == "UNKNOWN" else 0.0
        ambiguity_penalty += 0.04 * max(0, len(negative_signals) - 3)
        return round(
            clamp(
                role_classification.confidence * 0.4
                + skill_coverage * 0.3
                + completeness * 0.3
                - ambiguity_penalty
            ),
            4,
        )

    def estimate(self, analysis: JDAnalysis) -> float:
        """Estimate confidence for a full analysis object."""

        return self.estimate_partial(
            role_classification=analysis.role_classification,
            requirements=analysis.requirements,
            negative_signals=analysis.negative_signals,
        )

