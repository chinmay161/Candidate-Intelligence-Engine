# Optimization Recommendations

**Largest Bottleneck**: ranking_time consumes 48.53% of total runtime.

## Targeted Recommendations

Consider:
- Minimizing unnecessary sorting
- Avoiding repeated score calculations
- Utilizing min/max heaps for Top-K extraction

## General Recommendations
- Memory: If peak memory is high, consider generator expressions instead of list comprehensions.
- I/O Bound: Use async I/O or batching for external calls.