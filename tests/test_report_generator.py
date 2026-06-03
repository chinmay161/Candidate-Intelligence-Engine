import json

import pytest

from reasoning.reasoning_models import CandidateRecommendation
from submission.report_generator import ReportGenerator
from submission.submission_models import SubmissionFile, SubmissionMetadata, SubmissionRow


def test_report_generator(tmp_path):
    rows = (
        SubmissionRow("C1", 1, 0.9, "Reason one has enough words to count"),
        SubmissionRow("C2", 2, 0.8, "Reason two has enough words to count"),
    )
    metadata = SubmissionMetadata(2, 2, 1.0)
    sub = SubmissionFile(rows, metadata)

    recs = [
        CandidateRecommendation("C1", 1, 0.9, "Reason one has enough words to count", 0.95),
        CandidateRecommendation("C2", 2, 0.8, "Reason two has enough words to count", 0.85),
    ]

    out_file = tmp_path / "report.json"
    ReportGenerator.generate(sub, recs, out_file)

    assert out_file.exists()
    with open(out_file, "r") as f:
        data = json.load(f)

    assert data["ranking_metrics"]["top_k_selected"] == 2
    assert data["quality_metrics"]["average_score"] == pytest.approx(0.85)
