"""Deterministic candidate feature extraction and evidence capture."""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from datetime import date
from statistics import median

from candidate_processor.normalizer import TextNormalizer
from candidate_processor.constants import (
    AS_OF_DATE,
    CODING_TERMS,
    CONSULTING_COMPANIES,
    CORE_AI_SKILLS,
    CV_SPEECH_ROBOTICS_TERMS,
    DATA_PIPELINE_TERMS,
    DEMO_ONLY_TERMS,
    EMBEDDING_TERMS,
    EVALUATION_TERMS,
    INDIA_METRO_CITIES,
    JD_QUERY_TERMS,
    LLM_TERMS,
    MLOPS_TERMS,
    ML_TERMS,
    NEGATIVE_ARCHETYPES,
    OWNERSHIP_TERMS,
    PREFERRED_CITIES,
    PRODUCT_IMPACT_TERMS,
    PRODUCT_INDUSTRIES,
    PRODUCTION_TERMS,
    PYTHON_TERMS,
    RANKING_TERMS,
    RESEARCH_TERMS,
    RETRIEVAL_TERMS,
    SKILL_PROFICIENCY_ORDER,
    STARTUP_TERMS,
    TIER_SCORE,
    VECTOR_DB_TERMS,
)
from candidate_processor.models import Candidate, CandidateEvidence, CandidateFeatureRecord, CareerHistory, Education, Skill
from candidate_processor.normalizer import TextNormalizer, clamp, log_scale, safe_mean, score_by_terms, score_by_terms_normalized, weighted_flag

logger = logging.getLogger(__name__)


class EvidenceExtractor:
    """Collect compact, feature-keyed evidence snippets from candidate records."""

    IMPORTANT_FEATURE_TERMS: dict[str, tuple[str, ...]] = {
        "production_ir_evidence_score": RETRIEVAL_TERMS + RANKING_TERMS + PRODUCTION_TERMS,
        "production_eval_cooccurrence_score": PRODUCTION_TERMS + EVALUATION_TERMS,
        "ranking_eval_phrase_score": EVALUATION_TERMS,
        "query_understanding_score": ("query understanding", "query rewriting", "search intent", "search relevance"),
        "embedding_system_evidence": EMBEDDING_TERMS + VECTOR_DB_TERMS,
        "hybrid_search_evidence": ("hybrid", "bm25") + VECTOR_DB_TERMS,
        "candidate_matching_domain_score": ("candidate", "recruiter", "job matching", "talent marketplace"),
        "python_strength_score": PYTHON_TERMS,
        "retrieval_skill_depth": RETRIEVAL_TERMS + EMBEDDING_TERMS,
        "ranking_skill_depth": RANKING_TERMS + EVALUATION_TERMS,
        "product_company_exposure_months": PRODUCT_INDUSTRIES,
        "ownership_verbs_score": OWNERSHIP_TERMS,
        "role_family_fit_score": ML_TERMS + RETRIEVAL_TERMS + CODING_TERMS,
        "nontech_role_penalty": NEGATIVE_ARCHETYPES,
        "honeypot_score": NEGATIVE_ARCHETYPES + DEMO_ONLY_TERMS,
        "title_description_mismatch": NEGATIVE_ARCHETYPES + ML_TERMS,
        "summary_profile_years_mismatch": ("years", "yrs"),
        "availability_multiplier": ("open to work", "active", "response"),
    }

    def __init__(self):
        self._feature_terms = {
            name: TextNormalizer.normalize_terms(tuple(terms))
            for name, terms in self.IMPORTANT_FEATURE_TERMS.items()
        }
        self._all_terms = set(term for terms in self._feature_terms.values() for term in terms if term)

    def extract(self, candidate: Candidate) -> CandidateEvidence:
        text = candidate.full_text
        sentences = TextNormalizer.sentences(text)
        normalized_sentences = [TextNormalizer.normalize(sentence) for sentence in sentences]
        
        # Pre-filter sentences that have AT LEAST ONE of the relevant terms across ALL features
        # This drastically reduces the number of sentences to check for specific features
        valid_sentence_pairs = []
        for sentence, norm_sentence in zip(sentences, normalized_sentences):
            if any(term in norm_sentence for term in self._all_terms):
                valid_sentence_pairs.append((sentence, norm_sentence))

        evidence: dict[str, list[str]] = {}
        for feature_name, normalized_terms in self._feature_terms.items():
            snippets = []
            for sentence, norm_sentence in valid_sentence_pairs:
                if any(term and term in norm_sentence for term in normalized_terms):
                    snippets.append(sentence[:280])
                    if len(snippets) >= 3:
                        break
            if snippets:
                evidence[feature_name] = snippets

        skill_evidence = [f"{skill.name} ({skill.proficiency}, {skill.duration_months} months)" for skill in candidate.skills[:25]]
        if skill_evidence:
            evidence["skill_profile"] = skill_evidence

        role_evidence = [
            f"{role.title} at {role.company}: {role.description[:220]}"
            for role in candidate.career_history[:5]
        ]
        if role_evidence:
            evidence["career_roles"] = role_evidence

        signals = candidate.redrob_signals
        evidence["redrob_signals"] = [
            f"open_to_work={signals.open_to_work_flag}",
            f"last_active_date={signals.last_active_date.isoformat()}",
            f"recruiter_response_rate={signals.recruiter_response_rate:.2f}",
            f"notice_period_days={signals.notice_period_days}",
        ]
        return CandidateEvidence(candidate_id=candidate.candidate_id, by_feature=evidence)


class CandidateFeatureExtractor:
    """Extract structured feature groups for downstream ranking."""

    def __init__(self, *, as_of_date: date = AS_OF_DATE, logger_: logging.Logger | None = None) -> None:
        self.as_of_date = as_of_date
        self.logger = logger_ or logger
        self.evidence_extractor = EvidenceExtractor()

    def extract(self, candidate: Candidate) -> CandidateFeatureRecord:
        context = _CandidateContext(candidate=candidate, as_of_date=self.as_of_date)
        semantic = self._semantic_features(context)
        experience = self._experience_features(context)
        skill = self._skill_features(context)
        behavioral = self._behavioral_features(context, semantic)
        career = self._career_features(context)
        education = self._education_features(context)
        logistics = self._logistics_features(context)
        anomaly = self._anomaly_features(context, skill, career, education, logistics, semantic)
        evidence = self.evidence_extractor.extract(candidate)

        text_parts: list[str] = []
        for snippets in evidence.by_feature.values():
            text_parts.extend(snippets)
        
        for group in (semantic, experience, skill, behavioral, career, education, logistics):
            for feature, value in group.items():
                numeric = float(value)
                if numeric > 0:
                    repetitions = 2 if numeric >= 0.65 else 1
                    text_parts.extend(feature.replace("_", " ") for _ in range(repetitions))
                    
        terms = TextNormalizer.tokenize(" ".join(text_parts))
        from collections import Counter
        retrieval_term_counts = dict(Counter(terms))
        retrieval_doc_len = len(terms)

        return CandidateFeatureRecord(
            candidate_id=candidate.candidate_id,
            semantic_features=semantic,
            experience_features=experience,
            skill_features=skill,
            behavioral_features=behavioral,
            career_features=career,
            education_features=education,
            logistics_features=logistics,
            anomaly_features=anomaly,
            evidence=evidence,
            retrieval_term_counts=retrieval_term_counts,
            retrieval_doc_len=retrieval_doc_len,
        )

    def extract_many(self, candidates: list[Candidate] | tuple[Candidate, ...]) -> list[CandidateFeatureRecord]:
        return [self.extract(candidate) for candidate in candidates]

    def _semantic_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        text = context.full_text
        career_text = context.career_text
        profile_text = context.profile_text
        ir_count = TextNormalizer.count_terms_normalized(context.norm_career_text, RETRIEVAL_TERMS + RANKING_TERMS)
        production_ir_roles = sum(
            1
            for role in context.candidate.career_history
            if _role_has(role, RETRIEVAL_TERMS + RANKING_TERMS) and _role_has(role, PRODUCTION_TERMS + EVALUATION_TERMS)
        )
        production_eval_roles = sum(
            1
            for role in context.candidate.career_history
            if _role_has(role, PRODUCTION_TERMS) and _role_has(role, EVALUATION_TERMS)
        )
        embedding_terms = TextNormalizer.has_any_normalized(context.norm_full_text, EMBEDDING_TERMS)
        vector_terms = TextNormalizer.has_any_normalized(context.norm_full_text, VECTOR_DB_TERMS)
        bm25_terms = TextNormalizer.has_any_normalized(context.norm_full_text, ("bm25", "tf-idf"))
        dense_terms = TextNormalizer.has_any_normalized(context.norm_full_text, ("dense", "vector", "embedding", "semantic"))
        title_family = TextNormalizer.role_family(context.candidate.profile.current_title)
        summary_family = TextNormalizer.role_family(profile_text)
        consistency = 1.0 if title_family == summary_family else 0.5 if title_family in {"software", "ai_ml", "retrieval"} and summary_family in {"software", "ai_ml", "retrieval"} else 0.0
        specificity_terms = TextNormalizer.count_terms_normalized(context.norm_full_text, PRODUCTION_TERMS + OWNERSHIP_TERMS + PRODUCT_IMPACT_TERMS)
        generic_penalty = TextNormalizer.count_terms_normalized(context.norm_full_text, ("professional with", "open to roles", "curious about", "emerging ai capabilities"))

        return {
            "jd_semantic_bm25_score": _lexical_jd_score(context.norm_full_text),
            "core_ir_phrase_count": ir_count,
            "production_ir_evidence_score": clamp(production_ir_roles / 2.0 + TextNormalizer.count_terms_normalized(context.norm_career_text, PRODUCTION_TERMS) * 0.03),
            "production_eval_cooccurrence_score": clamp(production_eval_roles / 2.0),
            "ranking_eval_phrase_score": score_by_terms_normalized(context.norm_full_text, EVALUATION_TERMS, cap=4),
            "query_understanding_score": score_by_terms_normalized(context.norm_full_text, ("query understanding", "query rewriting", "search intent", "search relevance"), cap=3),
            "embedding_system_evidence": weighted_flag(embedding_terms and vector_terms),
            "hybrid_search_evidence": weighted_flag(bm25_terms and dense_terms) + 0,
            "candidate_matching_domain_score": score_by_terms_normalized(context.norm_full_text, ("candidate matching", "job matching", "recruiter search", "talent marketplace", "matching system"), cap=3),
            "llm_integration_depth_score": _llm_depth(context.norm_full_text),
            "framework_demo_penalty_text": weighted_flag(
                TextNormalizer.has_any_normalized(context.norm_full_text, DEMO_ONLY_TERMS)
                and not TextNormalizer.has_any_normalized(context.norm_career_text, PRODUCTION_TERMS)
            ),
            "product_impact_phrase_score": score_by_terms_normalized(context.norm_full_text, PRODUCT_IMPACT_TERMS, cap=8),
            "writing_clarity_score": clamp((specificity_terms / 12.0) - (generic_penalty * 0.08)),
            "title_summary_consistency": consistency,
        }

    def _experience_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        candidate = context.candidate
        roles = candidate.career_history
        durations = [role.duration_months for role in roles]
        recent_role = roles[0]
        yoe = candidate.profile.years_of_experience
        avg_tenure = safe_mean(float(duration) for duration in durations)
        short_hops = sum(1 for duration in durations if duration < 18)
        senior_title = TextNormalizer.has_any(candidate.profile.current_title, ("senior", "lead", "staff", "principal", "architect"))
        ownership = TextNormalizer.count_terms_normalized(context.norm_career_text, OWNERSHIP_TERMS)

        applied_ml_months = _sum_role_months(roles, ML_TERMS + RETRIEVAL_TERMS + RANKING_TERMS)
        ir_months = _sum_role_months(roles, RETRIEVAL_TERMS + RANKING_TERMS + EMBEDDING_TERMS)
        production_ml_months = sum(
            role.duration_months
            for role in roles
            if _role_has(role, ML_TERMS + RETRIEVAL_TERMS + RANKING_TERMS) and _role_has(role, PRODUCTION_TERMS)
        )
        duration_gap_months = abs(yoe * 12.0 - sum(durations))
        current_role_coding = TextNormalizer.has_any(recent_role.title + " " + recent_role.description, CODING_TERMS)
        management_only = TextNormalizer.has_any(recent_role.title, ("manager", "director", "head", "architect")) and not current_role_coding
        title_inflation = _title_chaser_signal(roles)
        hands_on_ml_roles = sum(
            1
            for role in roles
            if _role_has(role, ML_TERMS + RETRIEVAL_TERMS + RANKING_TERMS) and _role_has(role, CODING_TERMS + OWNERSHIP_TERMS)
        )

        return {
            "yoe_target_band_score": _yoe_target_score(yoe),
            "senior_judgment_experience_score": clamp((yoe / 10.0) * 0.45 + weighted_flag(senior_title) * 0.25 + min(ownership, 8) / 8.0 * 0.3),
            "applied_ml_years_proxy": round(applied_ml_months / 12.0, 3),
            "ir_retrieval_years_proxy": round(ir_months / 12.0, 3),
            "production_ml_years_proxy": round(production_ml_months / 12.0, 3),
            "recent_coding_role_flag": weighted_flag(current_role_coding),
            "management_only_recent_penalty": weighted_flag(management_only),
            "pre_llm_ml_experience_flag": weighted_flag(applied_ml_months > 36 or any(skill.duration_months > 36 and _skill_has(skill, ML_TERMS) for skill in candidate.skills)),
            "career_duration_consistency": clamp(1.0 - duration_gap_months / 60.0),
            "current_role_duration_score": _current_role_duration_score(recent_role.duration_months),
            "average_tenure_score": _average_tenure_score(avg_tenure),
            "job_hop_title_chaser_penalty": clamp(short_hops / max(len(roles), 1) * 0.6 + title_inflation * 0.4),
            "hands_on_ml_role_ratio": round(hands_on_ml_roles / max(len(roles), 1), 4),
        }

    def _skill_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        candidate = context.candidate
        skills = candidate.skills
        skill_text = context.skill_text
        career_text = context.career_text
        core_skill_count = sum(1 for skill in skills if _skill_has(skill, CORE_AI_SKILLS))
        supported_core_count = sum(
            1
            for skill in skills
            if _skill_has(skill, CORE_AI_SKILLS) and TextNormalizer.has_any_normalized(context.norm_career_text, (skill.name,))
        )
        assessment_scores = {
            name: score
            for name, score in candidate.redrob_signals.skill_assessment_scores.items()
            if TextNormalizer.has_any(name, CORE_AI_SKILLS + PYTHON_TERMS)
        }
        expert_zero = sum(1 for skill in skills if skill.proficiency == "expert" and skill.duration_months == 0)
        impossible_core = sum(1 for skill in skills if _skill_has(skill, CORE_AI_SKILLS) and skill.duration_months == 0)
        nontech_title = TextNormalizer.has_any(candidate.profile.current_title, NEGATIVE_ARCHETYPES)
        cv_speech = sum(1 for skill in skills if _skill_has(skill, CV_SPEECH_ROBOTICS_TERMS))
        nlp_ir = sum(1 for skill in skills if _skill_has(skill, RETRIEVAL_TERMS + RANKING_TERMS + ("nlp",)))

        return {
            "python_strength_score": _skill_depth(skills, PYTHON_TERMS, context.norm_full_text, cap_months=48),
            "vector_db_skill_coverage": clamp(_matching_skill_count(skills, VECTOR_DB_TERMS) / 4.0),
            "retrieval_skill_depth": _skill_depth(skills, RETRIEVAL_TERMS + EMBEDDING_TERMS + VECTOR_DB_TERMS, context.norm_full_text, cap_months=60),
            "ranking_skill_depth": _skill_depth(skills, RANKING_TERMS + EVALUATION_TERMS, context.norm_full_text, cap_months=60),
            "llm_finetuning_skill_score": _skill_depth(skills, ("lora", "qlora", "peft", "fine-tuning", "finetuning", "hugging face", "transformers"), context.norm_full_text, cap_months=48),
            "mlops_skill_score": _skill_depth(skills, MLOPS_TERMS, context.norm_full_text, cap_months=48),
            "data_pipeline_support_score": _skill_depth(skills, DATA_PIPELINE_TERMS, context.norm_full_text, cap_months=48),
            "skill_assessment_core_mean": round(safe_mean((score / 100.0 for score in assessment_scores.values())), 4),
            "skill_assessment_core_max": round(max((score / 100.0 for score in assessment_scores.values()), default=0.0), 4),
            "skill_assessment_coverage": len(assessment_scores),
            "skill_history_support_ratio": round(supported_core_count / core_skill_count, 4) if core_skill_count else 1.0,
            "expert_zero_duration_penalty": expert_zero,
            "ai_keyword_stuffing_penalty": weighted_flag(core_skill_count >= 5 and (nontech_title or supported_core_count / max(core_skill_count, 1) < 0.25)),
            "cv_speech_robotics_dominance_penalty": weighted_flag(cv_speech >= 2 and cv_speech > max(nlp_ir, 0)),
            "certification_relevance_score": _certification_score(candidate),
            "skill_duration_impossibility_count": expert_zero + impossible_core,
            "core_ai_skill_count": core_skill_count,
        }

    def _behavioral_features(self, context: "_CandidateContext", semantic: dict[str, float | int]) -> dict[str, float | int]:
        signals = context.candidate.redrob_signals
        days_since_active = max(0, (self.as_of_date - signals.last_active_date).days)
        active_score = math.exp(-days_since_active / 90.0)
        response_score = signals.recruiter_response_rate if signals.recruiter_response_rate >= 0.2 else signals.recruiter_response_rate * 0.5
        response_speed = 1.0 / (1.0 + math.log1p(signals.avg_response_time_hours) / math.log1p(168))
        notice_score = _notice_score(signals.notice_period_days)
        demand = clamp(
            log_scale(signals.saved_by_recruiters_30d, 20) * 0.45
            + log_scale(signals.profile_views_received_30d, 200) * 0.25
            + log_scale(signals.search_appearance_30d, 500) * 0.30
        )
        completeness = signals.profile_completeness_score / 100.0
        contact = (weighted_flag(signals.verified_email) + weighted_flag(signals.verified_phone) + weighted_flag(signals.linkedin_connected)) / 3.0
        github = 0.45 if signals.github_activity_score < 0 else signals.github_activity_score / 100.0
        intent = 0.2 + 0.35 * weighted_flag(signals.open_to_work_flag) + 0.2 * log_scale(signals.applications_submitted_30d, 10)
        availability = clamp(intent + active_score * 0.2 + response_score * 0.15 + notice_score * 0.1)
        fit = float(semantic["production_ir_evidence_score"]) + float(semantic["jd_semantic_bm25_score"])

        return {
            "availability_multiplier": round(0.75 + availability * 0.5, 4),
            "days_since_active_score": round(active_score, 4),
            "recruiter_response_score": round(response_score, 4),
            "response_speed_score": round(clamp(response_speed), 4),
            "notice_period_score": notice_score,
            "interview_reliability_score": signals.interview_completion_rate if signals.interview_completion_rate >= 0.5 else signals.interview_completion_rate * 0.6,
            "offer_acceptance_known_score": 0.5 if signals.offer_acceptance_rate < 0 else signals.offer_acceptance_rate,
            "recruiter_demand_score": round(demand, 4),
            "profile_completeness_confidence": round(completeness, 4),
            "contact_verification_score": round(contact, 4),
            "contactability_multiplier": round(0.85 + contact * 0.3, 4),
            "github_external_validation_score": round(github, 4),
            "platform_activity_recency_x_fit": round(clamp(active_score * fit / 2.0), 4),
            "applications_activity_score": round(log_scale(signals.applications_submitted_30d, 10), 4),
        }

    def _career_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        candidate = context.candidate
        roles = candidate.career_history
        product_months = _sum_role_months(roles, PRODUCT_INDUSTRIES)
        services_only = all(_is_consulting_role(role) for role in roles) and product_months == 0
        startup_months = sum(role.duration_months for role in roles if role.company_size in {"11-50", "51-200", "201-500"} and _role_has(role, PRODUCT_INDUSTRIES))
        large_scale = score_by_terms_normalized(context.norm_career_text, ("50m", "million", "throughput", "large index", "distributed", "high traffic", "500gb"), cap=4)
        ownership = score_by_terms_normalized(context.norm_career_text, OWNERSHIP_TERMS, cap=10)
        cross_functional = score_by_terms_normalized(context.norm_career_text, PRODUCT_IMPACT_TERMS + ("cross-functional", "stakeholder"), cap=8)
        title_family = TextNormalizer.role_family(candidate.profile.current_title)
        role_fit = 1.0 if title_family in {"ai_ml", "retrieval"} else 0.75 if title_family == "software" else 0.35 if title_family == "management" else 0.0
        nontech = weighted_flag(TextNormalizer.has_any(candidate.profile.current_title, NEGATIVE_ARCHETYPES))
        current_product_ai = weighted_flag(
            _role_has(roles[0], ML_TERMS + RETRIEVAL_TERMS + RANKING_TERMS)
            and _role_has(roles[0], PRODUCT_INDUSTRIES)
        )

        return {
            "product_company_exposure_months": product_months,
            "services_only_penalty": weighted_flag(services_only),
            "current_industry_fit_score": score_by_terms_normalized(TextNormalizer.normalize(candidate.profile.current_industry), PRODUCT_INDUSTRIES, cap=1),
            "startup_or_scaleup_exposure": round(startup_months / 12.0, 3),
            "large_scale_exposure": large_scale,
            "ownership_verbs_score": ownership,
            "cross_functional_product_score": cross_functional,
            "role_family_fit_score": role_fit,
            "nontech_role_penalty": nontech,
            "current_product_ai_role_flag": current_product_ai,
        }

    def _education_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        education = context.candidate.education
        fields = " ".join(item.field_of_study for item in education)
        degrees = " ".join(item.degree for item in education)
        timeline_valid = weighted_flag(all(item.end_year >= item.start_year for item in education))
        tier = max((TIER_SCORE.get(item.tier, 0.35) for item in education), default=0.35)
        degree_score = max((_degree_level_score(item.degree) for item in education), default=0.0)
        production_present = TextNormalizer.has_any(context.career_text, PRODUCTION_TERMS)
        research_only = TextNormalizer.has_any(fields + " " + degrees + " " + context.profile_text, RESEARCH_TERMS) and not production_present

        return {
            "cs_ai_field_score": score_by_terms_normalized(TextNormalizer.normalize(fields), ("computer science", "artificial intelligence", "machine learning", "data science", "statistics", "mathematics", "information technology"), cap=2),
            "degree_level_score": degree_score,
            "institution_tier_score": tier,
            "education_timeline_validity": timeline_valid,
            "research_only_phd_penalty": weighted_flag(research_only),
            "grade_parse_score": _grade_score(education),
        }

    def _logistics_features(self, context: "_CandidateContext") -> dict[str, float | int]:
        candidate = context.candidate
        profile = candidate.profile
        signals = candidate.redrob_signals
        location = f"{profile.location} {profile.country}"
        preferred = TextNormalizer.has_any(location, PREFERRED_CITIES)
        metro = TextNormalizer.has_any(location, INDIA_METRO_CITIES)
        india = profile.country.casefold() == "india"
        outside_preferred = not preferred
        salary_mid = (signals.expected_salary_range_inr_lpa.min + signals.expected_salary_range_inr_lpa.max) / 2.0
        salary_width = signals.expected_salary_range_inr_lpa.max - signals.expected_salary_range_inr_lpa.min
        expected_mid = 8.0 + min(profile.years_of_experience, 12.0) * 3.0
        salary_realism = clamp(1.0 - abs(salary_mid - expected_mid) / max(expected_mid, 1.0))
        work_mode = {"hybrid": 1.0, "flexible": 0.9, "onsite": 0.75, "remote": 0.55}[signals.preferred_work_mode]

        return {
            "preferred_location_score": 1.0 if preferred else 0.75 if metro else 0.45 if india else 0.2,
            "india_location_score": 1.0 if india else 0.35,
            "relocation_fit_score": 1.0 if preferred else 0.85 if signals.willing_to_relocate else 0.35 if outside_preferred else 1.0,
            "work_mode_fit_score": work_mode,
            "salary_midpoint_realism": round(salary_realism, 4),
            "salary_range_width_penalty": weighted_flag(salary_width < 0 or salary_width > max(12.0, salary_mid * 0.7)),
            "notice_buyout_fit": _notice_score(signals.notice_period_days),
        }

    def _anomaly_features(
        self,
        context: "_CandidateContext",
        skill: dict[str, float | int],
        career: dict[str, float | int],
        education: dict[str, float | int],
        logistics: dict[str, float | int],
        semantic: dict[str, float | int],
    ) -> dict[str, float | int]:
        candidate = context.candidate
        summary_years = TextNormalizer.extract_years(candidate.profile.summary + " " + candidate.profile.headline)
        stated_years = candidate.profile.years_of_experience
        summary_mismatch = weighted_flag(any(abs(year - stated_years) > 2.0 for year in summary_years))
        title_mismatch = weighted_flag(_title_description_mismatch(candidate))
        date_mismatch = sum(1 for role in candidate.career_history if _role_date_duration_mismatch(role, self.as_of_date))
        current_count = sum(1 for role in candidate.career_history if role.is_current)
        template_duplicate = weighted_flag(
            TextNormalizer.has_any(candidate.profile.summary, ("professional with", "open to roles"))
            and TextNormalizer.has_any(candidate.profile.current_title, NEGATIVE_ARCHETYPES)
            and TextNormalizer.count_terms_normalized(context.norm_skill_text, CORE_AI_SKILLS) >= 3
        )
        signals = candidate.redrob_signals
        behavioral_inconsistent = weighted_flag(
            (signals.open_to_work_flag is False and signals.applications_submitted_30d >= 8)
            or (signals.saved_by_recruiters_30d >= 10 and not (signals.verified_email or signals.verified_phone))
        )
        retrieval_stuffing = weighted_flag(
            TextNormalizer.count_terms_normalized(context.norm_skill_text, RETRIEVAL_TERMS + VECTOR_DB_TERMS + EMBEDDING_TERMS) >= 4
            and float(semantic["production_ir_evidence_score"]) < 0.2
        )
        honeypot = (
            summary_mismatch * 0.12
            + title_mismatch * 0.14
            + clamp(float(skill["skill_duration_impossibility_count"]) / 3.0) * 0.14
            + (1.0 - float(education["education_timeline_validity"])) * 0.08
            + clamp(date_mismatch / 3.0) * 0.08
            + weighted_flag(current_count != 1) * 0.08
            + float(career["services_only_penalty"]) * 0.08
            + float(skill["ai_keyword_stuffing_penalty"]) * 0.12
            + retrieval_stuffing * 0.08
            + float(logistics["salary_range_width_penalty"]) * 0.04
            + behavioral_inconsistent * 0.04
        )
        confidence = clamp(
            0.35
            + float(semantic["production_ir_evidence_score"]) * 0.2
            + float(skill["skill_history_support_ratio"]) * 0.2
            + (1.0 - clamp(honeypot)) * 0.25
        )

        return {
            "honeypot_score": round(clamp(honeypot), 4),
            "summary_profile_years_mismatch": summary_mismatch,
            "title_description_mismatch": title_mismatch,
            "skill_duration_impossibility_count": int(skill["skill_duration_impossibility_count"]),
            "education_end_before_start_flag": weighted_flag(float(education["education_timeline_validity"]) == 0.0),
            "role_date_duration_mismatch": date_mismatch,
            "multiple_current_roles_flag": weighted_flag(current_count != 1),
            "template_duplicate_suspicion": template_duplicate,
            "behavioral_inconsistency_score": behavioral_inconsistent,
            "reasoning_confidence_score": round(confidence, 4),
        }


class _CandidateContext:
    def __init__(self, *, candidate: Candidate, as_of_date: date) -> None:
        self.candidate = candidate
        self.as_of_date = as_of_date
        self.profile_text = candidate.profile_text
        self.career_text = candidate.career_text
        self.skill_text = candidate.skill_text
        self.full_text = candidate.full_text
        
        self.norm_profile_text = TextNormalizer.normalize(self.profile_text)
        self.norm_career_text = TextNormalizer.normalize(self.career_text)
        self.norm_skill_text = TextNormalizer.normalize(self.skill_text)
        self.norm_full_text = TextNormalizer.normalize(self.full_text)


def _role_text(role: CareerHistory) -> str:
    return f"{role.title} {role.company} {role.industry} {role.description}"


def _role_has(role: CareerHistory, terms: tuple[str, ...]) -> bool:
    return TextNormalizer.has_any(_role_text(role), terms)


def _skill_has(skill: Skill, terms: tuple[str, ...]) -> bool:
    return TextNormalizer.has_any(skill.name, terms)


def _matching_skill_count(skills: tuple[Skill, ...], terms: tuple[str, ...]) -> int:
    return sum(1 for skill in skills if _skill_has(skill, terms))


def _sum_role_months(roles: tuple[CareerHistory, ...], terms: tuple[str, ...]) -> int:
    return sum(role.duration_months for role in roles if _role_has(role, terms))


def _lexical_jd_score(norm_text: str) -> float:
    tokens = [t for t in norm_text.split() if t]
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    score = 0.0
    for term in JD_QUERY_TERMS:
        term_tokens = TextNormalizer.tokenize(term)
        if not term_tokens:
            continue
        if len(term_tokens) == 1:
            score += math.log1p(counts.get(term_tokens[0], 0))
        elif TextNormalizer.has_any_normalized(norm_text, (term,)):
            score += 1.5
    return clamp(score / 25.0)


def _llm_depth(norm_text: str) -> float:
    strong = TextNormalizer.count_terms_normalized(norm_text, ("fine-tuning", "finetuning", "lora", "qlora", "peft", "hugging face", "reranking"))
    rag = TextNormalizer.count_terms_normalized(norm_text, ("rag", "llm", "openai embeddings", "transformers"))
    demo = TextNormalizer.count_terms_normalized(norm_text, ("langchain", "prompt", "chatgpt", "demo", "side project"))
    return clamp(strong * 0.22 + rag * 0.08 - demo * 0.04)


def _yoe_target_score(yoe: float) -> float:
    if 6.0 <= yoe <= 8.0:
        return 1.0
    if 5.0 <= yoe < 6.0 or 8.0 < yoe <= 9.0:
        return 0.85
    if 4.0 <= yoe < 5.0 or 9.0 < yoe <= 11.0:
        return 0.6
    return clamp(1.0 - abs(7.0 - yoe) / 10.0)


def _current_role_duration_score(months: int) -> float:
    if 18 <= months <= 48:
        return 1.0
    if 12 <= months < 18 or 48 < months <= 72:
        return 0.75
    if months < 6:
        return 0.25
    return 0.55


def _average_tenure_score(months: float) -> float:
    if months >= 30:
        return 1.0
    if months >= 24:
        return 0.8
    if months >= 18:
        return 0.55
    return 0.25


def _title_chaser_signal(roles: tuple[CareerHistory, ...]) -> float:
    if len(roles) < 3:
        return 0.0
    durations = [role.duration_months for role in roles]
    title_words = " ".join(role.title for role in roles[:3])
    inflation = TextNormalizer.count_terms(title_words, ("senior", "lead", "staff", "principal", "manager", "head"))
    return weighted_flag(median(durations) < 18 and inflation >= 2)


def _skill_depth(skills: tuple[Skill, ...], terms: tuple[str, ...], norm_text: str, *, cap_months: int) -> float:
    score = 0.0
    for skill in skills:
        if _skill_has(skill, terms):
            proficiency = SKILL_PROFICIENCY_ORDER[skill.proficiency]
            duration = clamp(skill.duration_months / cap_months)
            endorsement = log_scale(skill.endorsements, 50)
            score += proficiency * 0.45 + duration * 0.4 + endorsement * 0.15
    text_support = 0.15 if TextNormalizer.has_any_normalized(norm_text, terms) else 0.0
    return round(clamp(score / 2.0 + text_support), 4)


def _certification_score(candidate: Candidate) -> float:
    text = " ".join(f"{cert.name} {cert.issuer}" for cert in candidate.certifications)
    if not text:
        return 0.0
    return score_by_terms_normalized(TextNormalizer.normalize(text), ("aws machine learning", "gcp", "azure ai", "deep learning", "nlp", "machine learning"), cap=2)


def _notice_score(days: int) -> float:
    if days <= 30:
        return 1.0
    if days <= 60:
        return 0.75
    if days <= 90:
        return 0.45
    return 0.2


def _is_consulting_role(role: CareerHistory) -> bool:
    role_text = f"{role.company} {role.industry}"
    return TextNormalizer.has_any(role_text, CONSULTING_COMPANIES + ("consulting", "it services"))


def _degree_level_score(degree: str) -> float:
    normalized = TextNormalizer.normalize(degree)
    if TextNormalizer.has_any(normalized, ("ph.d", "phd", "doctor")):
        return 0.85
    if TextNormalizer.has_any(normalized, ("m.tech", "m.e", "m.sc", "ms", "masters", "master")):
        return 0.7
    if TextNormalizer.has_any(normalized, ("b.tech", "b.e", "b.sc", "bachelor")):
        return 0.5
    return 0.25


def _grade_score(education: tuple[Education, ...]) -> float:
    scores: list[float] = []
    for item in education:
        if item.grade is None:
            continue
        numbers = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", item.grade)]
        if not numbers:
            continue
        value = numbers[0]
        if "cgpa" in item.grade.casefold():
            scores.append(clamp(value / 10.0))
        elif "%" in item.grade:
            scores.append(clamp(value / 100.0))
    return round(max(scores, default=0.0), 4)


def _title_description_mismatch(candidate: Candidate) -> bool:
    title_family = TextNormalizer.role_family(candidate.profile.current_title)
    current_role = next((role for role in candidate.career_history if role.is_current), candidate.career_history[0])
    description_family = TextNormalizer.role_family(current_role.description)
    if title_family == "unknown" or description_family == "unknown":
        return False
    if title_family == "nontech" and description_family in {"ai_ml", "retrieval", "software"}:
        return True
    if title_family in {"ai_ml", "retrieval"} and description_family == "nontech":
        return True
    return False


def _role_date_duration_mismatch(role: CareerHistory, as_of_date: date) -> bool:
    end_date = role.end_date or as_of_date
    approx_months = max(0, (end_date.year - role.start_date.year) * 12 + end_date.month - role.start_date.month)
    return abs(approx_months - role.duration_months) > 3
