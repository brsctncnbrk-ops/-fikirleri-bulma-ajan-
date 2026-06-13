"""Signal Processor: dedupe, cluster by keyword overlap, and score by demand.

Deterministic (no LLM) so it is fast, cheap and fully testable. A cluster seen
across multiple sources is treated as a stronger demand signal.
"""

from __future__ import annotations

import math
import re

from trendidea.models import Cluster, Signal

_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "with",
    "to",
    "of",
    "in",
    "on",
    "is",
    "are",
    "be",
    "your",
    "you",
    "how",
    "what",
    "why",
    "new",
    "best",
    "this",
    "that",
    "it",
    "we",
    "i",
    "my",
    "show",
    "hn",
    "ask",
    "using",
    "use",
    "app",
    "tool",
    "tools",
    "via",
    "from",
    "at",
    "by",
    "as",
    "vs",
}
_WORD_RE = re.compile(r"[a-zçğıöşü0-9]+", re.IGNORECASE)


def tokenize(text: str) -> set[str]:
    """Lowercase keyword set, dropping stopwords and very short tokens."""
    return {w for w in _WORD_RE.findall(text.lower()) if len(w) > 2 and w not in _STOPWORDS}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class SignalProcessor:
    def __init__(self, similarity_threshold: float = 0.25) -> None:
        self.similarity_threshold = similarity_threshold

    def process(self, signals: list[Signal]) -> list[Cluster]:
        clean = self._dedupe(signals)
        clusters = self._cluster(clean)
        for cluster in clusters:
            cluster.score = self._score(cluster)
        clusters.sort(key=lambda c: c.score, reverse=True)
        return clusters

    @staticmethod
    def _dedupe(signals: list[Signal]) -> list[Signal]:
        seen: set[str] = set()
        out: list[Signal] = []
        for s in signals:
            if not s.title or len(s.title) < 5:
                continue
            key = s.url or s.title
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
        return out

    def _cluster(self, signals: list[Signal]) -> list[Cluster]:
        clusters: list[Cluster] = []
        keywords: list[set[str]] = []
        for signal in signals:
            tokens = tokenize(f"{signal.title} {signal.summary}")
            placed = False
            for idx, cluster in enumerate(clusters):
                if _jaccard(tokens, keywords[idx]) >= self.similarity_threshold:
                    cluster.signals.append(signal)
                    keywords[idx] |= tokens
                    placed = True
                    break
            if not placed:
                clusters.append(Cluster(label=self._label(tokens), signals=[signal]))
                keywords.append(tokens)
        # refresh labels now that clusters are complete
        for idx, cluster in enumerate(clusters):
            cluster.label = self._label(keywords[idx])
        return clusters

    @staticmethod
    def _label(tokens: set[str]) -> str:
        top = sorted(tokens)[:4]
        return ", ".join(top) if top else "misc"

    @staticmethod
    def _score(cluster: Cluster) -> float:
        distinct_sources = len({s.source for s in cluster.signals})
        total_metric = sum(s.metric for s in cluster.signals)
        size = len(cluster.signals)
        # cross-source recurrence dominates; metric and size contribute log-scaled
        score = (
            0.5 * min(distinct_sources / 3.0, 1.0)
            + 0.3 * min(math.log1p(total_metric) / 7.0, 1.0)
            + 0.2 * min(size / 5.0, 1.0)
        )
        return round(score, 4)
