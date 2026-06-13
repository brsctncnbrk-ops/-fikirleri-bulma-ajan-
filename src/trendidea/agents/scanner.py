"""Scanner agent: runs each enabled source with graceful degradation."""

from __future__ import annotations

import logging

from trendidea.agents.sources.base import ScanResult, Source
from trendidea.agents.sources.hackernews import HackerNewsSource
from trendidea.config import Settings
from trendidea.models import Signal

logger = logging.getLogger(__name__)


def default_sources() -> list[Source]:
    """The registry of sources the scanner will attempt (extended in later tasks)."""
    return [HackerNewsSource()]


class Scanner:
    """Collects raw signals from all enabled sources, never failing the whole run."""

    def __init__(self, sources: list[Source] | None = None) -> None:
        self.sources = sources if sources is not None else default_sources()

    def scan(
        self, settings: Settings, window_hours: int | None = None, limit: int = 30
    ) -> tuple[list[Signal], list[ScanResult]]:
        window = window_hours if window_hours is not None else settings.scan_window_hours
        all_signals: list[Signal] = []
        results: list[ScanResult] = []

        for source in self.sources:
            if not source.enabled(settings):
                logger.info("source skipped (no key)", extra={"source": source.name})
                results.append(ScanResult(name=source.name, ok=False, error="no_key"))
                continue
            try:
                signals = source.fetch(settings, window, limit)
                all_signals.extend(signals)
                results.append(ScanResult(name=source.name, ok=True, count=len(signals)))
                logger.info("source scanned", extra={"source": source.name, "count": len(signals)})
            except Exception as exc:  # graceful degrade: one source must not kill the run
                logger.warning("source failed", extra={"source": source.name, "error": str(exc)})
                results.append(ScanResult(name=source.name, ok=False, error=str(exc)))

        return all_signals, results
