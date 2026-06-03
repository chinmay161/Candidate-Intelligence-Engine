"""Candidate processing and feature extraction pipeline."""

from candidate_processor.feature_extractor import CandidateFeatureExtractor
from candidate_processor.feature_store import CandidateFeatureStore
from candidate_processor.models import Candidate, CandidateFeatureRecord
from candidate_processor.parser import CandidateParser

__all__ = [
    "Candidate",
    "CandidateFeatureExtractor",
    "CandidateFeatureRecord",
    "CandidateFeatureStore",
    "CandidateParser",
]
