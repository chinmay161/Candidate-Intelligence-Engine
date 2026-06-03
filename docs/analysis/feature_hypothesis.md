# Feature Hypothesis Blueprint - Phase 1

## 1. Executive Summary

Redrob AI is hiring a founding Senior AI Engineer for a Series A recruiting intelligence platform. The role is not a generic AI keyword match. The company needs someone who can own candidate-job matching systems: retrieval, ranking, embeddings, hybrid search, LLM-assisted reranking, and evaluation infrastructure, while still writing production Python and shipping quickly with product feedback.

Candidates should rank highly when their career history proves they have shipped production search, ranking, recommendation, retrieval, or matching systems to real users, ideally in product companies or marketplace-like contexts. The strongest candidates will have 5-9 years of experience, strong Python, NLP/IR depth, ranking evaluation experience, product/startup judgment, recent coding, Indian location or relocation fit, and good Redrob availability signals.

Candidates should rank poorly when they are keyword-stuffed but role-incoherent, pure researchers without production deployments, framework-demo builders with only recent LangChain/OpenAI exposure, title-chasers with frequent short hops, lifelong services/consulting profiles without product-company exposure, inactive or unresponsive candidates, CV/speech/robotics specialists without NLP/IR evidence, and honeypot profiles with impossible timelines or unsupported skill claims.

The features most likely to improve NDCG@10 are: production retrieval/ranking evidence in career descriptions, ranking evaluation evidence, role/title coherence, product-company AI experience, experience-band fit, honeypot/anomaly penalties, and availability/contactability multipliers.

## 2. Job Description Analysis

### Required Skills

| Requirement | Evidence to search for |
|---|---|
| Production embeddings-based retrieval | Sentence Transformers, OpenAI embeddings, BGE, E5, embedding drift, index refresh, retrieval regression, dense retrieval deployed to users |
| Production vector or hybrid search infrastructure | Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS, hybrid BM25+dense systems |
| Strong Python | Python skill with advanced/expert proficiency, Python in role descriptions, backend/ML production coding |
| Ranking evaluation frameworks | NDCG, MRR, MAP, offline benchmarks, online A/B tests, recruiter feedback loops, offline-to-online correlation |
| Production deployment | Real users, scale, latency, monitoring, on-call, experiments, model/index refreshes |
| Hands-on current coding | Recent engineering role, not purely architecture/management |
| Senior judgment | Ownership of systems, tradeoffs, mentoring, v2 ranking system, long-term architecture |

### Preferred Skills

| Preference | Evidence to search for |
|---|---|
| LLM fine-tuning | LoRA, QLoRA, PEFT, fine-tuning LLMs, Hugging Face Transformers |
| Learning to rank | XGBoost ranker, LambdaMART, LTR, neural reranking, ranking model features |
| HR-tech, recruiting tech, marketplaces | Candidate matching, recruiter search, job matching, marketplace ranking, HR-tech |
| Distributed systems or inference optimization | Large-scale inference, low latency serving, distributed search, batch/stream pipelines |
| Open-source AI/ML contributions | GitHub activity, external validation, OSS, papers/talks if present |
| Startup/product engineering | Shipping fast, product feedback loops, ambiguous founding-team work |
| Location/logistics fit | Pune, Noida, Delhi NCR, Mumbai, Hyderabad, Bangalore; relocation; short notice |

### Negative Signals

| Negative signal | Why it matters |
|---|---|
| Pure research without deployment | Explicit disqualifier; role is production and product-facing |
| Only recent LangChain/OpenAI demo experience | Explicitly called out as insufficient unless backed by older ML production experience |
| No production coding in last 18 months | Role writes code |
| Title chasing and 1.5-year company hopping | Company wants likely 3+ year retention |
| Entire career in consulting/services firms | Explicitly discouraged unless prior product-company experience exists |
| CV/speech/robotics primary expertise without NLP/IR | Adjacent but not core to the role |
| Closed-source-only work for 5+ years with no external validation | Harder to evaluate thinking and public signal |
| Keyword-stuffed non-tech profiles | Explicit hackathon trap |
| Low activity or low recruiter response | Perfect profiles are not useful if unavailable |
| Long notice period | Still possible, but bar gets higher |

### Hidden Signals

| Hidden signal | Inference |
|---|---|
| Product-minded ranking ownership | They value engineers who optimize recruiter workflows, not model metrics alone |
| Evaluation maturity | NDCG@10, A/B tests, and feedback loops are central because the product is ranking quality |
| Pragmatic shipping bias | A working ranker in a week is valued over elegant research |
| Written communication | Async-first culture implies clear writing and reasoned decision logs |
| Startup resilience | JD changes every six months; ambiguity tolerance matters |
| Recruiter-marketplace intuition | Matching systems should understand both candidate fit and candidate availability |
| Explainability | Submission review rewards honest, specific reasoning; platform likely needs recruiter-facing explanations |

## 3. Candidate Schema Analysis

| Field | Meaning | Usefulness for ranking | Recommended transformations |
|---|---|---|---|
| `candidate_id` | Stable unique ID | Operational only | Tie-breaker, join key, deterministic ordering |
| `profile.anonymized_name` | Anonymized display name | Not useful for scoring | Do not score; only for reasoning if needed |
| `profile.headline` | One-line self-positioning | High | Keyword/phrase extraction, title coherence, semantic match to JD |
| `profile.summary` | Candidate narrative | Very high | BM25/TF-IDF against JD, phrase flags, contradiction checks, production evidence extraction |
| `profile.location` | City/region | Medium-high | Preferred city flag, India metro flag, Pune/Noida proximity, relocation logistics |
| `profile.country` | Country | Medium | India fit, outside-India penalty/case-by-case flag |
| `profile.years_of_experience` | Stated total experience | Very high | Target band score, seniority score, mismatch vs career duration |
| `profile.current_title` | Current role | Very high | Role family classification, non-tech penalty, seniority, title-summary mismatch |
| `profile.current_company` | Current employer | Medium | Consulting-only detection, product company signal, repeated companies |
| `profile.current_company_size` | Current employer size bucket | Medium | Startup/mid-market/product scale proxy, enterprise-only penalty when paired with services |
| `profile.current_industry` | Current industry | High | Product/AI/marketplace fit, consulting/services penalty, domain relevance |
| `career_history[].company` | Employer name | Medium-high | Product vs services flags, company diversity, consulting-only career |
| `career_history[].title` | Role title in each job | High | Career trajectory, recent coding role, ML/IR role evidence, title hopping |
| `career_history[].start_date` | Role start date | Medium | Timeline validation, recency, overlap checks |
| `career_history[].end_date` | Role end date | Medium | Timeline validation, tenure, current role checks |
| `career_history[].duration_months` | Tenure in role | High | Stability, job hopping, experience allocation, timeline anomalies |
| `career_history[].is_current` | Current role marker | Medium | Current role validation, current coding evidence |
| `career_history[].industry` | Role-level industry | High | Product-company exposure, HR-tech/marketplace/recruiting relevance |
| `career_history[].company_size` | Role employer size | Medium | Startup exposure, scale exposure, enterprise-only pattern |
| `career_history[].description` | Role responsibilities/achievements | Very high | Production/retrieval/ranking/eval evidence, scale signals, product ownership, contradiction checks |
| `education[].institution` | School name | Low-medium | Prestige if tier missing, external validation hint |
| `education[].degree` | Degree type | Medium | CS/ML graduate signal, PhD research-only caution |
| `education[].field_of_study` | Major | Medium | CS/AI/ML/stats fit, unrelated field penalty if no strong career evidence |
| `education[].start_year` | Education start | Low-medium | Timeline validation |
| `education[].end_year` | Education end | Low-medium | Timeline validation, experience consistency |
| `education[].grade` | Academic grade | Low | Normalize only when parseable; weak tie-breaker |
| `education[].tier` | Institution prestige tier | Medium | Tier score, especially for junior/ambiguous profiles |
| `skills[].name` | Skill label | High, but risky | Canonicalize synonyms, bucket into core/preferred/adjacent/trap skills |
| `skills[].proficiency` | Self-rated proficiency | Medium | Ordered numeric value, cap if unsupported by history |
| `skills[].endorsements` | Per-skill endorsement count | Low-medium | Log-normalized social proof; suspicious if high but unsupported |
| `skills[].duration_months` | Skill usage duration | High | Minimum credible experience, zero-duration honeypot, recency proxy |
| `certifications[].name` | Certification title | Low-medium | ML/cloud cert flags; LangChain-only penalty if unsupported |
| `certifications[].issuer` | Cert issuer | Low | Cloud/ML issuer quality |
| `certifications[].year` | Cert year | Low-medium | Recency, pre-LLM-era ML proof |
| `languages[].language` | Spoken language | Low | Operational fit only |
| `languages[].proficiency` | Language proficiency | Low | English/professional communication if available |
| `redrob_signals.profile_completeness_score` | Profile completeness | Medium | 0-1 scaling, missingness confidence |
| `redrob_signals.signup_date` | Platform signup date | Low-medium | Account age, new active candidate vs stale account |
| `redrob_signals.last_active_date` | Last login date | Very high | Days since active, stale-profile penalty |
| `redrob_signals.open_to_work_flag` | Availability intent | High | Binary multiplier, interacts with response rate |
| `redrob_signals.profile_views_received_30d` | Recruiter views | Medium | Log1p + percentile; demand proxy |
| `redrob_signals.applications_submitted_30d` | Recent applications | Medium | Availability and intent; cap very high values |
| `redrob_signals.recruiter_response_rate` | Reply probability | Very high | Direct multiplier; penalize below 0.2 |
| `redrob_signals.avg_response_time_hours` | Median response speed | High | Inverse/log transform; penalty above 72/168 hours |
| `redrob_signals.skill_assessment_scores` | Platform test scores | High | Extract core JD skill scores; max/mean/coverage |
| `redrob_signals.connection_count` | Network size | Low-medium | Log1p social proof; avoid dominance |
| `redrob_signals.endorsements_received` | Total endorsements | Low-medium | Log1p social proof; compare with skill evidence |
| `redrob_signals.notice_period_days` | Availability lead time | High | Step penalty: <=30 good, 60 acceptable, 90+ strong penalty |
| `redrob_signals.expected_salary_range_inr_lpa.min` | Lower salary expectation | Medium | Salary fit if comp known; otherwise seniority realism |
| `redrob_signals.expected_salary_range_inr_lpa.max` | Upper salary expectation | Medium | Salary affordability/risk, range width |
| `redrob_signals.preferred_work_mode` | Remote/hybrid/onsite/flexible | Medium | Hybrid/flexible/Pune-Noida fit |
| `redrob_signals.willing_to_relocate` | Relocation intent | High | Boost outside Pune/Noida; penalty if far and false |
| `redrob_signals.github_activity_score` | GitHub activity or -1 | Medium-high | External validation, OSS signal, missing-GitHub neutral/slight penalty |
| `redrob_signals.search_appearance_30d` | Recruiter search impressions | Medium | Demand/relevance proxy, log1p percentile |
| `redrob_signals.saved_by_recruiters_30d` | Recruiter saves | High | Strong marketplace demand proxy |
| `redrob_signals.interview_completion_rate` | Interview attendance | High | Reliability multiplier; penalize <0.5 |
| `redrob_signals.offer_acceptance_rate` | Historical offer acceptance | Medium | Hireability; -1 as missing, not zero |
| `redrob_signals.verified_email` | Contact verified | Medium | Contactability penalty if false |
| `redrob_signals.verified_phone` | Phone verified | Medium | Contactability penalty if false |
| `redrob_signals.linkedin_connected` | LinkedIn attached | Low-medium | Identity/external profile confidence |

## 4. Behavioral Signal Analysis

Behavioral signals should modify fit rather than replace it. A weak candidate with good availability should not outrank a strong production retrieval engineer, but among high-fit candidates these signals can strongly affect hireability.

| Rank | Signal | Importance | Ranking value | Normalization strategy | Expected effect on hireability |
|---:|---|---|---|---|---|
| 1 | `recruiter_response_rate` | Very high | Direct contact probability | Use raw 0-1; heavy penalty below 0.2; boost above 0.7 | Strong positive when high, severe negative when low |
| 2 | `last_active_date` | Very high | Recency/availability | Convert to days since active as of 2026-06-03; exponential decay | Recent activity strongly boosts; 180+ days penalizes |
| 3 | `open_to_work_flag` | High | Declared intent | Binary; interact with last active and applications | Boost if true, especially with recent activity |
| 4 | `notice_period_days` | High | Speed to hire | Piecewise: <=30 best, 31-60 ok, 90+ penalty | Short notice improves hireability |
| 5 | `saved_by_recruiters_30d` | High | Market demand | Log1p, percentile within pool | Strong positive social proof |
| 6 | `avg_response_time_hours` | High | Responsiveness | Inverse log; cap extreme values | Fast responders are more hireable |
| 7 | `interview_completion_rate` | High | Reliability | Raw 0-1 with penalty below 0.5 | Higher attendance improves funnel success |
| 8 | `skill_assessment_scores` | High | Validated skill quality | Extract JD-core score mean/max/coverage; missing separate | High scores on IR/Python/ML boost confidence |
| 9 | `willing_to_relocate` | High | Location feasibility | Binary; only important if not Pune/Noida/NCR/Pune-adjacent | Boost for non-preferred cities |
| 10 | `github_activity_score` | Medium-high | External validation | Treat -1 as missing; percentile for >=0 | Positive for OSS/active engineers; missing not fatal |
| 11 | `profile_completeness_score` | Medium | Profile quality/confidence | Scale 0-1; mild penalty below 50 | Better profiles aid explainability and trust |
| 12 | `applications_submitted_30d` | Medium | Active job search | Log1p then cap; very high can be desperation/noise | Moderate positive |
| 13 | `profile_views_received_30d` | Medium | Recruiter interest | Log1p percentile | Positive if not driven by keyword stuffing |
| 14 | `search_appearance_30d` | Medium | Search demand | Log1p percentile, damped | Positive but can reflect broad keywords |
| 15 | `offer_acceptance_rate` | Medium | Closing likelihood | Missing -1 separate; raw for known | High is positive; missing neutral |
| 16 | `verified_email` | Medium | Contactability | Binary | Unverified email penalizes |
| 17 | `verified_phone` | Medium | Contactability | Binary | Unverified phone penalizes |
| 18 | `expected_salary_range_inr_lpa` | Medium | Affordability/seniority realism | Midpoint, width, outlier flags; use only if comp target known | Helps avoid unrealistic expectations |
| 19 | `preferred_work_mode` | Medium | Hybrid-office fit | One-hot; hybrid/flexible best for this JD | Moderate logistics fit |
| 20 | `linkedin_connected` | Low-medium | Identity confidence | Binary | Mild positive |
| 21 | `endorsements_received` | Low-medium | Social proof | Log1p; compare to skill evidence | Mild positive, easy to game |
| 22 | `connection_count` | Low-medium | Network activity | Log1p; cap high values | Mild positive |
| 23 | `signup_date` | Low-medium | Platform tenure | Account age and new-user flag | Useful mainly with activity recency |

## 5. Candidate Quality Indicators

### Strong AI Engineer

- Current or recent title in AI/ML/NLP/applied ML/senior data science.
- Multiple years in production ML, not only courses or demos.
- Python plus PyTorch/TensorFlow/scikit-learn/Hugging Face with credible duration.
- Evidence of deployment, monitoring, latency, evaluation, model iteration, and ownership.
- Good GitHub or external validation, especially if work is otherwise proprietary.

### Strong Retrieval Engineer

- Career descriptions mention retrieval, search, ranking, recommendations, candidate matching, semantic search, BM25, dense retrieval, hybrid search, vector databases, index refresh, embedding drift, relevance regression, or query understanding.
- Skills include FAISS, OpenSearch, Elasticsearch, Qdrant, Pinecone, Weaviate, Milvus, pgvector, Sentence Transformers, BGE/E5-like embedding systems.
- Has evaluated retrieval with NDCG, MRR, MAP, recall@k, precision@k, human judgments, or online experiments.

### Production ML Engineer

- Role descriptions include deployed systems, real users, scale, A/B testing, monitoring, on-call, data/model pipelines, inference serving, and reliability.
- Experience includes MLOps tools like MLflow, Kubeflow, BentoML, Docker, Kubernetes, CI/CD, Airflow, Spark, Kafka.
- Has owned end-to-end systems rather than isolated notebooks.

### Startup Engineer

- Experience at small/mid product companies or fast-moving product orgs.
- Career descriptions show ambiguity, ownership, quick iteration, cross-functional PM/recruiter collaboration, and shipping imperfect v1 systems.
- Not overly title-optimized; reasonable tenure and willingness to be hands-on.

### Product-Minded Engineer

- Mentions recruiter workflows, marketplace metrics, user engagement, feedback loops, UX/product tradeoffs, or business metrics.
- Has built matching/recommendation/search systems with measurable user outcomes.
- Reasoning in profile balances model quality with product impact.

## 6. Honeypot Detection Opportunities

| Anomaly pattern | Detection method | Severity score |
|---|---|---:|
| Expert skill with `duration_months = 0` | Count expert skills whose duration is zero | 10 |
| Many skills with zero duration | Count zero-duration skills; flag if >=3 or if any are core JD skills | 9 |
| Stated years inconsistent with career durations | Compare `years_of_experience * 12` to sum of role durations; flag gap >36 months | 9 |
| Summary years contradict profile years | Regex extract "X years" from summary/headline and compare to profile years | 8 |
| Current title mismatch with summary/title family | Classify current_title and summary role family; flag non-tech title with ML-heavy summary or vice versa | 8 |
| Non-tech title with many AI skills | Marketing/HR/accounting/design/sales/civil/mechanical title plus >=5 core AI skills | 8 |
| Skill-history mismatch | Core skills listed but no supporting text in career descriptions | 8 |
| Retrieval keyword stuffing without production evidence | Many vector/RAG skills but no deployed/scale/eval terms in career history | 7 |
| Impossible education timeline | `end_year < start_year`, future degrees without explanation | 7 |
| Education and work overlap impossible for early career | Full-time role before degree end with large overlap and no part-time signal | 5 |
| Multiple current roles or no current role | Count `is_current` in career history != 1 | 6 |
| Role date/duration mismatch | Parse start/end dates and compare with `duration_months` tolerance | 6 |
| Unrealistic rapid seniority jump | Junior/non-tech to Staff/Lead AI in <24 months without bridge roles | 7 |
| Title-chasing pattern | >=3 role changes with average tenure <18 months and title inflation | 6 |
| Consulting-only career | All companies in known services list and no product-company role | 6 |
| Pure research-only profile | Research/lab/PhD/postdoc terms without deployed/production terms | 7 |
| Closed-source-only external validation gap | 5+ years proprietary/enterprise with no GitHub, no LinkedIn, no public signals | 4 |
| Salary expectation unrealistic | Salary midpoint extreme relative to years/location, or min > max | 5 |
| Behavioral twin / suspicious platform pattern | Duplicate or near-identical Redrob signal vector across many profiles | 4 |
| Duplicated text templates with changed skills | Near-duplicate summaries plus inconsistent skills/title | 5 |
| Recent LLM-only pivot | LangChain/OpenAI/RAG mentions only in last <12 months and no prior ML | 7 |
| CV/speech/robotics dominance | High CV/speech skills and career text, low NLP/IR evidence | 5 |

## 7. Feature Engineering Blueprint

Priority: 5 = likely major NDCG@10 contributor, 4 = strong, 3 = useful secondary, 2 = tie-breaker, 1 = mostly diagnostics.

### Semantic Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `jd_semantic_bm25_score` | BM25 between JD query terms and headline+summary+career descriptions | 5 |
| `core_ir_phrase_count` | Count retrieval/ranking/search/recommendation phrases in career text | 5 |
| `production_ir_evidence_score` | Count co-occurrence of IR terms with production/deployed/scale/eval terms in same role | 5 |
| `ranking_eval_phrase_score` | Count NDCG, MRR, MAP, A/B, offline, online, relevance regression, feedback loops | 5 |
| `embedding_system_evidence` | Flag embeddings plus index/vector DB/refresh/drift language | 5 |
| `hybrid_search_evidence` | Flag BM25 + dense/vector/hybrid terms | 5 |
| `candidate_matching_domain_score` | Search for candidate-JD matching, recruiter search, job matching, talent marketplace terms | 5 |
| `llm_integration_depth_score` | Fine-tuning/reranking/RAG terms weighted above prompt/demo terms | 4 |
| `framework_demo_penalty_text` | Penalize LangChain/tutorial/demo-only language without production terms | 4 |
| `product_impact_phrase_score` | Count metrics/user impact/recruiter engagement/conversion/product workflow phrases | 4 |
| `writing_clarity_score` | Heuristic for specific, measurable career descriptions vs generic templates | 3 |
| `semantic_title_summary_consistency` | Similarity or rule agreement between title family and profile text family | 4 |

### Experience Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `yoe_target_band_score` | Peak at 6-8 years, high for 5-9, soft decay outside | 5 |
| `senior_judgment_experience_score` | Combine yoe, senior/lead title, ownership verbs, architecture mentions | 4 |
| `applied_ml_years_proxy` | Sum durations of roles whose title/description include ML/AI/NLP/retrieval | 5 |
| `ir_retrieval_years_proxy` | Sum durations of roles containing IR/retrieval/ranking/search/recommendation terms | 5 |
| `production_ml_years_proxy` | Sum durations of ML roles with production/deployed/scale terms | 5 |
| `recent_coding_role_flag` | Current/recent title is engineer/scientist/developer and description has hands-on code | 5 |
| `management_only_recent_penalty` | Penalize architect/manager/lead-only language without coding in last role | 4 |
| `pre_llm_ml_experience_flag` | ML role or skill duration >36 months before current LLM trend; proxy via durations and role history | 4 |
| `career_duration_consistency` | Negative absolute gap between stated yoe months and summed durations | 4 |
| `current_role_duration_score` | Tenure in current role; avoid too short unless startup context | 3 |
| `average_tenure_score` | Median/mean role duration; penalize chronic <18 month hops | 4 |
| `job_hop_title_chaser_penalty` | Frequent short roles plus title inflation Senior->Staff->Principal | 4 |

### Skill Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `python_strength_score` | Python skill proficiency/duration plus Python in career text | 5 |
| `vector_db_skill_coverage` | Count Pinecone/Weaviate/Qdrant/Milvus/FAISS/OpenSearch/Elasticsearch/pgvector | 5 |
| `retrieval_skill_depth` | Weighted proficiency*log(duration) for IR/search/ranking/embedding skills | 5 |
| `ranking_skill_depth` | Learning to Rank, recommendation systems, ranking, BM25, evaluation skill weights | 5 |
| `llm_finetuning_skill_score` | LoRA/QLoRA/PEFT/fine-tuning/Hugging Face with duration/proficiency | 4 |
| `mlops_skill_score` | MLflow/Kubeflow/BentoML/Docker/Kubernetes/CI/CD/deployment skills | 4 |
| `data_pipeline_support_score` | Spark/Kafka/Airflow/Beam/SQL/warehouse for feature pipeline readiness | 3 |
| `skill_assessment_core_mean` | Mean assessment score for Python, IR, vector search, embeddings, LTR, ML | 4 |
| `skill_assessment_core_max` | Max validated score among core JD skills | 3 |
| `skill_assessment_coverage` | Number of JD-core skills with assessment scores | 3 |
| `skill_history_support_ratio` | Fraction of core listed skills also present in career descriptions | 5 |
| `expert_zero_duration_penalty` | Count expert skills with zero months | 5 |
| `ai_keyword_stuffing_penalty` | High AI skill count but non-tech title or no supporting career text | 5 |
| `cv_speech_robotics_dominance_penalty` | CV/speech/robotics skills outweigh NLP/IR skills | 3 |
| `certification_relevance_score` | AWS ML/GCP ML/NLP/deep learning certs positive; LangChain-only weak | 2 |

### Behavioral Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `availability_multiplier` | Combine open_to_work, days_since_active, applications, response rate | 5 |
| `days_since_active_score` | Exponential decay from `last_active_date` as of 2026-06-03 | 5 |
| `recruiter_response_score` | Raw response rate with nonlinear penalty below 0.2 | 5 |
| `response_speed_score` | Inverse log of avg response hours; cap slow tail | 4 |
| `notice_period_score` | Piecewise score: <=30 best, 60 ok, 90+ penalty | 4 |
| `interview_reliability_score` | Interview completion rate, stronger penalty below 0.5 | 4 |
| `offer_acceptance_known_score` | If known, use acceptance rate; missing separate | 3 |
| `recruiter_demand_score` | Log/percentile of saved_by_recruiters + profile views + search appearances | 4 |
| `profile_completeness_confidence` | 0-1 scaled completeness; mild confidence factor | 3 |
| `contact_verification_score` | Email + phone + LinkedIn connected | 3 |
| `github_external_validation_score` | Percentile of GitHub score; -1 handled as missing | 4 |
| `platform_activity_recency_x_fit` | Interaction of high semantic fit and recent activity | 5 |

### Career Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `product_company_exposure_months` | Sum months in Software/SaaS/Fintech/E-commerce/AI/ML/Internet/marketplace industries | 5 |
| `services_only_penalty` | All career companies are services/consulting names and no product-company role | 5 |
| `current_industry_fit_score` | AI/ML, Software, SaaS, Fintech, E-commerce, HR-tech-like industries positive | 4 |
| `startup_or_scaleup_exposure` | Months in 11-50, 51-200, 201-500 product companies | 3 |
| `large_scale_exposure` | Role text has 50M+, high throughput, large index, distributed system, high traffic | 4 |
| `ownership_verbs_score` | Built, owned, led, shipped, designed, migrated, evaluated in career descriptions | 4 |
| `cross_functional_product_score` | PM/recruiter/customer/user feedback references | 3 |
| `role_family_fit_score` | Current/recent title maps to AI/ML/NLP/retrieval/data engineer/backend ML | 5 |
| `nontech_role_penalty` | Current title in HR/marketing/accounting/design/sales/civil/mechanical/support | 5 |
| `current_product_ai_role_flag` | Current role combines ML/AI title and product-fit industry | 5 |

### Education Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `cs_ai_field_score` | CS/AI/ML/data science/statistics/math fields positive | 3 |
| `degree_level_score` | M.Tech/MS/ME/MSc/PhD moderate boost; PhD not enough without production | 2 |
| `institution_tier_score` | tier_1 strongest, tier_2 moderate, tier_3/4 weak | 2 |
| `education_timeline_validity` | start/end order and plausible dates | 3 |
| `research_only_phd_penalty` | PhD/research terms with no production deployment | 4 |
| `grade_parse_score` | Parse CGPA/percentage where possible; low weight | 1 |

### Logistics Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `preferred_location_score` | Pune/Noida highest; Delhi NCR/Mumbai/Hyderabad/Bangalore welcome | 4 |
| `india_location_score` | India positive; outside India case-by-case penalty unless exceptional | 3 |
| `relocation_fit_score` | If outside preferred cities, willing_to_relocate boosts | 4 |
| `work_mode_fit_score` | Hybrid/flexible/onsite fit for Pune/Noida offices; remote weaker | 3 |
| `salary_midpoint_realism` | Salary midpoint relative to senior AI engineer market and years | 2 |
| `salary_range_width_penalty` | Very wide range implies uncertainty/noise | 1 |
| `notice_buyout_fit` | <=30 days strong, 31-60 acceptable, 90+ bar higher | 4 |

### Anomaly Features

| Feature | Calculation logic | Priority |
|---|---|---:|
| `honeypot_score` | Weighted sum of severe anomaly flags | 5 |
| `summary_profile_years_mismatch` | Compare extracted summary/headline years to profile yoe | 5 |
| `title_description_mismatch` | Role title family contradicts description family | 5 |
| `skill_duration_impossibility_count` | Count expert/core skills with zero or impossible duration | 5 |
| `education_end_before_start_flag` | Education end before start | 4 |
| `role_date_duration_mismatch` | Parsed date diff far from duration_months | 4 |
| `multiple_current_roles_flag` | Current role count != 1 | 4 |
| `template_duplicate_suspicion` | Near-duplicate summary across unrelated titles with changed skills | 3 |
| `behavioral_inconsistency_score` | Very high demand but no verification/activity, or open_to_work false with many applications | 2 |
| `reasoning_confidence_score` | Internal confidence from evidence coverage and anomaly absence | 4 |

## 8. Ranking Strategy Recommendations

### Dominant Features

The top of the ranking should be dominated by career-evidence features, not the raw skill list. The highest weights should go to production retrieval/ranking experience, ranking evaluation evidence, role/title coherence, product-company AI exposure, target experience band, and anomaly-free profiles. These are most likely to move NDCG@10 because the top 10 needs true senior founding-team fit, not broad relevance.

### Secondary Features

Behavioral availability, Redrob demand, GitHub activity, education, certifications, MLOps/data-pipeline adjacency, startup exposure, and location should break ties among candidates who already satisfy the core role. Behavioral signals should act as a multiplier: high-fit but inactive candidates move down; low-fit but active candidates should not jump to the top.

### Penalty-Only Features

Use penalties for honeypots, impossible timelines, zero-duration expert skills, non-tech keyword stuffing, consulting-only careers, pure research without deployment, CV/speech/robotics-only profiles, no recent coding, title chasing, long notice periods, stale activity, and low response rates. These should mostly prevent false positives from entering the top 100.

### Practical Model Shape

For Phase 2, a practical CPU-only architecture should be:

1. Parse all profiles into structured text blocks: profile, current role, full career, skills, education, Redrob signals.
2. Build deterministic lexical features with curated JD dictionaries for IR, ranking, vector DBs, production, evaluation, product, and negative archetypes.
3. Add lightweight BM25 or TF-IDF similarity features over candidate text. Avoid hosted APIs during ranking.
4. Use rule-based gates for severe honeypot/negative patterns.
5. Score with an explainable weighted model or small gradient-boosted ranker trained on synthetic labels if labels are constructed carefully.
6. Generate reasoning from the top contributing evidence snippets, never from unsupported inferred facts.

## 9. Risk Analysis

### Overfitting Risks

- Overweighting exact JD keywords like RAG, Pinecone, or LangChain will rank traps.
- Overweighting Redrob popularity signals will favor broadly searchable keyword-stuffed candidates.
- Over-penalizing outside 5-9 years may miss exceptional candidates, since the JD says the band is flexible.
- Over-penalizing missing GitHub can hurt strong proprietary production engineers; use it as a confidence signal, not a requirement.
- Using sample submission as signal is dangerous; it is explicitly format-only and contains obvious poor rankings.

### Misleading Signals

- Skill count is noisy and synthetic; use support from career history.
- Endorsements and connections are weak social proof and can be gamed.
- `offer_acceptance_rate = -1` means missing, not bad.
- `github_activity_score = -1` means no GitHub linked, not necessarily zero quality.
- High `search_appearance_30d` may reflect keyword stuffing rather than true fit.
- Certifications are weak unless paired with production experience.

### Trap Candidate Types

- Marketing/HR/accounting/design/sales profiles with many AI skills.
- Engineers who only mention recent LangChain or RAG demos.
- Senior titles with short tenures and no hands-on coding evidence.
- ML researchers with publications/labs but no production deployment.
- CV/speech/robotics specialists with little NLP/IR.
- Consulting-only profiles from services firms with generic enterprise project language.
- Candidates with perfect skills but inactive for months and low response rate.
- Honeypots with impossible years, zero-duration expert skills, or title-summary contradictions.

### Common Competitor Mistakes

- Counting AI keywords instead of reading career history.
- Building embeddings over the entire profile without anomaly gates.
- Treating behavioral signals as the main ranker rather than a hireability modifier.
- Ignoring the "what the JD means" text and ranking generic ML engineers.
- Not distinguishing product-company deployment from services/consulting delivery.
- Generating reasoning that hallucinates unsupported facts.
- Ignoring CPU/runtime limits and designing a per-candidate LLM reranking system.

## 10. Deliverables

This document is the Phase 1 deliverable: `feature_hypothesis.md`.

### Final Feature List With Priority Scores

The final recommended feature set contains 91 features:

| Priority | Feature families | Implementation recommendation |
|---:|---|---|
| 5 | Production IR/ranking evidence, ranking evaluation, role fit, product-company ML, target yoe, anomaly/honeypot gates, availability multiplier | Implement first; these drive NDCG@10 |
| 4 | LLM depth, MLOps, ownership, recruiter demand, GitHub, location/notice, title-chasing/services penalties | Implement second; strong top-50/top-100 gains |
| 3 | Education field, startup exposure, cross-functional product signals, assessments coverage, work mode, profile completeness | Useful tie-breakers and reasoning support |
| 2 | Degree level, certifications, salary realism, offer acceptance, LinkedIn/connections/endorsements | Low-weight confidence features |
| 1 | Grade parsing, salary width | Diagnostics/tie-breakers only |

### Highest Expected NDCG@10 Contributors

1. `production_ir_evidence_score`
2. `ranking_eval_phrase_score`
3. `ir_retrieval_years_proxy`
4. `role_family_fit_score`
5. `skill_history_support_ratio`
6. `honeypot_score`
7. `nontech_role_penalty`
8. `yoe_target_band_score`
9. `product_company_exposure_months`
10. `availability_multiplier`
11. `candidate_matching_domain_score`
12. `services_only_penalty`

### Implementation Recommendations

- Build synonym dictionaries for core JD concepts and negative archetypes. Keep them explicit and reviewable.
- Score career-history evidence more heavily than skill-list evidence.
- Use text windows by role so "production retrieval" is stronger than isolated "production" and "retrieval" anywhere in the profile.
- Treat Redrob behavioral features as multipliers after technical fit.
- Add hard or near-hard gates for severe honeypots before selecting the top 100.
- Generate reasoning from feature evidence: current title, years, retrieval/ranking evidence, product context, availability signals, and honest concerns.
- Keep ranking CPU-only and deterministic. A full pass over 100,000 JSONL records with regex/rule features plus sparse text similarity is well within the 5-minute budget.
- Avoid hosted LLMs, per-candidate heavy models, and unexplainable black-box scores during ranking.

