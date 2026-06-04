import cProfile
import pstats
import io
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('tests'))

from ranking_fixtures import retrieval_jd, candidate_record
from ranking.pre_rank_retriever import HybridRetriever

jd = retrieval_jd()
cands = [candidate_record(f"CAND_{i}", fit=0.5) for i in range(10000)]

pr = cProfile.Profile()
pr.enable()

retriever = HybridRetriever()
retriever.retrieve(jd, cands)

pr.disable()
s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats('cumtime').print_stats(15)
print(s.getvalue())
