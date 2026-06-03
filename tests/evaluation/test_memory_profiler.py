import pytest
from src.evaluation.memory_profiler import MemoryProfiler

def test_memory_profiler():
    profiler = MemoryProfiler()
    mem = profiler.snapshot()
    assert mem > 0
    
    # allocate some memory
    large_list = [0] * (10 ** 6)
    profiler.snapshot()
    
    profiler.compute_metrics(num_candidates=10)
    profile = profiler.get_profile()
    
    assert profile["peak_memory_mb"] >= mem
    assert profile["average_memory_mb"] > 0
    assert profile["memory_per_candidate"] > 0
