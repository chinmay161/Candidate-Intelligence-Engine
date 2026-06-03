import json
import time
from typing import Dict, Any, Callable
from pathlib import Path


class BenchmarkRunner:
    """
    Runs scale benchmarks on the pipeline and records runtime, memory, and throughput.
    """

    def __init__(self, scales: list[int] = None):
        self.scales = scales or [1000, 10000, 50000, 100000]

    def run(self, pipeline_func: Callable[[int], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the pipeline with varying numbers of candidates.
        pipeline_func should accept the number of candidates as an integer,
        run the pipeline, and optionally return memory peak and runtime inside a dict.
        """
        results = {}

        for scale in self.scales:
            start_time = time.perf_counter()
            
            # The pipeline should handle the memory profiling internally or return it.
            # If not provided, we calculate standard runtime.
            pipeline_result = pipeline_func(scale)
            
            runtime = time.perf_counter() - start_time
            # override with pipeline runtime if provided
            runtime = pipeline_result.get("runtime", runtime)
            memory = pipeline_result.get("memory_mb", 0.0)
            
            throughput = scale / runtime if runtime > 0 else 0.0

            results[str(scale)] = {
                "runtime": round(runtime, 2),
                "memory": round(memory, 2),
                "throughput": round(throughput, 2)
            }

        return results

    def save_report(self, results: Dict[str, Any], output_dir: str = "reports/benchmarks") -> str:
        """Saves the benchmark results to a JSON file."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_dir) / "benchmark_report.json"

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        return str(output_path)
