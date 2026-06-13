"""Structured (JSON) logging setup and a simple LLM cost/token tracker."""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field


class JsonFormatter(logging.Formatter):
    """Minimal JSON log formatter (stdlib-only)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # include any extra structured fields attached via logger.*(..., extra={...})
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


_RESERVED = set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime", "taskName"}


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging once with a JSON handler to stderr."""
    root = logging.getLogger()
    root.setLevel(level.upper())
    # avoid duplicate handlers on repeated setup (tests, reloads)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


@dataclass
class CostTracker:
    """Accumulates LLM token usage across a run for cost visibility."""

    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    by_model: dict[str, dict[str, int]] = field(default_factory=dict)

    def add(self, model: str, input_tokens: int, output_tokens: int) -> None:
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        bucket = self.by_model.setdefault(model, {"input": 0, "output": 0, "calls": 0})
        bucket["input"] += input_tokens
        bucket["output"] += output_tokens
        bucket["calls"] += 1

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def estimate_cost(self, price_input_per_mtok: float, price_output_per_mtok: float) -> float:
        """USD estimate from configured per-1M-token prices (0 if not configured)."""
        cost = (
            self.input_tokens / 1_000_000 * price_input_per_mtok
            + self.output_tokens / 1_000_000 * price_output_per_mtok
        )
        return round(cost, 4)

    def summary(self) -> dict:
        return {
            "calls": self.calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "by_model": self.by_model,
        }
