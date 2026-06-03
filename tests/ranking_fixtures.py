from __future__ import annotations

from candidate_processor.models import CandidateEvidence, CandidateFeatureRecord
from jd_parser.jd_parser import JDParser
from jd_parser.jd_models import JDAnalysis


def retrieval_jd() -> JDAnalysis:
    return JDParser().parse(
        """
        Senior AI Engineer for an HR Tech recruitment marketplace.
        Required: 5-9 years, Python, semantic search, embeddings, vector database,
        hybrid search, learning to rank, NDCG, and production ranking systems.
        Must be hands-on with ownership and product thinking. Pune or Noida, hybrid.
        No consulting-only or research-only background.
        """,
        title="Senior AI Engineer",
    )


def candidate_record(
    candidate_id: str = "CAND_MATCH",
    *,
    fit: float = 1.0,
    penalty: float = 0.0,
    notice_score: float = 1.0,
) -> CandidateFeatureRecord:
    semantic = {
        "jd_semantic_bm25_score": 0.80 * fit,
        "core_ir_phrase_count": int(5 * fit),
        "production_ir_evidence_score": 0.90 * fit,
        "production_eval_cooccurrence_score": 0.80 * fit,
        "ranking_eval_phrase_score": 0.85 * fit,
        "query_understanding_score": 0.65 * fit,
        "embedding_system_evidence": 1.0 if fit >= 0.6 else 0.0,
        "hybrid_search_evidence": 1.0 if fit >= 0.6 else 0.0,
        "candidate_matching_domain_score": 0.80 * fit,
        "llm_integration_depth_score": 0.50 * fit,
        "framework_demo_penalty_text": penalty,
        "product_impact_phrase_score": 0.65 * fit,
        "writing_clarity_score": 0.70 * fit,
        "title_summary_consistency": 1.0 if fit >= 0.5 else 0.3,
    }
    experience = {
        "yoe_target_band_score": 0.95 * fit,
        "senior_judgment_experience_score": 0.85 * fit,
        "applied_ml_years_proxy": 6.0 * fit,
        "ir_retrieval_years_proxy": 4.0 * fit,
        "production_ml_years_proxy": 5.0 * fit,
        "recent_coding_role_flag": 1.0 if fit >= 0.5 else 0.0,
        "management_only_recent_penalty": penalty,
        "pre_llm_ml_experience_flag": 1.0 if fit >= 0.7 else 0.0,
        "career_duration_consistency": 0.90,
        "current_role_duration_score": 0.80,
        "average_tenure_score": 0.80,
        "job_hop_title_chaser_penalty": penalty,
        "hands_on_ml_role_ratio": 0.85 * fit,
    }
    skill = {
        "python_strength_score": 0.90 * fit,
        "vector_db_skill_coverage": 0.85 * fit,
        "retrieval_skill_depth": 0.92 * fit,
        "ranking_skill_depth": 0.88 * fit,
        "llm_finetuning_skill_score": 0.45 * fit,
        "mlops_skill_score": 0.55 * fit,
        "data_pipeline_support_score": 0.40 * fit,
        "skill_assessment_core_mean": 0.80 * fit,
        "skill_assessment_core_max": 0.90 * fit,
        "skill_assessment_coverage": 3,
        "skill_history_support_ratio": 0.90 * fit,
        "expert_zero_duration_penalty": penalty,
        "ai_keyword_stuffing_penalty": penalty,
        "cv_speech_robotics_dominance_penalty": 0.0,
        "certification_relevance_score": 0.40,
        "skill_duration_impossibility_count": int(4 * penalty),
        "core_ai_skill_count": 8,
    }
    behavioral = {
        "availability_multiplier": 1.15,
        "days_since_active_score": 0.90,
        "recruiter_response_score": 0.75,
        "response_speed_score": 0.80,
        "notice_period_score": notice_score,
        "interview_reliability_score": 0.90,
        "offer_acceptance_known_score": 0.75,
        "recruiter_demand_score": 0.70,
        "profile_completeness_confidence": 0.92,
        "contact_verification_score": 1.0,
        "contactability_multiplier": 1.15,
        "github_external_validation_score": 0.65,
        "platform_activity_recency_x_fit": 0.80 * fit,
        "applications_activity_score": 0.50,
    }
    career = {
        "product_company_exposure_months": 48 * fit,
        "services_only_penalty": penalty,
        "current_industry_fit_score": 0.85 * fit,
        "startup_or_scaleup_exposure": 3.0 * fit,
        "large_scale_exposure": 0.75 * fit,
        "ownership_verbs_score": 0.85 * fit,
        "cross_functional_product_score": 0.75 * fit,
        "role_family_fit_score": 0.95 * fit,
        "nontech_role_penalty": penalty,
        "current_product_ai_role_flag": 1.0 if fit >= 0.7 else 0.0,
    }
    education = {
        "cs_ai_field_score": 0.80,
        "degree_level_score": 0.70,
        "institution_tier_score": 0.70,
        "education_timeline_validity": 1.0,
        "research_only_phd_penalty": penalty,
        "grade_parse_score": 0.0,
    }
    logistics = {
        "preferred_location_score": 0.90,
        "india_location_score": 1.0,
        "relocation_fit_score": 1.0,
        "work_mode_fit_score": 1.0,
        "salary_midpoint_realism": 0.80,
        "salary_range_width_penalty": 0.0,
        "notice_buyout_fit": notice_score,
    }
    anomaly = {
        "honeypot_score": penalty,
        "summary_profile_years_mismatch": penalty,
        "title_description_mismatch": penalty,
        "skill_duration_impossibility_count": int(4 * penalty),
        "education_end_before_start_flag": 0.0,
        "role_date_duration_mismatch": 0,
        "multiple_current_roles_flag": 0.0,
        "template_duplicate_suspicion": penalty,
        "behavioral_inconsistency_score": 0.0,
        "reasoning_confidence_score": max(0.2, 0.90 - penalty),
    }
    evidence = CandidateEvidence(
        candidate_id=candidate_id,
        by_feature={
            "production_ir_evidence_score": ["Built production hybrid retrieval and ranking systems."],
            "retrieval_skill_depth": ["Semantic search, embeddings, Pinecone, Elasticsearch."],
            "role_family_fit_score": ["Senior ML Search Engineer."],
            "availability_multiplier": ["active and open to work"],
        },
    )
    return CandidateFeatureRecord(
        candidate_id=candidate_id,
        semantic_features=semantic,
        experience_features=experience,
        skill_features=skill,
        behavioral_features=behavioral,
        career_features=career,
        education_features=education,
        logistics_features=logistics,
        anomaly_features=anomaly,
        evidence=evidence,
    )
