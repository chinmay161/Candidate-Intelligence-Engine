import sys
import os
from collections import Counter

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.parser import CandidateParser
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from jd_parser.jd_parser import JDParser
from ranking.ranker import Ranker

def main():
    with open("data/job_description.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    
    jd_analysis = JDParser().parse(jd_text)
    extractor = CandidateFeatureExtractor()
    parser = CandidateParser()
    
    cand_stream = parser.stream("data/candidates.jsonl")
    
    def generate_features():
        for i, cand in enumerate(cand_stream):
            if i >= 5000:
                break
            yield extractor.extract(cand)
            
    ranker = Ranker()
    result = ranker.rank(jd_analysis, generate_features(), top_k=None, pre_rank_limit=None)
    
    reasons = Counter()
    for match in result.matches:
        for p in match.penalties:
            if getattr(p, "severity", "low") != "low":
                reasons[p.reason] += 1
                
    print("Penalty Distribution (5000 candidates):")
    for reason, count in reasons.most_common():
        print(f"- {reason}: {count} ({count/5000*100:.2f}%)")

if __name__ == "__main__":
    main()
