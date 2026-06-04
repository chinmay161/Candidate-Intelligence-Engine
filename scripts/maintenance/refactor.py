import re

with open('src/candidate_processor/feature_extractor.py', 'r') as f:
    content = f.read()

# 1. Imports
content = content.replace("from candidate_processor.normalizer import TextNormalizer, clamp, log_scale, safe_mean, score_by_terms, weighted_flag", "from candidate_processor.normalizer import TextNormalizer, clamp, log_scale, safe_mean, score_by_terms, score_by_terms_normalized, weighted_flag")

# 2. Update _CandidateContext
context_replacement = """class _CandidateContext:
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
        self.norm_full_text = TextNormalizer.normalize(self.full_text)"""
content = re.sub(r"class _CandidateContext:.*?(?=\n\n\ndef _role_text)", context_replacement, content, flags=re.DOTALL)

# 3. Simple replacements in methods
content = content.replace("TextNormalizer.count_terms(career_text", "TextNormalizer.count_terms_normalized(context.norm_career_text")
content = content.replace("TextNormalizer.count_terms(text", "TextNormalizer.count_terms_normalized(context.norm_full_text")
content = content.replace("TextNormalizer.has_any(text", "TextNormalizer.has_any_normalized(context.norm_full_text")
content = content.replace("TextNormalizer.has_any(career_text", "TextNormalizer.has_any_normalized(context.norm_career_text")

content = content.replace("score_by_terms(text", "score_by_terms_normalized(context.norm_full_text")
content = content.replace("score_by_terms(context.career_text", "score_by_terms_normalized(context.norm_career_text")
content = content.replace("score_by_terms(context.profile_text", "score_by_terms_normalized(context.norm_profile_text")
content = content.replace("score_by_terms(context.skill_text", "score_by_terms_normalized(context.norm_skill_text")
content = content.replace("score_by_terms(candidate.profile.current_industry", "score_by_terms_normalized(TextNormalizer.normalize(candidate.profile.current_industry)")
content = content.replace("score_by_terms(fields,", "score_by_terms_normalized(TextNormalizer.normalize(fields),")

content = content.replace("TextNormalizer.count_terms(context.skill_text", "TextNormalizer.count_terms_normalized(context.norm_skill_text")
content = content.replace("TextNormalizer.count_terms(context.career_text", "TextNormalizer.count_terms_normalized(context.norm_career_text")

# 4. _lexical_jd_score
lex_replace = """def _lexical_jd_score(norm_text: str) -> float:
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
    return clamp(score / 25.0)"""
content = re.sub(r"def _lexical_jd_score\(text: str\) -> float:.*?(?=\n\n\ndef _llm_depth)", lex_replace, content, flags=re.DOTALL)

# 5. _llm_depth
llm_replace = """def _llm_depth(norm_text: str) -> float:
    strong = TextNormalizer.count_terms_normalized(norm_text, ("fine-tuning", "finetuning", "lora", "qlora", "peft", "hugging face", "reranking"))
    rag = TextNormalizer.count_terms_normalized(norm_text, ("rag", "llm", "openai embeddings", "transformers"))
    demo = TextNormalizer.count_terms_normalized(norm_text, ("langchain", "prompt", "chatgpt", "demo", "side project"))
    return clamp(strong * 0.22 + rag * 0.08 - demo * 0.04)"""
content = re.sub(r"def _llm_depth\(text: str\) -> float:.*?(?=\n\n\ndef _yoe_target_score)", llm_replace, content, flags=re.DOTALL)

# Update calls to _lexical_jd_score and _llm_depth
content = content.replace("_lexical_jd_score(text)", "_lexical_jd_score(context.norm_full_text)")
content = content.replace("_llm_depth(text)", "_llm_depth(context.norm_full_text)")

# 6. Update _skill_depth
skill_depth_replace = """def _skill_depth(skills: tuple[Skill, ...], terms: tuple[str, ...], norm_text: str, *, cap_months: int) -> float:
    score = 0.0
    for skill in skills:
        if _skill_has(skill, terms):
            proficiency = SKILL_PROFICIENCY_ORDER[skill.proficiency]
            duration = clamp(skill.duration_months / cap_months)
            endorsement = log_scale(skill.endorsements, 50)
            score += proficiency * 0.45 + duration * 0.4 + endorsement * 0.15
    text_support = 0.15 if TextNormalizer.has_any_normalized(norm_text, terms) else 0.0
    return round(clamp(score / 2.0 + text_support), 4)"""
content = re.sub(r"def _skill_depth\(skills: tuple\[Skill, \.\.\.\], terms: tuple\[str, \.\.\.\], text: str, \*, cap_months: int\) -> float:.*?(?=\n\n\ndef _certification_score)", skill_depth_replace, content, flags=re.DOTALL)

# Update _skill_depth calls
content = content.replace("_skill_depth(skills, PYTHON_TERMS, context.full_text,", "_skill_depth(skills, PYTHON_TERMS, context.norm_full_text,")
content = content.replace("_skill_depth(skills, RETRIEVAL_TERMS + EMBEDDING_TERMS + VECTOR_DB_TERMS, context.full_text,", "_skill_depth(skills, RETRIEVAL_TERMS + EMBEDDING_TERMS + VECTOR_DB_TERMS, context.norm_full_text,")
content = content.replace("_skill_depth(skills, RANKING_TERMS + EVALUATION_TERMS, context.full_text,", "_skill_depth(skills, RANKING_TERMS + EVALUATION_TERMS, context.norm_full_text,")
content = content.replace("""_skill_depth(skills, ("lora", "qlora", "peft", "fine-tuning", "finetuning", "hugging face", "transformers"), context.full_text,""", """_skill_depth(skills, ("lora", "qlora", "peft", "fine-tuning", "finetuning", "hugging face", "transformers"), context.norm_full_text,""")
content = content.replace("_skill_depth(skills, MLOPS_TERMS, context.full_text,", "_skill_depth(skills, MLOPS_TERMS, context.norm_full_text,")
content = content.replace("_skill_depth(skills, DATA_PIPELINE_TERMS, context.full_text,", "_skill_depth(skills, DATA_PIPELINE_TERMS, context.norm_full_text,")

with open('src/candidate_processor/feature_extractor.py', 'w') as f:
    f.write(content)
