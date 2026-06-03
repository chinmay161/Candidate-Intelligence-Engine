"""Industry classification and reusable career-industry features."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_processor.constants import CONSULTING_COMPANIES
from candidate_processor.models import Candidate, CareerHistory
from candidate_processor.normalizer import TextNormalizer, clamp


INDUSTRY_CATEGORIES = (
    "AI_ML",
    "HRTECH",
    "SAAS",
    "FINTECH",
    "ECOMMERCE",
    "HEALTHTECH",
    "MARKETPLACE",
    "SOFTWARE",
    "PRODUCT",
    "CONSULTING",
    "SERVICES",
    "MANUFACTURING",
    "LOGISTICS",
    "EDTECH",
    "MEDIA",
    "UNKNOWN",
)


@dataclass(frozen=True, slots=True)
class IndustryClassification:
    """Primary industry category, confidence, and compact matching evidence."""

    primary_industry: str
    confidence: float
    evidence: tuple[str, ...]


class IndustryClassifier:
    """Classify employer and role-history industry context."""

    CONSULTING_COMPANY_TERMS = CONSULTING_COMPANIES + (
        "tata consultancy services",
        "infosys",
        "wipro",
        "accenture",
        "cognizant",
        "capgemini",
        "hcl",
        "tech mahindra",
    )
    PRODUCT_COMPANY_INDICATORS = (
        "product",
        "saas",
        "platform",
        "marketplace",
        "software",
        "subscription",
        "users",
    )
    PRODUCT_CATEGORIES = ("AI_ML", "HRTECH", "SAAS", "FINTECH", "ECOMMERCE", "HEALTHTECH", "MARKETPLACE", "SOFTWARE", "PRODUCT")
    STARTUP_COMPANY_SIZES = ("1-10", "11-50", "51-200", "201-500")

    INDUSTRY_KEYWORDS: dict[str, tuple[str, ...]] = {
        "AI_ML": ("ai/ml", "artificial intelligence", "machine learning", "ml platform", "genai"),
        "HRTECH": ("hr-tech", "hrtech", "recruiting", "recruitment", "talent marketplace", "ats"),
        "SAAS": ("saas", "subscription", "b2b software", "cloud software"),
        "FINTECH": ("fintech", "payments", "banking", "lending", "insurance", "wealthtech"),
        "ECOMMERCE": ("e-commerce", "ecommerce", "commerce", "retail marketplace", "online retail"),
        "HEALTHTECH": ("healthtech", "healthcare", "medical", "clinical", "hospital"),
        "MARKETPLACE": ("marketplace", "two-sided", "buyer seller", "matching platform"),
        "SOFTWARE": ("software", "internet", "developer platform", "api platform"),
        "PRODUCT": PRODUCT_COMPANY_INDICATORS,
        "CONSULTING": CONSULTING_COMPANY_TERMS + ("consulting", "advisory"),
        "SERVICES": ("services", "it services", "client delivery", "outsourcing", "managed services"),
        "MANUFACTURING": ("manufacturing", "automotive", "factory", "industrial", "mechanical"),
        "LOGISTICS": ("logistics", "supply chain", "shipping", "delivery", "fleet"),
        "EDTECH": ("edtech", "education", "learning platform", "course platform"),
        "MEDIA": ("media", "publishing", "advertising", "content platform", "streaming"),
    }

    def classify(self, candidate: Candidate) -> IndustryClassification:
        """Classify a candidate's overall career industry family."""

        company_names = tuple(role.company for role in candidate.career_history)
        industries = (candidate.profile.current_industry,) + tuple(role.industry for role in candidate.career_history)
        descriptions = tuple(role.description for role in candidate.career_history)
        return self.classify_fields(company_names=company_names, industries=industries, descriptions=descriptions)

    def classify_fields(
        self,
        *,
        company_names: tuple[str, ...],
        industries: tuple[str, ...],
        descriptions: tuple[str, ...],
    ) -> IndustryClassification:
        """Classify from explicit company, industry, and description fields."""

        scores = {category: 0.0 for category in INDUSTRY_CATEGORIES if category != "UNKNOWN"}
        evidence: dict[str, list[str]] = {category: [] for category in scores}
        for company in company_names:
            self._add_scores(scores, evidence, company, 5.0, "company")
        for industry in industries:
            self._add_scores(scores, evidence, industry, 4.0, "industry")
        for description in descriptions:
            self._add_scores(scores, evidence, description, 1.5, "description")

        primary, top_score = max(scores.items(), key=lambda item: item[1])
        if top_score <= 0:
            return IndustryClassification(primary_industry="UNKNOWN", confidence=0.0, evidence=())

        sorted_scores = sorted(scores.values(), reverse=True)
        second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
        confidence = clamp((top_score - second_score * 0.25) / max(top_score + second_score, 1.0))
        return IndustryClassification(
            primary_industry=primary,
            confidence=round(confidence, 4),
            evidence=tuple(evidence[primary][:5]),
        )

    def extract_features(self, candidate: Candidate) -> dict[str, float | int]:
        """Generate reusable industry-derived candidate features."""

        role_classifications = [self._classify_role(role) for role in candidate.career_history]
        product_months = sum(
            role.duration_months
            for role, classification in zip(candidate.career_history, role_classifications)
            if classification.primary_industry in self.PRODUCT_CATEGORIES
        )
        services_roles = [
            classification.primary_industry in {"CONSULTING", "SERVICES"}
            for classification in role_classifications
        ]
        known_categories = {classification.primary_industry for classification in role_classifications if classification.primary_industry != "UNKNOWN"}
        startup_months = sum(
            role.duration_months
            for role, classification in zip(candidate.career_history, role_classifications)
            if role.company_size in self.STARTUP_COMPANY_SIZES and classification.primary_industry in self.PRODUCT_CATEGORIES
        )
        total_months = sum(role.duration_months for role in candidate.career_history)

        return {
            "product_company_exposure_months": product_months,
            "services_only_penalty": 1.0 if services_roles and all(services_roles) else 0.0,
            "industry_diversity_score": round(clamp(len(known_categories) / 4.0), 4),
            "startup_exposure_score": round(clamp(startup_months / max(total_months, 1)), 4),
        }

    def _classify_role(self, role: CareerHistory) -> IndustryClassification:
        return self.classify_fields(
            company_names=(role.company,),
            industries=(role.industry,),
            descriptions=(role.description,),
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
        for category, terms in self.INDUSTRY_KEYWORDS.items():
            matched = [term for term in terms if TextNormalizer.has_any(normalized_text, (term,))]
            if not matched:
                continue
            scores[category] += weight * min(len(matched), 3)
            evidence[category].append(f"{source}: {text[:180]}")

