"""Persistence layer for extracted candidate features."""

from __future__ import annotations

import csv
import json
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from candidate_processor.constants import FEATURE_COLUMNS
from candidate_processor.models import CandidateFeatureRecord

logger = logging.getLogger(__name__)


class CandidateFeatureStore:
    """Save and load nested candidate feature records."""

    def __init__(self, *, logger_: logging.Logger | None = None) -> None:
        self.logger = logger_ or logger

    def save_csv(self, records: Iterable[CandidateFeatureRecord], path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(FEATURE_COLUMNS))
            writer.writeheader()
            for record in records:
                row = record.to_row()
                writer.writerow({column: _csv_value(row[column]) for column in FEATURE_COLUMNS})
                count += 1
        self.logger.info("Saved candidate features to CSV", extra={"path": str(output_path), "records": count})

    def load_csv(self, path: str | Path) -> list[dict[str, Any]]:
        input_path = Path(path)
        rows: list[dict[str, Any]] = []
        with input_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                parsed = dict(row)
                for column in FEATURE_COLUMNS:
                    if column != "candidate_id" and column in parsed:
                        parsed[column] = json.loads(parsed[column])
                rows.append(parsed)
        return rows

    def save_parquet(self, records: Iterable[CandidateFeatureRecord], path: str | Path) -> None:
        """Save records to Parquet using pandas/pyarrow when available."""

        try:
            import pandas as pd  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Saving Parquet requires pandas and a Parquet engine such as pyarrow.") from exc

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [record.to_row() for record in records]
        frame = pd.DataFrame(rows, columns=list(FEATURE_COLUMNS))
        for column in FEATURE_COLUMNS:
            if column != "candidate_id":
                frame[column] = frame[column].map(lambda value: json.dumps(value, sort_keys=True))
        frame.to_parquet(output_path, index=False)
        self.logger.info("Saved candidate features to Parquet", extra={"path": str(output_path), "records": len(rows)})

    def load_parquet(self, path: str | Path) -> list[dict[str, Any]]:
        try:
            import pandas as pd  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("Loading Parquet requires pandas and a Parquet engine such as pyarrow.") from exc

        frame = pd.read_parquet(Path(path))
        rows = frame.to_dict(orient="records")
        for row in rows:
            for column in FEATURE_COLUMNS:
                if column != "candidate_id" and column in row:
                    row[column] = json.loads(row[column])
        return rows


def _csv_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)
