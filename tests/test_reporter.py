"""Tests for the Reporter rendering (TASK-012)."""

from trendidea.agents.reporter import Reporter
from trendidea.agents.sources.base import ScanResult
from trendidea.models import Competitor, Idea, IdeaStatus


def _idea():
    return Idea(
        title="Fatura asistanı",
        signal_refs=["http://a", "http://b"],
        target_customer="Serbest çalışanlar",
        revenue_model="abonelik",
        first_revenue_estimate="2-4 hafta",
        mvp_scope="Fatura + hatırlatma",
        dev_time="1 hafta",
        competitors=[Competitor(name="Acme", verified=True)],
        main_risk="Doygunluk",
        confidence=82,
        validation_notes="rakip doğrulandı",
        status=IdeaStatus.PASSED,
    )


def _scan():
    return [
        ScanResult(name="hackernews", ok=True, count=12),
        ScanResult(name="reddit", ok=False, error="no_key"),
    ]


def test_markdown_contains_section_5_structure():
    report = Reporter().build(
        date="2026-06-13",
        ideas=[_idea()],
        scan_results=_scan(),
        trends=["AI fatura araçları", "no-code"],
        unknowns=["Pazar büyüklüğü"],
    )
    md = Reporter.render_markdown(report)
    assert "GÜNLÜK İŞ FİKRİ RAPORU — 2026-06-13" in md
    assert "Taranan kaynaklar:" in md
    assert "hackernews" in md and "reddit" in md
    assert "1. Fatura asistanı — Güven: 82/100" in md
    assert "http://a, http://b" in md
    assert "Acme (doğrulandı)" in md
    assert "Bilinmeyenler (TBD): Pazar büyüklüğü" in md


def test_no_ideas_states_no_filler():
    report = Reporter().build(date="2026-06-13", ideas=[], scan_results=_scan(), trends=[])
    md = Reporter.render_markdown(report)
    assert "Dolgu fikir sunulmaz" in md
    assert "kanıtlı fikir çıkmadı" in report.telegram_summary


def test_trend_delta_marks_repeats():
    report = Reporter().build(
        date="2026-06-13",
        ideas=[],
        scan_results=_scan(),
        trends=["AI ajanları", "yeni şey"],
        previous_trends=["AI ajanları"],
    )
    md = Reporter.render_markdown(report)
    assert "AI ajanları (dün de görüldü — güçlendi)" in md
    assert "- yeni şey" in md


def test_telegram_summary_lists_top_ideas():
    report = Reporter().build(
        date="2026-06-13", ideas=[_idea()], scan_results=_scan(), trends=["x"]
    )
    assert "1 doğrulanmış fikir" in report.telegram_summary
    assert "1. Fatura asistanı — 82/100" in report.telegram_summary
