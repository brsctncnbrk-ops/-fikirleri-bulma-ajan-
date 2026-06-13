"""Reddit source via praw (requires API credentials; skipped when missing)."""

from __future__ import annotations

from trendidea.agents.sources.base import Source
from trendidea.config import Settings
from trendidea.models import Signal, now_iso

DEFAULT_SUBREDDITS = ["SaaS", "Entrepreneur", "sideproject", "artificial"]


class RedditSource(Source):
    name = "reddit"

    def __init__(self, subreddits: list[str] | None = None) -> None:
        self.subreddits = subreddits or DEFAULT_SUBREDDITS

    def enabled(self, settings: Settings) -> bool:
        return settings.has_reddit

    def fetch(self, settings: Settings, window_hours: int, limit: int = 30) -> list[Signal]:
        import praw

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        time_filter = "day" if window_hours <= 24 else "week"
        per_sub = max(1, limit // len(self.subreddits))
        signals: list[Signal] = []
        for name in self.subreddits:
            for submission in reddit.subreddit(name).top(time_filter=time_filter, limit=per_sub):
                signals.append(self._submission_to_signal(submission, name))
        return signals[:limit]

    @staticmethod
    def _submission_to_signal(submission, subreddit_name: str) -> Signal:
        permalink = getattr(submission, "permalink", "")
        url = f"https://www.reddit.com{permalink}" if permalink else getattr(submission, "url", "")
        return Signal(
            source="reddit",
            url=url,
            title=getattr(submission, "title", ""),
            summary=(getattr(submission, "selftext", "") or "")[:500],
            published_at=now_iso(),
            metric=int(getattr(submission, "score", 0)),
            fetched_at=now_iso(),
        )
