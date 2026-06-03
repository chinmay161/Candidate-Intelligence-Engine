import pytest
from src.evaluation.ablation_runner import AblationRunner, AblationConfig

def dummy_pipeline(config: AblationConfig):
    return {
        "runtime": 1.5,
        "score_distribution": {"mean": 0.8},
        "candidate_diversity": 0.9,
        "reasoning_quality": 0.95
    }

def test_ablation_runner():
    runner = AblationRunner()
    results = runner.run(dummy_pipeline)
    
    assert "full_system" in results
    assert "no_behavioral_signals" in results
    assert results["full_system"]["runtime"] == 1.5
    assert results["no_reasoning_layer"]["reasoning_quality"] == 0.95
