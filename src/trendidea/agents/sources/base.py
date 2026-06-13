"""Source abstraction: every trend source implements this contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from trendidea.config import Settings
from trendidea.models import Signal


@dataclass
class ScanResult:
    """Outcome of scanning one source (for the report's source-status section)."""

    name: str
    ok: bool
    count: int = 0
    error: str | None = None

    def as_dict(self) -> dict:
        return {"name": self.name, "ok": self.ok, "count": self.count, "error": self.error}


class Source(ABC):
    """Base class for a trend source."""

    name: str = "base"

    def enabled(self, settings: Settings) -> bool:
        """Whether this source can run with the current configuration."""
        return True

    @abstractmethod
    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        """Return recent signals; raise on failure (scanner handles graceful skip)."""
        raise NotImplementedError
