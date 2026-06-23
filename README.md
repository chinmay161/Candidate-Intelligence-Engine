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
