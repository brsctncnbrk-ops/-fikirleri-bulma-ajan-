"""Tests for configuration loading and capability detection (TASK-003)."""

from trendidea.config import Settings
from trendidea.logging_conf import CostTracker, setup_logging


def _settings(**env: str) -> Settings:
    # _env_file=None disables reading a developer's local .env during tests
    return Settings(_env_file=None, **env)


def test_missing_required_when_empty():
    s = _settings()
    missing = s.missing_required()
    assert "ANTHROPIC_API_KEY" in missing
    assert "TELEGRAM_BOT_TOKEN" in missing
    assert "TELEGRAM_CHAT_ID" in missing


def test_free_sources_always_enabled():
    s = _settings()
    sources = s.enabled_sources()
    assert {"hackernews", "github_trending", "google_trends", "rss"} <= set(sources)
    assert "reddit" not in sources
    assert "producthunt" not in sources


def test_optional_sources_enabled_with_keys():
    s = _settings(
        REDDIT_CLIENT_ID="id",
        REDDIT_CLIENT_SECRET="secret",
        PRODUCTHUNT_TOKEN="tok",
    )
    assert s.has_reddit
    assert s.has_producthunt
    assert "reddit" in s.enabled_sources()
    assert "producthunt" in s.enabled_sources()


def test_full_run_ready_with_required_keys():
    s = _settings(
        ANTHROPIC_API_KEY="a",
        TELEGRAM_BOT_TOKEN="b",
        TELEGRAM_CHAT_ID="c",
    )
    assert s.missing_required() == []
    assert s.has_anthropic
    assert s.has_telegram


def test_cost_tracker_accumulates():
    setup_logging("INFO")
    t = CostTracker()
    t.add("claude-sonnet-4-6", 100, 50)
    t.add("claude-sonnet-4-6", 10, 5)
    t.add("claude-haiku-4-5", 1, 1)
    assert t.calls == 3
    assert t.total_tokens == 167
    assert t.by_model["claude-sonnet-4-6"]["calls"] == 2
