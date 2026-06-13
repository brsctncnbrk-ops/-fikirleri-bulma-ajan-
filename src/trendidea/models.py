"""Dataclasses exchanged between agents (the structured inter-agent contract)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class IdeaStatus(StrEnum):
    CANDIDATE = "candidate"
    PASSED = "passed"
    REJECTED = "rejected"


@dataclass
class Signal:
    """A raw trend signal collected from one source."""

    source: str
    url: str
    title: str
    summary: str = ""
    published_at: str | None = None  # ISO 8601
    metric: int = 0  # upvotes / stars / comments
    fetched_at: str | None = None
    run_id: int | None = None
    id: int | None = None


@dataclass
class Cluster:
    """A group of related signals representing one recurring demand/pain."""

    label: str
    score: float = 0.0
    signals: list[Signal] = field(default_factory=list)
    run_id: int | None = None
    id: int | None = None


@dataclass
class Competitor:
    name: str
    url: str = ""
    verified: bool = False
    note: str = ""


@dataclass
class Idea:
    """A concrete, Claude-Code-buildable business idea (Reality Rule template)."""

    title: str
    signal_refs: list[str] = field(default_factory=list)  # source URLs
    target_customer: str = "TBD"
    pain: str = "TBD"
    revenue_model: str = "TBD"
    first_revenue_estimate: str = "TBD"
    mvp_scope: str = "TBD"
    dev_time: str = "TBD"
    competitors: list[Competitor] = field(default_factory=list)
    main_risk: str = "TBD"
    confidence: int = 0  # 0-100
    validation_notes: str = ""
    status: IdeaStatus = IdeaStatus.CANDIDATE
    run_id: int | None = None
    id: int | None = None


@dataclass
class Report:
    """A daily report aggregating scanned sources, trends and passing ideas."""

    date: str  # YYYY-MM-DD
    scanned_sources: list[dict] = field(default_factory=list)  # {name, ok, count|error}
    trends: list[str] = field(default_factory=list)
    ideas: list[Idea] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    markdown_path: str | None = None
    telegram_summary: str = ""
    token_usage: int = 0
    cost_estimate: float = 0.0
    cost_configured: bool = False
    run_id: int | None = None
    id: int | None = None


@dataclass
class RunRecord:
    """Audit record for a single pipeline execution."""

    started_at: str
    finished_at: str | None = None
    status: str = "running"
    token_usage: int = 0
    cost_estimate: float = 0.0
    error: str | None = None
    id: int | None = None


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")
