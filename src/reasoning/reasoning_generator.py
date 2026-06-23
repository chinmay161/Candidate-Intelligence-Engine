"""End-to-end deterministic reasoning generation."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from jd_parser.jd_models import JDAnalysis
from ranking.match_models import CandidateMatch
from reasoning.concern_detector import ConcernDetector
from reasoning.confidence_estimator import ReasoningConfidenceEstimator
from reasoning.evidence_selector import EvidenceSelector
from reasoning.reasoning_models import ReasoningResult
from reasoning.reasoning_templates import ReasoningTemplates
from reasoning.strength_detector import StrengthDetector


class ReasoningGenerator:
    """Generate one evidence-backed explanation for one candidate match."""

    def __init__(
        self,
        *,
        evidence_selector: EvidenceSelector | None = None,
        strength_detector: StrengthDetector | None = None,
        concern_detector: ConcernDetector | None = None,
        templates: ReasoningTemplates | None = None,
        confidence_estimator: ReasoningConfidenceEstimator | None = None,
    ) -> None:
        self.evidence_selector = evidence_selector or EvidenceSelector()
        self.strength_detector = strength_detector or StrengthDetector()
        self.concern_detector = concern_detector or ConcernDetector()
        self.templates = templates or ReasoningTemplates()
        self.confidence_estimator = confidence_estimator or ReasoningConfidenceEstimator()

    def generate(
        self,
        analysis: JDAnalysis,
        match: CandidateMatch,
        candidate: CandidateFeatureRecord,
        rank: int | None = None,
    ) -> ReasoningResult:
        evidence = self.evidence_selector.select(match, candidate)
        strengths = self.strength_detector.detect(analysis, match, candidate, evidence)
        concerns = self.concern_detector.detect(analysis, match, candidate)
        reasoning = self.templates.render(match, strengths, concerns, candidate=candidate, rank=rank)
        confidence = self.confidence_estimator.estimate(match, candidate, evidence, strengths, concerns)

        return ReasoningResult(
            candidate_id=match.candidate_id,
            reasoning=reasoning,
            confidence=confidence,
            evidence=tuple(evidence),
            strengths=tuple(strengths),
            concerns=tuple(concerns),
        )
