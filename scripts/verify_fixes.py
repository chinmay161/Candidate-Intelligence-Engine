import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.parser import CandidateParser
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from jd_parser.jd_parser import JDParser
from ranking.ranker import Ranker
from reasoning.reasoning_generator import ReasoningGenerator

def main():
    with open("data/job_description.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    
    jd_analysis = JDParser().parse(jd_text)
    extractor = CandidateFeatureExtractor()
    parser = CandidateParser()
    
    cand_stream = parser.stream("data/candidates.jsonl")
    
    def generate_features():
        for i, cand in enumerate(cand_stream):
            if i >= 1000:
                break
            yield extractor.extract(cand)
            
    ranker = Ranker()
    # Ranking now does normalization inside
    result = ranker.rank(jd_analysis, generate_features(), top_k=10, pre_rank_limit=1000)
    
    generator = ReasoningGenerator()
    
    print("Top 10 Candidates Post-Fix:")
    missing_cnt = 0
    scores = set()
    reasons = set()
    
    for match in result.matches:
        # Dummy candidate just for reasoning generation
        cand = next(c for c in extractor.extract_batch([next((cx for cx in parser.stream("data/candidates.jsonl") if cx.candidate_id == match.candidate_id), None)]) if c is not None)
        reasoning = generator.generate(jd_analysis, match, cand)
        
        scores.add(match.score)
        reasons.add(reasoning.reasoning)
        if match.missing_requirements:
            missing_cnt += 1
            
        print(f"\nID: {match.candidate_id}, Score: {match.score}")
        print(f"Missing: {match.missing_requirements}")
        print(f"Reasoning: {reasoning.reasoning}")
        
    print(f"\nVerification Results:")
    print(f"Unique Scores: {len(scores)}")
    print(f"Unique Reasonings: {len(reasons)}")
    print(f"Top 10 missing requirements count: {missing_cnt}")

if __name__ == "__main__":
    main()
