# Candidate Intelligence Engine

Intelligent Candidate Discovery & Ranking Engine built for the Redrob Hackathon v4.

The system streams, parses, ranks, and explains candidate-job matches under strict production-style constraints:

* CPU only
* Offline execution
* No external APIs
* Deterministic output
* Scalable to 100,000 candidate profiles

---

# Overview

The Candidate Intelligence Engine is an explainable ranking system that identifies the Top-100 candidates for a target Job Description (JD).

The pipeline combines:

* Structured feature extraction
* Retrieval and ranking signals
* Candidate anomaly detection
* Deterministic scoring
* Evidence-backed reasoning generation

The output is a submission-ready CSV containing:

* candidate_id
* rank
* score
* reasoning

---

# Dataset

The official Redrob candidate dataset is intentionally excluded from this repository due to its size.

Place the provided competition dataset at:

```text
data/candidates.jsonl
```

before running the ranking pipeline.

---

# Compute Compliance

The ranking stage is designed to satisfy the Redrob evaluation constraints.

| Constraint     | Status            |
| -------------- | ----------------- |
| CPU Only       | ✅                 |
| Network Access | ❌ Not Required    |
| External APIs  | ❌ None            |
| Runtime Limit  | ✅ Under 5 Minutes |
| Memory Limit   | ✅ Under 16 GB     |

Measured on the full 100,000-candidate dataset:

| Metric         | Value       |
| -------------- | ----------- |
| Runtime        | ~91.58 seconds |
| Peak Memory    | ~302.96 MB     |
| Average Memory | ~191.22 MB     |

---

# Single-Command Reproduction

Generate the submission CSV using:

```bash
python rank.py \
  --candidates data/candidates.jsonl \
  --out submission.csv
```

Optional parameters:

```bash
--jd data/job_description.txt
```

Output:

```text
submission.csv
```

---

# Reproducibility

The ranking pipeline is fully deterministic.

Running the same command with:

* the same candidate dataset
* the same job description
* the same code revision

will always produce identical:

* rankings
* scores
* reasoning strings
* submission CSV output

Determinism is verified using:

```bash
python scripts/verify_determinism.py
```

---

# Architecture

```text
Job Description
      │
      ▼
JD Parser
      │
      ▼
Candidate Stream
      │
      ▼
Feature Extraction
      │
      ▼
Anomaly Detection
      │
      ▼
Scoring Engine
      │
      ▼
Top-100 Selection
      │
      ▼
Reasoning Generator
      │
      ▼
Submission CSV
```

---

# Repository Structure

```text
Candidate-Intelligence-Engine/
│
├── src/
│   ├── candidate_processor/
│   ├── jd_parser/
│   ├── ranking/
│   ├── reasoning/
│   └── submission/
│
├── tests/
├── scripts/
├── reports/
├── sample_data/
│
├── requirements.txt
├── submission_metadata.yaml
├── rank.py
└── README.md
```

---

# Design Highlights

## Offline Ranking

The entire ranking pipeline executes locally without external services.

No hosted LLM APIs, cloud inference, or network requests are required during ranking.

---

## Candidate Anomaly Detection

The anomaly detection layer identifies inconsistent or suspicious profile signals, including:

* Impossible employment timelines
* Multi-current-role conflicts
* Skill-experience mismatches
* Excessive keyword stuffing
* Contradictory profile information

Detected issues are incorporated into candidate scoring through deterministic penalties.

---

## Explainable Reasoning Layer

The reasoning engine generates evidence-backed candidate justifications using:

* Candidate experience
* Current role
* Technical skills
* Behavioral signals
* Availability indicators
* Ranking concerns

Characteristics:

* Deterministic output
* Approximately 98% reasoning uniqueness
* Rank-aware tone
* Candidate-specific evidence
* No external language models

Designed specifically for Stage 4 manual review requirements.

---

# Setup & Installation

## Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
.\venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running Tests

Run the complete test suite:

```bash
pytest
```

Windows PowerShell:

```bash
$env:PYTHONPATH="."
pytest
```

Linux/macOS:

```bash
export PYTHONPATH="."
pytest
```

---

# Sandbox & Docker Reproduction

Build:

```bash
docker build -t candidate-ranker .
```

Run:

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/outputs:/app/outputs" \
  candidate-ranker \
  --candidates data/candidates.jsonl \
  --out outputs/submission.csv
```

---

# Evaluation & Diagnostic Metrics

The repository includes diagnostic reports used to evaluate performance, scalability, explainability, and reproducibility.

## Runtime Metrics

* `jd_parsing_time`
* `candidate_parsing_time`
* `feature_extraction_time`
* `matching_time`
* `ranking_time`
* `reasoning_time`
* `submission_time`
* `total_runtime`

These metrics quantify end-to-end execution cost.

---

## Memory Metrics

* `peak_memory`
* `average_memory`
* `memory_per_candidate`

Used to validate memory efficiency and sandbox compliance.

---

## Scalability Metrics

* Dataset scale
* Throughput (candidates/sec)

Measured across multiple dataset sizes up to 100,000 candidates.

---

## Explainability Metrics

### Score Range

Minimum and maximum scores assigned within the Top-100 ranking.

### Score Variance

Variance of ranking scores. Higher variance indicates greater separation between candidates and stronger ranking distinctions.

### Duplicate Score Rate

Percentage of identical scores among Top-100 candidates.

The system resolves ties deterministically to ensure stable rankings.

### Candidate Warning Rate

Percentage of Top-100 candidates receiving at least one medium/high ranking penalty such as:

* Long notice periods
* Consulting-heavy career history
* Salary inconsistencies
* Profile quality warnings

This metric is not the competition honeypot rate and does not indicate synthetic trap candidates.

---

## Ablation Metrics

### Diversity Metric

Measures candidate diversity across ranking configurations.

### Reasoning Quality

Measures whether evidence-backed candidate explanations are successfully generated.

---

# Submission Metadata

All portal metadata is maintained in:

```text
submission_metadata.yaml
```


---

# License

This repository was developed for the Redrob Hackathon v4 candidate ranking challenge.
