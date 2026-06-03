"""Validates the integrity of a submission file."""

from submission.submission_models import SubmissionFile, ValidationResult


class SubmissionValidator:
    """Validates submission integrity before export."""

    @staticmethod
    def validate(submission: SubmissionFile, expected_top_k: int = 100) -> ValidationResult:
        """
        Perform all integrity checks on the submission.
        - Structure (exact row count)
        - Rank integrity
        - Candidate integrity
        - Score integrity
        - Reasoning integrity
        """
        errors = []
        warnings = []

        rows = submission.rows

        # 1. Structure
        if len(rows) != expected_top_k:
            errors.append(f"Expected exactly {expected_top_k} rows, found {len(rows)}")

        # 2-5. Iterative Integrity Checks
        seen_ranks = set()
        seen_candidates = set()
        prev_score = float("inf")

        for i, row in enumerate(rows):
            # 2. Rank Integrity
            if row.rank in seen_ranks:
                errors.append(f"Duplicate rank found: {row.rank}")
            if row.rank != i + 1:
                errors.append(f"Rank sequence error at row {i+1}: expected {i+1}, got {row.rank}")
            seen_ranks.add(row.rank)

            # 3. Candidate Integrity
            if row.candidate_id in seen_candidates:
                errors.append(f"Duplicate candidate_id found: {row.candidate_id}")
            seen_candidates.add(row.candidate_id)

            # 4. Score Integrity
            if row.score > prev_score:
                errors.append(f"Score ordering error at rank {row.rank}: {row.score} > {prev_score}")
            prev_score = row.score

            # 5. Reasoning Integrity
            if not row.reasoning or not row.reasoning.strip():
                errors.append(f"Empty reasoning at rank {row.rank} for candidate {row.candidate_id}")
            else:
                words = len(row.reasoning.split())
                if words < 10:
                    errors.append(f"Reasoning too short at rank {row.rank}: {words} words")
                if words > 1000:
                    errors.append(f"Reasoning too long at rank {row.rank}: {words} words")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
