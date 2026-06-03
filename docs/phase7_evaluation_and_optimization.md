# Phase 7: Evaluation and Optimization Layer

This document details the Evaluation and Optimization Layer of the Candidate Intelligence Engine. 
The goal of this phase is to provide the tooling required to identify bottlenecks and achieve the performance benchmark of processing 100,000 candidates in under 300 seconds with less than 16 GB of memory.

## Architecture

The evaluation layer is contained in `src/evaluation/` and consists of several decoupled tools:
- **RuntimeProfiler**: Measures execution time of pipeline stages.
- **MemoryProfiler**: Tracks peak and average memory footprint.
- **BottleneckAnalyzer**: Consumes runtime profiles to find the most expensive operations.
- **OptimizationRecommender**: Uses heuristics to suggest actionable optimizations.
- **AblationRunner**: Disables various subsystems (Behavioral Signals, Honeypot, Reasoning, etc.) to measure their impact on both runtime and ranking quality.
- **RankingDiagnostics**: Analyzes the statistical distribution of scores.
- **BenchmarkRunner**: Scales candidate loads (1k, 10k, 50k, 100k) to determine throughput limitations.
- **EvaluationReporter**: Aggregates all data into a comprehensive Markdown report.

## Profiling Methodology
- **Runtime**: Time is measured using `time.perf_counter()` to achieve high resolution. A decorator `@profile_runtime(phase_name)` can be used around critical pipeline functions to automatically log time.
- **Memory**: The `psutil` library is used to capture process memory RSS snapshots at key pipeline boundaries. Peak memory is calculated iteratively.

## Optimization Strategy
The `OptimizationRecommender` will look at the `BottleneckAnalyzer` output. Based on the largest runtime component (e.g., `feature_extraction_time` vs `ranking_time`), it will suggest specific structural changes, such as lazy evaluation, caching, minimizing sorts, or optimizing regexes. 

*Note: The optimization strategy strictly avoids changing core business logic or ranking feature math.*

## Benchmark Methodology
Benchmarks are run deterministically against synthetic datasets of 1k, 10k, 50k, and 100k candidates.
Throughput is calculated as `candidates / total_runtime_seconds`.

## Ablation Methodology
Ablations test the value-add versus the performance cost of various layers:
- **Full System**
- **No Behavioral Signals**
- **No Honeypot Detection**
- **No Reasoning Layer**
- **Semantic Only** (removes structured matching)

By comparing `candidate_diversity` and `runtime` across configurations, we ensure that heavy layers justify their cost.

## Interpretation Guide
- Review `reports/final_evaluation_report.md` for a holistic summary.
- If runtime > 300s, look directly at `reports/optimization_report.md` to see which stage failed.
- If memory > 16GB, investigate stages that hold large dicts/lists simultaneously in memory, primarily during feature extraction or submission serialization.
