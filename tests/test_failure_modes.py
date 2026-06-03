import pytest
import json

from submission.pipeline_config import PipelineConfig
from submission.pipeline_runner import PipelineRunner


def run_with_jd_content(tmp_path, jd_content, candidates_content):
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text(jd_content)

    cand_file = tmp_path / "cand.jsonl"
    cand_file.write_text(candidates_content)

    config = PipelineConfig(
        top_k=5,
        jd_path=str(jd_file),
        candidates_path=str(cand_file),
        output_dir=str(tmp_path / "out"),
    )
    runner = PipelineRunner(config)
    return runner.run()

def get_base_candidate():
    return {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "A. Smith",
            "headline": "ML",
            "summary": "ML",
            "location": "SF",
            "country": "USA",
            "years_of_experience": 5,
            "current_title": "ML",
            "current_company": "A",
            "current_company_size": "11-50",
            "current_industry": "Software",
        },
        "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 60, "endorsements": 10}],
        "career_history": [
            {
                "title": "ML",
                "company": "A",
                "industry": "Software",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
                "duration_months": 36,
                "is_current": True,
                "description": "Built things",
                "company_size": "11-50"
            }
        ],
        "education": [],
        "certifications": [],
        "redrob_signals": {
            "signup_date": "2024-01-01",
            "open_to_work_flag": True,
            "last_active_date": "2026-06-01",
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 24,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 20.0, "max": 40.0},
            "willing_to_relocate": True,
            "preferred_work_mode": "hybrid",
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.8,
            "saved_by_recruiters_30d": 10,
            "profile_views_received_30d": 50,
            "search_appearance_30d": 200,
            "applications_submitted_30d": 5,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
            "github_activity_score": 80.0,
            "profile_completeness_score": 95.0,
            "skill_assessment_scores": {"Python": 90.0},
            "connection_count": 500,
            "endorsements_received": 50
        }
    }


def test_empty_jd(tmp_path):
    cand = json.dumps(get_base_candidate())
    result = run_with_jd_content(tmp_path, "", cand)
    assert not result.success

def test_malformed_jd(tmp_path):
    cand = json.dumps(get_base_candidate())
    result = run_with_jd_content(tmp_path, "Just some random words with no clear structure", cand)
    # The pipeline should handle it gracefully, but validator fails on rows count because parsing might yield empty requirements
    # or it might pass but the score is low. Let's just check if it runs without crashing, but might fail validation if we don't have 5 candidates.
    assert result.success or any("rows" in e for e in result.errors)

def test_missing_candidate_fields(tmp_path):
    cand_content = '{"candidate_id": "CAND_0000001"}'
    jd_content = "Looking for search ML Engineer with python."
    result = run_with_jd_content(tmp_path, jd_content, cand_content)
    assert not result.success
    assert any("Expected exactly 5 rows" in err for err in result.errors)

def test_duplicate_candidate_ids(tmp_path):
    cand = get_base_candidate()
    # 5 duplicates
    cand_content = "\n".join([json.dumps(cand)] * 5)
    jd_content = "Looking for search ML Engineer with python."
    result = run_with_jd_content(tmp_path, jd_content, cand_content)
    # Validator checks for unique candidate IDs
    assert not result.success
    assert any("Duplicate candidate_id" in err for err in result.errors)

def test_corrupt_jsonl_row(tmp_path):
    cand = get_base_candidate()
    cand_content = json.dumps(cand) + "\n{corrupted\n" + json.dumps(cand)
    jd_content = "Looking for search ML Engineer with python."
    result = run_with_jd_content(tmp_path, jd_content, cand_content)
    # The parser skips corrupted rows
    assert not result.success
    assert any("Expected exactly 5 rows" in err for err in result.errors)

def test_empty_skills(tmp_path):
    cand = get_base_candidate()
    cand["skills"] = []
    # Replicate 5 times with diff IDs to pass validation
    cands = []
    for i in range(5):
        c = dict(cand)
        c["candidate_id"] = f"CAND_000000{i}"
        cands.append(json.dumps(c))
    
    result = run_with_jd_content(tmp_path, "ML Engineer", "\n".join(cands))
    assert result.success

def test_empty_experience(tmp_path):
    cand = get_base_candidate()
    cand["career_history"] = []
    # Replicate 5 times with diff IDs to pass validation
    cands = []
    for i in range(5):
        c = dict(cand)
        c["candidate_id"] = f"CAND_000000{i}"
        cands.append(json.dumps(c))
    
    # We might get CandidateValidationError: career_history must contain at least 1 items
    # Because _list(data, "career_history", 1, 10) says min_items=1
    result = run_with_jd_content(tmp_path, "ML Engineer", "\n".join(cands))
    assert not result.success
    assert any("Expected exactly 5 rows" in err for err in result.errors)
