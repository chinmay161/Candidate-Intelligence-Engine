"""Candidate processing and feature extraction pipeline."""

from candidate_processor.feature_registry import DEFAULT_FEATURE_REGISTRY, FeatureDefinition, FeatureRegistry
from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.feature_store import CandidateFeatureStore
from candidate_processor.industry_classifier import IndustryClassification, IndustryClassifier
from candidate_processor.models import Candidate, CandidateFeatureRecord
from candidate_processor.parser import CandidateParser
from candidate_processor.role_classifier import RoleClassification, RoleClassifier
from candidate_processor.text_builder import CandidateTextBuilder

__all__ = [
    "Candidate",
    "CandidateFeatureExtractor",
    "CandidateFeatureRecord",
    "CandidateFeatureStore",
    "CandidateParser",
    "CandidateTextBuilder",
    "DEFAULT_FEATURE_REGISTRY",
    "FeatureDefinition",
    "FeatureRegistry",
    "IndustryClassification",
    "IndustryClassifier",
    "RoleClassification",
    "RoleClassifier",
]
