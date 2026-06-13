"""Tests for LLM cost estimation and its visibility in the report (TASK-016)."""

from trendidea.agents.reporter import Reporter
from trendidea.agents.sources.base import ScanResult
from trendidea.config import Settings
from trendidea.logging_conf import CostTracker


def test_estimate_cost_from_prices():
    t = CostTracker()
    t.add("claude-sonnet-4-6", 1_000_000, 500_000)
    # 1M input @ $3, 0.5M output @ $15 = 3 + 7.5 = 10.5
    assert t.estimate_cost(3.0, 15.0) == 10.5


def test_estimate_zero_when_unconfigured():
    t = CostTracker()
    t.add("m", 100, 200)
    assert t.estimate_cost(0.0, 0.0) == 0.0


def test_pricing_configured_flag():
    assert Settings(_env_file=None).pricing_configured is False
    assert Settings(_env_file=None, LLM_PRICE_INPUT_PER_MTOK="3").pricing_configured is True


def test_report_shows_tokens_without_price():
    report = Reporter().build(
        date="2026-06-13",
        ideas=[],
        scan_results=[ScanResult(name="hn", ok=True, count=1)],
        trends=["x"],
        token_usage=1234,
        cost_estimate=0.0,
        cost_configured=False,
    )
    md = Reporter.render_markdown(report)
    assert "LLM kullanımı: 1234 token" in md
    assert "fiyat yapılandırılmadı" in md
    assert "1234 token" in report.telegram_summary


def test_report_shows_cost_when_configured():
    report = Reporter().build(
        date="2026-06-13",
        ideas=[],
        scan_results=[ScanResult(name="hn", ok=True, count=1)],
        trends=["x"],
        token_usage=2000,
        cost_estimate=0.0123,
        cost_configured=True,
    )
    md = Reporter.render_markdown(report)
    assert "≈ $0.0123" in md
