"""Audit logger to persist explainability metadata."""

import json
from pathlib import Path
from typing import Sequence

from reasoning.reasoning_models import CandidateRecommendation


class AuditLogger:
    """Logs detailed explainability metadata for audits."""

    @staticmethod
    def export(recommendations: Sequence[CandidateRecommendation], output_path: str | Path) -> None:
        """
        Export explainability metadata for recruiters or judges to inspect.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        audit_data = []
        for rec in recommendations:
            audit_entry = {
                "candidate_id": rec.candidate_id,
                "score": rec.score,
                "feature_contributions": [e.to_dict() for e in rec.evidence],
                "matched_requirements": [s.to_dict() for s in rec.strengths],
                "penalties": [c.to_dict() for c in rec.concerns],
                "reasoning_confidence": rec.confidence,
            }
            audit_data.append(audit_entry)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2)
