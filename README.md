# Candidate Intelligence Engine

Intelligent Candidate Discovery & Ranking Engine designed for the Redrob Hackathon v4. 
It streams, parses, processes, ranks, and generates explainable reasoning for candidates against a job description under offline CPU-only constraints.

---

## 🚀 Single-Command Reproduction

To generate the submission CSV from the candidate pool, run the following command from the root of the repository:

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
```

### Options:
*   `--candidates`: Path to the candidate JSONL database (e.g., `data/candidates.jsonl`).
*   `--out`: Target path where the output ranking CSV will be saved (e.g., `./submission.csv`).
*   `--jd`: (Optional) Path to the job description text file. Defaults to `data/job_description.txt`.

---

## 📦 Sandbox & Docker Reproduction

If you wish to test or reproduce the results in an isolated sandbox matching the hackathon CPU and memory limits:

### 1. Build the Docker image:
```bash
docker build -t candidate-ranker .
```

### 2. Run the ranker container:
Mount your local data directory and produce the submission:
```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/outputs:/app/outputs" \
  candidate-ranker --candidates data/candidates.jsonl --out outputs/submission.csv
```

---

## 🛠️ Setup & Installation

### Local Virtual Environment:
Ensure you have Python 3.12+ installed.

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Run the complete performance & diagnostics suite:
   ```bash
   python run_evaluations.py
   ```

---

## 🧪 Running Tests

The test suite validates features, scorers, validators, retrievers, and anomaly detection. Run the suite using `pytest`:

```bash
$env:PYTHONPATH="." # On Windows PowerShell
# OR export PYTHONPATH="." (On Linux/macOS)
pytest
```

---

## 🏗️ Architecture

```text
src/
├── candidate_processor/   # Streams JSONL candidates & extracts structured features (semantics, skills, career, logistics, anomalies)
├── jd_parser/             # Parses the target Job Description to extract roles, skills, and generate feature weights
├── ranking/               # Pre-filters candidates, normalizes signals, scores candidates, and handles honeypot/trap penalization
├── reasoning/             # Explains candidates' strengths/concerns and outputs structured human-readable justification
└── submission/            # Enforces integrity checks (duplicate detection, score ordering, word limit validation) and exports CSV
```

### Design Highlights:
*   **Zero-Dependency Offline Ranking**: Fully offline, CPU-bound ranking that scales efficiently to 100K candidate pools (completing in ~97 seconds, using <320 MB peak memory).
*   **Trap & Honeypot Protection**: The `AnomalyDetector` identifies impossible profile signals (such as negative durations, multi-current roles, or mismatched skill experience) and penalizes them deterministically, achieving a **0% honeypot leak rate** in the top 100 picks.
*   **Explainable Reasoning Layer**: Emits deterministic, evidence-backed justifications (10-1000 words, >10 unique reasonings across candidate lists) for Stage 4 manual reviews.

---

## 📋 Portal Metadata

All submission metadata is structured inside [submission_metadata.yaml](file:///c:/Users/Chinmay/Desktop/Vs%20Code/Candidate%20Intelligence%20Engine/submission_metadata.yaml) at the repository root. Ensure you mirror this information on the upload portal during final submission.

---

## 📊 Evaluation & Diagnostic Metrics Explained

The diagnostic report in `reports/final_evaluation_report.md` evaluates the performance, throughput, and robustness of the ranking system using the following metrics:

### ⏱️ Runtime Profile Metrics
*   **`jd_parsing_time`**: The wall-clock time required to load and parse the target Job Description (JD) to extract roles, skills, and compute keyword importance weights.
*   **`candidate_parsing_time`**: The initialization overhead of opening the candidate dataset streams.
*   **`feature_extraction_time`**: The CPU time consumed while processing candidate records through multi-process tokenizers and extracting structured features (semantics, skills, experience, anomalies, etc.).
*   **`matching_time`**: The time spent matching parsed JD attributes against structured candidate features.
*   **`ranking_time`**: The time spent scoring the shortlisted candidates, normalizing the scores, resolving score ties deterministically, and selecting the top $K$ matches.
*   **`reasoning_time`**: The time taken to analyze matching details for top-selected candidates and deterministically assemble explanation summaries.
*   **`submission_time`**: The time required to serialize and write the output data rows to the final CSV file.
*   **`Total Runtime`**: The total elapsed execution time from pipeline startup to final output generation.

### 💾 Memory Profile Metrics
*   **`Peak Memory`**: The highest resident memory footprint recorded during pipeline execution (crucial for verifying compliance with the $\le 16$ GB sandbox limit).
*   **`Average Memory`**: The mean memory footprint tracked across snapshots during pipeline processing.
*   **`Memory per Candidate`**: The average memory overhead allocated per candidate record processed (indicates scaling efficiency).

### 📈 Scalability Metrics
*   **`Scale`**: The dataset size (number of candidates) evaluated during scaling trials (ranges from 1,000 to 100,000).
*   **`Throughput (cands/s)`**: The number of candidate profiles parsed, scored, and processed per second.

### 🔍 Explainability & Robustness Metrics
*   **`Score Range`**: The minimum and maximum final scores assigned to candidates within the top 100 list (quantifies the score span).
*   **`Score Variance`**: The statistical variance of the scores assigned in the top 100 list. Higher variance indicates greater score separation between candidates, suggesting the ranker is making stronger distinctions among candidate profiles.
*   **`Duplicate Score Rate`**: The percentage of identical scores in the top 100 list. A rate of `0.0%` is expected as the ranker deterministically resolves score ties to assign unique ranks.
*   **`Candidate Warning Rate`**: Percentage of Top-100 candidates that received at least one medium/high ranking penalty such as notice period, consulting-heavy history, salary inconsistency, or profile-quality warnings. This metric is not the competition honeypot rate and does not indicate synthetic trap candidates.

### 🔬 Ablation Studies Metrics
*   **`Diversity Metric`**: The candidate diversity score across different pipeline configurations (measures the range of unique candidate attributes).
*   **`Reasoning Quality`**: An evaluation rating indicating whether explainable justification was successfully generated for matches.

