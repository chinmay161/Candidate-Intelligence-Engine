from __future__ import annotations

import unittest

from ranking.pre_rank_retriever import BM25Retriever, HybridRetriever, TFIDFRetriever
from ranking_fixtures import candidate_record, retrieval_jd


class PreRankRetrieverTests(unittest.TestCase):
    def test_hybrid_retriever_shortlists_best_candidates_stably(self) -> None:
        analysis = retrieval_jd()
        candidates = (
            candidate_record("LOW", fit=0.1),
            candidate_record("TOP_A", fit=1.0),
            candidate_record("MID", fit=0.55),
            candidate_record("TOP_B", fit=1.0),
        )

        result = HybridRetriever().retrieve(analysis, candidates, limit=2)

        self.assertEqual(result.total_candidates, 4)
        self.assertEqual([hit.candidate.candidate_id for hit in result.hits], ["TOP_A", "TOP_B"])
        self.assertGreaterEqual(result.hits[0].score, result.hits[1].score)

    def test_bm25_and_tfidf_score_relevant_candidate_above_weak_candidate(self) -> None:
        analysis = retrieval_jd()
        strong = candidate_record("STRONG", fit=1.0)
        weak = candidate_record("WEAK", fit=0.1)
        hybrid = HybridRetriever()
        query = hybrid._query_terms(analysis)

        strong_counts = strong.retrieval_term_counts
        weak_counts = weak.retrieval_term_counts

        self.assertGreater(BM25Retriever().score_candidate(analysis, strong, query, strong_counts, strong.retrieval_doc_len), BM25Retriever().score_candidate(analysis, weak, query, weak_counts, weak.retrieval_doc_len))
        self.assertGreater(TFIDFRetriever().score_candidate(analysis, strong, query, strong_counts, strong.retrieval_doc_len), TFIDFRetriever().score_candidate(analysis, weak, query, weak_counts, weak.retrieval_doc_len))


if __name__ == "__main__":
    unittest.main()
