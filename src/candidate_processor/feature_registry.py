"""Central registry of candidate feature metadata."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable


FEATURE_GROUPS = (
    "semantic",
    "experience",
    "skill",
    "behavioral",
    "career",
    "education",
    "logistics",
    "anomaly",
)
FEATURE_PRIORITIES = (1, 2, 3, 4, 5)


@dataclass(frozen=True, slots=True)
class FeatureDefinition:
    """Metadata describing one machine-readable candidate feature."""

    name: str
    group: str
    priority: int
    description: str
    feature_type: str
    is_penalty: bool
    requires_evidence: bool


class FeatureRegistry:
    """Validated catalog for feature documentation, tuning, and explainability."""

    def __init__(self, definitions: Iterable[FeatureDefinition] = ()) -> None:
        self._definitions: dict[str, FeatureDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: FeatureDefinition) -> None:
        """Register a feature definition after validating its group and priority."""

        if definition.group not in FEATURE_GROUPS:
            raise ValueError(f"Unsupported feature group: {definition.group!r}")
        if definition.priority not in FEATURE_PRIORITIES:
            raise ValueError(f"Unsupported feature priority: {definition.priority!r}")
        if definition.name in self._definitions:
            raise ValueError(f"Feature already registered: {definition.name}")
        self._definitions[definition.name] = definition

    def get(self, name: str) -> FeatureDefinition:
        """Return a definition by name."""

        try:
            return self._definitions[name]
        except KeyError as exc:
            raise KeyError(f"Unknown feature: {name}") from exc

    def list_all(self) -> tuple[FeatureDefinition, ...]:
        """Return all feature definitions in registration order."""

        return tuple(self._definitions.values())

    def list_by_group(self, group: str) -> tuple[FeatureDefinition, ...]:
        """Return all features for one feature group."""

        if group not in FEATURE_GROUPS:
            raise ValueError(f"Unsupported feature group: {group!r}")
        return tuple(definition for definition in self._definitions.values() if definition.group == group)

    def list_by_priority(self, priority: int) -> tuple[FeatureDefinition, ...]:
        """Return all features with the requested priority."""

        if priority not in FEATURE_PRIORITIES:
            raise ValueError(f"Unsupported feature priority: {priority!r}")
        return tuple(definition for definition in self._definitions.values() if definition.priority == priority)

    def as_mapping(self) -> MappingProxyType[str, FeatureDefinition]:
        """Expose a read-only mapping for callers that need keyed lookup."""

        return MappingProxyType(self._definitions)


def build_default_registry() -> FeatureRegistry:
    """Build the default catalog for all currently emitted candidate features."""

    return FeatureRegistry(_DEFAULT_FEATURES)


def _feature(
    name: str,
    group: str,
    priority: int,
    description: str,
    feature_type: str = "score",
    *,
    is_penalty: bool = False,
    requires_evidence: bool = False,
) -> FeatureDefinition:
    return FeatureDefinition(
        name=name,
        group=group,
        priority=priority,
        description=description,
        feature_type=feature_type,
        is_penalty=is_penalty,
        requires_evidence=requires_evidence,
    )


_DEFAULT_FEATURES: tuple[FeatureDefinition, ...] = (
    _feature("jd_semantic_bm25_score", "semantic", 4, "Lexical similarity between candidate text and the target JD."),
    _feature("core_ir_phrase_count", "semantic", 4, "Count of retrieval and ranking phrases in career evidence.", "count", requires_evidence=True),
    _feature("production_ir_evidence_score", "semantic", 5, "Production retrieval or ranking evidence found in role history.", requires_evidence=True),
    _feature("production_eval_cooccurrence_score", "semantic", 5, "Roles where production system language appears with evaluation language.", requires_evidence=True),
    _feature("ranking_eval_phrase_score", "semantic", 5, "Evidence of ranking or retrieval evaluation methodology.", requires_evidence=True),
    _feature("query_understanding_score", "semantic", 4, "Evidence of query understanding, rewriting, or intent work.", requires_evidence=True),
    _feature("embedding_system_evidence", "semantic", 4, "Evidence that embeddings are paired with vector infrastructure.", "flag", requires_evidence=True),
    _feature("hybrid_search_evidence", "semantic", 5, "Evidence of hybrid sparse and dense search systems.", "flag", requires_evidence=True),
    _feature("candidate_matching_domain_score", "semantic", 5, "Evidence of candidate, job, recruiter, or talent matching domain work.", requires_evidence=True),
    _feature("llm_integration_depth_score", "semantic", 3, "Depth of LLM integration beyond demos and prompts."),
    _feature("framework_demo_penalty_text", "semantic", 3, "Penalty for demo-only framework language without production evidence.", "flag", is_penalty=True),
    _feature("product_impact_phrase_score", "semantic", 4, "Product and user-impact language in candidate text."),
    _feature("writing_clarity_score", "semantic", 2, "Specificity of profile language after generic phrasing penalties."),
    _feature("title_summary_consistency", "semantic", 5, "Consistency between current title family and profile summary family.", "score", requires_evidence=True),
    _feature("yoe_target_band_score", "experience", 5, "Fit to the target seniority range of roughly five to nine years."),
    _feature("senior_judgment_experience_score", "experience", 4, "Composite signal for seniority, ownership, and judgment."),
    _feature("applied_ml_years_proxy", "experience", 5, "Approximate years in applied ML-relevant roles.", "years", requires_evidence=True),
    _feature("ir_retrieval_years_proxy", "experience", 5, "Approximate years in retrieval, ranking, embeddings, or search roles.", "years", requires_evidence=True),
    _feature("production_ml_years_proxy", "experience", 5, "Approximate years in production ML roles.", "years", requires_evidence=True),
    _feature("recent_coding_role_flag", "experience", 4, "Whether the current role appears hands-on and coding-oriented.", "flag"),
    _feature("management_only_recent_penalty", "experience", 3, "Penalty for management-only recent role language.", "flag", is_penalty=True),
    _feature("pre_llm_ml_experience_flag", "experience", 4, "Evidence of ML work predating recent LLM hype.", "flag"),
    _feature("career_duration_consistency", "experience", 4, "Consistency between stated experience and role durations."),
    _feature("current_role_duration_score", "experience", 3, "Healthy tenure score for the current role."),
    _feature("average_tenure_score", "experience", 3, "Average tenure stability across roles."),
    _feature("job_hop_title_chaser_penalty", "experience", 4, "Penalty for short hops combined with title inflation.", is_penalty=True),
    _feature("hands_on_ml_role_ratio", "experience", 4, "Share of roles combining ML relevance with hands-on evidence."),
    _feature("python_strength_score", "skill", 5, "Strength of Python-related skill evidence.", requires_evidence=True),
    _feature("vector_db_skill_coverage", "skill", 4, "Coverage of vector database and ANN tooling."),
    _feature("retrieval_skill_depth", "skill", 5, "Depth of retrieval, embedding, and vector search skills.", requires_evidence=True),
    _feature("ranking_skill_depth", "skill", 5, "Depth of ranking and evaluation skills.", requires_evidence=True),
    _feature("llm_finetuning_skill_score", "skill", 3, "Depth of fine-tuning and transformer ecosystem skills."),
    _feature("mlops_skill_score", "skill", 3, "Depth of MLOps and deployment tooling skills."),
    _feature("data_pipeline_support_score", "skill", 3, "Depth of data pipeline tooling skills."),
    _feature("skill_assessment_core_mean", "skill", 3, "Mean assessment score for core AI and Python skills."),
    _feature("skill_assessment_core_max", "skill", 2, "Best assessment score for core AI and Python skills."),
    _feature("skill_assessment_coverage", "skill", 2, "Number of relevant skill assessments.", "count"),
    _feature("skill_history_support_ratio", "skill", 5, "Share of core skills supported by career text.", requires_evidence=True),
    _feature("expert_zero_duration_penalty", "skill", 4, "Count of expert skills with zero stated duration.", "count", is_penalty=True),
    _feature("ai_keyword_stuffing_penalty", "skill", 5, "Penalty for AI skill lists unsupported by role evidence.", "flag", is_penalty=True),
    _feature("cv_speech_robotics_dominance_penalty", "skill", 3, "Penalty for adjacent AI domains dominating NLP/IR evidence.", "flag", is_penalty=True),
    _feature("certification_relevance_score", "skill", 2, "Relevance of AI and cloud certifications."),
    _feature("skill_duration_impossibility_count", "skill", 5, "Count of impossible or suspicious skill-duration claims.", "count", is_penalty=True),
    _feature("core_ai_skill_count", "skill", 2, "Number of listed skills matching core AI dictionaries.", "count"),
    _feature("availability_multiplier", "behavioral", 5, "Hireability multiplier based on activity, intent, response, and notice.", requires_evidence=True),
    _feature("days_since_active_score", "behavioral", 4, "Recency score from last active date."),
    _feature("recruiter_response_score", "behavioral", 4, "Recruiter response quality signal."),
    _feature("response_speed_score", "behavioral", 4, "Speed of recruiter response."),
    _feature("notice_period_score", "behavioral", 3, "Shorter notice-period fit signal."),
    _feature("interview_reliability_score", "behavioral", 4, "Interview completion reliability."),
    _feature("offer_acceptance_known_score", "behavioral", 2, "Offer acceptance signal with missing values treated neutrally."),
    _feature("recruiter_demand_score", "behavioral", 3, "Platform demand from saves, views, and searches."),
    _feature("profile_completeness_confidence", "behavioral", 2, "Confidence from profile completeness."),
    _feature("contact_verification_score", "behavioral", 3, "Verification coverage across email, phone, and LinkedIn."),
    _feature("contactability_multiplier", "behavioral", 4, "Multiplier based on verified contact channels."),
    _feature("github_external_validation_score", "behavioral", 2, "External validation from GitHub activity, neutral when missing."),
    _feature("platform_activity_recency_x_fit", "behavioral", 4, "Interaction of recent activity with technical fit."),
    _feature("applications_activity_score", "behavioral", 2, "Recent application activity signal."),
    _feature("product_company_exposure_months", "career", 5, "Months in product or product-like industries.", "months", requires_evidence=True),
    _feature("services_only_penalty", "career", 5, "Penalty for consulting or services-only careers.", "flag", is_penalty=True),
    _feature("current_industry_fit_score", "career", 4, "Fit of the current industry to product AI context."),
    _feature("startup_or_scaleup_exposure", "career", 3, "Years of startup or scaleup product exposure.", "years"),
    _feature("large_scale_exposure", "career", 4, "Evidence of large-scale systems or traffic."),
    _feature("ownership_verbs_score", "career", 4, "Ownership and shipping language in career history.", requires_evidence=True),
    _feature("cross_functional_product_score", "career", 3, "Cross-functional product collaboration evidence."),
    _feature("role_family_fit_score", "career", 5, "Fit of current role family to the target role.", requires_evidence=True),
    _feature("nontech_role_penalty", "career", 5, "Penalty for non-technical current role families.", "flag", is_penalty=True),
    _feature("current_product_ai_role_flag", "career", 4, "Current role combines product industry and AI evidence.", "flag"),
    _feature("cs_ai_field_score", "education", 3, "Education field relevance to CS, AI, ML, statistics, or math."),
    _feature("degree_level_score", "education", 2, "Highest degree level score."),
    _feature("institution_tier_score", "education", 2, "Highest available institution tier signal."),
    _feature("education_timeline_validity", "education", 3, "Validity of education start and end years."),
    _feature("research_only_phd_penalty", "education", 3, "Penalty for research-only signals without production evidence.", "flag", is_penalty=True),
    _feature("grade_parse_score", "education", 1, "Parsed grade or CGPA signal when available."),
    _feature("preferred_location_score", "logistics", 3, "Fit to preferred hiring locations."),
    _feature("india_location_score", "logistics", 3, "India-based location fit."),
    _feature("relocation_fit_score", "logistics", 3, "Fit based on preferred location and relocation willingness."),
    _feature("work_mode_fit_score", "logistics", 2, "Fit of preferred work mode."),
    _feature("salary_midpoint_realism", "logistics", 2, "Realism of expected salary midpoint for experience."),
    _feature("salary_range_width_penalty", "logistics", 2, "Penalty for suspicious or overly wide salary ranges.", "flag", is_penalty=True),
    _feature("notice_buyout_fit", "logistics", 2, "Notice-period fit for possible buyout planning."),
    _feature("honeypot_score", "anomaly", 5, "Composite suspicious-profile and honeypot risk score.", is_penalty=True, requires_evidence=True),
    _feature("summary_profile_years_mismatch", "anomaly", 5, "Mismatch between stated years and summary years.", "flag", is_penalty=True),
    _feature("title_description_mismatch", "anomaly", 5, "Mismatch between current title family and role description family.", "flag", is_penalty=True, requires_evidence=True),
    _feature("education_end_before_start_flag", "anomaly", 3, "Education timeline has end year before start year.", "flag", is_penalty=True),
    _feature("role_date_duration_mismatch", "anomaly", 4, "Count of role date and duration mismatches.", "count", is_penalty=True),
    _feature("multiple_current_roles_flag", "anomaly", 4, "Candidate has zero or multiple current roles.", "flag", is_penalty=True),
    _feature("template_duplicate_suspicion", "anomaly", 3, "Template-like profile with suspicious keyword stuffing.", "flag", is_penalty=True),
    _feature("behavioral_inconsistency_score", "anomaly", 3, "Inconsistency between platform behavior and profile state.", "flag", is_penalty=True),
    _feature("reasoning_confidence_score", "anomaly", 3, "Confidence that later reasoning can rely on observed evidence."),
)

DEFAULT_FEATURE_REGISTRY = build_default_registry()

