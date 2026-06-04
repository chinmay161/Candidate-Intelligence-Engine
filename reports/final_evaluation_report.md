# Final Evaluation Report

## Performance
- **Target**: < 300 seconds runtime, < 16 GB memory (100,000 candidates)

### Runtime Profile
- **jd_parsing_time**: 0.02s
- **candidate_parsing_time**: 13.24s
- **feature_extraction_time**: 255.83s
- **matching_time**: 0.00s
- **ranking_time**: 284.24s
- **reasoning_time**: 0.02s
- **submission_time**: 0.00s
- **Total Runtime**: 297.52s

### Memory Profile
- **Peak Memory**: 3303.95 MB
- **Average Memory**: 1969.03 MB
- **Memory per Candidate**: 0.0330 MB

## Scalability
| Scale | Runtime (s) | Memory (MB) | Throughput (cands/s) |
|-------|-------------|-------------|----------------------|
| 1000 | 8.3 | 12.48 | 120.42 |
| 10000 | 89.74 | 403.31 | 111.43 |
| 50000 | 405.47 | 1412.74 | 123.31 |
| 100000 | 851.66 | 1912.88 | 117.42 |

## Explainability & Robustness
- **Score Range**: 0.00 - 100.00
- **Score Variance**: 526.2563
- **Duplicate Score Rate**: 1.00%
- **Penalty Rate (Honeypot/Anomalies)**: 92.35%

### Penalty Distribution (Sample: 5,000 candidates)
- **non-technical current role signal**: 51.36%
- **unusual expected salary range**: 44.56%
- **demo-only framework language**: 30.82%
- **90 day notice period**: 29.62%
- **behavioral inconsistency score**: 21.60%
- **recent non-hands-on role**: 10.08%
- **title description mismatch**: 9.60%

## Ablation Studies
| Configuration | Runtime (s) | Diversity Metric | Reasoning Quality |
|---------------|-------------|------------------|-------------------|
| full_system | 3.87 | 0.90 | High |
| no_behavioral_signals | 2.91 | 0.75 | High |
| no_honeypot_detection | 2.87 | 0.90 | High |
| no_reasoning_layer | 2.90 | 0.90 | None |
| semantic_only | 2.79 | 0.75 | High |

## Optimization Summary
**Largest Bottleneck**: ranking_time (95.54%)

### Recommendations
Please refer to `optimization_report.md` for deterministic recommendations to reduce the runtime toward the target benchmark without degrading explainability and ranking quality.