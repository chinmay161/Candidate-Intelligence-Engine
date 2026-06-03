"""Heap-based top-k candidate selection."""

from __future__ import annotations

import heapq

from collections.abc import Iterable

from ranking.match_models import CandidateMatch


class TopKSelector:
    """Select high-scoring candidates without sorting a full pool."""

    def select(self, matches: Iterable[CandidateMatch], *, k: int = 100) -> tuple[CandidateMatch, ...]:
        if k <= 0:
            return ()
        heap: list[tuple[float, int, CandidateMatch]] = []
        for index, match in enumerate(matches):
            item = (match.score, -index, match)
            if len(heap) < k:
                heapq.heappush(heap, item)
            elif item > heap[0]:
                heapq.heapreplace(heap, item)
        selected = sorted(heap, key=lambda item: (-item[0], -item[1]))
        return tuple(item[2] for item in selected)
