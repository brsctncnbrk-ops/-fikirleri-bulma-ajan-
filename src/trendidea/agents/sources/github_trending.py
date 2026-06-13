"""GitHub Trending source (HTML scrape; no key, robots-friendly single request)."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.http_util import request_text
from trendidea.models import Signal, now_iso

TRENDING_URL = "https://github.com/trending"


class GitHubTrendingSource(Source):
    name = "github_trending"

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        html = request_text(TRENDING_URL, params={"since": "daily"})
        return self._parse_html(html)[:limit]

    @staticmethod
    def _parse_html(html: str) -> list[Signal]:
        soup = BeautifulSoup(html, "html.parser")
        signals: list[Signal] = []
        for article in soup.select("article.Box-row"):
            link = article.select_one("h2 a")
            if link is None or not link.get("href"):
                continue
            repo = link["href"].strip("/")
            desc_el = article.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""
            stars = _parse_stars(article)
            signals.append(
                Signal(
                    source="github_trending",
                    url=f"https://github.com/{repo}",
                    title=repo,
                    summary=description,
                    published_at=now_iso(),
                    metric=stars,
                    fetched_at=now_iso(),
                )
            )
        return signals


def _parse_stars(article) -> int:
    star_link = article.select_one('a[href$="/stargazers"]')
    if star_link is None:
        return 0
    digits = re.sub(r"[^\d]", "", star_link.get_text())
    return int(digits) if digits else 0
