# Phase 4 Matching Engine

## Scope

Phase 4 converts a structured `JDAnalysis` and one or more `CandidateFeatureRecord` objects into explainable candidate ranking scores. It does not generate recruiter-facing reasoning and does not create final CSV submissions.

## Architecture

```text
JDAnalysis + CandidateFeatureRecord
    |
    v
PreRankRetriever
    |
    v
SemanticMatcher
    |
    v
FeatureMatcher
    |
    v
PenaltyEngine
    |
    v
ScoreCalculator + ContributionTracker
    |
    v
CandidateScorer
    |
    v
Ranker + TopKSelector + ScoreNormalizer
    |
    v
RankingResult
```

The package lives in `src/ranking/` and exposes the main entry points from `ranking.__init__`.

## Pre-Rank Retrieval

For large pools, the ranker supports a low-cost retrieval stage before full scoring:

```text
100,000 candidates
    |
    v
Fast retrieval
    |
    v
Top 5,000 shortlist
    |
    v
Full scoring engine
    |
    v
Top 100 ranked candidates
```

`PreRankRetriever` is the base interface. The concrete retrievers are:

- `BM25Retriever`: lexical candidate evidence and active feature token retrieval
- `TFIDFRetriever`: normalized query/candidate term overlap
- `HybridRetriever`: BM25 + TF-IDF + cheap JD-weighted feature hint

`Ranker.rank()` uses `HybridRetriever` by default when `top_k` is set and `pre_rank_limit` is not `None`:

```python
result = Ranker().rank(
    analysis,
    candidate_feature_records,
    top_k=100,
    pre_rank_limit=5_000,
)
```

Set `pre_rank_limit=None` to score every candidate with the full engine.

## Scoring Flow

`SemanticMatcher` computes a deterministic 0-1 alignment score from semantic features, role fit, skill overlap, and evidence density. It uses no LLM calls.

`FeatureMatcher` evaluates structured JD requirements: required skills, preferred skills, experience, location, industry, and behavioral preferences. It emits a `FeatureMatchResult` with `matched_requirements`, `missing_requirements`, and per-requirement scores.

`PenaltyEngine` turns suspicious-profile and negative-fit features into bounded deductions. It handles feature penalties such as `honeypot_score`, `services_only_penalty`, `research_only_phd_penalty`, `management_only_recent_penalty`, and inferred logistics penalties such as inactive candidates and 90-day notice periods.

`ScoreCalculator` combines:

- semantic score
- requirement match score
- JD-weighted candidate feature score
- penalty score

The output is a `ScoringBreakdown` with raw score, final score, penalty score, and feature-group scores.

## Contribution Tracking

`ContributionTracker` records every JD-weighted feature that participates in scoring:

```python
FeatureContribution(
    feature="retrieval_skill_depth",
    group="skill",
    weight=0.034,
    raw_value=0.91,
    contribution=0.03094,
    reason="Required skill: retrieval systems",
    evidence=("Semantic search and embeddings...",),
)
```

Composite components are also recorded:

- `semantic_alignment`
- `requirement_match_score`
- `weighted_candidate_feature_score`
- `penalty_score`

Penalty feature contributions are signed negative. These machine-readable records are intended to power Phase 5 reasoning without producing recruiter-facing prose in Phase 4.

## Ranking Process

`CandidateScorer` scores one candidate and returns:

```python
CandidateMatch(
    candidate_id,
    score,
    confidence,
    feature_contributions,
    matched_requirements,
    penalties,
)
```

`Ranker.rank()` accepts an iterable of `CandidateFeatureRecord`s, optionally retrieves a shortlist, scores shortlisted candidates deterministically, selects the requested top-k set, normalizes selected scores to 0-100, and returns a `RankingResult`.

Sorting is descending and stable. Ties preserve input order.

## Performance Strategy

The implementation is CPU-only and streaming-friendly at the component level:

- scoring uses dictionary lookups over precomputed features
- no model calls, embedding calls, or network calls occur
- `PreRankRetriever` uses `heapq` to shortlist the top 5,000 candidates before full scoring
- `TopKSelector` uses `heapq` to avoid sorting the full scored shortlist when only the top 100 are needed
- dataclasses use slots where practical to reduce per-object overhead
- ranking output stores only selected normalized matches when `top_k` is supplied

For 100,000 candidates, the expected path is:

```python
result = Ranker().rank(analysis, candidate_feature_records, top_k=100)
```

With the default pre-rank path, cheap retrieval scans all candidates and full scoring only runs on the shortlisted candidates. This keeps expensive work bounded by `pre_rank_limit` and keeps selection work at `O(n log k)`.
