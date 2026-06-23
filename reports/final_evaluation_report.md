# Final Evaluation Report

## Performance
- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)

### Runtime Profile
- **jd_parsing_time**: 0.02s
- **candidate_parsing_time**: 0.00s
- **feature_extraction_time**: 39.40s
- **matching_time**: 0.00s
- **ranking_time**: 44.44s
- **reasoning_time**: 7.72s
- **submission_time**: 0.00s
- **Total Runtime**: 91.58s

### Memory Profile
- **Peak Memory**: 302.96 MB
- **Average Memory**: 191.22 MB
- **Memory per Candidate**: 0.0030 MB

## Scalability
| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |
|-------|-------------|-------------|----------------------|
| 1000 | 4.27 | 252.8 | 234.02 |
| 10000 | 13.55 | 273.76 | 737.77 |
| 50000 | 53.12 | 305.51 | 941.29 |
| 100000 | 99.01 | 333.7 | 1009.96 |

## Explainability & Robustness
- **Score Range**: 38.33 - 100.00
- **Score Variance**: 201.5957
- **Duplicate Score Rate**: 0.00%
- **Candidate Warning Rate**: 89.00%

## Ablation Studies
| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |
|---------------|-------------|------------------|-------------------|
| full_system | 4.31 | 0.90 | High |
| no_behavioral_signals | 4.21 | 0.75 | High |
| no_honeypot_detection | 4.25 | 0.90 | High |
| no_reasoning_layer | 4.23 | 0.90 | None |
| semantic_only | 4.23 | 0.75 | High |

## Optimization Summary
**Largest Bottleneck**: ranking_time (48.53%)

### Recommendations
Please refer to `optimization_report.md` for deterministic recommendations to reduce the runtime toward the target benchmark without degrading explainability and ranking quality.