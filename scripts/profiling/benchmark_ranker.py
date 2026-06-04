import time
import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.parser import CandidateParser
from ranking.ranker import Ranker
from jd_parser.jd_parser import JDParser

parser = CandidateParser()
cand_stream = parser.stream("data/candidates.jsonl")

extractor = CandidateFeatureExtractor()

jd_text = """
Senior AI Engineer for an HR Tech recruitment marketplace.
Required: 5-9 years, Python, semantic search, embeddings, vector database,
hybrid search, learning to rank, NDCG, and production ranking systems.
Must be hands-on with ownership and product thinking. Pune or Noida, hybrid.
No consulting-only or research-only background.
"""
jd_parser = JDParser()
analysis = jd_parser.parse(jd_text, title="Senior AI Engineer")

def generate_features():
    for i, cand in enumerate(cand_stream):
        if i >= 10000:
            break
        yield extractor.extract(cand)

ranker = Ranker()
start = time.perf_counter()
result = ranker.rank(analysis, generate_features(), top_k=100, pre_rank_limit=5000)
print(f"Total time for ranker.rank on 10000 candidates: {time.perf_counter() - start:.2f}s")
