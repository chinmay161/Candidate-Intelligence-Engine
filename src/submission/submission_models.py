"""Immutable dataclasses for the submission layer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SubmissionRow:
    """A single row in the final submission file."""

    candidate_id: str
    rank: int
    score: float
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "reasoning": self.reasoning,
        }


@dataclass(frozen=True, slots=True)
class SubmissionMetadata:
    """Metadata about the pipeline run that generated the submission."""

    total_candidates_processed: int
    top_k: int
    pipeline_runtime_seconds: float
    memory_usage_mb: float | None = None


@dataclass(frozen=True, slots=True)
class SubmissionFile:
    """The complete structured submission."""

    rows: tuple[SubmissionRow, ...]
    metadata: SubmissionMetadata


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of validating a submission."""

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Result of running the full ranking pipeline."""

    success: bool
    submission_path: str | None = None
    report_path: str | None = None
    audit_path: str | None = None
    errors: tuple[str, ...] = ()
