"""End-to-end orchestrator tests with injected components (TASK-014)."""

import json

import pytest

from trendidea.agents.scanner import Scanner
from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.db import Database
from trendidea.models import Idea, IdeaStatus, Signal
from trendidea.orchestrator import Orchestrator


class FakeSource(Source):
    name = "fake"

    def fetch(self, settings, window_hours, limit=30):
        return [
            Signal(source="hn", url="http://a", title="billing automation pain", metric=100),
            Signal(source="reddit", url="http://b", title="billing automation needed", metric=80),
            Signal(source="github_trending", url="http://c", title="totally different thing"),
        ]


@pytest.fixture
def db(tmp_path):
    database = Database(path=str(tmp_path / "t.db"))
    yield database
    database.close()


def _settings(**over):
    return Settings(_env_file=None, **over)


def test_dry_run_writes_artifact_and_skips_llm(tmp_path, db):
    orch = Orchestrator(
        _settings(),
        db,
        scanner=Scanner(sources=[FakeSource()]),
        runs_dir=str(tmp_path / "runs"),
    )
    report = orch.run(dry_run=True, today="2026-06-13")

    assert report.ideas == []
    assert report.trends  # cluster labels became trends
    assert any("LLM adımları atlandı" in u for u in report.unknowns)

    # markdown + run.json artifacts exist
    assert report.markdown_path is not None
    md = open(report.markdown_path, encoding="utf-8").read()
    assert "GÜNLÜK İŞ FİKRİ RAPORU — 2026-06-13" in md
    run_json = json.loads(
        open(report.markdown_path.replace("report.md", "run.json"), encoding="utf-8").read()
    )
    assert run_json["date"] == "2026-06-13"

    # persisted to DB
    assert db.get_report_by_date("2026-06-13") is not None
    run_row = db.conn.execute("SELECT status FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    assert run_row["status"] == "success"


class FakeGenerator:
    def generate(self, clusters, max_ideas=5):
        return [
            Idea(
                title="Billing autopilot",
                signal_refs=["http://a", "http://b"],
                revenue_model="abonelik",
            )
        ]


class FakeValidator:
    def validate(self, ideas):
        for idea in ideas:
            idea.status = IdeaStatus.PASSED
            idea.confidence = 77
        return ideas


def test_full_run_with_injected_llm_agents(tmp_path, db):
    orch = Orchestrator(
        _settings(ANTHROPIC_API_KEY="x", TELEGRAM_BOT_TOKEN="y", TELEGRAM_CHAT_ID="z"),
        db,
        scanner=Scanner(sources=[FakeSource()]),
        generator=FakeGenerator(),
        validator=FakeValidator(),
        runs_dir=str(tmp_path / "runs"),
    )
    report = orch.run(dry_run=False, today="2026-06-14")

    assert len(report.ideas) == 1
    assert report.ideas[0].confidence == 77
    assert "Billing autopilot" in report.telegram_summary
    # idea persisted with PASSED status
    passed = db.get_ideas(report.run_id, status=IdeaStatus.PASSED)
    assert len(passed) == 1


def test_run_records_error_on_failure(tmp_path, db):
    class BoomScanner(Scanner):
        def scan(self, settings, window_hours=None, limit=30):
            raise RuntimeError("scan exploded")

    orch = Orchestrator(_settings(), db, scanner=BoomScanner(), runs_dir=str(tmp_path / "runs"))
    with pytest.raises(RuntimeError):
        orch.run(dry_run=True)
    row = db.conn.execute("SELECT status, error FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    assert row["status"] == "error"
    assert "scan exploded" in row["error"]
