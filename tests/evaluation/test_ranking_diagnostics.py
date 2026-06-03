import pytest
from src.evaluation.ranking_diagnostics import RankingDiagnostics

def test_ranking_diagnostics():
    candidates = [
        {"score": 0.9, "penalties": ["honeypot"], "confidence": 0.8},
        {"score": 0.85, "confidence": 0.75},
        {"score": 0.85, "confidence": 0.9}
    ]
    
    diagnostics = RankingDiagnostics().analyze(candidates)
    
    assert diagnostics["candidate_score_distribution"]["max"] == 0.9
    assert diagnostics["candidate_score_distribution"]["min"] == 0.85
    assert diagnostics["duplicate_score_rate"] > 0.0 # 0.85 is duplicated
    assert diagnostics["penalty_rate"] == 1/3
    assert diagnostics["confidence_distribution"]["max"] == 0.9
