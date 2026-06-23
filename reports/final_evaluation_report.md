# Final Evaluation Report

## Performance
- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)

### Runtime Profile
- **jd_parsing_time**: 0.01s
- **candidate_parsing_time**: 0.00s
- **feature_extraction_time**: 38.43s
- **matching_time**: 0.00s
- **ranking_time**: 43.29s
- **reasoning_time**: 7.63s
- **submission_time**: 0.00s
- **Total Runtime**: 89.37s

### Memory Profile
- **Peak Memory**: 301.02 MB
- **Average Memory**: 190.14 MB
- **Memory per Candidate**: 0.0030 MB

## Scalability
| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |
|-------|-------------|-------------|----------------------|
| 1000 | 4.28 | 280.45 | 233.75 |
| 10000 | 12.47 | 297.99 | 802.15 |
| 50000 | 51.49 | 316.39 | 971.12 |
| 100000 | 89.08 | 316.39 | 1122.55 |

## Explainability & Robustness
- **Score Range**: 38.33 - 100.00
- **Score Variance**: 201.5957
- **Duplicate Score Rate**: 0.00%
- **Penalty Rate (Honeypot/Anomalies)**: 89.00%

## Ablation Studies
| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |
|---------------|-------------|------------------|-------------------|
| full_system | 4.33 | 0.90 | High |
| no_behavioral_signals | 4.27 | 0.75 | High |
| no_honeypot_detection | 4.24 | 0.90 | High |
| no_reasoning_layer | 4.27 | 0.90 | None |
| semantic_only | 4.23 | 0.75 | High |

## Optimization Summary
**Largest Bottleneck**: ranking_time (48.44%)

### Recommendations
Please refer to `optimization_report.md` for deterministic recommendations to reduce the runtime toward the target benchmark without degrading explainability and ranking quality.