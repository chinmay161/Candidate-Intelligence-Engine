import time
import tracemalloc
from pathlib import Path
import json

import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from submission.pipeline_config import PipelineConfig
from submission.pipeline_runner import PipelineRunner


def run_benchmark():
    tracemalloc.start()
    start_time = time.time()

    config = PipelineConfig(
        top_k=100,
        enable_audit_log=True,
        enable_reports=True,
        output_dir="benchmark_outputs",
        jd_path="data/sample_jd.txt",
        candidates_path="data/benchmark_candidates.jsonl",
    )

    runner = PipelineRunner(config)
    result = runner.run()

    end_time = time.time()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime = end_time - start_time
    peak_mb = peak / 10**6

    print("\nBenchmark Results:")
    print(f"Total Runtime: {runtime:.2f} seconds")
    print(f"Peak Memory: {peak_mb:.2f} MB")

    if not result.success:
        print("\nPipeline Failed!")
        print(result.errors)
    else:
        print("\nSuccess! Outputs written to benchmark_outputs/")
        with open("benchmark_results.json", "w") as f:
            json.dump(
                {
                    "candidate_count": 100000,
                    "total_runtime_seconds": runtime,
                    "peak_memory_mb": peak_mb,
                },
                f,
                indent=2,
            )


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "src"))
    run_benchmark()
