"""RSS/Atom source (stdlib XML parsing; configurable feed list)."""

from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

import httpx

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.http_util import request_text
from trendidea.models import Signal, now_iso

logger = logging.getLogger(__name__)

# Default feeds (sector/news). Extend via configuration as needed (TBD: curate list).
DEFAULT_FEEDS: list[str] = [
    "https://hnrss.org/frontpage",
]

_ATOM = "{http://www.w3.org/2005/Atom}"


class RSSSource(Source):
    name = "rss"

    def __init__(self, feeds: list[str] | None = None) -> None:
        self.feeds = feeds if feeds is not None else DEFAULT_FEEDS

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        signals: list[Signal] = []
        with httpx.Client(timeout=15.0) as client:
            for feed_url in self.feeds:
                try:
                    xml = request_text(feed_url, client=client)
                    signals.extend(self._parse_feed(xml))
                except Exception as exc:  # one bad feed must not sink the rest
                    logger.warning("rss feed failed", extra={"feed": feed_url, "error": str(exc)})
        return signals[:limit]

    @staticmethod
    def _parse_feed(xml: str) -> list[Signal]:
        """Parse RSS 2.0 <item> and Atom <entry> elements into Signals."""
        root = ET.fromstring(xml)
        signals: list[Signal] = []

        # RSS 2.0
        for item in root.iter("item"):
            title = _text(item.find("title"))
            link = _text(item.find("link"))
            if not title or not link:
                continue
            signals.append(_signal(title, link, _text(item.find("description"))))

        # Atom
        for entry in root.iter(f"{_ATOM}entry"):
            title = _text(entry.find(f"{_ATOM}title"))
            link_el = entry.find(f"{_ATOM}link")
            link = link_el.get("href") if link_el is not None else ""
            if not title or not link:
                continue
            signals.append(_signal(title, link, _text(entry.find(f"{_ATOM}summary"))))

        return signals


def _text(el) -> str:
    return el.text.strip() if el is not None and el.text else ""


def _signal(title: str, link: str, summary: str) -> Signal:
    return Signal(
        source="rss",
        url=link,
        title=title,
        summary=summary,
        published_at=now_iso(),
        metric=0,
        fetched_at=now_iso(),
    )
