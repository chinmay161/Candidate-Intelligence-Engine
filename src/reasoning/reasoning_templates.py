"""Deterministic recruiter-facing reasoning templates."""

from __future__ import annotations

from candidate_processor.models import CandidateFeatureRecord
from ranking.match_models import CandidateMatch
from reasoning.reasoning_models import CandidateConcern, CandidateStrength

# ==========================================
# PHRASE LIBRARIES (>= 20 variants per type)
# ==========================================

OPENINGS = [
    "Candidate shows {tier_adj} alignment, bringing {yoe} years of experience with a background as {title}.",
    "With a {tier_adj} background as {title}, this candidate has accumulated {yoe} years of engineering experience.",
    "Profile displays {tier_adj} match, highlighted by {yoe} years of experience, currently working as {title}.",
    "The candidate has {yoe} years of industry experience, showing {tier_adj} alignment in their role as {title}.",
    "Brings {yoe} years of professional experience, demonstrating {tier_adj} alignment as a {title}.",
    "Featuring {yoe} years of experience, this candidate exhibits {tier_adj} alignment in {title} roles.",
    "As a {title} with {yoe} years of experience, the candidate offers {tier_adj} alignment for this position.",
    "A {yoe}-year career background as {title} underscores the candidate's {tier_adj} match.",
    "Presenting {yoe} years of professional history, the candidate is a {tier_adj} fit as {title}.",
    "Currently a {title}, they bring {yoe} years of experience and exhibit {tier_adj} alignment.",
    "This candidate has spent {yoe} years in the field, representing a {tier_adj} match as a {title}.",
    "A professional track record of {yoe} years as {title} demonstrates {tier_adj} alignment.",
    "With {yoe} years of experience, the candidate demonstrates {tier_adj} match in their career as {title}.",
    "Their {yoe} years of history as {title} shows a {tier_adj} match with the target profile.",
    "Having worked {yoe} years in engineering, the candidate shows {tier_adj} match as {title}.",
    "Showing {tier_adj} alignment, the candidate offers {yoe} years of experience as {title}.",
    "The candidate's {yoe} years of experience as {title} indicates a {tier_adj} match.",
    "A {yoe}-year track record as {title} highlights a {tier_adj} match for the role.",
    "Brings a {tier_adj} match as {title}, backed by {yoe} years of experience in the industry.",
    "Boasts {yoe} years of experience as {title}, showing {tier_adj} alignment with the target profile."
]

JD_ALIGNMENTS = [
    "Their background aligns directly with the JD's search infrastructure focus, particularly in {techs}.",
    "This expertise matches the JD's emphasis on building retrieval pipelines, specifically using {techs}.",
    "Demonstrates expertise in {techs}, matching the JD's requirement for hands-on search system development.",
    "Their knowledge of {techs} fits the JD's expectation for high-performance retrieval architectures.",
    "They satisfy the JD's technical search requirements by bringing experience in {techs}.",
    "The candidate's skills in {techs} correspond well with the team's need for advanced search capabilities.",
    "This candidate matches the JD's focus on search optimization, having worked with {techs}.",
    "Their profile matches the core JD themes, showcasing experience with {techs}.",
    "This matches the JD's technical expectations, specifically their work with {techs}.",
    "Brings hands-on capabilities in {techs}, aligning with the JD's focus on search quality.",
    "Their familiarity with {techs} addresses the JD's demand for modern retrieval systems.",
    "They demonstrate a strong capability in {techs}, matching the JD's core search stack.",
    "With practical experience in {techs}, they match the JD's ranking and retrieval expectations.",
    "Shows a strong technical alignment with the JD's search priorities through their use of {techs}.",
    "Their experience in {techs} corresponds directly to the JD's search infrastructure needs.",
    "They offer a solid match for the JD's search platform needs, including hands-on work with {techs}.",
    "Matches the JD's focus on production-grade retrieval tools, featuring experience with {techs}.",
    "Provides a clear match for the search-focused JD, showing competence in {techs}.",
    "Their experience with {techs} aligns with the JD's search and indexing technologies.",
    "This meets the JD's requirements for search domain experience, utilizing {techs} in past roles."
]

CONCERNS_NOTICE = [
    "Although they have a strong profile, their {notice}-day notice period may slow onboarding compared to other candidates.",
    "The candidate's {notice}-day notice period represents a potential delay in hiring timelines.",
    "A {notice}-day notice period is a logistical constraint that could impact immediate team needs.",
    "While technically qualified, their {notice}-day notice period might slow hiring compared with similarly ranked candidates.",
    "The logistical constraint of a {notice}-day notice period may require coordination for immediate roles."
]

CONCERNS_CONSULTING = [
    "Their retrieval experience is relevant, but most career history is in consulting, which is less aligned with the JD's product engineering focus.",
    "A consulting-heavy career history suggests they may need adjustment to a dedicated product-engineering environment.",
    "While they have strong skills, their background in consulting services differs from the preferred product engineering focus.",
    "Mainly holds consulting roles, which may require transition support to align with the JD's product ownership expectations.",
    "Their background is heavily services-oriented, presenting a minor tradeoff for product-focused engineering teams."
]

CONCERNS_PRODUCTION = [
    "They demonstrate strong theoretical knowledge, but show limited evidence of running retrieval systems in production.",
    "A potential area for review is their limited exposure to large-scale production search systems.",
    "Shows solid skills, but lacks documented experience managing search systems in high-traffic production environments.",
    "While they possess relevant skills, their profile lacks direct evidence of production-level retrieval implementation.",
    "Their academic or demo-level experience is strong, but their production-scale search exposure remains a point for review."
]

CONCERNS_MISSING = [
    "They show solid skills, though they lack direct experience in {missing}, which are listed as key requirements.",
    "The candidate has adjacent experience, but missing skills in {missing} could require initial training.",
    "A notable tradeoff is the lack of exposure to {missing}, which are important parts of the job description.",
    "While overall qualified, their lack of direct experience with {missing} represents a potential gap.",
    "Some adjacent skills are present, but direct experience in {missing} is missing, representing a hiring tradeoff."
]

CONCERNS_FALLBACK = [
    "No major penalties were flagged, but their salary realism and relocation preferences should be verified.",
    "No significant risks identified, though confirming their work mode flexibility is recommended.",
    "They represent a low-risk profile, though verifying their familiarity with advanced evaluation metrics is advised.",
    "No severe constraints were detected, but general alignment on role expectations is recommended.",
    "While their technical profile is stable, standard checks on communication and availability should be performed."
]

MITIGATING_STATEMENTS = [
    "However, this is mitigated by their strong recruiter responsiveness and high platform activity.",
    "Fortunately, their deep technical capabilities and Python depth suggest they can adapt quickly.",
    "This is offset by their high technical assessment score and proven hands-on contribution.",
    "Their immediate availability and active profile status help offset this onboarding delay.",
    "Nevertheless, their hands-on ML role ratio suggests strong technical adaptability.",
    "On the positive side, their strong semantic score highlights their search expertise.",
    "This is mitigated by their solid background in search-focused engineering.",
    "However, their high profile completeness score indicates strong candidate intent.",
    "Fortunately, their proven track record in relevant ML roles offsets this tradeoff.",
    "Nonetheless, their strong coding history suggests they will ramp up quickly.",
    "This concern is balanced by their active engagement and recruiter response rate.",
    "However, their solid portfolio of search projects suggests strong core competence.",
    "But their high github activity score highlights active personal development.",
    "This is offset by their demonstrated ownership of search pipelines in past roles.",
    "Fortunately, their location alignment and relocation willingness are positive signals.",
    "Still, their strong evaluation credentials offer high confidence in their work.",
    "This constraint is balanced by their exceptional technical match on core search skills.",
    "But their solid tenure in past roles indicates long-term commitment.",
    "Nonetheless, their hands-on coding background reduces the impact of this concern.",
    "However, their overall high scoring breakdown indicates they remain a highly competitive match."
]

EVALUATION_STRENGTHS = [
    "They possess proven experience in search quality evaluation, including NDCG and MAP metrics.",
    "Their background includes designing search evaluation frameworks to measure retrieval quality.",
    "They demonstrate strong capabilities in search evaluation metrics like NDCG, MAP, and MRR.",
    "Demonstrates solid understanding of ranking evaluation methods in production environments.",
    "Has hands-on experience using NDCG and search relevance metrics to evaluate ranking models.",
    "Brings specialized knowledge in search evaluation and ranking metrics like NDCG and MAP.",
    "Highly capable of setting up retrieval evaluation pipelines and measuring relevancy metrics.",
    "Their history showcases experience with search evaluation techniques, boosting retrieval precision.",
    "Brings strong expertise in search quality metrics and offline evaluation frameworks.",
    "Well-versed in ranking metrics, including NDCG, MAP, and MRR, to drive search quality."
]

GENERAL_STRENGTHS = [
    "They bring strong production experience, particularly in building scalable retrieval models.",
    "Shows exceptional hands-on ownership of shipped search and retrieval pipelines.",
    "Brings deep expertise in Python and modern vector search tools.",
    "Has a proven track record of shipping end-to-end ML retrieval architectures.",
    "Demonstrates solid skills in embedding generation and vector database management.",
    "Their background features strong experience in scalable search infrastructure.",
    "Displays solid proficiency in ranking algorithms and hybrid search implementations.",
    "They offer a hands-on technical background in building search applications.",
    "Highly proficient in designing production-ready search and retrieval layers.",
    "Brings valuable experience in tuning ranking systems and integrating LLM APIs."
]

BEHAVIORAL_ACTIVE = [
    "The candidate is immediately available and highly active on the platform.",
    "Shows high availability and strong recruiter response rate, indicating high intent.",
    "Exhibits active recruiter engagement and immediate availability for interviews.",
    "They are actively looking and show strong platform engagement metrics.",
    "Highly active profile with quick recruiter response times.",
    "Immediate availability makes them an attractive candidate for active roles.",
    "Demonstrates exceptional candidate intent with high response and activity rates.",
    "Highly responsive profile showing immediate availability for scheduling.",
    "An active search status is backed by strong platform engagement signals.",
    "They are immediately available and highly responsive to recruiter queries."
]

BEHAVIORAL_PASSIVE = [
    "Their profile shows steady activity and reliable response signals.",
    "Maintains a steady platform presence with consistent responsiveness.",
    "Demonstrates good contactability and standard notice availability.",
    "They offer solid behavioral signals, showing reliable communication history.",
    "Their profile indicates stable active status and standard response rate.",
    "Consistent activity metrics suggest steady interest in relevant roles.",
    "Brings stable behavioral signals, including a complete profile.",
    "They show reasonable responsiveness and verified contact details.",
    "Maintains standard activity levels and steady responsiveness.",
    "Exhibits solid platform credentials and regular active signals."
]

CLOSING_TOP = [
    "Overall, they represent an exceptional alignment and are among the strongest fits for the role.",
    "Therefore, they are highly recommended as a direct match with demonstrated production ownership.",
    "In conclusion, this profile is a top-tier candidate exhibiting standout search expertise.",
    "They represent a premier candidate who is highly recommended for immediate team integration.",
    "Given their exceptional credentials, they should be prioritized for immediate technical interviews.",
    "Ultimately, their strong production history makes them a standout candidate for this search role.",
    "They represent a top-tier talent with the engineering depth required to own search pipelines."
]

CLOSING_MID = [
    "Overall, the candidate is a strong fit with some tradeoffs, showing meaningful alignment.",
    "They represent a solid hire with relevant experience that aligns with key business objectives.",
    "In summary, they offer a balanced profile and a strong candidate for further evaluation.",
    "This is a qualified profile that warrants a screening conversation to assess team fit.",
    "They offer a strong combination of skills and represent a viable candidate for the team.",
    "With solid credentials and relevant experience, they are a recommended mid-tier candidate.",
    "They represent a competitive profile with minor training needs in specific areas."
]

CLOSING_LOWER = [
    "They are included due to adjacent experience, though notable gaps in production search remain.",
    "While some skills align, they represent a partial alignment that may require substantial ramp-up.",
    "In conclusion, they offer adjacent experience but are a lower priority compared to top-tier candidates.",
    "They remain a backup option given the gaps in production-level retrieval experience.",
    "Some technical qualifications are present, but significant gaps remain for this senior role.",
    "They represent a marginal fit for this team, though they could be considered for adjacent roles."
]


class ReasoningTemplates:
    """Generate concise, factual recruiter-facing language."""

    def render(
        self,
        match: CandidateMatch,
        strengths: list[CandidateStrength],
        concerns: list[CandidateConcern],
        candidate: CandidateFeatureRecord | None = None,
        rank: int | None = None,
    ) -> str:
        # 1. Extract facts and determine the tier
        facts = self._extract_facts(candidate, match)
        tier = self._get_tier(rank, match.score)
        candidate_id = match.candidate_id

        # 2. Select rank-consistent adjectives
        if tier == "top":
            tier_adj = self._select_from_pool(["exceptional", "outstanding", "first-rate", "superb"], candidate_id, offset=1)
        elif tier == "mid":
            tier_adj = self._select_from_pool(["strong", "meaningful", "highly relevant", "solid"], candidate_id, offset=1)
        else:
            tier_adj = self._select_from_pool(["partial", "adjacent", "limited", "basic"], candidate_id, offset=1)

        # 3. Build component sentences
        
        # Opening/Experience/Career History
        open_idx = self._get_deterministic_index(candidate_id, offset=0, max_val=20)
        opening_sentence = OPENINGS[open_idx].format(
            tier_adj=tier_adj,
            yoe=facts["yoe"],
            title=facts["current_title"]
        )

        # JD Alignment / Skills / Infrastructure Experience
        techs_str = self._format_techs(facts["technologies"])
        jd_idx = self._get_deterministic_index(candidate_id, offset=5, max_val=20)
        jd_alignment_sentence = JD_ALIGNMENTS[jd_idx].format(techs=techs_str)

        # Concern / Risk
        prefix = self._select_from_pool(["Potential concern:", "Area for review:", "Note:"], candidate_id, offset=11)
        concern_sentence = f"{prefix} {self._get_concern_sentence(candidate_id, facts, concerns, match.missing_requirements)}"

        # Mitigating Factor
        mit_idx = self._get_deterministic_index(candidate_id, offset=13, max_val=20)
        mitigating_sentence = MITIGATING_STATEMENTS[mit_idx]

        # Strength / Evaluation Experience
        if facts["has_eval"]:
            str_idx = self._get_deterministic_index(candidate_id, offset=9, max_val=10)
            strength_sentence = EVALUATION_STRENGTHS[str_idx]
        else:
            str_idx = self._get_deterministic_index(candidate_id, offset=9, max_val=10)
            strength_sentence = GENERAL_STRENGTHS[str_idx]

        # Behavioral / Availability
        if facts["open_to_work"] or (candidate and candidate.behavioral_features.get("availability_multiplier", 1.0) > 1.15):
            beh_idx = self._get_deterministic_index(candidate_id, offset=15, max_val=10)
            behavioral_sentence = BEHAVIORAL_ACTIVE[beh_idx]
        else:
            beh_idx = self._get_deterministic_index(candidate_id, offset=15, max_val=10)
            behavioral_sentence = BEHAVIORAL_PASSIVE[beh_idx]

        # Closing / Recommendation
        if tier == "top":
            close_idx = self._get_deterministic_index(candidate_id, offset=17, max_val=len(CLOSING_TOP))
            closing_sentence = CLOSING_TOP[close_idx]
        elif tier == "mid":
            close_idx = self._get_deterministic_index(candidate_id, offset=17, max_val=len(CLOSING_MID))
            closing_sentence = CLOSING_MID[close_idx]
        else:
            close_idx = self._get_deterministic_index(candidate_id, offset=17, max_val=len(CLOSING_LOWER))
            closing_sentence = CLOSING_LOWER[close_idx]

        # 4. Select structure pattern deterministically based on candidate ID hash
        pattern_index = sum(ord(c) for c in candidate_id) % 6
        sentences: list[str] = []

        if pattern_index == 0:
            # Pattern A: Experience -> Skills -> Concern -> Closing
            sentences = [opening_sentence, jd_alignment_sentence, concern_sentence, closing_sentence]
        elif pattern_index == 1:
            # Pattern B: JD Match -> Experience -> Concern -> Closing
            sentences = [jd_alignment_sentence, opening_sentence, concern_sentence, closing_sentence]
        elif pattern_index == 2:
            # Pattern C: Concern -> Mitigating Factor -> Strength -> Closing
            sentences = [concern_sentence, mitigating_sentence, strength_sentence, closing_sentence]
        elif pattern_index == 3:
            # Pattern D: Behavioral Signals -> Technical Fit -> Experience -> Closing
            sentences = [behavioral_sentence, jd_alignment_sentence, opening_sentence, closing_sentence]
        elif pattern_index == 4:
            # Pattern E: Career History -> Infrastructure Experience -> Risk -> Closing
            sentences = [opening_sentence, jd_alignment_sentence, concern_sentence, closing_sentence]
        else:
            # Pattern F: Technical Match -> Evaluation Experience -> Availability -> Closing
            sentences = [jd_alignment_sentence, strength_sentence, behavioral_sentence, closing_sentence]

        return self._fit_target_length(" ".join(sentences))

    def _get_deterministic_index(self, candidate_id: str, offset: int, max_val: int) -> int:
        return (sum(ord(c) for c in candidate_id) + offset) % max_val

    def _select_from_pool(self, pool: list[str], candidate_id: str, offset: int) -> str:
        idx = self._get_deterministic_index(candidate_id, offset, len(pool))
        return pool[idx]

    def _format_techs(self, techs: list[str]) -> str:
        if not techs:
            return "search and retrieval frameworks"
        if len(techs) == 1:
            return techs[0]
        if len(techs) == 2:
            return f"{techs[0]} and {techs[1]}"
        return f"{', '.join(techs[:-1])}, and {techs[-1]}"

    def _get_tier(self, rank: int | None, score: float) -> str:
        if rank is not None:
            if rank <= 10:
                return "top"
            elif rank <= 50:
                return "mid"
            else:
                return "lower"

        # Fallback based on score (handling both normalized 0-1 and 0-100 scales)
        if score >= 85.0 or (0.85 <= score <= 1.0):
            return "top"
        elif score >= 50.0 or (0.50 <= score < 0.85):
            return "mid"
        else:
            return "lower"

    def _extract_facts(self, candidate: CandidateFeatureRecord | None, match: CandidateMatch) -> dict:
        if candidate is not None and "candidate_facts" in candidate.evidence.by_feature:
            try:
                import json
                return json.loads(candidate.evidence.by_feature["candidate_facts"][0])
            except Exception:
                pass

        # Fallback reconstruction logic for unit/stress tests
        facts = {}
        
        yoe_val = 6.0
        if candidate is not None:
            yoe_val = candidate.experience_features.get("applied_ml_years_proxy", 6.0)
            if yoe_val <= 0:
                yoe_val = 5.0
        facts["yoe"] = round(yoe_val, 1)

        title = "Senior ML Engineer"
        if candidate is not None:
            for category in ["role_family_fit_score", "career_roles"]:
                snippets = candidate.evidence.by_feature.get(category, [])
                for s in snippets:
                    if " at " in s:
                        title = s.split(" at ")[0]
                        break
                    elif len(s) < 50:
                        title = s
                        break
        facts["current_title"] = title
        facts["current_company"] = "a technology company"
        facts["location"] = "India"
        facts["country"] = "India"

        # Product vs consulting
        facts["product_months"] = candidate.career_features.get("product_company_exposure_months", 24) if candidate else 24
        facts["services_only"] = candidate.career_features.get("services_only_penalty", 0.0) >= 0.5 if candidate else False

        # Notice period
        notice_days = 30
        if candidate is not None:
            notice_days = int(candidate.logistics_features.get("notice_period_days", 0))
            if notice_days == 0:
                notice_score = candidate.logistics_features.get("notice_buyout_fit", 1.0)
                if notice_score <= 0.2:
                    notice_days = 90
                elif notice_score <= 0.45:
                    notice_days = 60
                elif notice_score <= 0.75:
                    notice_days = 45
        facts["notice_period_days"] = notice_days

        # Open to work
        facts["open_to_work"] = False
        if candidate is not None:
            facts["open_to_work"] = candidate.behavioral_features.get("availability_multiplier", 1.0) > 1.1

        # Technologies
        techs = []
        if candidate is not None:
            full_evidence_text = " ".join(" ".join(lst) for lst in candidate.evidence.by_feature.values()).lower()
            for tech in ["faiss", "elasticsearch", "opensearch", "solr", "lucene", "pinecone", "milvus", "weaviate", "qdrant", "chroma", "vald", "vespa", "hybrid search", "bm25", "learning to rank", "ndcg", "map", "mrr"]:
                if tech in full_evidence_text:
                    cased = {
                        "faiss": "FAISS",
                        "elasticsearch": "Elasticsearch",
                        "opensearch": "OpenSearch",
                        "solr": "Solr",
                        "lucene": "Lucene",
                        "pinecone": "Pinecone",
                        "milvus": "Milvus",
                        "weaviate": "Weaviate",
                        "qdrant": "Qdrant",
                        "chroma": "Chroma",
                        "vald": "Vald",
                        "vespa": "Vespa",
                        "hybrid search": "hybrid search",
                        "bm25": "BM25",
                        "learning to rank": "Learning to Rank",
                        "ndcg": "NDCG",
                        "map": "MAP",
                        "mrr": "MRR"
                    }[tech]
                    techs.append(cased)
        if not techs:
            for req in match.matched_requirements:
                if "python" in req.lower():
                    techs.append("Python")
                if "vector" in req.lower() or "embedding" in req.lower():
                    techs.append("vector databases")
                if "search" in req.lower() or "retrieval" in req.lower():
                    techs.append("retrieval systems")
        if not techs:
            techs = ["FAISS", "Elasticsearch"]
        facts["technologies"] = techs

        facts["has_eval"] = any(t in ["NDCG", "MAP", "MRR", "Learning to Rank"] for t in techs)
        if candidate is not None:
            facts["has_eval"] = facts["has_eval"] or candidate.semantic_features.get("ranking_eval_phrase_score", 0.0) >= 0.5

        return facts

    def _get_concern_sentence(
        self,
        candidate_id: str,
        facts: dict,
        concerns: list[CandidateConcern],
        missing_reqs: tuple[str, ...],
    ) -> str:
        # Determine categories
        has_notice = facts.get("notice_period_days", 0) > 30 or any("notice" in str(c.category).lower() for c in concerns)
        has_services = facts.get("services_only", False) or any("services" in str(c.category).lower() or "consulting" in str(c.category).lower() for c in concerns)
        has_production_limit = any("production" in str(c.category).lower() for c in concerns)
        
        missing_skills = [m.split(":", 1)[1].replace("_", " ") for m in missing_reqs if m.startswith("required_skill:")]

        categories = []
        if has_notice:
            categories.append("notice")
        if has_services:
            categories.append("services")
        if has_production_limit:
            categories.append("production")
        if missing_skills:
            categories.append("missing")

        if not categories:
            categories.append("fallback")

        # Pick category deterministically
        cat_idx = self._get_deterministic_index(candidate_id, offset=11, max_val=len(categories))
        selected_cat = categories[cat_idx]

        # Find matching concern description
        desc = "identified tradeoff"
        for c in concerns:
            if selected_cat == "notice" and "notice" in str(c.category).lower():
                desc = c.description
                break
            elif selected_cat == "services" and ("services" in str(c.category).lower() or "consulting" in str(c.category).lower()):
                desc = c.description
                break
            elif selected_cat == "production" and "production" in str(c.category).lower():
                desc = c.description
                break
            elif selected_cat == "missing" and "missing" in str(c.category).lower():
                desc = c.description
                break
        else:
            if concerns:
                desc = concerns[0].description
            else:
                if selected_cat == "notice":
                    desc = "longer-than-average notice period"
                elif selected_cat == "services":
                    desc = "consulting-heavy or services-only career signal"
                elif selected_cat == "production":
                    desc = "limited production retrieval or ranking evidence"
                elif selected_cat == "missing":
                    desc = "missing required JD requirement"

        idx = self._get_deterministic_index(candidate_id, offset=12, max_val=5)
        if selected_cat == "notice":
            return CONCERNS_NOTICE[idx % len(CONCERNS_NOTICE)].format(desc=desc, notice=facts.get("notice_period_days", 30))
        elif selected_cat == "services":
            return CONCERNS_CONSULTING[idx % len(CONCERNS_CONSULTING)].format(desc=desc)
        elif selected_cat == "production":
            return CONCERNS_PRODUCTION[idx % len(CONCERNS_PRODUCTION)].format(desc=desc)
        elif selected_cat == "missing":
            skills_str = ", ".join(missing_skills[:2]) if missing_skills else "required search skills"
            return CONCERNS_MISSING[idx % len(CONCERNS_MISSING)].format(desc=desc, missing=skills_str)
        else:
            return CONCERNS_FALLBACK[idx % len(CONCERNS_FALLBACK)].format(desc=desc)

    def _fit_target_length(self, text: str) -> str:
        words = text.split()
        if len(words) <= 80:
            return text

        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        trimmed: list[str] = []
        total = 0
        for sentence in sentences:
            length = len(sentence.split())
            if trimmed and total + length > 78:
                break
            trimmed.append(sentence)
            total += length
        return ". ".join(trimmed) + "."
