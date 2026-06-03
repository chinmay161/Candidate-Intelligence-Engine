"""Streaming candidate parsing for JSON and JSONL datasets."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from candidate_processor.models import Candidate
from candidate_processor.validators import CandidateValidationError, parse_candidate

logger = logging.getLogger(__name__)


class CandidateParser:
    """Parse candidate records without loading large datasets into memory."""

    def __init__(self, *, strict: bool = False, logger_: logging.Logger | None = None) -> None:
        self.strict = strict
        self.logger = logger_ or logger
        self.malformed_records = 0

    def stream_jsonl(self, path: str | Path) -> Iterator[Candidate]:
        """Yield valid Candidate objects from a JSONL file one line at a time."""

        input_path = Path(path)
        with input_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                    if not isinstance(payload, dict):
                        raise CandidateValidationError("JSONL record must be an object")
                    yield parse_candidate(payload)
                except (json.JSONDecodeError, CandidateValidationError) as exc:
                    self.malformed_records += 1
                    self.logger.warning(
                        "Skipping malformed candidate record",
                        extra={"path": str(input_path), "line_number": line_number, "error": str(exc)},
                    )
                    if self.strict:
                        raise

    def parse_json_array(self, path: str | Path) -> list[Candidate]:
        """Parse a small JSON array file, useful for samples and tests."""

        input_path = Path(path)
        with input_path.open("r", encoding="utf-8") as handle:
            payload: Any = json.load(handle)
        if not isinstance(payload, list):
            raise CandidateValidationError("JSON file must contain a list of candidate objects")
        candidates: list[Candidate] = []
        for index, item in enumerate(payload):
            try:
                if not isinstance(item, dict):
                    raise CandidateValidationError("candidate item must be an object")
                candidates.append(parse_candidate(item))
            except CandidateValidationError as exc:
                self.malformed_records += 1
                self.logger.warning(
                    "Skipping malformed candidate record",
                    extra={"path": str(input_path), "index": index, "error": str(exc)},
                )
                if self.strict:
                    raise
        return candidates

    def stream(self, path: str | Path) -> Iterator[Candidate]:
        """Stream JSONL files or parse JSON arrays based on file extension."""

        input_path = Path(path)
        if input_path.suffix.lower() == ".jsonl":
            yield from self.stream_jsonl(input_path)
            return
        yield from self.parse_json_array(input_path)
