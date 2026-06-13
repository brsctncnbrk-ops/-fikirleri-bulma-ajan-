"""Tests for the Hacker News source parsing and scanner graceful degrade (TASK-005)."""

import time

import httpx
import respx

from trendidea.agents.scanner import Scanner
from trendidea.agents.sources.base import Source
from trendidea.agents.sources.hackernews import (
    ITEM_URL,
    TOP_STORIES_URL,
    HackerNewsSource,
)
from trendidea.config import Settings


def _settings() -> Settings:
    return Settings(_env_file=None)


def test_parse_item_filters_old_and_nonstory():
    cutoff = time.time() - 72 * 3600
    fresh = {"id": 1, "type": "story", "title": "Fresh", "time": time.time(), "score": 50}
    old = {"id": 2, "type": "story", "title": "Old", "time": cutoff - 10, "score": 99}
    job = {"id": 3, "type": "job", "title": "Job", "time": time.time()}

    assert HackerNewsSource._parse_item(fresh, cutoff) is not None
    assert HackerNewsSource._parse_item(old, cutoff) is None
    assert HackerNewsSource._parse_item(job, cutoff) is None
    assert HackerNewsSource._parse_item(None, cutoff) is None


def test_parse_item_uses_hn_link_when_no_url():
    cutoff = time.time() - 3600
    item = {"id": 42, "type": "story", "title": "Ask HN", "time": time.time(), "score": 10}
    signal = HackerNewsSource._parse_item(item, cutoff)
    assert signal is not None
    assert "item?id=42" in signal.url
    assert signal.metric == 10


@respx.mock
def test_hackernews_fetch_end_to_end():
    now = time.time()
    respx.get(TOP_STORIES_URL).mock(return_value=httpx.Response(200, json=[100, 101]))
    respx.get(ITEM_URL.format(id=100)).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 100,
                "type": "story",
                "title": "AI tool",
                "time": now,
                "score": 120,
                "url": "http://example.com",
            },
        )
    )
    respx.get(ITEM_URL.format(id=101)).mock(
        return_value=httpx.Response(
            200,
            json={"id": 101, "type": "story", "title": "Old one", "time": now - 99 * 3600},
        )
    )

    signals = HackerNewsSource().fetch(_settings(), window_hours=72, limit=10)
    assert len(signals) == 1
    assert signals[0].title == "AI tool"
    assert signals[0].url == "http://example.com"


class _FailingSource(Source):
    name = "boom"

    def fetch(self, settings, window_hours, limit=30):
        raise RuntimeError("network down")


def test_scanner_graceful_degrade():
    scanner = Scanner(sources=[_FailingSource()])
    signals, results = scanner.scan(_settings())
    assert signals == []
    assert results[0].ok is False
    assert "network down" in results[0].error
