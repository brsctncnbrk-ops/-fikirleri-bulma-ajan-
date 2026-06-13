"""Round-trip tests for the SQLite repository layer (TASK-004)."""

import pytest

from trendidea.db import Database
from trendidea.models import Cluster, Competitor, Idea, IdeaStatus, Report, Signal


@pytest.fixture
def db(tmp_path):
    database = Database(path=str(tmp_path / "test.db"))
    yield database
    database.close()


def test_run_lifecycle(db):
    run = db.create_run()
    assert run.id is not None
    db.finish_run(run.id, status="success", token_usage=123, cost_estimate=0.5)
    row = db.conn.execute("SELECT * FROM runs WHERE id=?", (run.id,)).fetchone()
    assert row["status"] == "success"
    assert row["token_usage"] == 123


def test_signal_roundtrip(db):
    run = db.create_run()
    db.add_signal(Signal(run_id=run.id, source="hackernews", url="http://x", title="t", metric=42))
    signals = db.get_signals(run.id)
    assert len(signals) == 1
    assert signals[0].metric == 42
    assert signals[0].source == "hackernews"


def test_cluster_roundtrip(db):
    run = db.create_run()
    s = Signal(run_id=run.id, source="hn", url="http://x", title="t")
    db.add_signal(s)
    cid = db.add_cluster(Cluster(run_id=run.id, label="ai tools", score=0.9, signals=[s]))
    assert cid is not None


def test_idea_roundtrip_and_status_update(db):
    run = db.create_run()
    idea = Idea(
        run_id=run.id,
        title="AI changelog writer",
        signal_refs=["http://a", "http://b"],
        revenue_model="subscription",
        competitors=[Competitor(name="Acme", url="http://acme", verified=True)],
        status=IdeaStatus.CANDIDATE,
    )
    db.add_idea(idea)

    fetched = db.get_ideas(run.id)
    assert len(fetched) == 1
    assert fetched[0].signal_refs == ["http://a", "http://b"]
    assert fetched[0].competitors[0].name == "Acme"
    assert fetched[0].status == IdeaStatus.CANDIDATE

    db.update_idea_status(idea.id, IdeaStatus.PASSED, confidence=78, notes="verified")
    passed = db.get_ideas(run.id, status=IdeaStatus.PASSED)
    assert len(passed) == 1
    assert passed[0].confidence == 78


def test_report_roundtrip(db):
    run = db.create_run()
    db.add_report(
        Report(
            run_id=run.id,
            date="2026-06-13",
            scanned_sources=[{"name": "hackernews", "ok": True, "count": 10}],
            telegram_summary="özet",
        )
    )
    report = db.get_report_by_date("2026-06-13")
    assert report is not None
    assert report.scanned_sources[0]["name"] == "hackernews"


def test_session_upsert(db):
    db.save_session("123", {"last_report": "2026-06-13"})
    assert db.get_session("123")["last_report"] == "2026-06-13"
    db.save_session("123", {"last_report": "2026-06-14"})
    assert db.get_session("123")["last_report"] == "2026-06-14"
    assert db.get_session("missing") == {}
