"""Tests for the Signal Processor clustering and scoring (TASK-008)."""

from trendidea.agents.signal_processor import SignalProcessor, tokenize
from trendidea.models import Signal


def _sig(source, title, metric=0, summary="", url=None):
    return Signal(
        source=source,
        url=url or f"http://{source}/{title}",
        title=title,
        summary=summary,
        metric=metric,
    )


def test_tokenize_drops_stopwords_and_short():
    tokens = tokenize("The best AI invoicing platform for you")
    assert "invoicing" in tokens
    assert "platform" in tokens
    assert "the" not in tokens  # stopword
    assert "best" not in tokens  # stopword
    assert "ai" not in tokens  # too short (len <= 2)


def test_dedupe_removes_duplicate_urls_and_short_titles():
    p = SignalProcessor()
    signals = [
        _sig("hn", "Invoicing automation pain", url="http://x"),
        _sig("reddit", "Invoicing automation pain", url="http://x"),  # dup url
        _sig("hn", "Hi"),  # too short
    ]
    clusters = p.process(signals)
    total = sum(len(c.signals) for c in clusters)
    assert total == 1


def test_clusters_group_similar_titles():
    p = SignalProcessor(similarity_threshold=0.2)
    signals = [
        _sig("hn", "Invoicing automation for freelancers", metric=100),
        _sig("reddit", "Freelancer invoicing automation needed", metric=80),
        _sig("github_trending", "Quantum computing breakthrough", metric=500),
    ]
    clusters = p.process(signals)
    # the two invoicing signals cluster together, quantum stands alone
    sizes = sorted(len(c.signals) for c in clusters)
    assert sizes == [1, 2]


def test_cross_source_cluster_scores_higher():
    p = SignalProcessor(similarity_threshold=0.2)
    multi = [
        _sig("hn", "billing automation saas", metric=50),
        _sig("reddit", "billing automation saas", metric=50, url="http://r/1"),
        _sig("producthunt", "billing automation saas", metric=50, url="http://p/1"),
    ]
    single = [_sig("hn", "obscure niche thing", metric=50)]
    clusters = p.process(multi + single)
    top = clusters[0]
    assert len({s.source for s in top.signals}) == 3
    assert top.score == max(c.score for c in clusters)
