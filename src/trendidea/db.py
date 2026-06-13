"""SQLite schema and a thin repository layer (stdlib sqlite3 only)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime

from trendidea.models import (
    Cluster,
    Competitor,
    Idea,
    IdeaStatus,
    Report,
    RunRecord,
    Signal,
    now_iso,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    token_usage INTEGER NOT NULL DEFAULT 0,
    cost_estimate REAL NOT NULL DEFAULT 0,
    error TEXT
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT DEFAULT '',
    published_at TEXT,
    metric INTEGER DEFAULT 0,
    fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    label TEXT NOT NULL,
    score REAL DEFAULT 0,
    signal_ids_json TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    title TEXT NOT NULL,
    signal_refs_json TEXT DEFAULT '[]',
    target_customer TEXT DEFAULT 'TBD',
    pain TEXT DEFAULT 'TBD',
    revenue_model TEXT DEFAULT 'TBD',
    first_revenue_estimate TEXT DEFAULT 'TBD',
    mvp_scope TEXT DEFAULT 'TBD',
    dev_time TEXT DEFAULT 'TBD',
    competitors_json TEXT DEFAULT '[]',
    main_risk TEXT DEFAULT 'TBD',
    confidence INTEGER DEFAULT 0,
    validation_notes TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'candidate'
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    date TEXT NOT NULL,
    markdown_path TEXT,
    telegram_summary TEXT DEFAULT '',
    scanned_sources_json TEXT DEFAULT '[]',
    trends_json TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS sessions (
    chat_id TEXT PRIMARY KEY,
    context_json TEXT DEFAULT '{}',
    updated_at TEXT
);
"""


class Database:
    """Lightweight repository over a SQLite connection."""

    def __init__(self, path: str = "trendidea.db") -> None:
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # --- runs -------------------------------------------------------------
    def create_run(self) -> RunRecord:
        cur = self.conn.execute("INSERT INTO runs (started_at) VALUES (?)", (now_iso(),))
        self.conn.commit()
        return RunRecord(id=cur.lastrowid, started_at=now_iso())

    def finish_run(
        self,
        run_id: int,
        status: str,
        token_usage: int = 0,
        cost_estimate: float = 0.0,
        error: str | None = None,
    ) -> None:
        self.conn.execute(
            "UPDATE runs SET finished_at=?, status=?, token_usage=?, cost_estimate=?, error=? "
            "WHERE id=?",
            (now_iso(), status, token_usage, cost_estimate, error, run_id),
        )
        self.conn.commit()

    # --- signals ----------------------------------------------------------
    def add_signal(self, signal: Signal) -> int:
        cur = self.conn.execute(
            "INSERT INTO signals (run_id, source, url, title, summary, published_at, "
            "metric, fetched_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                signal.run_id,
                signal.source,
                signal.url,
                signal.title,
                signal.summary,
                signal.published_at,
                signal.metric,
                signal.fetched_at or now_iso(),
            ),
        )
        self.conn.commit()
        signal.id = cur.lastrowid
        return cur.lastrowid

    def get_signals(self, run_id: int) -> list[Signal]:
        rows = self.conn.execute("SELECT * FROM signals WHERE run_id=?", (run_id,)).fetchall()
        return [
            Signal(
                id=r["id"],
                run_id=r["run_id"],
                source=r["source"],
                url=r["url"],
                title=r["title"],
                summary=r["summary"],
                published_at=r["published_at"],
                metric=r["metric"],
                fetched_at=r["fetched_at"],
            )
            for r in rows
        ]

    # --- clusters ---------------------------------------------------------
    def add_cluster(self, cluster: Cluster) -> int:
        signal_ids = [s.id for s in cluster.signals if s.id is not None]
        cur = self.conn.execute(
            "INSERT INTO clusters (run_id, label, score, signal_ids_json) VALUES (?,?,?,?)",
            (cluster.run_id, cluster.label, cluster.score, json.dumps(signal_ids)),
        )
        self.conn.commit()
        cluster.id = cur.lastrowid
        return cur.lastrowid

    # --- ideas ------------------------------------------------------------
    def add_idea(self, idea: Idea) -> int:
        cur = self.conn.execute(
            "INSERT INTO ideas (run_id, title, signal_refs_json, target_customer, pain, "
            "revenue_model, first_revenue_estimate, mvp_scope, dev_time, competitors_json, "
            "main_risk, confidence, validation_notes, status) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                idea.run_id,
                idea.title,
                json.dumps(idea.signal_refs, ensure_ascii=False),
                idea.target_customer,
                idea.pain,
                idea.revenue_model,
                idea.first_revenue_estimate,
                idea.mvp_scope,
                idea.dev_time,
                json.dumps([asdict(c) for c in idea.competitors], ensure_ascii=False),
                idea.main_risk,
                idea.confidence,
                idea.validation_notes,
                idea.status.value if isinstance(idea.status, IdeaStatus) else str(idea.status),
            ),
        )
        self.conn.commit()
        idea.id = cur.lastrowid
        return cur.lastrowid

    def update_idea_status(
        self, idea_id: int, status: IdeaStatus, confidence: int, notes: str
    ) -> None:
        self.conn.execute(
            "UPDATE ideas SET status=?, confidence=?, validation_notes=? WHERE id=?",
            (status.value, confidence, notes, idea_id),
        )
        self.conn.commit()

    def get_ideas(self, run_id: int, status: IdeaStatus | None = None) -> list[Idea]:
        if status is None:
            rows = self.conn.execute("SELECT * FROM ideas WHERE run_id=?", (run_id,)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM ideas WHERE run_id=? AND status=?", (run_id, status.value)
            ).fetchall()
        return [self._row_to_idea(r) for r in rows]

    @staticmethod
    def _row_to_idea(r: sqlite3.Row) -> Idea:
        return Idea(
            id=r["id"],
            run_id=r["run_id"],
            title=r["title"],
            signal_refs=json.loads(r["signal_refs_json"]),
            target_customer=r["target_customer"],
            pain=r["pain"],
            revenue_model=r["revenue_model"],
            first_revenue_estimate=r["first_revenue_estimate"],
            mvp_scope=r["mvp_scope"],
            dev_time=r["dev_time"],
            competitors=[Competitor(**c) for c in json.loads(r["competitors_json"])],
            main_risk=r["main_risk"],
            confidence=r["confidence"],
            validation_notes=r["validation_notes"],
            status=IdeaStatus(r["status"]),
        )

    # --- reports ----------------------------------------------------------
    def add_report(self, report: Report) -> int:
        cur = self.conn.execute(
            "INSERT INTO reports (run_id, date, markdown_path, telegram_summary, "
            "scanned_sources_json, trends_json) VALUES (?,?,?,?,?,?)",
            (
                report.run_id,
                report.date,
                report.markdown_path,
                report.telegram_summary,
                json.dumps(report.scanned_sources, ensure_ascii=False),
                json.dumps(report.trends, ensure_ascii=False),
            ),
        )
        self.conn.commit()
        report.id = cur.lastrowid
        return cur.lastrowid

    def get_report_by_date(self, date: str) -> Report | None:
        r = self.conn.execute(
            "SELECT * FROM reports WHERE date=? ORDER BY id DESC LIMIT 1", (date,)
        ).fetchone()
        if r is None:
            return None
        return Report(
            id=r["id"],
            run_id=r["run_id"],
            date=r["date"],
            markdown_path=r["markdown_path"],
            telegram_summary=r["telegram_summary"],
            scanned_sources=json.loads(r["scanned_sources_json"]),
            trends=json.loads(r["trends_json"]),
        )

    def get_latest_report(self) -> Report | None:
        r = self.conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 1").fetchone()
        if r is None:
            return None
        return Report(
            id=r["id"],
            run_id=r["run_id"],
            date=r["date"],
            markdown_path=r["markdown_path"],
            telegram_summary=r["telegram_summary"],
            scanned_sources=json.loads(r["scanned_sources_json"]),
            trends=json.loads(r["trends_json"]),
        )

    # --- sessions ---------------------------------------------------------
    def save_session(self, chat_id: str, context: dict) -> None:
        self.conn.execute(
            "INSERT INTO sessions (chat_id, context_json, updated_at) VALUES (?,?,?) "
            "ON CONFLICT(chat_id) DO UPDATE SET context_json=excluded.context_json, "
            "updated_at=excluded.updated_at",
            (chat_id, json.dumps(context, ensure_ascii=False), datetime.utcnow().isoformat()),
        )
        self.conn.commit()

    def get_session(self, chat_id: str) -> dict:
        r = self.conn.execute(
            "SELECT context_json FROM sessions WHERE chat_id=?", (chat_id,)
        ).fetchone()
        return json.loads(r["context_json"]) if r else {}
