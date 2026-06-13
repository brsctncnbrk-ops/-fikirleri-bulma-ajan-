"""Tests for config-driven RSS feed resolution (TASK-017)."""

from trendidea.agents.sources.rss import DEFAULT_FEEDS, RSSSource
from trendidea.config import Settings


def test_uses_explicit_feeds_when_given():
    src = RSSSource(feeds=["http://a/feed", "http://b/feed"])
    assert src._resolve_feeds(Settings(_env_file=None)) == ["http://a/feed", "http://b/feed"]


def test_uses_settings_feeds_when_not_given():
    src = RSSSource()
    settings = Settings(_env_file=None, RSS_FEEDS="http://x/feed, http://y/feed")
    assert src._resolve_feeds(settings) == ["http://x/feed", "http://y/feed"]


def test_falls_back_to_default_when_empty():
    src = RSSSource()
    assert src._resolve_feeds(Settings(_env_file=None)) == DEFAULT_FEEDS
