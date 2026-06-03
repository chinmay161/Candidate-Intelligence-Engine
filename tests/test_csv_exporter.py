import csv

from submission.csv_exporter import CSVExporter
from submission.submission_models import SubmissionFile, SubmissionMetadata, SubmissionRow


def test_csv_exporter(tmp_path):
    rows = (
        SubmissionRow("C1", 1, 0.9, "Reason 1"),
        SubmissionRow("C2", 2, 0.8, "Reason 2"),
    )
    metadata = SubmissionMetadata(2, 2, 1.0)
    sub = SubmissionFile(rows, metadata)

    out_file = tmp_path / "out.csv"
    CSVExporter.export(sub, out_file)

    assert out_file.exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["candidate_id", "rank", "score", "reasoning"]
        
        row1 = next(reader)
        assert row1 == ["C1", "1", "0.9", "Reason 1"]
        
        row2 = next(reader)
        assert row2 == ["C2", "2", "0.8", "Reason 2"]
