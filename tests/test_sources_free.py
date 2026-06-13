"""Parsing tests for GitHub Trending, Google Trends and RSS sources (TASK-006)."""

from trendidea.agents.sources.github_trending import GitHubTrendingSource
from trendidea.agents.sources.google_trends import GoogleTrendsSource
from trendidea.agents.sources.rss import RSSSource

GITHUB_HTML = """
<div>
  <article class="Box-row">
    <h2 class="h3"><a href="/acme/coolproject">acme / coolproject</a></h2>
    <p class="col-9">An AI-powered widget</p>
    <a href="/acme/coolproject/stargazers">1,234</a>
  </article>
  <article class="Box-row">
    <h2 class="h3"><a href="/foo/bar">foo / bar</a></h2>
    <p>Another tool</p>
    <a href="/foo/bar/stargazers">56</a>
  </article>
</div>
"""

RSS_XML = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title>Pain with billing tools</title><link>http://ex/1</link>
    <description>People hate X</description></item>
  <item><title>New AI framework</title><link>http://ex/2</link></item>
</channel></rss>
"""

ATOM_XML = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>Atom entry</title><link href="http://atom/1"/>
    <summary>summary text</summary></entry>
</feed>
"""


def test_github_trending_parse():
    signals = GitHubTrendingSource._parse_html(GITHUB_HTML)
    assert len(signals) == 2
    assert signals[0].title == "acme/coolproject"
    assert signals[0].url == "https://github.com/acme/coolproject"
    assert signals[0].metric == 1234
    assert signals[0].summary == "An AI-powered widget"
    assert signals[1].metric == 56


def test_google_trends_terms_to_signals():
    signals = GoogleTrendsSource._terms_to_signals(["ai agents", "  ", "vibe coding"])
    assert len(signals) == 2
    assert signals[0].title == "ai agents"
    assert "ai+agents" in signals[0].url


def test_rss_parse_rss2():
    signals = RSSSource._parse_feed(RSS_XML)
    assert len(signals) == 2
    assert signals[0].title == "Pain with billing tools"
    assert signals[0].url == "http://ex/1"


def test_rss_parse_atom():
    signals = RSSSource._parse_feed(ATOM_XML)
    assert len(signals) == 1
    assert signals[0].title == "Atom entry"
    assert signals[0].url == "http://atom/1"
