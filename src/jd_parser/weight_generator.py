"""Dynamic candidate-feature weight generation from JD analysis."""

from __future__ import annotations

from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY, FEATURE_GROUPS, FeatureRegistry
from candidate_processor.normalizer import clamp
from jd_parser.jd_models import JDAnalysis, JobRequirement, JobSkill, RoleClassification, WeightProfile


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
    SKILL_REASON_LABELS: dict[str, str] = {
        "backend_api": "backend APIs",
        "computer_vision": "computer vision",
        "containerization": "containerization",
        "data_pipeline": "data pipelines",
        "deep_learning": "deep learning",
        "embeddings": "embeddings",
        "hybrid_search": "hybrid search",
        "llm": "LLM systems",
        "machine_learning": "machine learning",
        "mlops": "MLOps",
        "python": "Python",
        "rag": "retrieval systems",
        "ranking": "ranking systems",
        "ranking_evaluation": "ranking evaluation",
        "search": "search systems",
        "semantic_search": "semantic search",
        "sparse_retrieval": "sparse retrieval",
        "sql": "SQL",
        "transformers": "transformers",
        "vector_database": "vector databases",
    }

    def __init__(self, registry: FeatureRegistry = DEFAULT_FEATURE_REGISTRY) -> None:
        self.registry = registry
        self._feature_group = {definition.name: definition.group for definition in self.registry.list_all()}

    def generate(self, analysis: JDAnalysis) -> WeightProfile:
        """Generate grouped weights for all candidate feature groups."""

        grouped = self._empty_grouped_weights()
        reasons: dict[str, str] = {}
        self._apply_role(grouped, reasons, analysis.role_classification)
        self._apply_requirements(grouped, reasons, analysis.requirements)
        self._apply_negative_signals(grouped, reasons, analysis.negative_signals)
        self._clamp_grouped(grouped)
        profile = WeightProfile(by_group={group: dict(weights) for group, weights in grouped.items()}, reasons=reasons)
        return profile.normalize()

    def _empty_grouped_weights(self) -> dict[str, dict[str, float]]:
        grouped: dict[str, dict[str, float]] = {group: {} for group in FEATURE_GROUPS}
        for definition in self.registry.list_all():
            grouped[definition.group][definition.name] = 0.05
        return grouped

    def _apply_role(self, grouped: dict[str, dict[str, float]], reasons: dict[str, str], role: RoleClassification) -> None:
        role_strength = max(role.confidence, 0.35)
        for feature_name in self.ROLE_FEATURES.get(role.role_family, ()):
            self._add(grouped, reasons, feature_name, 0.65 * role_strength, f"Role family: {role.role_family}")

    def _apply_requirements(self, grouped: dict[str, dict[str, float]], reasons: dict[str, str], requirements: JobRequirement) -> None:
        for skill in requirements.required_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, reasons, feature_name, 1.15, self._skill_reason("Required", skill))
            self._add(grouped, reasons, "skill_history_support_ratio", 0.55, "Required skills need career-history support")
        for skill in requirements.preferred_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, reasons, feature_name, 0.55, self._skill_reason("Preferred", skill))
        for skill in requirements.optional_skills:
            for feature_name in self.SKILL_TO_FEATURES.get(skill.canonical_name, ()):
                self._add(grouped, reasons, feature_name, 0.25, self._skill_reason("Optional", skill))

        if requirements.experience_min:
            experience_reason = f"Experience requirement: {requirements.experience_min}-{requirements.experience_max} years"
            self._add(grouped, reasons, "yoe_target_band_score", 0.8, experience_reason)
            self._add(grouped, reasons, "career_duration_consistency", 0.35, experience_reason)
            if requirements.experience_min >= 5:
                self._add(grouped, reasons, "senior_judgment_experience_score", 0.5, "Senior experience requirement")

        for industry in requirements.industries:
            for feature_name in self.INDUSTRY_FEATURES.get(industry, ()):
                self._add(grouped, reasons, feature_name, 0.6, f"Industry context: {industry}")
        for location in requirements.locations:
            if location in {"pune", "noida", "bangalore", "hyderabad", "delhi_ncr", "mumbai"}:
                self._add(grouped, reasons, "preferred_location_score", 0.65, f"Location requirement: {location}")
                self._add(grouped, reasons, "relocation_fit_score", 0.45, f"Location requirement: {location}")
            if location == "india":
                self._add(grouped, reasons, "india_location_score", 0.55, "Location requirement: India")
            if location in {"remote", "hybrid", "onsite"}:
                self._add(grouped, reasons, "work_mode_fit_score", 0.45, f"Work mode requirement: {location}")

        for trait in requirements.behavioral_preferences:
            for feature_name in self.BEHAVIOR_FEATURES.get(trait, ()):
                self._add(grouped, reasons, feature_name, 0.45, f"Behavioral preference: {trait}")

        self._add(grouped, reasons, "honeypot_score", 0.7, "Baseline suspicious-profile guardrail")
        self._add(grouped, reasons, "title_description_mismatch", 0.45, "Baseline role-consistency guardrail")
        self._add(grouped, reasons, "availability_multiplier", 0.35, "Baseline hireability signal")
        self._add(grouped, reasons, "contactability_multiplier", 0.25, "Baseline contactability signal")

    def _apply_negative_signals(self, grouped: dict[str, dict[str, float]], reasons: dict[str, str], negative_signals: tuple[str, ...]) -> None:
        for signal in negative_signals:
            for feature_name in self.NEGATIVE_FEATURES.get(signal, ()):
                self._add(grouped, reasons, feature_name, 0.75, f"Negative signal: {signal}")
            self._add(grouped, reasons, "honeypot_score", 0.35, f"Negative signal: {signal}")

    def _add(
        self,
        grouped: dict[str, dict[str, float]],
        reasons: dict[str, str],
        feature_name: str,
        value: float,
        reason: str,
    ) -> None:
        group = self._feature_group.get(feature_name)
        if group is None:
            return
        grouped[group][feature_name] = grouped[group].get(feature_name, 0.05) + value
        self._add_reason(reasons, feature_name, reason)

    def _clamp_grouped(self, grouped: dict[str, dict[str, float]]) -> None:
        for weights in grouped.values():
            for feature_name, weight in list(weights.items()):
                weights[feature_name] = round(clamp(weight), 4)

    def _skill_reason(self, importance: str, skill: JobSkill) -> str:
        label = self.SKILL_REASON_LABELS.get(skill.canonical_name, skill.canonical_name.replace("_", " "))
        return f"{importance} skill: {label}"

    def _add_reason(self, reasons: dict[str, str], feature_name: str, reason: str) -> None:
        existing = reasons.get(feature_name)
        if existing is None:
            reasons[feature_name] = reason
            return
        existing_parts = existing.split("; ")
        if reason not in existing_parts:
            reasons[feature_name] = f"{existing}; {reason}"
