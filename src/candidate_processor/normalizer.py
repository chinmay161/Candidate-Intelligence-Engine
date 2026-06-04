"""Text normalization and reusable scoring helpers."""

from __future__ import annotations

import math
import re
from functools import lru_cache
from statistics import mean
from typing import Iterable, Sequence

from candidate_processor.constants import ROLE_FAMILY_TERMS


class TextNormalizer:
    """Cached text utilities shared by extraction and evidence layers."""

    _non_word_pattern = re.compile(r"[^a-z0-9@+./#-]+")
    _sentence_split_pattern = re.compile(r"(?<=[.!?])\s+")
    _years_pattern = re.compile(r"(?P<years>\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", re.IGNORECASE)

    @classmethod
    @lru_cache(maxsize=200_000)
    def normalize(cls, text: str) -> str:
        lowered = text.casefold()
        return cls._non_word_pattern.sub(" ", lowered).strip()

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        normalized = cls.normalize(text)
        return [token for token in normalized.split() if token]

    @classmethod
    @lru_cache(maxsize=50_000)
    def term_pattern(cls, terms: tuple[str, ...]) -> re.Pattern[str]:
        escaped = sorted((re.escape(term.casefold()) for term in terms), key=len, reverse=True)
        return re.compile(r"(?<![a-z0-9])(?:" + "|".join(escaped) + r")(?![a-z0-9])", re.IGNORECASE)

    @classmethod
    def count_terms(cls, text: str, terms: Sequence[str]) -> int:
        if not terms:
            return 0
        normalized = cls.normalize(text)
        return sum(normalized.count(term) for term in cls.normalize_terms(tuple(terms)) if term)

    @classmethod
    def count_terms_normalized(cls, normalized_text: str, terms: Sequence[str]) -> int:
        if not terms:
            return 0
        return sum(normalized_text.count(term) for term in cls.normalize_terms(tuple(terms)) if term)

    @classmethod
    def has_any(cls, text: str, terms: Sequence[str]) -> bool:
        if not terms:
            return False
        normalized = cls.normalize(text)
        return any(term in normalized for term in cls.normalize_terms(tuple(terms)) if term)

    @classmethod
    def has_any_normalized(cls, normalized_text: str, terms: Sequence[str]) -> bool:
        if not terms:
            return False
        return any(term in normalized_text for term in cls.normalize_terms(tuple(terms)) if term)

    @classmethod
    @lru_cache(maxsize=2_000)
    def normalize_terms(cls, terms: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(cls.normalize(term) for term in terms)

    @classmethod
    def sentences(cls, text: str) -> list[str]:
        normalized_space = " ".join(text.split())
        if not normalized_space:
            return []
        sentences = cls._sentence_split_pattern.split(normalized_space)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    @classmethod
    def snippets_with_terms(cls, text: str, terms: Sequence[str], limit: int = 3) -> list[str]:
        if not terms:
            return []
        pattern = cls.term_pattern(tuple(terms))
        snippets: list[str] = []
        for sentence in cls.sentences(text):
            if pattern.search(sentence):
                snippets.append(sentence[:280])
                if len(snippets) >= limit:
                    break
        return snippets

    @classmethod
    def extract_years(cls, text: str) -> list[float]:
        return [float(match.group("years")) for match in cls._years_pattern.finditer(text)]

    @classmethod
    def role_family(cls, text: str) -> str:
        normalized = cls.normalize(text)
        scores = {
            family: cls.count_terms_normalized(normalized, terms)
            for family, terms in ROLE_FAMILY_TERMS.items()
        }
        if not scores or max(scores.values()) == 0:
            return "unknown"
        return max(scores, key=scores.get)


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def safe_mean(values: Iterable[float], default: float = 0.0) -> float:
    collected = list(values)
    if not collected:
        return default
    return float(mean(collected))


def log_scale(value: float, cap: float) -> float:
    if cap <= 0:
        return 0.0
    return clamp(math.log1p(max(value, 0.0)) / math.log1p(cap))


def months_between_approx(start_year: int, end_year: int) -> int:
    return max(0, (end_year - start_year) * 12)


def score_by_terms(text: str, terms: Sequence[str], cap: int = 5) -> float:
    return clamp(TextNormalizer.count_terms(text, terms) / cap)

def score_by_terms_normalized(normalized_text: str, terms: Sequence[str], cap: int = 5) -> float:
    return clamp(TextNormalizer.count_terms_normalized(normalized_text, terms) / cap)


def weighted_flag(condition: bool) -> float:
    return 1.0 if condition else 0.0
