"""Role-family classification for candidate profiles."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_processor.models import Candidate, CareerHistory
from candidate_processor.normalizer import TextNormalizer, clamp


ROLE_FAMILIES = (
    "AI_ENGINEER",
    "ML_ENGINEER",
    "DATA_ENGINEER",
    "DATA_SCIENTIST",
    "BACKEND_ENGINEER",
    "SOFTWARE_ENGINEER",
    "DEVOPS_ENGINEER",
    "MLOPS_ENGINEER",
    "PRODUCT_MANAGER",
    "BUSINESS_ANALYST",
    "MARKETING",
    "SALES",
    "HR",
    "OPERATIONS",
    "ACCOUNTING",
    "SUPPORT",
    "RESEARCHER",
    "UNKNOWN",
)


@dataclass(frozen=True, slots=True)
class RoleClassification:
    """Primary role family, confidence, and compact matching evidence."""

    primary_role: str
    confidence: float
    evidence: tuple[str, ...]


class RoleClassifier:
    """Classify candidates into reusable role families with weighted voting."""

    TITLE_WEIGHT = 8.0
    HEADLINE_WEIGHT = 3.0
    SUMMARY_WEIGHT = 0.75
    ROLE_TITLE_WEIGHT = 4.0
    ROLE_DESCRIPTION_WEIGHT = 2.5

    ROLE_KEYWORDS: dict[str, tuple[str, ...]] = {
        "AI_ENGINEER": ("ai engineer", "artificial intelligence engineer", "genai engineer", "llm engineer"),
        "ML_ENGINEER": ("machine learning engineer", "ml engineer", "applied ml", "applied scientist"),
        "DATA_ENGINEER": ("data engineer", "etl", "spark", "kafka", "warehouse", "databricks"),
        "DATA_SCIENTIST": ("data scientist", "data science", "statistical modeling", "experimentation"),
        "BACKEND_ENGINEER": ("backend engineer", "backend developer", "api engineer", "server-side"),
        "SOFTWARE_ENGINEER": ("software engineer", "software developer", "full stack", "full-stack", "platform engineer"),
        "DEVOPS_ENGINEER": ("devops", "site reliability", "sre", "infrastructure engineer", "kubernetes"),
        "MLOPS_ENGINEER": ("mlops", "ml platform", "model serving", "model deployment", "mlflow", "kubeflow"),
        "PRODUCT_MANAGER": ("product manager", "pm", "product owner", "product lead"),
        "BUSINESS_ANALYST": ("business analyst", "analytics consultant", "business intelligence", "bi analyst"),
        "MARKETING": ("marketing manager", "marketing", "seo", "growth marketer", "content marketing"),
        "SALES": ("sales manager", "sales", "account executive", "business development", "bdm"),
        "HR": ("hr", "human resources", "recruiter", "talent acquisition", "people operations"),
        "OPERATIONS": ("operations manager", "operations", "program coordinator", "process associate"),
        "ACCOUNTING": ("accountant", "accounting", "finance executive", "accounts payable", "tax analyst"),
        "SUPPORT": ("customer support", "support engineer", "technical support", "helpdesk", "service desk"),
        "RESEARCHER": ("research scientist", "researcher", "phd", "postdoc", "publication", "research lab"),
    }

    def classify(self, candidate: Candidate) -> RoleClassification:
        """Classify a typed candidate record."""

        return self.classify_texts(
            current_title=candidate.profile.current_title,
            headline=candidate.profile.headline,
            summary=candidate.profile.summary,
            career_history=candidate.career_history,
        )

    def classify_texts(
        self,
        *,
        current_title: str,
        headline: str,
        summary: str,
        career_history: tuple[CareerHistory, ...],
    ) -> RoleClassification:
        """Classify from explicit text fields and career history."""

        scores = {family: 0.0 for family in ROLE_FAMILIES if family != "UNKNOWN"}
        evidence: dict[str, list[str]] = {family: [] for family in scores}

        self._add_scores(scores, evidence, current_title, self.TITLE_WEIGHT, "current title")
        self._add_scores(scores, evidence, headline, self.HEADLINE_WEIGHT, "headline")
        self._add_scores(scores, evidence, summary, self.SUMMARY_WEIGHT, "summary")
        for role in career_history:
            self._add_scores(scores, evidence, role.title, self.ROLE_TITLE_WEIGHT, f"role title at {role.company}")
            self._add_scores(
                scores,
                evidence,
                role.description,
                self.ROLE_DESCRIPTION_WEIGHT,
                f"role description at {role.company}",
            )

        primary, top_score = max(scores.items(), key=lambda item: item[1])
        if top_score <= 0:
            return RoleClassification(primary_role="UNKNOWN", confidence=0.0, evidence=())

        sorted_scores = sorted(scores.values(), reverse=True)
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
        confidence = clamp((top_score - second_score * 0.35) / max(top_score + second_score, 1.0))
        return RoleClassification(
            primary_role=primary,
            confidence=round(confidence, 4),
            evidence=tuple(evidence[primary][:5]),
        )

    def _add_scores(
        self,
        scores: dict[str, float],
        evidence: dict[str, list[str]],
        text: str,
        weight: float,
        source: str,
    ) -> None:
        normalized_text = TextNormalizer.normalize(text)
        if not normalized_text:
            return
        for family, terms in self.ROLE_KEYWORDS.items():
            matched = [term for term in terms if TextNormalizer.has_any(normalized_text, (term,))]
            if not matched:
                continue
            score = weight * min(len(matched), 3)
            scores[family] += score
            evidence[family].append(f"{source}: {text[:180]}")

