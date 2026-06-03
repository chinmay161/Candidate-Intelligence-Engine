"""Deterministic semantic alignment between JD analysis and candidate features."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis


class SemanticMatcher:
    """Score JD/candidate semantic fit without model calls."""

    SKILL_FEATURES: dict[str, tuple[str, ...]] = {
        "python": ("python_strength_score",),
        "machine_learning": ("applied_ml_years_proxy", "production_ml_years_proxy"),
        "deep_learning": ("applied_ml_years_proxy",),
        "transformers": ("llm_integration_depth_score", "llm_finetuning_skill_score"),
        "llm": ("llm_integration_depth_score",),
        "rag": ("retrieval_skill_depth", "embedding_system_evidence"),
        "embeddings": ("retrieval_skill_depth", "embedding_system_evidence"),
        "vector_database": ("vector_db_skill_coverage", "embedding_system_evidence"),
        "search": ("production_ir_evidence_score", "retrieval_skill_depth"),
        "semantic_search": ("production_ir_evidence_score", "retrieval_skill_depth", "candidate_matching_domain_score"),
        "hybrid_search": ("hybrid_search_evidence", "production_ir_evidence_score"),
        "ranking": ("ranking_skill_depth", "ranking_eval_phrase_score"),
        "ranking_evaluation": ("ranking_eval_phrase_score", "production_eval_cooccurrence_score"),
        "mlops": ("mlops_skill_score", "production_ml_years_proxy"),
        "data_pipeline": ("data_pipeline_support_score",),
        "computer_vision": ("applied_ml_years_proxy",),
    }

    def score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        semantic_weighted = self._weighted_semantic_score(analysis, candidate)
        role_fit = float(candidate.career_features.get("role_family_fit_score", 0.0))
        skill_fit = self._skill_overlap_score(analysis, candidate)
        evidence_fit = self._evidence_support_score(analysis, candidate)
        score = semantic_weighted * 0.42 + role_fit * 0.18 + skill_fit * 0.30 + evidence_fit * 0.10
        return round(clamp(score), 6)

    def _weighted_semantic_score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        weights = analysis.feature_weights.by_group.get("semantic", {})
        if not weights:
            values = [self._normalize_feature(name, float(value)) for name, value in candidate.semantic_features.items()]
            return sum(values) / len(values) if values else 0.0
        total = sum(weight for weight in weights.values() if weight > 0)
        if total <= 0:
            return 0.0
        score = 0.0
        for feature, weight in weights.items():
            score += weight * self._normalize_feature(feature, float(candidate.semantic_features.get(feature, 0.0)))
        return clamp(score / total)

    def _skill_overlap_score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        scores: list[float] = []
        for skill in analysis.required_skills:
            scores.append(self._canonical_skill_score(skill.canonical_name, candidate) * 1.0)
        for skill in analysis.preferred_skills:
            scores.append(self._canonical_skill_score(skill.canonical_name, candidate) * 0.65)
        if not scores:
            return float(candidate.skill_features.get("skill_history_support_ratio", 0.0))
        return clamp(sum(scores) / max(len(scores), 1))

    def _canonical_skill_score(self, canonical_name: str, candidate: CandidateFeatureRecord) -> float:
        features = self.SKILL_FEATURES.get(canonical_name, ())
        if not features:
            return 0.0
        return max(self._candidate_feature_score(candidate, feature) for feature in features)

    def _candidate_feature_score(self, candidate: CandidateFeatureRecord, feature: str) -> float:
        for group in (
            candidate.semantic_features,
            candidate.experience_features,
            candidate.skill_features,
            candidate.career_features,
        ):
            if feature in group:
                return self._normalize_feature(feature, float(group[feature]))
        return 0.0

    def _evidence_support_score(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        important_features = set(analysis.feature_weights.reasons)
        if not important_features:
            important_features = {"production_ir_evidence_score", "retrieval_skill_depth", "role_family_fit_score"}
        supported = sum(1 for feature in important_features if candidate.evidence.get(feature))
        return clamp(supported / max(len(important_features), 1))

    def _normalize_feature(self, feature: str, value: float) -> float:
        if feature.endswith("_count"):
            return clamp(value / 5.0)
        if feature.endswith("_months"):
            return clamp(value / 60.0)
        if feature.endswith("_years_proxy") or feature.endswith("_exposure"):
            return clamp(value / 6.0)
        return clamp(value)
