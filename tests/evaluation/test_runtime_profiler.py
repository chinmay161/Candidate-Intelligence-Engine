import pytest
import time
from src.evaluation.runtime_profiler import RuntimeProfiler

def test_runtime_profiler():
    profiler = RuntimeProfiler()
    profiler.start("feature_extraction_time")
    time.sleep(0.01)
    profiler.stop("feature_extraction_time")
    
    profile = profiler.get_profile()
    assert profile["feature_extraction_time"] > 0
    assert profile["ranking_time"] == 0.0
