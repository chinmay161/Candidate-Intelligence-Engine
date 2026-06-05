# Optimization Recommendations

**Largest Bottleneck**: feature_extraction_time consumes 83.26% of total runtime.

## Targeted Recommendations

Consider:
- Caching (e.g., standardizing text once and reusing)
- Vectorization of operations across candidates
- Compiled regex (using `re.compile` at module level)
- Lazy evaluation of expensive features

## General Recommendations
- Memory: If peak memory is high, consider generator expressions instead of list comprehensions.
- I/O Bound: Use async I/O or batching for external calls.