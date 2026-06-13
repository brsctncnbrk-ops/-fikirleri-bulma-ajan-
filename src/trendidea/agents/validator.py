"""Validator / Gatekeeper: enforces the Reality Rule and scores ideas 0-100.

Cheap deterministic gates run first (and can reject without spending tokens);
surviving ideas get an LLM + web_search verification pass that verifies real
competitors and judges Claude-Code feasibility.
"""

from __future__ import annotations

import logging

from trendidea.llm import LLMClient
from trendidea.models import Competitor, Idea, IdeaStatus

logger = logging.getLogger(__name__)

MIN_SOURCES = 2
DEFAULT_THRESHOLD = 50

SYSTEM_PROMPT = """Sen titiz bir doğrulama uzmanısın (gatekeeper). Sana bir iş
fikri verilecek. Görevin GERÇEKLİĞİ doğrulamak:

1. Rakipleri WEB ARAMASI ile doğrula: adı geçen rakipler GERÇEKTEN var mı?
   Var olduğunu doğrulayamadığını "verified": false ve nedenini yaz. Rakip UYDURMA.
2. İstatistik/iddialar kaynaklı mı, yoksa havada mı?
3. Erişilebilirlik: bu MVP gerçekten Claude Code ile kısa sürede yapılabilir mi?
4. Gelir yolu somut mu?
Bu testlerden zayıf geçen fikrin güven skorunu DÜŞÜR.

Yanıtı YALNIZCA şu JSON şemasında ver (Türkçe açıklamalar):
{"verdict": "pass" | "reject", "confidence": 0-100,
 "notes": "kısa gerekçe",
 "competitors": [{"name": str, "url": str, "verified": true|false, "note": str}]}"""


class Validator:
    def __init__(self, llm: LLMClient, threshold: int = DEFAULT_THRESHOLD) -> None:
        self.llm = llm
        self.threshold = threshold

    def validate(self, ideas: list[Idea]) -> list[Idea]:
        passed: list[Idea] = []
        for idea in ideas:
            reason = self._deterministic_reject(idea)
            if reason:
                self._mark_rejected(idea, reason)
                continue
            self._llm_validate(idea)
            if idea.status == IdeaStatus.PASSED:
                passed.append(idea)
        passed.sort(key=lambda i: i.confidence, reverse=True)
        logger.info("validation done", extra={"passed": len(passed), "total": len(ideas)})
        return passed

    @staticmethod
    def _deterministic_reject(idea: Idea) -> str | None:
        unique_sources = {u for u in idea.signal_refs if u and u.strip()}
        if len(unique_sources) < MIN_SOURCES:
            return f"Gerçeklik Kuralı: en az {MIN_SOURCES} kaynak yok (kanıtsız fikir)."
        if not idea.revenue_model or idea.revenue_model.strip() in ("", "TBD"):
            return "Gerçeklik Kuralı: somut gelir modeli yok."
        return None

    def _llm_validate(self, idea: Idea) -> None:
        prompt = self._build_prompt(idea)
        try:
            result = self.llm.complete_json(
                SYSTEM_PROMPT, prompt, use_web_search=True, max_tokens=2000
            )
        except Exception as exc:  # validation must fail safe (reject), never crash run
            self._mark_rejected(idea, f"Doğrulama hatası: {exc}")
            return

        confidence = int(result.get("confidence", 0) or 0)
        confidence = max(0, min(100, confidence))
        notes = result.get("notes", "")
        verified = result.get("competitors")
        if isinstance(verified, list) and verified:
            idea.competitors = [
                Competitor(
                    name=c.get("name", ""),
                    url=c.get("url", ""),
                    verified=bool(c.get("verified", False)),
                    note=c.get("note", ""),
                )
                for c in verified
                if c.get("name")
            ]

        idea.confidence = confidence
        idea.validation_notes = notes
        if result.get("verdict") == "pass" and confidence >= self.threshold:
            idea.status = IdeaStatus.PASSED
        else:
            idea.status = IdeaStatus.REJECTED

    @staticmethod
    def _mark_rejected(idea: Idea, reason: str) -> None:
        idea.status = IdeaStatus.REJECTED
        idea.confidence = 0
        idea.validation_notes = reason

    @staticmethod
    def _build_prompt(idea: Idea) -> str:
        competitors = ", ".join(c.name for c in idea.competitors) or "(belirtilmemiş)"
        return (
            f"Fikir: {idea.title}\n"
            f"Hedef müşteri: {idea.target_customer}\n"
            f"Acı: {idea.pain}\n"
            f"Gelir modeli: {idea.revenue_model} | İlk gelir: {idea.first_revenue_estimate}\n"
            f"MVP kapsamı: {idea.mvp_scope}\n"
            f"Tahmini geliştirme süresi: {idea.dev_time}\n"
            f"İddia edilen rakipler: {competitors}\n"
            f"Kaynaklar: {', '.join(idea.signal_refs)}\n"
        )
