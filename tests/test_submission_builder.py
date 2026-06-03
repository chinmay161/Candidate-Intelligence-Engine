import pytest

from reasoning.reasoning_models import CandidateRecommendation
from submission.submission_builder import SubmissionBuilder


def test_builder_sorts_by_score_and_tie_breaks():
    recs = [
        CandidateRecommendation("C3", rank=0, score=0.8, reasoning="Good", confidence=0.9),
        CandidateRecommendation("C2", rank=0, score=0.9, reasoning="Better", confidence=0.9),
        CandidateRecommendation("C1", rank=0, score=0.9, reasoning="Also Better", confidence=0.9),
    ]
    submission = SubmissionBuilder.build(recs, top_k=2)
    assert len(submission.rows) == 2

    # Scores: C1=0.9, C2=0.9, C3=0.8
    # Tie break on id: C1 before C2
    assert submission.rows[0].candidate_id == "C1"
    assert submission.rows[0].rank == 1
    assert submission.rows[1].candidate_id == "C2"
    assert submission.rows[1].rank == 2

    assert submission.metadata.total_candidates_processed == 3
    assert submission.metadata.top_k == 2


def test_builder_handles_fewer_than_k():
    recs = [
        CandidateRecommendation("C1", rank=0, score=0.8, reasoning="Good", confidence=0.9),
    ]
    submission = SubmissionBuilder.build(recs, top_k=100)
    assert len(submission.rows) == 1
    assert submission.rows[0].rank == 1
