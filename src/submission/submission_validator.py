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

        unique_scores = len(set(r.score for r in rows))
        unique_reasonings = len(set(r.reasoning for r in rows))
        
        if unique_scores < 20 and len(rows) >= 20:
            errors.append(f"Score diversity collapsed: only {unique_scores} unique scores in {len(rows)} candidates.")
            
        if unique_reasonings < 10 and len(rows) >= 10:
            errors.append(f"Reasoning diversity collapsed: only {unique_reasonings} unique explanations in {len(rows)} candidates.")
            
        top10_missing = 0
        for row in rows[:10]:
            if "missing required JD requirements:" in row.reasoning.lower():
                # Count commas + 1 or just check if the phrase exists. We will just count if they have missing skills.
                top10_missing += 1
                
        if top10_missing > 3:
            warnings.append(f"Top candidates missing core skills: {top10_missing} of Top 10 are missing required JD skills.")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )
