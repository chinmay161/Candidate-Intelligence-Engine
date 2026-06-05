"""Batch ranking orchestration."""

from __future__ import annotations

from collections.abc import Iterable

from candidate_processor.models import CandidateFeatureRecord
from jd_parser.jd_models import JDAnalysis
from ranking.candidate_scorer import CandidateScorer
from ranking.match_models import CandidateMatch, RankingResult
from ranking.pre_rank_retriever import HybridRetriever, PreRankRetriever
from ranking.score_normalizer import ScoreNormalizer
from ranking.topk_selector import TopKSelector


class Ranker:
    """Rank a stream or list of candidate feature records."""

    def __init__(
        self,
        *,
        scorer: CandidateScorer | None = None,
        normalizer: ScoreNormalizer | None = None,
        topk_selector: TopKSelector | None = None,
        pre_rank_retriever: PreRankRetriever | None = None,
    ) -> None:
        self.scorer = scorer or CandidateScorer()
        self.normalizer = normalizer or ScoreNormalizer()
        self.topk_selector = topk_selector or TopKSelector()
        self.pre_rank_retriever = pre_rank_retriever or HybridRetriever()

    def rank(
        self,
        analysis: JDAnalysis,
        candidates: Iterable[CandidateFeatureRecord],
        *,
        top_k: int | None = 100,
        normalization: str = "minmax",
        pre_rank_limit: int | None = 5_000,
    ) -> RankingResult:
        total = 0
        candidate_pool = candidates
        if top_k is not None and pre_rank_limit is not None:
            shortlist_size = max(top_k, pre_rank_limit)
            pre_ranked = self.pre_rank_retriever.retrieve(analysis, candidates, limit=shortlist_size)
            candidate_pool = pre_ranked.candidates
            total = pre_ranked.total_candidates

        scored: list[CandidateMatch] = []
        for candidate in candidate_pool:
            if top_k is not None and pre_rank_limit is None:
                total += 1
            scored.append(self.scorer.score(analysis, candidate))

        # Normalize across the entire pool before truncating
        normalized = self.normalizer.normalize(tuple(scored), method=normalization)

        if top_k is None:
            ranked = tuple(match for _, match in sorted(enumerate(normalized), key=lambda item: (-item[1].score, item[0])))
        else:
            selected = self.topk_selector.select(normalized, k=top_k)
            ranked = tuple(match for _, match in sorted(enumerate(selected), key=lambda item: (-item[1].score, item[0])))
        return RankingResult(
            matches=ranked,
            total_candidates=total,
            selected_count=len(ranked),
            normalized=True,
            method=normalization,
        )
