"""Dynamic candidate-feature weight generation from JD analysis."""

from __future__ import annotations

from collections import defaultdict

from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY, FEATURE_GROUPS, FeatureRegistry
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis, JobRequirement, RoleClassification, WeightProfile


class WeightGenerator:
    """Generate grouped candidate-feature weights from JD requirements."""

    SKILL_TO_FEATURES: dict[str, tuple[str, ...]] = {
        "python": ("python_strength_score", "recent_coding_role_flag"),
        "backend_api": ("recent_coding_role_flag", "role_family_fit_score"),
        "machine_learning": ("applied_ml_years_proxy", "production_ml_years_proxy", "pre_llm_ml_experience_flag"),
        "deep_learning": ("applied_ml_years_proxy", "production_ml_years_proxy"),
        "transformers": ("llm_integration_depth_score", "llm_finetuning_skill_score"),
        "llm": ("llm_integration_depth_score", "framework_demo_penalty_text"),
        "rag": ("retrieval_skill_depth", "embedding_system_evidence", "hybrid_search_evidence"),
        "embeddings": ("retrieval_skill_depth", "embedding_system_evidence"),
        "vector_database": ("vector_db_skill_coverage", "embedding_system_evidence"),
        "search": ("production_ir_evidence_score", "retrieval_skill_depth", "query_understanding_score"),
        "sparse_retrieval": ("hybrid_search_evidence", "production_ir_evidence_score"),
        "semantic_search": ("production_ir_evidence_score", "retrieval_skill_depth", "candidate_matching_domain_score"),
        "hybrid_search": ("hybrid_search_evidence", "production_ir_evidence_score"),
        "ranking": ("ranking_skill_depth", "ranking_eval_phrase_score", "production_eval_cooccurrence_score"),
        "ranking_evaluation": ("ranking_eval_phrase_score", "production_eval_cooccurrence_score"),
        "mlops": ("mlops_skill_score", "production_ml_years_proxy"),
        "containerization": ("mlops_skill_score", "production_ml_years_proxy"),
        "data_pipeline": ("data_pipeline_support_score",),
        "sql": ("data_pipeline_support_score",),
        "computer_vision": ("cv_speech_robotics_dominance_penalty", "applied_ml_years_proxy"),
    }
    ROLE_FEATURES: dict[str, tuple[str, ...]] = {
        "AI_ENGINEER": ("role_family_fit_score", "llm_integration_depth_score", "production_ml_years_proxy", "python_strength_score"),
        "ML_ENGINEER": ("role_family_fit_score", "production_ml_years_proxy", "applied_ml_years_proxy", "python_strength_score"),
        "MLOPS_ENGINEER": ("mlops_skill_score", "production_ml_years_proxy", "recent_coding_role_flag"),
        "DATA_ENGINEER": ("data_pipeline_support_score", "recent_coding_role_flag", "services_only_penalty"),
        "DATA_SCIENTIST": ("applied_ml_years_proxy", "skill_assessment_core_mean", "cs_ai_field_score"),
        "BACKEND_ENGINEER": ("recent_coding_role_flag", "python_strength_score", "role_family_fit_score"),
        "SOFTWARE_ENGINEER": ("recent_coding_role_flag", "python_strength_score", "role_family_fit_score"),
        "PRODUCT_MANAGER": ("cross_functional_product_score", "product_impact_phrase_score", "role_family_fit_score"),
        "RESEARCHER": ("research_only_phd_penalty", "cs_ai_field_score", "degree_level_score"),
    }
    INDUSTRY_FEATURES: dict[str, tuple[str, ...]] = {
        "recruitment": ("candidate_matching_domain_score", "product_company_exposure_months"),
        "hrtech": ("candidate_matching_domain_score", "current_industry_fit_score"),
        "marketplace": ("candidate_matching_domain_score", "product_company_exposure_months", "cross_functional_product_score"),
        "fintech": ("product_company_exposure_months", "current_industry_fit_score"),
        "healthcare": ("product_company_exposure_months", "current_industry_fit_score"),
        "ecommerce": ("product_company_exposure_months", "large_scale_exposure"),
        "saas": ("product_company_exposure_months", "current_industry_fit_score"),
        "software": ("product_company_exposure_months", "current_product_ai_role_flag"),
    }
    BEHAVIOR_FEATURES: dict[str, tuple[str, ...]] = {
        "startup_mindset": ("startup_or_scaleup_exposure", "ownership_verbs_score"),
        "ownership": ("ownership_verbs_score", "senior_judgment_experience_score"),
        "communication": ("cross_functional_product_score", "writing_clarity_score"),
        "product_thinking": ("product_impact_phrase_score", "cross_functional_product_score"),
        "experimentation": ("ranking_eval_phrase_score", "product_impact_phrase_score"),
        "hands_on": ("recent_coding_role_flag", "management_only_recent_penalty"),
    }
    NEGATIVE_FEATURES: dict[str, tuple[str, ...]] = {
        "research_only": ("research_only_phd_penalty",),
        "consulting_only": ("services_only_penalty",),
        "non_hands_on": ("management_only_recent_penalty", "recent_coding_role_flag"),
        "framework_demo_only": ("framework_demo_penalty_text",),
        "job_hopper": ("job_hop_title_chaser_penalty", "average_tenure_score"),
    }

    def __init__(self, registry: FeatureRegistry = DEFAULT_FEATURE_REGISTRY) -> None:
        self.registry = registry
        self._feature_group = {definition.name: definition.group for definition in self.registry.list_all()}

    def generate(self, analysis: JDAnalysis) -> WeightProfile:
        """Generate grouped weights for all candidate feature groups."""

        grouped = self._empty_grouped_weights()
        self._apply_role(grouped, analysis.role_classification)
        self._apply_requirements(grouped, analysis.requirements)
        self._apply_negative_signals(grouped, analysis.negative_signals)
        self._normalize_grouped(grouped)
        return WeightProfile(by_group={group: dict(weights) for group, weights in grouped.items()})

    def _empty_grouped_weights(self) -> dict[str, dict[str, float]]:
        grouped: dict[str, dict[str, float]] = {group: {} for group in FEATURE_GROUPS}
        for definition in self.registry.list_all():
            grouped[definition.group][definition.name] = 0.05
        return grouped

    def _apply_role(self, grouped: dict[str, dict[str, float]], role: RoleClassification) -> None:
        role_strength = max(role.confidence, 0.35)
        for feature_name in self.ROLE_FEATURES.get(role.role_family, ()):
            self._add(grouped, feature_name, 0.65 * role_strength)

    def _apply_requirements(self, grouped: dict[str, dict[str, float]], requirements: JobRequirement) -> None:
        for skill in requirements.required_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, feature_name, 1.15)
            self._add(grouped, "skill_history_support_ratio", 0.55)
        for skill in requirements.preferred_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, feature_name, 0.55)
        for skill in requirements.optional_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, feature_name, 0.25)

        if requirements.experience_min:
            self._add(grouped, "yoe_target_band_score", 0.8)
            self._add(grouped, "career_duration_consistency", 0.35)
            if requirements.experience_min >= 5:
                self._add(grouped, "senior_judgment_experience_score", 0.5)

        for industry in requirements.industries:
            for feature_name in self.INDUSTRY_FEATURES.get(industry, ()):
                self._add(grouped, feature_name, 0.6)
        for location in requirements.locations:
            if location in {"pune", "noida", "bangalore", "hyderabad", "delhi_ncr", "mumbai"}:
                self._add(grouped, "preferred_location_score", 0.65)
                self._add(grouped, "relocation_fit_score", 0.45)
            if location == "india":
                self._add(grouped, "india_location_score", 0.55)
            if location in {"remote", "hybrid", "onsite"}:
                self._add(grouped, "work_mode_fit_score", 0.45)

        for trait in requirements.behavioral_preferences:
            for feature_name in self.BEHAVIOR_FEATURES.get(trait, ()):
                self._add(grouped, feature_name, 0.45)

        self._add(grouped, "honeypot_score", 0.7)
        self._add(grouped, "title_description_mismatch", 0.45)
        self._add(grouped, "availability_multiplier", 0.35)
        self._add(grouped, "contactability_multiplier", 0.25)

    def _apply_negative_signals(self, grouped: dict[str, dict[str, float]], negative_signals: tuple[str, ...]) -> None:
        for signal in negative_signals:
            for feature_name in self.NEGATIVE_FEATURES.get(signal, ()):
                self._add(grouped, feature_name, 0.75)
            self._add(grouped, "honeypot_score", 0.35)

    def _add(self, grouped: dict[str, dict[str, float]], feature_name: str, value: float) -> None:
        group = self._feature_group.get(feature_name)
        if group is None:
            return
        grouped[group][feature_name] = grouped[group].get(feature_name, 0.05) + value

    def _normalize_grouped(self, grouped: dict[str, dict[str, float]]) -> None:
        for weights in grouped.values():
            for feature_name, weight in list(weights.items()):
                weights[feature_name] = round(clamp(weight), 4)
