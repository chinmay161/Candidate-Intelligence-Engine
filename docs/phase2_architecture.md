# Phase 2 Architecture: Candidate Processing and Feature Extraction

## Scope

Phase 2 converts raw candidate JSON records into structured machine-readable feature records. It does not rank candidates and does not generate recruiter-facing reasoning. The output is designed to feed those later stages with deterministic feature values plus evidence snippets.

## Package Layout

```text
src/
candidate_processor/
|-- constants.py
|-- models.py
|-- validators.py
|-- normalizer.py
|-- parser.py
|-- feature_extractor.py
|-- feature_store.py
`-- __init__.py
```

## Data Flow

```text
candidates.jsonl
    |
    v
CandidateParser
    |
    v
validators.parse_candidate
    |
    v
Candidate dataclasses
    |
    v
CandidateFeatureExtractor
    |-- Semantic features
    |-- Experience features
    |-- Skill features
    |-- Behavioral features
    |-- Career features
    |-- Education features
    |-- Logistics features
    `-- Anomaly features
    |
    v
EvidenceExtractor
    |
    v
CandidateFeatureRecord
    |
    v
CandidateFeatureStore
    |
    +-- candidate_features.csv
    `-- candidate_features.parquet
```

## Parser

`CandidateParser.stream_jsonl()` reads one JSONL line at a time and yields typed `Candidate` objects. Malformed JSON or schema-invalid records are logged and skipped by default; `strict=True` turns those cases into exceptions for tests and diagnostics.

## Validation and Models

The pipeline uses standard-library dataclasses plus explicit validators. This keeps runtime dependencies small while still enforcing schema constraints such as candidate ID format, enum values, numeric ranges, date parsing, and required nested objects.

## Feature Extraction

`CandidateFeatureExtractor` is deterministic and CPU-only. It uses:

- Curated dictionaries in `constants.py`
- Cached text normalization
- Compiled regex term matchers
- Role-window evidence checks
- Lightweight lexical scoring
- Rule-based anomaly and honeypot features

The extractor emits 91 deterministic features across the required output groups:

- `semantic_features`
- `experience_features`
- `skill_features`
- `behavioral_features`
- `career_features`
- `education_features`
- `logistics_features`
- `anomaly_features`

The implementation includes the Phase 1 feature blueprint names and a small number of diagnostic support features used for later quality checks.

## Evidence Layer

`EvidenceExtractor` stores evidence by feature name. Important production, retrieval, ranking, role-fit, skill, anomaly, and availability features receive compact snippets from profile, career history, skills, and Redrob signals. Later reasoning should only use these snippets or directly observed feature values.

## Feature Store

`CandidateFeatureStore` writes nested records to CSV and Parquet-compatible tabular rows:

```text
candidate_id
semantic_features
experience_features
skill_features
behavioral_features
career_features
education_features
logistics_features
anomaly_features
evidence
```

Nested feature groups are JSON-encoded in CSV and Parquet. CSV streaming is memory-light. Parquet uses pandas and a Parquet engine such as pyarrow when installed.

## Performance Considerations

- JSONL parsing streams candidates and does not load the 100,000-record dataset.
- Feature extraction is per-candidate and does not need a global corpus pass.
- Regex patterns are compiled once and cached.
- Text normalization is cached for repeated phrases and dictionary checks.
- No hosted APIs, GPU libraries, or per-candidate language model calls are used.
- The expected runtime profile is linear in candidate count and profile text size, suitable for 100,000+ candidates on CPU under the stated memory budget.
