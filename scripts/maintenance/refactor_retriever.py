import re

with open('src/ranking/pre_rank_retriever.py', 'r') as f:
    content = f.read()

# 1. Update PreRankRetriever.retrieve
retrieve_replacement = """        for ordinal, candidate in enumerate(candidates):
            total += 1
            terms = self._candidate_terms(candidate)
            counts = Counter(terms)
            doc_len = len(terms)
            score = self.score_candidate(analysis, candidate, query_terms, counts, doc_len)
            hit = RetrievalHit(candidate=candidate, score=round(score, 6), ordinal=ordinal)"""
content = re.sub(r"        for ordinal, candidate in enumerate\(candidates\):\n            total \+= 1\n            score = self.score_candidate\(analysis, candidate, query_terms\)\n            hit = RetrievalHit\(candidate=candidate, score=round\(score, 6\), ordinal=ordinal\)", retrieve_replacement, content)

# 2. Update score_candidate base signature
base_sig_replacement = """    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: Counter[str],
        doc_len: int,
    ) -> float:"""
content = re.sub(r"    def score_candidate\(\n        self,\n        analysis: JDAnalysis,\n        candidate: CandidateFeatureRecord,\n        query_terms: tuple\[str, \.\.\.\],\n    \) -> float:", base_sig_replacement, content)

# 3. Update BM25Retriever.score_candidate
bm25_sig = """    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: Counter[str],
        doc_len: int,
    ) -> float:
        if not term_counts or not query_terms:
            return 0.0
        score = 0.0
        for term in query_terms:
            frequency = term_counts.get(term, 0)
            if frequency <= 0:
                continue
            denominator = frequency + self.k1 * (1.0 - self.b + self.b * doc_len / self.average_doc_length)
            score += (frequency * (self.k1 + 1.0)) / denominator
        return clamp(score / max(len(query_terms), 1))"""
content = re.sub(r"    def score_candidate\(\n        self,\n        analysis: JDAnalysis,\n        candidate: CandidateFeatureRecord,\n        query_terms: tuple\[str, \.\.\.\],\n    \) -> float:\n        terms = self\._candidate_terms\(candidate\)\n        if not terms or not query_terms:\n            return 0\.0\n        counts = Counter\(terms\)\n        doc_len = len\(terms\)\n        score = 0\.0\n        for term in query_terms:\n            frequency = counts\.get\(term, 0\)\n            if frequency <= 0:\n                continue\n            denominator = frequency \+ self\.k1 \* \(1\.0 - self\.b \+ self\.b \* doc_len / self\.average_doc_length\)\n            score \+= \(frequency \* \(self\.k1 \+ 1\.0\)\) / denominator\n        return clamp\(score / max\(len\(query_terms\), 1\)\)", bm25_sig, content)

# 4. Update TFIDFRetriever.score_candidate
tfidf_sig = """    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: Counter[str],
        doc_len: int,
    ) -> float:
        if not term_counts or not query_terms:
            return 0.0
        length_norm = math.sqrt(sum(value * value for value in term_counts.values())) or 1.0
        query_counts = Counter(query_terms)
        query_norm = math.sqrt(sum(value * value for value in query_counts.values())) or 1.0
        dot = sum((term_counts.get(term, 0) / length_norm) * (weight / query_norm) for term, weight in query_counts.items())
        return clamp(dot * 3.0)"""
content = re.sub(r"    def score_candidate\(\n        self,\n        analysis: JDAnalysis,\n        candidate: CandidateFeatureRecord,\n        query_terms: tuple\[str, \.\.\.\],\n    \) -> float:\n        terms = self\._candidate_terms\(candidate\)\n        if not terms or not query_terms:\n            return 0\.0\n        counts = Counter\(terms\)\n        length_norm = math\.sqrt\(sum\(value \* value for value in counts\.values\(\)\)\) or 1\.0\n        query_counts = Counter\(query_terms\)\n        query_norm = math\.sqrt\(sum\(value \* value for value in query_counts\.values\(\)\)\) or 1\.0\n        dot = sum\(\(counts\.get\(term, 0\) / length_norm\) \* \(weight / query_norm\) for term, weight in query_counts\.items\(\)\)\n        return clamp\(dot \* 3\.0\)", tfidf_sig, content)

# 5. Update HybridRetriever.score_candidate
hybrid_sig = """    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: Counter[str],
        doc_len: int,
    ) -> float:
        bm25_score = self.bm25.score_candidate(analysis, candidate, query_terms, term_counts, doc_len)
        tfidf_score = self.tfidf.score_candidate(analysis, candidate, query_terms, term_counts, doc_len)
        feature_score = self._weighted_feature_hint(analysis, candidate)
        lexical = bm25_score * 0.60 + tfidf_score * 0.40
        return clamp(lexical * self.lexical_weight + feature_score * (1.0 - self.lexical_weight))"""
content = re.sub(r"    def score_candidate\(\n        self,\n        analysis: JDAnalysis,\n        candidate: CandidateFeatureRecord,\n        query_terms: tuple\[str, \.\.\.\],\n    \) -> float:\n        bm25_score = self\.bm25\.score_candidate\(analysis, candidate, query_terms\)\n        tfidf_score = self\.tfidf\.score_candidate\(analysis, candidate, query_terms\)\n        feature_score = self\._weighted_feature_hint\(analysis, candidate\)\n        lexical = bm25_score \* 0\.60 \+ tfidf_score \* 0\.40\n        return clamp\(lexical \* self\.lexical_weight \+ feature_score \* \(1\.0 - self\.lexical_weight\)\)", hybrid_sig, content)

# Also need to import Counter in type checking or fix annotations if needed. Counter is already imported.
# Fix type hints in PreRankRetriever.score_candidate
content = content.replace("term_counts: Counter[str]", "term_counts: Counter")

with open('src/ranking/pre_rank_retriever.py', 'w') as f:
    f.write(content)
