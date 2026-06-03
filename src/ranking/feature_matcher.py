"""Requirement-level matching against extracted candidate features."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis
from ranking.semantic_matcher import SemanticMatcher


@dataclass(frozen=True, slots=True)
class FeatureMatchResult:
    match_score: float
    matched_requirements: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    requirement_scores: dict[str, float] = field(default_factory=dict)


class FeatureMatcher:
    """Match JD requirements to candidate feature values."""

    def __init__(self) -> None:
        self.semantic_matcher = SemanticMatcher()

    def match(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> FeatureMatchResult:
        matched: list[str] = []
        missing: list[str] = []
        scored: list[tuple[float, float]] = []
        requirement_scores: dict[str, float] = {}

        for skill in analysis.required_skills:
            label = f"required_skill:{skill.canonical_name}"
            score = self.semantic_matcher._canonical_skill_score(skill.canonical_name, candidate)
            requirement_scores[label] = score
            (matched if score >= 0.55 else missing).append(label)
            scored.append((score, 1.4))

        for skill in analysis.preferred_skills:
            label = f"preferred_skill:{skill.canonical_name}"
            score = self.semantic_matcher._canonical_skill_score(skill.canonical_name, candidate)
            requirement_scores[label] = score
            if score >= 0.40:
                matched.append(label)
            scored.append((score, 0.7))

        if analysis.experience_min:
            score = self._experience_score(analysis, candidate)
            label = f"experience:{analysis.experience_min}-{analysis.experience_max or 'open'}"
            requirement_scores[label] = score
            (matched if score >= 0.55 else missing).append(label)
            scored.append((score, 1.1))

        for location in analysis.locations:
            score = self._location_score(location, candidate)
            label = f"location:{location}"
            requirement_scores[label] = score
            if score >= 0.50:
                matched.append(label)
            elif location not in {"remote", "hybrid", "onsite"}:
                missing.append(label)
            scored.append((score, 0.45))

        for industry in analysis.industries:
            score = self._industry_score(candidate)
            label = f"industry:{industry}"
            requirement_scores[label] = score
            if score >= 0.45:
                matched.append(label)
            scored.append((score, 0.45))

        for preference in analysis.behavioral_preferences:
            score = self._behavioral_score(preference, candidate)
            label = f"behavioral:{preference}"
            requirement_scores[label] = score
            if score >= 0.45:
                matched.append(label)
            scored.append((score, 0.35))

        if not scored:
            default_score = self.semantic_matcher.score(analysis, candidate)
            return FeatureMatchResult(
                match_score=default_score,
                matched_requirements=(),
                missing_requirements=(),
                requirement_scores={},
            )

        weighted_total = sum(score * weight for score, weight in scored)
        weight_total = sum(weight for _, weight in scored)
        return FeatureMatchResult(
            match_score=round(clamp(weighted_total / weight_total), 6),
            matched_requirements=tuple(matched),
            missing_requirements=tuple(missing),
            requirement_scores=requirement_scores,
        )

    def _experience_score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        yoe = float(candidate.experience_features.get("yoe_target_band_score", 0.0))
        senior = float(candidate.experience_features.get("senior_judgment_experience_score", 0.0))
        applied_years = float(candidate.experience_features.get("applied_ml_years_proxy", 0.0))
        production_years = float(candidate.experience_features.get("production_ml_years_proxy", 0.0))
        minimum = max(float(analysis.experience_min), 1.0)
        years_fit = clamp(max(applied_years, production_years) / minimum)
        return clamp(yoe * 0.45 + senior * 0.20 + years_fit * 0.35)

    def _location_score(self, location: str, candidate: CandidateFeatureRecord) -> float:
        if location == "india":
            return float(candidate.logistics_features.get("india_location_score", 0.0))
        if location in {"remote", "hybrid", "onsite"}:
            return float(candidate.logistics_features.get("work_mode_fit_score", 0.0))
        return max(
            float(candidate.logistics_features.get("preferred_location_score", 0.0)),
            float(candidate.logistics_features.get("relocation_fit_score", 0.0)) * 0.85,
        )

    def _industry_score(self, candidate: CandidateFeatureRecord) -> float:
        return max(
            float(candidate.career_features.get("current_industry_fit_score", 0.0)),
            clamp(float(candidate.career_features.get("product_company_exposure_months", 0.0)) / 48.0),
            float(candidate.semantic_features.get("candidate_matching_domain_score", 0.0)),
        )

    def _behavioral_score(self, preference: str, candidate: CandidateFeatureRecord) -> float:
        if preference in {"ownership", "startup_mindset"}:
            return max(
                float(candidate.career_features.get("ownership_verbs_score", 0.0)),
                clamp(float(candidate.career_features.get("startup_or_scaleup_exposure", 0.0)) / 4.0),
            )
        if preference == "product_thinking":
            return max(
                float(candidate.semantic_features.get("product_impact_phrase_score", 0.0)),
                float(candidate.career_features.get("cross_functional_product_score", 0.0)),
            )
        if preference == "hands_on":
            return float(candidate.experience_features.get("recent_coding_role_flag", 0.0))
        return max(candidate.behavioral_features.values(), default=0.0)
