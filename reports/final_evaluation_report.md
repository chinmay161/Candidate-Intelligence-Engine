# Final Evaluation Report

## Performance
- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)

### Runtime Profile
- **jd_parsing_time**: 0.02s
- **candidate_parsing_time**: 12.67s
- **feature_extraction_time**: 254.59s
- **matching_time**: 0.00s
- **ranking_time**: 353.17s
- **reasoning_time**: 0.02s
- **submission_time**: 0.00s
- **Total Runtime**: 365.88s

### Memory Profile
- **Peak Memory**: 3353.09 MB
- **Average Memory**: 1993.40 MB
- **Memory per Candidate**: 0.0335 MB

## Scalability
| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |
|-------|-------------|-------------|----------------------|
| 1000 | 9.07 | 12.38 | 110.25 |
| 10000 | 111.41 | 429.37 | 89.76 |
| 50000 | 450.75 | 1286.73 | 110.93 |
| 100000 | 932.99 | 1801.88 | 107.18 |

## Explainability & Robustness
- **Score Range**: 0.00 - 100.00
- **Score Variance**: 526.2563
- **Duplicate Score Rate**: 1.00%
- **Penalty Rate (Honeypot/Anomalies)**: 0.00%

## Ablation Studies
| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |
|---------------|-------------|------------------|-------------------|
| full_system | 4.00 | 0.90 | High |
| no_behavioral_signals | 3.12 | 0.75 | High |
| no_honeypot_detection | 3.06 | 0.90 | High |
| no_reasoning_layer | 3.02 | 0.90 | None |
| semantic_only | 3.00 | 0.75 | High |

## Optimization Summary
**Largest Bottleneck**: ranking_time (96.53%)

### Recommendations
Please refer to `optimization_report.md` for deterministic recommendations to reduce the runtime toward the target benchmark without degrading explainability and ranking quality.