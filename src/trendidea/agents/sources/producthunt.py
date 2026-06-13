"""Product Hunt source via GraphQL (requires developer token; skipped when missing)."""

from __future__ import annotations

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.http_util import post_json
from trendidea.models import Signal, now_iso

GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
QUERY = """
query TopPosts($first: Int!) {
  posts(order: VOTES, first: $first) {
    edges { node { name tagline url votesCount createdAt } }
  }
}
"""


class ProductHuntSource(Source):
    name = "producthunt"

    def enabled(self, settings: Settings) -> bool:
        return settings.has_producthunt

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        headers = {"Authorization": f"Bearer {settings.producthunt_token}"}
        data = post_json(
            GRAPHQL_URL,
            json_body={"query": QUERY, "variables": {"first": limit}},
            headers=headers,
        )
        return self._parse_response(data)[:limit]

    @staticmethod
    def _parse_response(data: dict) -> list[Signal]:
        edges = (data.get("data", {}).get("posts", {}) or {}).get("edges", []) or []
        signals: list[Signal] = []
        for edge in edges:
            node = edge.get("node") or {}
            name = node.get("name")
            if not name:
                continue
            signals.append(
                Signal(
                    source="producthunt",
                    url=node.get("url", ""),
                    title=name,
                    summary=node.get("tagline", "") or "",
                    published_at=node.get("createdAt") or now_iso(),
                    metric=int(node.get("votesCount", 0) or 0),
                    fetched_at=now_iso(),
                )
            )
        return signals
