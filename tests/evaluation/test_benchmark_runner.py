import pytest
from src.evaluation.benchmark_runner import BenchmarkRunner

def dummy_pipeline(scale: int):
    return {
        "runtime": 0.001 * scale,
        "memory_mb": 10.0 + (scale * 0.01)
    }

def test_benchmark_runner():
    runner = BenchmarkRunner(scales=[100, 1000])
    results = runner.run(dummy_pipeline)
    
    assert "100" in results
    assert "1000" in results
    assert results["100"]["runtime"] > 0
    assert results["100"]["memory"] > 0
    assert results["100"]["throughput"] > 0
