"""Reporter: renders the daily Turkish report (Markdown + Telegram summary)."""

from __future__ import annotations

from trendidea.agents.sources.base import ScanResult
from trendidea.models import Idea, Report


class Reporter:
    def build(
        self,
        date: str,
        ideas: list[Idea],
        scan_results: list[ScanResult],
        trends: list[str],
        unknowns: list[str] | None = None,
        run_id: int | None = None,
        previous_trends: list[str] | None = None,
        token_usage: int = 0,
        cost_estimate: float = 0.0,
        cost_configured: bool = False,
    ) -> Report:
        trend_lines = self._with_deltas(trends, previous_trends or [])
        report = Report(
            date=date,
            scanned_sources=[r.as_dict() for r in scan_results],
            trends=trend_lines,
            ideas=ideas,
            unknowns=unknowns or [],
            run_id=run_id,
            token_usage=token_usage,
            cost_estimate=cost_estimate,
            cost_configured=cost_configured,
        )
        report.telegram_summary = self.render_telegram_summary(report)
        return report

    @staticmethod
    def _cost_line(report: Report) -> str:
        if report.cost_configured:
            return f"💸 LLM kullanımı: {report.token_usage} token (≈ ${report.cost_estimate})"
        return (
            f"💸 LLM kullanımı: {report.token_usage} token "
            f"(maliyet tahmini için fiyat yapılandırılmadı)"
        )

    @staticmethod
    def _with_deltas(trends: list[str], previous: list[str]) -> list[str]:
        prev = set(previous)
        out: list[str] = []
        for t in trends:
            if t in prev:
                out.append(f"{t} (dün de görüldü — güçlendi)")
            else:
                out.append(t)
        return out

    @staticmethod
    def render_markdown(report: Report) -> str:
        lines = [f"📊 GÜNLÜK İŞ FİKRİ RAPORU — {report.date}", ""]

        sources_str = ", ".join(
            f"{s['name']} ({'✅' if s['ok'] else '❌ ' + str(s.get('error') or 'hata')}"
            f"{', ' + str(s['count']) if s['ok'] else ''})"
            for s in report.scanned_sources
        )
        lines.append(f"🔎 Taranan kaynaklar: {sources_str or '—'}")
        lines.append("")

        lines.append("📈 Günün öne çıkan trendleri:")
        if report.trends:
            lines.extend(f"- {t}" for t in report.trends)
        else:
            lines.append("- TBD")
        lines.append("")

        lines.append("💡 FİKİRLER (güven skoruna göre sıralı):")
        if not report.ideas:
            lines.append(
                "\nBugün Gerçeklik Kuralı'nı geçen kanıtlı fikir bulunamadı. Dolgu fikir sunulmaz."
            )
        for i, idea in enumerate(report.ideas, 1):
            competitors = (
                ", ".join(
                    f"{c.name}{' (doğrulandı)' if c.verified else ' (doğrulanamadı)'}"
                    for c in idea.competitors
                )
                or "TBD"
            )
            lines.extend(
                [
                    "",
                    f"{i}. {idea.title} — Güven: {idea.confidence}/100",
                    f"   • Sinyal kaynakları: {', '.join(idea.signal_refs) or 'TBD'}",
                    f"   • Hedef müşteri: {idea.target_customer}",
                    f"   • Gelir modeli: {idea.revenue_model} | "
                    f"İlk gelir tahmini: {idea.first_revenue_estimate}",
                    f"   • MVP kapsamı (Claude Code): {idea.mvp_scope}",
                    f"   • Geliştirme süresi: {idea.dev_time}",
                    f"   • Rakipler: {competitors}",
                    f"   • Risk: {idea.main_risk}",
                ]
            )
            if idea.validation_notes:
                lines.append(f"   • Doğrulama notu: {idea.validation_notes}")

        lines.append("")
        unknowns = ", ".join(report.unknowns) if report.unknowns else "—"
        lines.append(f"⚠️ Bilinmeyenler (TBD): {unknowns}")
        lines.append("")
        lines.append(Reporter._cost_line(report))
        return "\n".join(lines)

    @staticmethod
    def render_telegram_summary(report: Report) -> str:
        ok_count = sum(1 for s in report.scanned_sources if s["ok"])
        head = (
            f"📊 {report.date} — {len(report.ideas)} doğrulanmış fikir "
            f"({ok_count}/{len(report.scanned_sources)} kaynak tarandı)"
        )
        cost = Reporter._cost_line(report)
        if not report.ideas:
            return f"{head}\nBugün kanıtlı fikir çıkmadı.\n{cost}"
        tops = "\n".join(
            f"{i}. {idea.title} — {idea.confidence}/100"
            for i, idea in enumerate(report.ideas[:5], 1)
        )
        return f"{head}\n\n{tops}\n\n{cost}\n\nDetay için /bugun"
