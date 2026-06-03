import json
import os
import random

def generate_jd(path):
    jd_content = """
    Senior Machine Learning Engineer (Search & Ranking)
    We are looking for a Senior ML Engineer to build search and recommendation systems.
    Must have 5+ years of experience with Python, Retrieval techniques, LLMs, and Elasticsearch.
    Experience with PyTorch, Transformers, and MLOps is preferred.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(jd_content.strip())

def generate_candidates(path, count):
    with open(path, "w", encoding="utf-8") as f:
        for i in range(count):
            cand_id = f"CAND_{i:07d}"
            candidate = {
                "candidate_id": cand_id,
                "profile": {
                    "anonymized_name": "A. Smith",
                    "headline": "ML Engineer @ Tech Corp",
                    "summary": "Experienced ML Engineer specializing in search.",
                    "location": "San Francisco",
                    "country": "USA",
                    "years_of_experience": round(random.uniform(2, 10), 1),
                    "current_title": "Senior ML Engineer",
                    "current_company": "Tech Corp",
                    "current_company_size": "51-200",
                    "current_industry": "Software",
                },
                "skills": [
                    {"name": "Python", "proficiency": "expert", "duration_months": 60, "endorsements": 10},
                    {"name": "Machine Learning", "proficiency": "advanced", "duration_months": 48, "endorsements": 5},
                    {"name": "PyTorch", "proficiency": "advanced", "duration_months": 36, "endorsements": 2}
                ],
                "career_history": [
                    {
                        "title": "ML Engineer",
                        "company": "Tech Corp",
                        "industry": "Software",
                        "start_date": "2020-01-01",
                        "end_date": "2023-01-01",
                        "duration_months": 36,
                        "is_current": True,
                        "description": "Built ranking systems and search algorithms.",
                        "company_size": "11-50"
                    }
                ],
                "education": [
                    {
                        "degree": "MS Computer Science",
                        "field_of_study": "Computer Science",
                        "institution": "Stanford",
                        "start_year": 2018,
                        "end_year": 2020,
                        "grade": "3.8 GPA",
                        "tier": "tier_1"
                    }
                ],
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
            try:
                from src.candidate_processor.validators import parse_candidate
                parse_candidate(candidate)
            except Exception as e:
                print(f"Validation error: {e}")
                raise
            f.write(json.dumps(candidate) + "\n")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    os.makedirs("data", exist_ok=True)
    generate_jd("data/sample_jd.txt")
    print("Generating 1000 sample candidates...")
    generate_candidates("data/sample_candidates.jsonl", 1000)
    print("Generating 100,000 benchmark candidates...")
    generate_candidates("data/benchmark_candidates.jsonl", 100000)
    print("Done!")
