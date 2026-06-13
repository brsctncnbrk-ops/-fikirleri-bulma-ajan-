"""Hacker News source via the official Firebase API (no key required)."""

from __future__ import annotations

import time

import httpx

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.http_util import request_json
from trendidea.models import Signal, now_iso

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HN_ITEM_LINK = "https://news.ycombinator.com/item?id={id}"


class HackerNewsSource(Source):
    name = "hackernews"

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        cutoff = time.time() - window_hours * 3600
        with httpx.Client(timeout=15.0) as client:
            ids = request_json(TOP_STORIES_URL, client=client)
            signals: list[Signal] = []
            for item_id in ids[: limit * 2]:  # over-fetch; time filter trims the list
                if len(signals) >= limit:
                    break
                item = request_json(ITEM_URL.format(id=item_id), client=client)
                signal = self._parse_item(item, cutoff)
                if signal is not None:
                    signals.append(signal)
        return signals

    @staticmethod
    def _parse_item(item: dict | None, cutoff: float) -> Signal | None:
        """Convert a HN item dict into a Signal, or None if it should be skipped."""
        if not item or item.get("type") != "story" or item.get("dead") or item.get("deleted"):
            return None
        if item.get("time", 0) < cutoff:
            return None
        title = item.get("title")
        if not title:
            return None
        item_id = item["id"]
        return Signal(
            source="hackernews",
            url=item.get("url") or HN_ITEM_LINK.format(id=item_id),
            title=title,
            summary=item.get("text", "") or "",
            published_at=now_iso(),
            metric=int(item.get("score", 0)),
            fetched_at=now_iso(),
        )
