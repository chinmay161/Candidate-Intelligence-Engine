"""Ranking score normalization utilities."""

from __future__ import annotations

import math
from dataclasses import replace

from ranking.match_models import CandidateMatch


class ScoreNormalizer:
    """Normalize raw 0-1 scores to a 0-100 ranking scale."""

    SUPPORTED_METHODS = {"minmax", "zscore", "softmax"}

    def normalize(self, matches: tuple[CandidateMatch, ...], *, method: str = "minmax") -> tuple[CandidateMatch, ...]:
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported normalization method: {method!r}")
        if not matches:
            return ()
        if method == "minmax":
            scores = self._minmax([match.score for match in matches])
        elif method == "zscore":
            scores = self._zscore([match.score for match in matches])
        else:
            scores = self._softmax([match.score for match in matches])
        return tuple(replace(match, score=round(score, 6)) for match, score in zip(matches, scores))

    def _minmax(self, scores: list[float]) -> list[float]:
        low = min(scores)
        high = max(scores)
        if high == low:
            return [100.0 for _ in scores]
        return [((score - low) / (high - low)) * 100.0 for score in scores]

    def _zscore(self, scores: list[float]) -> list[float]:
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        stddev = math.sqrt(variance)
        if stddev == 0:
            return [100.0 for _ in scores]
        return [(1.0 / (1.0 + math.exp(-((score - mean) / stddev)))) * 100.0 for score in scores]

    def _softmax(self, scores: list[float]) -> list[float]:
        maximum = max(scores)
        exps = [math.exp(score - maximum) for score in scores]
        total = sum(exps)
        if total <= 0:
            return [0.0 for _ in scores]
        return [(value / total) * 100.0 for value in exps]
