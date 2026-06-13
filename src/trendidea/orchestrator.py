"""Orchestrator: runs the full pipeline and records an auditable run artifact."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from trendidea.agents.reporter import Reporter
from trendidea.agents.scanner import Scanner
from trendidea.agents.signal_processor import SignalProcessor
from trendidea.config import Settings
from trendidea.db import Database
from trendidea.logging_conf import CostTracker
from trendidea.models import IdeaStatus, Report

logger = logging.getLogger(__name__)

TOP_TRENDS = 5


class Orchestrator:
    """Coordinates scan -> process -> generate -> validate -> report -> persist."""

    def __init__(
        self,
        settings: Settings,
        db: Database,
        scanner: Scanner | None = None,
        processor: SignalProcessor | None = None,
        reporter: Reporter | None = None,
        generator=None,
        validator=None,
        runs_dir: str = "runs",
    ) -> None:
        self.settings = settings
        self.db = db
        self.scanner = scanner or Scanner()
        self.processor = processor or SignalProcessor()
        self.reporter = reporter or Reporter()
        self._generator = generator
        self._validator = validator
        self.runs_dir = Path(runs_dir)

    def run(self, dry_run: bool = False, today: str | None = None) -> Report:
        today = today or date.today().isoformat()
        run_rec = self.db.create_run()
        cost = CostTracker()
        try:
            signals, scan_results = self.scanner.scan(self.settings)
            for s in signals:
                s.run_id = run_rec.id
                self.db.add_signal(s)

            clusters = self.processor.process(signals)
            for c in clusters:
                c.run_id = run_rec.id
                self.db.add_cluster(c)
            trends = [c.label for c in clusters[:TOP_TRENDS]]

            ideas = []
            unknowns: list[str] = []
            if dry_run or not self.settings.has_anthropic:
                unknowns.append("LLM adımları atlandı (dry-run / anahtar yok); fikir üretilmedi.")
            else:
                ideas = self._generate_and_validate(clusters, run_rec.id, cost)

            cost_estimate = cost.estimate_cost(
                self.settings.price_input_per_mtok, self.settings.price_output_per_mtok
            )
            previous = self.db.get_report_by_date(self._yesterday(today))
            report = self.reporter.build(
                date=today,
                ideas=ideas,
                scan_results=scan_results,
                trends=trends,
                unknowns=unknowns,
                run_id=run_rec.id,
                previous_trends=previous.trends if previous else [],
                token_usage=cost.total_tokens,
                cost_estimate=cost_estimate,
                cost_configured=self.settings.pricing_configured,
            )
            report.markdown_path = self._write_artifacts(run_rec.id, report, cost)
            self.db.add_report(report)
            self.db.finish_run(run_rec.id, "success", cost.total_tokens, cost_estimate, error=None)
            logger.info(
                "run complete",
                extra={"run_id": run_rec.id, "ideas": len(ideas), "tokens": cost.total_tokens},
            )
            return report
        except Exception as exc:
            self.db.finish_run(run_rec.id, "error", cost.total_tokens, 0.0, error=str(exc))
            logger.exception("run failed", extra={"run_id": run_rec.id})
            raise

    def _generate_and_validate(self, clusters, run_id: int, cost: CostTracker):
        from trendidea.agents.idea_generator import IdeaGenerator
        from trendidea.agents.validator import Validator
        from trendidea.llm import LLMClient

        llm = LLMClient(self.settings, cost_tracker=cost)
        generator = self._generator or IdeaGenerator(llm)
        validator = self._validator or Validator(llm)

        candidates = generator.generate(clusters)
        for idea in candidates:
            idea.run_id = run_id
            self.db.add_idea(idea)

        passed = validator.validate(candidates)
        for idea in candidates:
            if idea.id is not None:
                self.db.update_idea_status(
                    idea.id, idea.status, idea.confidence, idea.validation_notes
                )
        return [i for i in passed if i.status == IdeaStatus.PASSED]

    def _write_artifacts(self, run_id: int, report: Report, cost: CostTracker) -> str:
        stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        run_path = self.runs_dir / f"{stamp}_run{run_id}"
        run_path.mkdir(parents=True, exist_ok=True)

        md_path = run_path / "report.md"
        md_path.write_text(self.reporter.render_markdown(report), encoding="utf-8")

        (run_path / "run.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "date": report.date,
                    "scanned_sources": report.scanned_sources,
                    "trends": report.trends,
                    "idea_count": len(report.ideas),
                    "cost": cost.summary(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return str(md_path)

    @staticmethod
    def _yesterday(today: str) -> str:
        return (date.fromisoformat(today) - timedelta(days=1)).isoformat()
