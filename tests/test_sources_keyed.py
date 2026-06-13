"""Tests for keyed sources: graceful skip + response parsing (TASK-007)."""

from types import SimpleNamespace

from trendidea.agents.scanner import Scanner
from trendidea.agents.sources.producthunt import ProductHuntSource
from trendidea.agents.sources.reddit import RedditSource
from trendidea.config import Settings


def _settings(**env: str) -> Settings:
    return Settings(_env_file=None, **env)


def test_keyed_sources_disabled_without_keys():
    s = _settings()
    assert RedditSource().enabled(s) is False
    assert ProductHuntSource().enabled(s) is False


def test_keyed_sources_enabled_with_keys():
    s = _settings(
        REDDIT_CLIENT_ID="id",
        REDDIT_CLIENT_SECRET="secret",
        PRODUCTHUNT_TOKEN="tok",
    )
    assert RedditSource().enabled(s) is True
    assert ProductHuntSource().enabled(s) is True


def test_scanner_marks_disabled_source_as_no_key():
    scanner = Scanner(sources=[RedditSource(), ProductHuntSource()])
    signals, results = scanner.scan(_settings())
    assert signals == []
    assert all(r.ok is False and r.error == "no_key" for r in results)


def test_reddit_submission_parse():
    sub = SimpleNamespace(
        title="Need a better invoicing tool",
        permalink="/r/SaaS/comments/abc/",
        selftext="Current tools are bad",
        score=321,
        url="http://old",
    )
    signal = RedditSource._submission_to_signal(sub, "SaaS")
    assert signal.title == "Need a better invoicing tool"
    assert signal.url == "https://www.reddit.com/r/SaaS/comments/abc/"
    assert signal.metric == 321


def test_producthunt_response_parse():
    data = {
        "data": {
            "posts": {
                "edges": [
                    {
                        "node": {
                            "name": "CoolApp",
                            "tagline": "Does cool things",
                            "url": "http://ph/cool",
                            "votesCount": 250,
                            "createdAt": "2026-06-13T00:00:00Z",
                        }
                    },
                    {"node": {"name": None}},
                ]
            }
        }
    }
    signals = ProductHuntSource._parse_response(data)
    assert len(signals) == 1
    assert signals[0].title == "CoolApp"
    assert signals[0].metric == 250


def test_producthunt_empty_response():
    assert ProductHuntSource._parse_response({}) == []
