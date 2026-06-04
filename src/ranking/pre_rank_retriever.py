"""Fast deterministic retrieval before full candidate scoring."""

from __future__ import annotations

import heapq
import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from candidate_processor.models import CandidateFeatureRecord
from candidate_processor.normalizer import TextNormalizer, clamp
from jd_parser.jd_models import JDAnalysis


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """One pre-rank retrieval hit."""

    candidate: CandidateFeatureRecord
    score: float
    ordinal: int


@dataclass(frozen=True, slots=True)
class PreRankResult:
    """Shortlist and total scanned candidate count."""

    hits: tuple[RetrievalHit, ...]
    total_candidates: int

    @property
    def candidates(self) -> tuple[CandidateFeatureRecord, ...]:
        return tuple(hit.candidate for hit in self.hits)


class PreRankRetriever:
    """Base class for low-cost candidate shortlisting."""

    def retrieve(
        self,
        analysis: JDAnalysis,
        candidates: Iterable[CandidateFeatureRecord],
        *,
        limit: int = 5_000,
    ) -> PreRankResult:
        if limit <= 0:
            return PreRankResult(hits=(), total_candidates=sum(1 for _ in candidates))

        query_terms = self._query_terms(analysis)
        heap: list[tuple[float, int, RetrievalHit]] = []
        total = 0
        for ordinal, candidate in enumerate(candidates):
            total += 1
            counts = candidate.retrieval_term_counts
            doc_len = candidate.retrieval_doc_len
            score = self.score_candidate(analysis, candidate, query_terms, counts, doc_len)
            candidate.retrieval_term_counts.clear()
            hit = RetrievalHit(candidate=candidate, score=round(score, 6), ordinal=ordinal)
            item = (hit.score, -ordinal, hit)
            if len(heap) < limit:
                heapq.heappush(heap, item)
            elif item > heap[0]:
                heapq.heapreplace(heap, item)

        hits = tuple(item[2] for item in sorted(heap, key=lambda item: (-item[0], -item[1])))
        return PreRankResult(hits=hits, total_candidates=total)

    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: dict[str, int],
        doc_len: int,
    ) -> float:
        raise NotImplementedError

    def _query_terms(self, analysis: JDAnalysis) -> tuple[str, ...]:
        parts = [
            analysis.job_description.title,
            analysis.job_description.raw_text,
            analysis.role_family,
            " ".join(skill.canonical_name.replace("_", " ") for skill in analysis.required_skills),
            " ".join(skill.canonical_name.replace("_", " ") for skill in analysis.preferred_skills),
            " ".join(analysis.industries),
            " ".join(analysis.behavioral_preferences),
        ]
        tokens = TextNormalizer.tokenize(" ".join(parts))
        stopwords = {
            "and",
            "or",
            "the",
            "for",
            "with",
            "must",
            "no",
            "not",
            "years",
            "required",
            "preferred",
        }
        ordered_unique: dict[str, None] = {}
        for token in tokens:
            if len(token) >= 3 and token not in stopwords:
                ordered_unique[token] = None
        return tuple(ordered_unique)




class BM25Retriever(PreRankRetriever):
    """Single-document BM25-style scoring for precomputed candidate features."""

    def __init__(self, *, k1: float = 1.2, b: float = 0.55, average_doc_length: float = 160.0) -> None:
        self.k1 = k1
        self.b = b
        self.average_doc_length = average_doc_length

    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: dict[str, int],
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
        return clamp(score / max(len(query_terms), 1))


class TFIDFRetriever(PreRankRetriever):
    """Fast query-overlap retriever using local term frequency and JD weights."""

    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: dict[str, int],
        doc_len: int,
    ) -> float:
        if not term_counts or not query_terms:
            return 0.0
        length_norm = math.sqrt(sum(value * value for value in term_counts.values())) or 1.0
        query_counts = Counter(query_terms)
        query_norm = math.sqrt(sum(value * value for value in query_counts.values())) or 1.0
        dot = sum((term_counts.get(term, 0) / length_norm) * (weight / query_norm) for term, weight in query_counts.items())
        return clamp(dot * 3.0)


class HybridRetriever(PreRankRetriever):
    """Blend lexical retrieval with cheap JD-weighted feature fit."""

    def __init__(
        self,
        *,
        bm25: BM25Retriever | None = None,
        tfidf: TFIDFRetriever | None = None,
        lexical_weight: float = 0.65,
    ) -> None:
        self.bm25 = bm25 or BM25Retriever()
        self.tfidf = tfidf or TFIDFRetriever()
        self.lexical_weight = lexical_weight

    def score_candidate(
        self,
        analysis: JDAnalysis,
        candidate: CandidateFeatureRecord,
        query_terms: tuple[str, ...],
        term_counts: dict[str, int],
        doc_len: int,
    ) -> float:
        bm25_score = self.bm25.score_candidate(analysis, candidate, query_terms, term_counts, doc_len)
        tfidf_score = self.tfidf.score_candidate(analysis, candidate, query_terms, term_counts, doc_len)
        feature_score = self._weighted_feature_hint(analysis, candidate)
        lexical = bm25_score * 0.60 + tfidf_score * 0.40
        return clamp(lexical * self.lexical_weight + feature_score * (1.0 - self.lexical_weight))

    def _weighted_feature_hint(self, analysis: JDAnalysis, candidate: CandidateFeatureRecord) -> float:
        groups = {
            "semantic": candidate.semantic_features,
            "experience": candidate.experience_features,
            "skill": candidate.skill_features,
            "career": candidate.career_features,
            "logistics": candidate.logistics_features,
        }
        total = 0.0
        weighted = 0.0
        for group, weights in analysis.feature_weights.by_group.items():
            if group not in groups:
                continue
            values = groups[group]
            for feature, weight in weights.items():
                if weight <= 0:
                    continue
                weighted += weight * self._normalize_feature_value(feature, float(values.get(feature, 0.0)))
                total += weight
        return clamp(weighted / total) if total else 0.0

    def _normalize_feature_value(self, feature: str, value: float) -> float:
        if feature.endswith("_count"):
            return clamp(value / 5.0)
        if feature.endswith("_months"):
            return clamp(value / 60.0)
        if feature.endswith("_years_proxy") or feature.endswith("_exposure"):
            return clamp(value / 6.0)
        return clamp(value)
