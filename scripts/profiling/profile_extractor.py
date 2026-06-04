import cProfile
import pstats
import io
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('tests'))

import json
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.parser import CandidateParser

parser = CandidateParser()
cand_stream = parser.stream("data/candidates.jsonl")
cand = next(cand_stream)
extractor = CandidateFeatureExtractor()

pr = cProfile.Profile()
pr.enable()

for _ in range(10000):
    extractor.extract(cand)

pr.disable()
s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats('cumtime').print_stats(20)
print(s.getvalue())
