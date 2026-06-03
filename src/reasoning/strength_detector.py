"""Deterministic candidate strength detection."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from jd_parser.jd_models import JDAnalysis
from ranking.contribution_tracker import feature_group
from ranking.match_models import CandidateMatch
from reasoning.evidence_selector import FEATURE_DESCRIPTIONS
from reasoning.reasoning_models import CandidateStrength, ReasoningEvidence


class StrengthDetector:
    """Identify evidence-backed strengths without inventing unsupported claims."""

    RULES: tuple[tuple[str, str, str, float], ...] = (
        ("production", "production retrieval and ranking systems", "production_ir_evidence_score", 0.60),
        ("evaluation", "ranking and retrieval evaluation frameworks", "ranking_eval_phrase_score", 0.55),
        ("retrieval", "retrieval, embedding, and vector-search depth", "retrieval_skill_depth", 0.60),
        ("role_fit", "strong target role-family alignment", "role_family_fit_score", 0.60),
        ("availability", "strong recruiter engagement and recent activity", "availability_multiplier", 1.05),
        ("product", "product-company background", "product_company_exposure_months", 24.0),
        ("ownership", "hands-on ownership of shipped systems", "ownership_verbs_score", 0.60),
    )

    def detect(
        self,
        analysis: JDAnalysis,
        match: CandidateMatch,
        candidate: CandidateFeatureRecord,
        evidence: list[ReasoningEvidence],
    ) -> list[CandidateStrength]:
        evidence_by_feature = {item.feature: item for item in evidence}
        strengths: list[CandidateStrength] = []

        for category, description, feature, threshold in self.RULES:
            raw_value, group = self._candidate_value(candidate, feature)
            if raw_value < threshold:
                continue
            support = evidence_by_feature.get(feature) or self._direct_evidence(candidate, feature, group, raw_value)
            if support is None:
                continue
            if feature == "role_family_fit_score" and analysis.role_family != "UNKNOWN":
                description = f"strong {analysis.role_family.replace('_', ' ')} role-family alignment"
            strengths.append(
                CandidateStrength(
                    category=category,
                    description=description,
                    supporting_evidence=(support,),
                )
            )

        matched_required = sum(1 for item in match.matched_requirements if item.startswith("required_skill:"))
        if matched_required >= 2:
            support = self._requirement_evidence(match, matched_required)
            strengths.append(
                CandidateStrength(
                    category="requirements",
                    description="coverage of multiple required JD skills",
                    supporting_evidence=(support,),
                )
            )

        return self._dedupe(strengths)[:5]

    def _candidate_value(self, candidate: CandidateFeatureRecord, feature: str) -> tuple[float, str]:
        for group in ("semantic", "experience", "skill", "behavioral", "career", "education", "logistics", "anomaly"):
            values = feature_group(candidate, group)
            if feature in values:
                return float(values[feature]), group
        return 0.0, ""

    def _direct_evidence(
        self,
        candidate: CandidateFeatureRecord,
        feature: str,
        group: str,
        raw_value: float,
    ) -> ReasoningEvidence | None:
        snippets = tuple(candidate.evidence.get(feature))
        if not snippets:
            return None
        return ReasoningEvidence(
            feature=feature,
            group=group,
            description=FEATURE_DESCRIPTIONS.get(feature, feature.replace("_", " ")),
            contribution=0.0,
            raw_value=raw_value,
            snippets=snippets[:2],
            source="candidate_evidence",
        )

    def _requirement_evidence(self, match: CandidateMatch, matched_required: int) -> ReasoningEvidence:
        matched = tuple(item for item in match.matched_requirements if item.startswith("required_skill:"))[:5]
        return ReasoningEvidence(
            feature="matched_requirements",
            group="requirements",
            description=f"{matched_required} required skills matched",
            contribution=0.0,
            raw_value=float(matched_required),
            snippets=matched,
            source="candidate_match",
        )

    def _dedupe(self, strengths: list[CandidateStrength]) -> list[CandidateStrength]:
        seen: set[str] = set()
        deduped: list[CandidateStrength] = []
        for strength in strengths:
            if strength.category in seen:
                continue
            seen.add(strength.category)
            deduped.append(strength)
        return deduped
