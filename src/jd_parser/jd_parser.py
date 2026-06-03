"""Top-level orchestration for job-description intelligence."""

from __future__ import annotations

from jd_parser.confidence_estimator import ConfidenceEstimator
from jd_parser.jd_models import JDAnalysis, JobDescription, WeightProfile
from jd_parser.negative_signal_detector import NegativeSignalDetector
from jd_parser.requirement_extractor import RequirementExtractor
from jd_parser.role_detector import RoleDetector
from jd_parser.weight_generator import WeightGenerator


class JDParser:
    """Convert raw job descriptions into structured machine-readable analysis."""

    def __init__(
        self,
        *,
        role_detector: RoleDetector | None = None,
        requirement_extractor: RequirementExtractor | None = None,
        negative_signal_detector: NegativeSignalDetector | None = None,
        weight_generator: WeightGenerator | None = None,
        confidence_estimator: ConfidenceEstimator | None = None,
    ) -> None:
        self.role_detector = role_detector or RoleDetector()
        self.requirement_extractor = requirement_extractor or RequirementExtractor()
        self.negative_signal_detector = negative_signal_detector or NegativeSignalDetector()
        self.weight_generator = weight_generator or WeightGenerator()
        self.confidence_estimator = confidence_estimator or ConfidenceEstimator()

    def parse(self, raw_text: str, *, title: str = "", company: str = "", location_hint: str = "") -> JDAnalysis:
        """Parse raw JD text and optional metadata into a complete analysis."""

        job_description = JobDescription(
            raw_text=raw_text,
            title=title,
            company=company,
            location_hint=location_hint,
        )
        combined_text = "\n".join(part for part in (title, location_hint, raw_text) if part)
        role_classification = self.role_detector.detect(title=title, jd_text=combined_text)
        requirements = self.requirement_extractor.extract(combined_text)
        negative_signals = self.negative_signal_detector.detect(combined_text)
        draft = JDAnalysis(
            job_description=job_description,
            role_classification=role_classification,
            requirements=requirements,
            negative_signals=negative_signals,
            feature_weights=WeightProfile(),
            confidence=0.0,
        )
        feature_weights = self.weight_generator.generate(draft)
        confidence = self.confidence_estimator.estimate_partial(
            role_classification=role_classification,
            requirements=requirements,
            negative_signals=negative_signals,
        )
        return JDAnalysis(
            job_description=job_description,
            role_classification=role_classification,
            requirements=requirements,
            negative_signals=negative_signals,
            feature_weights=feature_weights,
            confidence=confidence,
        )

