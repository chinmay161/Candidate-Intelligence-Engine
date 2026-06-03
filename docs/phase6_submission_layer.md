# Phase 6: Submission & Orchestration Layer

## Overview
The Submission Layer orchestrates the `Candidate Intelligence Engine` pipelines (JD Processing -> Candidate Feature Extraction -> Ranking -> Reasoning) into a single deterministic workflow. The system produces a competition-ready CSV submission alongside comprehensive JSON audit logs and evaluation reports.

## Architecture

```text
src/submission/
├── submission_models.py     # Immutable dataclasses representing outputs
├── submission_builder.py    # Generates a valid Top-K SubmissionFile
├── submission_validator.py  # Checks integrity (ranks, scores, limits)
├── csv_exporter.py          # Deterministic CSV output generator
├── report_generator.py      # Produces evaluation_report.json
├── audit_logger.py          # Captures explainability metadata
├── pipeline_runner.py       # Orchestrates the execution sequence
├── pipeline_config.py       # YAML configuration schema
└── cli.py                   # Argument parser and application entry
```

## Pipeline Flow
1. **Config Load**: `PipelineConfig` parses `default_config.yaml` or CLI arguments.
2. **JD Processing**: `JDParser` evaluates the raw job description string to an analysis object.
3. **Candidate Streaming**: JSONL candidate files are streamed to avoid OOM errors for large datasets (e.g., 100k+ rows).
4. **Ranking Orchestration**: `Ranker` is utilized (with optional `PreRankRetriever`) to filter the candidates to the `top_k`.
5. **Explainable Reasoning**: `ReasoningGenerator` emits deterministic, evidence-backed explanations for each `CandidateMatch`.
6. **Integrity Validation**: `SubmissionValidator` enforces that output data abides strictly by competition requirements.
7. **Export**: CSV, Audit JSON, and Report JSON are serialized.

## Usage

```bash
python generate_submission.py \
    --jd data/jd.txt \
    --candidates data/candidates.jsonl \
    --config configs/default_config.yaml
```

## Output Formats

### submission.csv
| candidate_id | rank | score | reasoning |
|--------------|------|-------|-----------|
| C123         | 1    | 0.95  | ...       |

### evaluation_report.json
Metrics on runtime, unique reasoning counts, rank score distribution, and configuration flags.

### audit_log.json
Detailed tracking of the features, ML match probabilities, penalties, and explicit strengths that factored into the `rank`.

## Validation Rules
- **Exactly N rows**: Bounded to `--top-k` configured value (default 100).
- **Descending Scores**: Row $i$ score $\ge$ Row $i+1$ score.
- **Unique Ranks**: No ties allowed. Ties are deterministically resolved via internal heuristics / sorting by candidate ID.
- **Reasoning**: Strings cannot be blank, under 10 words, or over 1000 words.
