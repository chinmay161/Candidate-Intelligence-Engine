import pytest

from submission.submission_models import SubmissionFile, SubmissionMetadata, SubmissionRow
from submission.submission_validator import SubmissionValidator


@pytest.fixture
def valid_rows():
    return tuple(
        SubmissionRow(
            candidate_id=f"C{i}",
            rank=i,
            score=1.0 - (i * 0.001),
            reasoning=f"This is a valid length reasoning string that has more than ten words easily and explains things {i}."
        )
        for i in range(1, 101)
    )


def test_valid_submission(valid_rows):
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(valid_rows, metadata)

    result = SubmissionValidator.validate(sub)
    assert result.is_valid
    assert not result.errors


def test_duplicate_ranks(valid_rows):
    # Make the second row have rank 1
    bad_rows = list(valid_rows)
    bad_rows[1] = SubmissionRow(
        candidate_id="C2", rank=1, score=bad_rows[1].score, reasoning=bad_rows[1].reasoning
    )
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(tuple(bad_rows), metadata)

    result = SubmissionValidator.validate(sub)
    assert not result.is_valid
    assert any("Duplicate rank" in e for e in result.errors)


def test_duplicate_candidates(valid_rows):
    bad_rows = list(valid_rows)
    bad_rows[1] = SubmissionRow(
        candidate_id="C1", rank=2, score=bad_rows[1].score, reasoning=bad_rows[1].reasoning
    )
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(tuple(bad_rows), metadata)

    result = SubmissionValidator.validate(sub)
    assert not result.is_valid
    assert any("Duplicate candidate_id" in e for e in result.errors)


def test_score_ordering_error(valid_rows):
    bad_rows = list(valid_rows)
    bad_rows[1] = SubmissionRow(
        candidate_id="C2", rank=2, score=1.5, reasoning=bad_rows[1].reasoning
    )
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(tuple(bad_rows), metadata)

    result = SubmissionValidator.validate(sub)
    assert not result.is_valid
    assert any("Score ordering error" in e for e in result.errors)


def test_reasoning_length(valid_rows):
    bad_rows = list(valid_rows)
    bad_rows[0] = SubmissionRow(
        candidate_id="C1", rank=1, score=bad_rows[0].score, reasoning="Too short"
    )
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(tuple(bad_rows), metadata)

    result = SubmissionValidator.validate(sub)
    assert not result.is_valid
    assert any("too short" in e for e in result.errors)


def test_wrong_row_count(valid_rows):
    metadata = SubmissionMetadata(1000, 100, 10.0, 50.0)
    sub = SubmissionFile(valid_rows[:50], metadata)

    result = SubmissionValidator.validate(sub)
    assert not result.is_valid
    assert any("Expected exactly 100 rows" in e for e in result.errors)
