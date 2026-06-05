import sys
import os

sys.path.insert(0, os.path.abspath('src'))

from candidate_processor.parser import CandidateParser
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from jd_parser.jd_parser import JDParser
from ranking.candidate_scorer import CandidateScorer

def main():
    with open("data/job_description.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    
    jd_analysis = JDParser().parse(jd_text)
    extractor = CandidateFeatureExtractor()
    parser = CandidateParser()
    
    cand_stream = parser.stream("data/candidates.jsonl")
    
    cand = None
    for c in cand_stream:
        if c["candidate_id"] == "CAND_0000739":
            cand = extractor.extract(c)
            break
            
    scorer = CandidateScorer()
    match = scorer.score(jd_analysis, cand)
    
    print(f"Breakdown for {match.candidate_id}:")
    print(f"Semantic Score: {match.scoring_breakdown.semantic_score}")
    print(f"Feature Match Score: {match.scoring_breakdown.feature_match_score}")
    print(f"Weighted Feature Score: {match.scoring_breakdown.weighted_feature_score}")
    print(f"Penalty Score: {match.scoring_breakdown.penalty_score}")
    print(f"Raw Score: {match.scoring_breakdown.raw_score}")
    print(f"Final Score: {match.scoring_breakdown.final_score}")
    print(f"Missing: {match.missing_requirements}")
    
    print("\nFeature Scores:")
    for label, score in match.scoring_breakdown.group_scores.items():
        print(f"{label}: {score}")

if __name__ == "__main__":
    main()
