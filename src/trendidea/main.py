"""Entry point: dry-run CLI and the scheduler + Telegram bot service."""

from __future__ import annotations

import argparse
import logging
from datetime import date

from trendidea.agents.reporter import Reporter
from trendidea.config import Settings, get_settings
from trendidea.db import Database
from trendidea.logging_conf import setup_logging
from trendidea.orchestrator import Orchestrator
from trendidea.telegram.handlers import CommandRouter

logger = logging.getLogger(__name__)


def run_pipeline_once(settings: Settings, db: Database, dry_run: bool = False):
    """Run the whole pipeline a single time and return the produced Report."""
    return Orchestrator(settings, db).run(dry_run=dry_run)


def _build_router(settings: Settings, db: Database) -> CommandRouter:
    def get_today_report() -> str:
        report = db.get_report_by_date(date.today().isoformat()) or db.get_latest_report()
        if report is None:
            return "Henüz rapor yok. /tara ile bir tarama başlatabilirsin."
        if report.markdown_path:
            try:
                with open(report.markdown_path, encoding="utf-8") as fh:
                    return fh.read()
            except OSError:
                pass
        return report.telegram_summary or "Rapor bulunamadı."

    def trigger_scan() -> str:
        try:
            report = run_pipeline_once(settings, db, dry_run=not settings.has_anthropic)
            return "Tarama tamamlandı.\n\n" + report.telegram_summary
        except Exception as exc:  # surface failure to the user, keep bot alive
            logger.exception("manual scan failed")
            return f"Tarama sırasında hata: {exc}"

    def get_sources_status() -> str:
        report = db.get_latest_report()
        if report and report.scanned_sources:
            lines = []
            for s in report.scanned_sources:
                state = f"✅ {s['count']}" if s["ok"] else f"❌ {s.get('error')}"
                lines.append(f"- {s['name']}: {state}")
            return "Son tarama kaynak durumu:\n" + "\n".join(lines)
        return "Etkin kaynaklar: " + ", ".join(settings.enabled_sources())

    def deepen_idea(n: int) -> str:
        report = db.get_latest_report()
        if report is None or not report.run_id:
            return "Henüz rapor yok."
        from trendidea.models import IdeaStatus

        ideas = db.get_ideas(report.run_id, status=IdeaStatus.PASSED)
        if n < 1 or n > len(ideas):
            return f"Geçerli fikir numarası 1-{len(ideas)} aralığında."
        idea = ideas[n - 1]
        detail = (
            f"{idea.title} (Güven: {idea.confidence}/100)\n"
            f"Hedef: {idea.target_customer}\nAcı: {idea.pain}\n"
            f"Gelir: {idea.revenue_model} | İlk gelir: {idea.first_revenue_estimate}\n"
            f"MVP: {idea.mvp_scope}\nRisk: {idea.main_risk}\n"
            f"Kaynaklar: {', '.join(idea.signal_refs)}"
        )
        return detail

    def answer_freeform(question: str, chat_id: str) -> str:
        if not settings.has_anthropic:
            return "Sohbet için ANTHROPIC_API_KEY gerekli. /bugun ile raporu görebilirsin."
        from trendidea.llm import LLMClient

        report = db.get_latest_report()
        context = report.telegram_summary if report else "(rapor yok)"
        history = db.get_session(chat_id)
        llm = LLMClient(settings)
        answer = llm.complete(
            system="Türkçe yanıt ver. Sadece verilen rapor bağlamına dayan; uydurma.",
            user=f"Rapor bağlamı:\n{context}\n\nÖnceki bağlam: {history}\n\nSoru: {question}",
            max_tokens=800,
        )
        db.save_session(chat_id, {"last_question": question})
        return answer

    return CommandRouter(
        get_today_report=get_today_report,
        trigger_scan=trigger_scan,
        get_sources_status=get_sources_status,
        deepen_idea=deepen_idea,
        answer_freeform=answer_freeform,
        allowed_chat_id=settings.telegram_chat_id,
    )


def _serve(settings: Settings, db: Database) -> None:
    missing = settings.missing_required()
    if missing:
        raise SystemExit("Eksik zorunlu ayarlar: " + ", ".join(missing) + " (bkz. docs/SETUP.md)")

    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    from trendidea.telegram.bot import TelegramBot

    router = _build_router(settings, db)
    bot = TelegramBot(settings.telegram_bot_token, router)
    app = bot.build_application()

    async def _daily_job() -> None:
        report = run_pipeline_once(settings, db, dry_run=False)
        await bot.send_message(settings.telegram_chat_id, report.telegram_summary)

    async def _post_init(application) -> None:
        scheduler = AsyncIOScheduler(timezone=settings.timezone)
        scheduler.add_job(
            _daily_job,
            CronTrigger(hour=settings.daily_report_hour, minute=0),
            misfire_grace_time=3600,
        )
        scheduler.start()
        logger.info("scheduler started", extra={"hour": settings.daily_report_hour})

    app.post_init = _post_init
    logger.info("bot starting")
    app.run_polling()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Trend -> business idea agent")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run the pipeline once without LLM/Telegram"
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    setup_logging(settings.log_level)
    db = Database(settings.database_path)

    if args.dry_run:
        report = run_pipeline_once(settings, db, dry_run=True)
        print(Reporter.render_markdown(report))
        print(f"\n[dry-run] Rapor yazıldı: {report.markdown_path}")
        return

    _serve(settings, db)


if __name__ == "__main__":
    main()
