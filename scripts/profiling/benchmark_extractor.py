import time
import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.parser import CandidateParser

parser = CandidateParser()
cand_stream = parser.stream("data/candidates.jsonl")

extractor = CandidateFeatureExtractor()

start = time.perf_counter()

count = 0
for cand in cand_stream:
    extractor.extract(cand)
    count += 1
    if count % 1000 == 0:
        print(f"{count} candidates processed in {time.perf_counter() - start:.2f}s")
    if count == 10000:
        break

print(f"Total time for {count} candidates: {time.perf_counter() - start:.2f}s")
