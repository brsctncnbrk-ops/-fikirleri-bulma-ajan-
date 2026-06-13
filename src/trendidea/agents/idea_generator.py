"""Idea Generator: turns scored signal clusters into concrete business ideas."""

from __future__ import annotations

import logging

from trendidea.llm import LLMClient
from trendidea.models import Cluster, Competitor, Idea, IdeaStatus

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Sen kıdemli bir ürün stratejistisin. Sana güncel trend
sinyallerinden oluşan kümeler verilecek. Her kümeden, BİR GELİŞTİRİCİNİN Claude
Code ile kısa sürede (günler, haftalar değil) MVP'sini çıkarabileceği ve kısa
sürede gelir üretebilecek SOMUT iş fikirleri üret.

Kurallar (mutlak):
- Sadece gerçekten uygulanabilir, somut fikirler üret. Genel/havada fikir yazma.
- Bilmediğin alana "TBD" yaz; istatistik/rakip UYDURMA.
- Her fikir, doğduğu sinyalin kaynak URL'lerini signal_refs içinde listelemeli.
- Gelir modeli somut olmalı (abonelik/tek seferlik/komisyon) + ilk gelir tahmini.
- Tüm metinler TÜRKÇE olmalı.

Yanıtı YALNIZCA şu şemada JSON dizisi olarak ver:
[{"title": str, "target_customer": str, "pain": str, "revenue_model": str,
  "first_revenue_estimate": str, "mvp_scope": str, "dev_time": str,
  "competitors": [{"name": str, "url": str}], "main_risk": str,
  "signal_refs": [str]}]"""


class IdeaGenerator:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def generate(self, clusters: list[Cluster], max_ideas: int = 5) -> list[Idea]:
        top = [c for c in clusters if c.signals][:max_ideas]
        if not top:
            return []
        prompt = self._build_prompt(top, max_ideas)
        raw = self.llm.complete_json(SYSTEM_PROMPT, prompt, max_tokens=3000)
        items = raw if isinstance(raw, list) else raw.get("ideas", [])
        ideas = [self._to_idea(item) for item in items if item.get("title")]
        logger.info("ideas generated", extra={"count": len(ideas)})
        return ideas

    @staticmethod
    def _build_prompt(clusters: list[Cluster], max_ideas: int) -> str:
        lines = [f"En fazla {max_ideas} fikir üret. Trend kümeleri:\n"]
        for i, cluster in enumerate(clusters, 1):
            lines.append(f"\n## Küme {i}: {cluster.label} (skor: {cluster.score})")
            for signal in cluster.signals[:5]:
                lines.append(f"- [{signal.source}] {signal.title} — {signal.url}")
        return "\n".join(lines)

    @staticmethod
    def _to_idea(item: dict) -> Idea:
        competitors = [
            Competitor(name=c.get("name", ""), url=c.get("url", ""))
            for c in item.get("competitors", [])
            if c.get("name")
        ]
        return Idea(
            title=item["title"],
            signal_refs=list(item.get("signal_refs", [])),
            target_customer=item.get("target_customer", "TBD"),
            pain=item.get("pain", "TBD"),
            revenue_model=item.get("revenue_model", "TBD"),
            first_revenue_estimate=item.get("first_revenue_estimate", "TBD"),
            mvp_scope=item.get("mvp_scope", "TBD"),
            dev_time=item.get("dev_time", "TBD"),
            competitors=competitors,
            main_risk=item.get("main_risk", "TBD"),
            status=IdeaStatus.CANDIDATE,
        )
