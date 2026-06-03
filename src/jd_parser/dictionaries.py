"""Configurable dictionaries for job-description intelligence."""

from __future__ import annotations


ROLE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "AI_ENGINEER": (
        "ai engineer",
        "artificial intelligence engineer",
        "generative ai engineer",
        "genai engineer",
        "llm engineer",
        "rag engineer",
    ),
    "ML_ENGINEER": (
        "machine learning engineer",
        "ml engineer",
        "applied ml",
        "model training",
        "model deployment",
        "recommendation system",
        "ranking system",
    ),
    "MLOPS_ENGINEER": (
        "mlops",
        "ml platform",
        "model serving",
        "model monitoring",
        "kubeflow",
        "mlflow",
        "feature store",
    ),
    "DATA_ENGINEER": (
        "data engineer",
        "data pipeline",
        "etl",
        "spark",
        "kafka",
        "warehouse",
        "airflow",
    ),
    "DATA_SCIENTIST": (
        "data scientist",
        "data science",
        "experiment design",
        "statistical modeling",
        "analytics",
        "ab testing",
    ),
    "BACKEND_ENGINEER": (
        "backend engineer",
        "backend developer",
        "api",
        "microservices",
        "server-side",
        "distributed systems",
    ),
    "SOFTWARE_ENGINEER": (
        "software engineer",
        "software developer",
        "full stack",
        "platform engineer",
        "product engineer",
    ),
    "PRODUCT_MANAGER": (
        "product manager",
        "product owner",
        "product lead",
        "roadmap",
        "prioritization",
    ),
    "RESEARCHER": (
        "research scientist",
        "researcher",
        "phd",
        "publication",
        "papers",
        "novel algorithms",
    ),
}

ROLE_TITLE_PATTERNS: dict[str, tuple[str, ...]] = {
    role: tuple(term for term in terms if " " in term or term.isupper() is False)
    for role, terms in ROLE_KEYWORDS.items()
}

SKILL_ALIASES: dict[str, tuple[str, str]] = {
    "python": ("python", "programming"),
    "pyspark": ("python", "programming"),
    "fastapi": ("backend_api", "backend"),
    "django": ("backend_api", "backend"),
    "flask": ("backend_api", "backend"),
    "pytorch": ("deep_learning", "ml_framework"),
    "tensorflow": ("deep_learning", "ml_framework"),
    "scikit-learn": ("machine_learning", "ml_framework"),
    "sklearn": ("machine_learning", "ml_framework"),
    "hugging face": ("transformers", "llm"),
    "transformers": ("transformers", "llm"),
    "llm": ("llm", "llm"),
    "large language model": ("llm", "llm"),
    "rag": ("rag", "retrieval_augmented_generation"),
    "retrieval augmented generation": ("rag", "retrieval_augmented_generation"),
    "sentence transformers": ("embeddings", "embeddings"),
    "sentence-transformers": ("embeddings", "embeddings"),
    "embeddings": ("embeddings", "embeddings"),
    "embedding": ("embeddings", "embeddings"),
    "bge": ("embeddings", "embeddings"),
    "e5": ("embeddings", "embeddings"),
    "openai embeddings": ("embeddings", "embeddings"),
    "pinecone": ("vector_database", "vector_database"),
    "weaviate": ("vector_database", "vector_database"),
    "qdrant": ("vector_database", "vector_database"),
    "milvus": ("vector_database", "vector_database"),
    "faiss": ("vector_database", "vector_database"),
    "pgvector": ("vector_database", "vector_database"),
    "chromadb": ("vector_database", "vector_database"),
    "elasticsearch": ("search", "search"),
    "elastic search": ("search", "search"),
    "opensearch": ("search", "search"),
    "bm25": ("sparse_retrieval", "search"),
    "semantic search": ("semantic_search", "search"),
    "hybrid search": ("hybrid_search", "search"),
    "learning to rank": ("ranking", "ranking"),
    "ltr": ("ranking", "ranking"),
    "reranking": ("ranking", "ranking"),
    "ranking": ("ranking", "ranking"),
    "ndcg": ("ranking_evaluation", "evaluation"),
    "mrr": ("ranking_evaluation", "evaluation"),
    "map": ("ranking_evaluation", "evaluation"),
    "recall@k": ("ranking_evaluation", "evaluation"),
    "precision@k": ("ranking_evaluation", "evaluation"),
    "mlflow": ("mlops", "mlops"),
    "kubeflow": ("mlops", "mlops"),
    "docker": ("containerization", "mlops"),
    "kubernetes": ("containerization", "mlops"),
    "airflow": ("data_pipeline", "data"),
    "spark": ("data_pipeline", "data"),
    "kafka": ("data_pipeline", "data"),
    "sql": ("sql", "data"),
    "computer vision": ("computer_vision", "computer_vision"),
    "opencv": ("computer_vision", "computer_vision"),
    "object detection": ("computer_vision", "computer_vision"),
}

REQUIRED_MARKERS = (
    "required",
    "must have",
    "must-have",
    "need to have",
    "requirements",
    "you have",
    "strong experience",
    "hands-on experience",
)
PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "good to have",
    "ideal",
)
OPTIONAL_MARKERS = (
    "optional",
    "familiarity",
    "exposure to",
    "some experience",
)

INDUSTRY_ALIASES: dict[str, tuple[str, ...]] = {
    "recruitment": ("recruitment", "recruiting", "talent acquisition", "hiring"),
    "hrtech": ("hr tech", "hr-tech", "hrtech", "people tech", "ats"),
    "marketplace": ("marketplace", "two-sided", "matching platform", "supply demand"),
    "fintech": ("fintech", "payments", "banking", "lending", "wealthtech"),
    "healthcare": ("healthcare", "healthtech", "medical", "clinical"),
    "ecommerce": ("e-commerce", "ecommerce", "commerce", "retail"),
    "saas": ("saas", "subscription", "b2b software"),
    "software": ("software", "internet", "platform", "developer tools"),
}

LOCATION_ALIASES: dict[str, tuple[str, ...]] = {
    "pune": ("pune",),
    "noida": ("noida",),
    "bangalore": ("bangalore", "bengaluru"),
    "hyderabad": ("hyderabad",),
    "delhi_ncr": ("delhi", "ncr", "gurgaon", "gurugram"),
    "mumbai": ("mumbai",),
    "india": ("india", "indian"),
    "remote": ("remote", "work from home", "wfh"),
    "hybrid": ("hybrid",),
    "onsite": ("onsite", "on-site", "office"),
}

BEHAVIORAL_TRAIT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "startup_mindset": ("startup mindset", "0 to 1", "zero to one", "ambiguous", "fast-moving", "fast paced", "fast-paced"),
    "ownership": ("ownership", "own end-to-end", "drive independently", "accountable", "take ownership"),
    "communication": ("communication", "stakeholder", "cross-functional", "collaborate", "influence"),
    "product_thinking": ("product thinking", "product sense", "user empathy", "customer impact", "business metrics"),
    "experimentation": ("experimentation", "a/b", "ab testing", "iterate", "measure", "hypothesis"),
    "hands_on": ("hands-on", "hands on", "write code", "coding", "build systems"),
}

NEGATIVE_SIGNAL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "research_only": ("not research focused", "not purely academic", "no purely academic", "avoid pure research"),
    "consulting_only": ("no consulting background", "avoid consulting", "not services", "not agency", "avoid agency experience"),
    "non_hands_on": ("must be hands-on", "not just managing", "not management only", "must code"),
    "framework_demo_only": ("not only langchain", "not demo only", "production experience required", "not toy projects"),
    "job_hopper": ("stable tenure", "avoid frequent job changes", "not a title chaser"),
}

SENIORITY_TERMS: dict[str, tuple[str, ...]] = {
    "junior": ("junior", "entry level", "0-2 years", "1-2 years"),
    "mid": ("mid-level", "mid level", "3+ years", "3-5 years"),
    "senior": ("senior", "5+ years", "6+ years", "lead", "staff", "principal"),
    "lead": ("lead", "staff", "principal", "architect", "founding"),
}

