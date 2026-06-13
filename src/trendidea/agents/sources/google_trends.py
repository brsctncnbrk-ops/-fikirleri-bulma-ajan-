"""Google Trends source via pytrends (no key; unofficial endpoint)."""

from __future__ import annotations

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.models import Signal, now_iso

GOOGLE_TRENDS_SEARCH = "https://trends.google.com/trends/explore?q={q}"


class GoogleTrendsSource(Source):
    name = "google_trends"

    def __init__(self, geo: str = "") -> None:
        # empty geo = worldwide (global market focus)
        self.geo = geo

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=0)
        df = pytrends.trending_searches(pn="united_states" if not self.geo else self.geo)
        terms = [str(t) for t in df[0].tolist()] if not df.empty else []
        return self._terms_to_signals(terms)[:limit]

    @staticmethod
    def _terms_to_signals(terms: list[str]) -> list[Signal]:
        signals: list[Signal] = []
        for term in terms:
            term = term.strip()
            if not term:
                continue
            signals.append(
                Signal(
                    source="google_trends",
                    url=GOOGLE_TRENDS_SEARCH.format(q=term.replace(" ", "+")),
                    title=term,
                    summary="Google'da yükselen arama terimi",
                    published_at=now_iso(),
                    metric=0,
                    fetched_at=now_iso(),
                )
            )
        return signals
