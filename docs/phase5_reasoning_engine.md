# Phase 5 Reasoning Engine

## Scope

Phase 5 converts ranked `CandidateMatch` objects and stored `CandidateFeatureRecord` evidence into concise recruiter-facing explanations. It is deterministic, CPU-only, and does not call LLMs or external APIs.

The engine explains why a candidate was ranked highly, while also surfacing grounded concerns such as missing requirements, notice-period risk, suspicious-profile signals, or limited production evidence.

## Architecture

```text
JDAnalysis + CandidateMatch + CandidateFeatureRecord
    |
    v
EvidenceSelector
    |
    v
StrengthDetector
    |
    v
ConcernDetector
    |
    v
ReasoningTemplates
    |
    v
ReasoningConfidenceEstimator
    |
    v
ReasoningGenerator
    |
    v
RecommendationBuilder
    |
    v
CandidateRecommendation
```

The package lives in `src/reasoning/`:

- `reasoning_models.py`: immutable serializable dataclasses
- `evidence_selector.py`: top evidence selection from ranking contributions and stored snippets
- `strength_detector.py`: positive signal detection
- `concern_detector.py`: penalty, anomaly, and missing requirement detection
- `reasoning_templates.py`: deterministic recruiter-facing prose
- `confidence_estimator.py`: explanation confidence scoring
- `reasoning_generator.py`: end-to-end reasoning pipeline
- `recommendation_builder.py`: final ranked recommendation packaging

## Reasoning Flow

`EvidenceSelector` first selects up to five evidence items. It prioritizes:

```text
production_ir_evidence_score
ranking_eval_phrase_score
retrieval_skill_depth
role_family_fit_score
availability_multiplier
```

Only evidence with stored snippets is used for primary positive reasoning. This prevents unsupported praise and keeps explanations traceable.

`StrengthDetector` then emits `CandidateStrength` records when the relevant candidate feature crosses a deterministic threshold and evidence exists. Example strength categories include production systems, retrieval depth, evaluation frameworks, role fit, availability, product background, and ownership.

`ConcernDetector` emits `CandidateConcern` records from:

- `CandidateMatch.penalties`
- `CandidateMatch.missing_requirements`
- anomaly features such as `honeypot_score`
- low production evidence when the JD requires production ranking or retrieval experience

`ReasoningTemplates` converts strengths and concerns into professional language. The target output is 40-80 words for normal ranked candidates, with shorter explanations allowed when the ranking output contains limited support.

## Evidence Traceability

Every strength and concern stores supporting `ReasoningEvidence`:

```python
ReasoningEvidence(
    feature="retrieval_skill_depth",
    group="skill",
    description="retrieval, embedding, and vector-search skill depth",
    contribution=0.031,
    raw_value=0.92,
    snippets=("Semantic search, embeddings, Pinecone, Elasticsearch.",),
)
```

The final `ReasoningResult` keeps the rendered prose plus the full evidence, strength, and concern payload. Downstream UI or audit tooling can inspect exactly which feature and snippet supported each statement.

## Confidence Estimation

`ReasoningConfidenceEstimator` returns a deterministic 0.0-1.0 confidence score. It combines:

- evidence quality: snippets plus contribution strength
- evidence coverage: how many of the top five evidence slots are filled
- feature support: number of evidence-backed strengths
- ranking confidence from `CandidateMatch`
- anomaly level from candidate anomaly features
- unresolved medium or high severity concerns

High confidence means the generated prose is well supported by stored candidate evidence. It does not mean the candidate is guaranteed to be a good hire.

## Example

```text
Strong match due to production retrieval and ranking systems, ranking and retrieval evaluation frameworks, and retrieval, embedding, and vector-search depth. Also demonstrates strong retrieval role-family alignment and coverage of multiple required JD skills. Candidate also shows strong recruiter engagement and recent activity. Potential concern: longer-than-average notice period.
```

This explanation is deterministic and grounded in feature evidence, matched requirements, and explicit match penalties.

## Usage

```python
from reasoning import ReasoningGenerator, RecommendationBuilder

reasoning = ReasoningGenerator().generate(analysis, match, candidate_record)
recommendation = RecommendationBuilder().build(
    rank=1,
    match=match,
    reasoning=reasoning,
)
```

The resulting object is serializable:

```python
payload = recommendation.to_dict()
```

## Performance

The engine uses dictionary lookups, simple sorting over scored features, and small bounded lists. For top-100 ranked candidates, the reasoning pass is bounded by the number of already selected matches and is designed to run in well under 10 seconds on CPU.
