"""Exports submissions to CSV."""

import csv
from pathlib import Path

from submission.submission_models import SubmissionFile


class CSVExporter:
    """Exports a SubmissionFile to a reproducible CSV format."""

    @staticmethod
    def export(submission: SubmissionFile, output_path: str | Path) -> None:
        """
        Write submission to CSV.
        Requires:
        - UTF-8
        - deterministic column order
        - reproducible output
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Deterministic column order
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])

            for row in submission.rows:
                writer.writerow([
                    row.candidate_id,
                    row.rank,
                    row.score,
                    row.reasoning,
                ])
