"""Detection of explicit negative fit signals in job descriptions."""

from __future__ import annotations

from candidate_processor.normalizer import TextNormalizer
from jd_parser.dictionaries import NEGATIVE_SIGNAL_KEYWORDS


class NegativeSignalDetector:
    """Detect who the company explicitly does not want."""

    def detect(self, jd_text: str) -> tuple[str, ...]:
        """Return canonical negative signal names in deterministic order."""

        signals: list[str] = []
        for signal, terms in NEGATIVE_SIGNAL_KEYWORDS.items():
            if TextNormalizer.has_any(jd_text, terms):
                signals.append(signal)
        return tuple(signals)

