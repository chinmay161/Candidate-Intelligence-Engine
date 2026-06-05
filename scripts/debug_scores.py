import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.parser import CandidateParser
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from jd_parser.jd_parser import JDParser
from ranking.ranker import Ranker
from ranking.score_normalizer import ScoreNormalizer

def main():
    with open("data/job_description.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    
    jd_analysis = JDParser().parse(jd_text)
    extractor = CandidateFeatureExtractor()
    parser = CandidateParser()
    
    cand_stream = parser.stream("data/candidates.jsonl")
    
    def generate_features():
        for i, cand in enumerate(cand_stream):
            if i >= 1000:  # test on 1000
                break
            yield extractor.extract(cand)
            
    ranker = Ranker()
    # Rank without normalization to see raw scores
    result = ranker.rank(jd_analysis, generate_features(), top_k=10, pre_rank_limit=1000)
    
    print("Raw Top 10 (Selected before Normalization):")
    for match in result.matches:
        print(f"ID: {match.candidate_id}, Score: {match.score}, Missing: {match.missing_requirements}")

    # Test normalization bug
    normalizer = ScoreNormalizer()
    norm = normalizer.normalize(result.matches, method="minmax")
    print("\nAfter Normalizing Top 10 Slice:")
    for match in norm:
        print(f"ID: {match.candidate_id}, Norm Score: {match.score}")

if __name__ == "__main__":
    main()
