"""Evidence selection for recruiter-facing reasoning."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from ranking.contribution_tracker import feature_group
from ranking.match_models import CandidateMatch
from reasoning.reasoning_models import ReasoningEvidence


PRIORITY_FEATURES: tuple[str, ...] = (
    "production_ir_evidence_score",
    "ranking_eval_phrase_score",
    "retrieval_skill_depth",
    "role_family_fit_score",
    "availability_multiplier",
)

FEATURE_DESCRIPTIONS: dict[str, str] = {
    "production_ir_evidence_score": "production retrieval or ranking evidence",
    "ranking_eval_phrase_score": "ranking and retrieval evaluation evidence",
    "retrieval_skill_depth": "retrieval, embedding, and vector-search skill depth",
    "role_family_fit_score": "target role-family fit",
    "availability_multiplier": "recruiter engagement and availability",
    "python_strength_score": "Python strength",
    "vector_db_skill_coverage": "vector database coverage",
    "ranking_skill_depth": "ranking skill depth",
    "yoe_target_band_score": "target experience range fit",
    "senior_judgment_experience_score": "seniority and ownership signal",
    "product_company_exposure_months": "product-company background",
    "ownership_verbs_score": "ownership and shipping evidence",
    "candidate_matching_domain_score": "talent matching domain evidence",
    "semantic_alignment": "overall semantic alignment",
    "requirement_match_score": "structured JD requirement match",
    "weighted_candidate_feature_score": "weighted feature support",
}


class EvidenceSelector:
    """Select the most important evidence supporting a candidate rank."""

    def __init__(self, *, limit: int = 5) -> None:
        self.limit = limit

    def select(self, match: CandidateMatch, candidate: CandidateFeatureRecord) -> list[ReasoningEvidence]:
        """Return the top evidence items in deterministic priority order."""

        selected: dict[str, ReasoningEvidence] = {}
        for contribution in match.feature_contributions:
            if contribution.contribution <= 0:
                continue
            snippets = contribution.evidence or tuple(candidate.evidence.get(contribution.feature))
            if not snippets:
                continue
            selected[contribution.feature] = ReasoningEvidence(
                feature=contribution.feature,
                group=contribution.group,
                description=self._description(contribution.feature),
                contribution=contribution.contribution,
                raw_value=contribution.raw_value,
                snippets=self._clean_snippets(snippets),
            )

        for feature in PRIORITY_FEATURES:
            if feature in selected:
                continue
            snippets = tuple(candidate.evidence.get(feature))
            raw_value, group = self._candidate_value(candidate, feature)
            if snippets and raw_value > 0:
                selected[feature] = ReasoningEvidence(
                    feature=feature,
                    group=group,
                    description=self._description(feature),
                    contribution=0.0,
                    raw_value=raw_value,
                    snippets=self._clean_snippets(snippets),
                    source="candidate_evidence",
                )

        ranked = sorted(selected.values(), key=self._sort_key)
        return ranked[: self.limit]

    def _sort_key(self, evidence: ReasoningEvidence) -> tuple[int, float, float, str]:
        priority = PRIORITY_FEATURES.index(evidence.feature) if evidence.feature in PRIORITY_FEATURES else len(PRIORITY_FEATURES)
        return (priority, -abs(evidence.contribution), -evidence.raw_value, evidence.feature)

    def _candidate_value(self, candidate: CandidateFeatureRecord, feature: str) -> tuple[float, str]:
        for group in ("semantic", "experience", "skill", "behavioral", "career", "education", "logistics", "anomaly"):
            values = feature_group(candidate, group)
            if feature in values:
                return float(values[feature]), group
        return 0.0, ""

    def _description(self, feature: str) -> str:
        return FEATURE_DESCRIPTIONS.get(feature, feature.replace("_", " "))

    def _clean_snippets(self, snippets: tuple[str, ...]) -> tuple[str, ...]:
        cleaned = []
        for snippet in snippets:
            text = " ".join(str(snippet).split())
            if text and text not in cleaned:
                cleaned.append(text)
        return tuple(cleaned[:2])
