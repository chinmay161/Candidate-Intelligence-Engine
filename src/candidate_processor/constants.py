"""Configurable dictionaries and feature names for candidate processing."""

from __future__ import annotations

from datetime import date

AS_OF_DATE: date = date(2026, 6, 3)

CANDIDATE_ID_PATTERN = r"^CAND_[0-9]{7}$"
COMPANY_SIZE_BUCKETS = (
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "501-1000",
    "1001-5000",
    "5001-10000",
    "10001+",
)
SKILL_PROFICIENCY_ORDER = {
    "beginner": 0.25,
    "intermediate": 0.5,
    "advanced": 0.75,
    "expert": 1.0,
}
LANGUAGE_PROFICIENCY_ORDER = {
    "basic": 0.25,
    "conversational": 0.5,
    "professional": 0.75,
    "native": 1.0,
}
WORK_MODES = ("remote", "hybrid", "onsite", "flexible")
EDUCATION_TIERS = ("tier_1", "tier_2", "tier_3", "tier_4", "unknown")

RETRIEVAL_TERMS = (
    "retrieval",
    "information retrieval",
    "semantic search",
    "dense retrieval",
    "sparse retrieval",
    "query understanding",
    "search relevance",
    "relevance",
    "document search",
    "candidate search",
    "recommender",
    "recommendation",
    "recommendation system",
    "matching",
    "matchmaking",
    "bm25",
    "tf-idf",
)
RANKING_TERMS = (
    "ranking",
    "reranking",
    "re-ranking",
    "learning to rank",
    "ltr",
    "lambdamart",
    "xgboost ranker",
    "ranker",
    "neural ranker",
    "ranked",
)
VECTOR_DB_TERMS = (
    "pinecone",
    "weaviate",
    "qdrant",
    "milvus",
    "faiss",
    "opensearch",
    "elastic search",
    "elasticsearch",
    "pgvector",
    "chromadb",
    "ann index",
    "hnsw",
    "vector database",
    "vector db",
)
EMBEDDING_TERMS = (
    "embedding",
    "embeddings",
    "sentence transformers",
    "sentence-transformers",
    "openai embeddings",
    "bge",
    "e5",
    "index refresh",
    "embedding drift",
    "vector index",
)
PRODUCTION_TERMS = (
    "production",
    "deployed",
    "deployed to users",
    "real users",
    "scale",
    "latency",
    "monitoring",
    "on-call",
    "on call",
    "observability",
    "sla",
    "reliability",
    "high throughput",
    "low latency",
    "ci/cd",
    "serving",
    "inference",
)
EVALUATION_TERMS = (
    "ndcg",
    "mrr",
    "map",
    "recall@k",
    "precision@k",
    "offline benchmark",
    "offline evaluation",
    "online experiment",
    "a/b",
    "ab test",
    "human judgment",
    "relevance regression",
    "feedback loop",
    "experiment",
)
LLM_TERMS = (
    "llm",
    "rag",
    "langchain",
    "openai",
    "anthropic",
    "prompt",
    "fine-tuning",
    "finetuning",
    "lora",
    "qlora",
    "peft",
    "hugging face",
    "transformers",
    "neural reranking",
)
PYTHON_TERMS = ("python", "pyspark", "fastapi", "flask", "django")
MLOPS_TERMS = (
    "mlflow",
    "kubeflow",
    "bentoml",
    "docker",
    "kubernetes",
    "airflow",
    "ci/cd",
    "terraform",
    "monitoring",
)
DATA_PIPELINE_TERMS = (
    "spark",
    "pyspark",
    "kafka",
    "airflow",
    "beam",
    "sql",
    "warehouse",
    "snowflake",
    "databricks",
    "dbt",
    "etl",
    "data pipeline",
)
PRODUCT_IMPACT_TERMS = (
    "user",
    "users",
    "recruiter",
    "customer",
    "conversion",
    "engagement",
    "marketplace",
    "workflow",
    "kpi",
    "business metric",
    "feedback",
    "pm",
    "product manager",
)
OWNERSHIP_TERMS = (
    "built",
    "owned",
    "led",
    "shipped",
    "designed",
    "migrated",
    "evaluated",
    "architected",
    "launched",
    "implemented",
    "maintained",
)
STARTUP_TERMS = (
    "startup",
    "founding",
    "0 to 1",
    "zero to one",
    "ambiguous",
    "fast-moving",
    "v1",
    "iteration",
)
CODING_TERMS = (
    "engineer",
    "developer",
    "scientist",
    "backend",
    "full stack",
    "full-stack",
    "python",
    "api",
    "code",
    "implemented",
)
ML_TERMS = (
    "machine learning",
    "ml",
    "ai",
    "nlp",
    "data science",
    "deep learning",
    "model",
    "feature engineering",
    "classification",
)
CORE_AI_SKILLS = tuple(sorted(set(ML_TERMS + RETRIEVAL_TERMS + RANKING_TERMS + EMBEDDING_TERMS + VECTOR_DB_TERMS)))
CV_SPEECH_ROBOTICS_TERMS = (
    "computer vision",
    "image classification",
    "object detection",
    "opencv",
    "speech recognition",
    "tts",
    "asr",
    "robotics",
    "ros",
    "gan",
    "gans",
)
DEMO_ONLY_TERMS = (
    "tutorial",
    "demo",
    "toy project",
    "side project",
    "self-directed",
    "course",
    "kaggle",
    "experimented with chatgpt",
)
RESEARCH_TERMS = ("research", "publication", "paper", "lab", "phd", "postdoc", "thesis")
NEGATIVE_ARCHETYPES = (
    "marketing",
    "hr",
    "accounting",
    "sales",
    "customer support",
    "operations",
    "mechanical",
    "civil",
    "designer",
    "content writer",
    "seo",
)
CONSULTING_COMPANIES = (
    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "accenture",
    "capgemini",
    "mindtree",
    "ltimindtree",
    "hcl",
    "tech mahindra",
    "ibm",
    "deloitte",
    "pwc",
    "ey",
    "kpmg",
)
PRODUCT_INDUSTRIES = (
    "software",
    "saas",
    "fintech",
    "e-commerce",
    "ecommerce",
    "internet",
    "ai/ml",
    "artificial intelligence",
    "machine learning",
    "hr-tech",
    "marketplace",
)
PREFERRED_CITIES = ("pune", "noida")
INDIA_METRO_CITIES = (
    "delhi",
    "ncr",
    "gurgaon",
    "gurugram",
    "mumbai",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
)
TIER_SCORE = {
    "tier_1": 1.0,
    "tier_2": 0.7,
    "tier_3": 0.4,
    "tier_4": 0.2,
    "unknown": 0.35,
}
ROLE_FAMILY_TERMS = {
    "ai_ml": ("ai", "ml", "machine learning", "data scientist", "nlp", "applied scientist"),
    "retrieval": ("search", "retrieval", "ranking", "recommendation", "relevance"),
    "software": ("engineer", "developer", "backend", "full stack", "platform", "data engineer"),
    "management": ("manager", "director", "head", "lead", "architect"),
    "nontech": NEGATIVE_ARCHETYPES,
}
JD_QUERY_TERMS = tuple(
    sorted(
        set(
            RETRIEVAL_TERMS
            + RANKING_TERMS
            + VECTOR_DB_TERMS
            + EMBEDDING_TERMS
            + PRODUCTION_TERMS
            + EVALUATION_TERMS
            + PYTHON_TERMS
        )
    )
)

FEATURE_COLUMNS = (
    "candidate_id",
    "semantic_features",
    "experience_features",
    "skill_features",
    "behavioral_features",
    "career_features",
    "education_features",
    "logistics_features",
    "anomaly_features",
    "evidence",
)
