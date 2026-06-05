# Final Evaluation Report

## Performance
- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)

### Runtime Profile
- **jd_parsing_time**: 0.02s
- **candidate_parsing_time**: 0.00s
- **feature_extraction_time**: 277.42s
- **matching_time**: 0.00s
- **ranking_time**: 47.12s
- **reasoning_time**: 8.65s
- **submission_time**: 0.00s
- **Total Runtime**: 333.21s

### Memory Profile
- **Peak Memory**: 212.37 MB
- **Average Memory**: 137.88 MB
- **Memory per Candidate**: 0.0021 MB

## Scalability
| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |
|-------|-------------|-------------|----------------------|
| 1000 | 4.24 | 156.96 | 235.85 |
| 10000 | 36.52 | 206.21 | 273.8 |
| 50000 | 172.37 | 203.73 | 290.07 |
| 100000 | 316.9 | 205.16 | 315.56 |

## Explainability & Robustness
- **Score Range**: 38.33 - 100.00
- **Score Variance**: 201.5957
- **Duplicate Score Rate**: 0.00%
- **Penalty Rate (Honeypot/Anomalies)**: 89.00%

## Ablation Studies
| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |
|---------------|-------------|------------------|-------------------|
| full_system | 4.27 | 0.90 | High |
| no_behavioral_signals | 4.21 | 0.75 | High |
| no_honeypot_detection | 4.18 | 0.90 | High |
| no_reasoning_layer | 4.18 | 0.90 | None |
| semantic_only | 4.13 | 0.75 | High |

## Optimization Summary
**Largest Bottleneck**: feature_extraction_time (83.26%)

### Recommendations
Please refer to `optimization_report.md` for deterministic recommendations to reduce the runtime toward the target benchmark without degrading explainability and ranking quality.