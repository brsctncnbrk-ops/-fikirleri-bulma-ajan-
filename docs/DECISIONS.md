# DECISIONS.md

> Son güncelleme: 2026-06-13 · Önemli teknik kararlar: tarih, gerekçe, alternatifler, sonuç.

## 2026-06-13 — Dil: Python 3.11+
- Gerekçe: Trend kütüphanelerinin (pytrends, praw) ve Anthropic/Telegram SDK'larının ekosistemi.
- Alternatifler: Node.js/TypeScript.
- Sonuç: Python 3.11+ benimsendi.

## 2026-06-13 — Doğrulama: Anthropic web_search tool
- Gerekçe: Claude'un bilgi kesimi nedeniyle güncel rakipleri canlı arama olmadan doğrulayamaz. Server-side web_search ekstra anahtar gerektirmez, kaynak+tarih döner; Gerçeklik Kuralı'na tam uyum. (Kullanıcı onayı ile.)
- Alternatifler: Brave/SerpAPI (ayrı anahtar), arama yapmamak (zayıf doğrulama).
- Sonuç: `web_search_20250305` server tool kullanılacak.

## 2026-06-13 — Pazar & dil: Global tarama, Türkçe rapor
- Gerekçe: En geniş sinyal havuzu global kaynaklarda; kullanıcı Türkçe rapor istiyor.
- Sonuç: Tarama global, fikir/rapor metinleri Türkçe.

## 2026-06-13 — Deploy: Railway
- Gerekçe: Tek konteyner için en düşük sürtünmeli deploy; kullanıcı tercihi.
- Alternatifler: Fly.io, Hetzner VPS.
- Sonuç: Dockerfile + railway.json hazırlanacak.

## 2026-06-13 — Depolama: SQLite (stdlib sqlite3)
- Gerekçe: Tek kullanıcı/tek konteyner için yeterli; gereksiz bağımlılık eklemez (AI kuralı #9).
- Alternatifler: SQLModel/SQLAlchemy, Postgres.
- Sonuç: stdlib sqlite3 + ince repository katmanı; ölçeklenirse Postgres'e geçiş (RISKS).

## 2026-06-13 — LLM modelleri: Sonnet (reasoning) + Haiku (ucuz işler)
- Gerekçe: Maliyet/kalite dengesi; fikir üretimi/doğrulama Sonnet, kümeleme/skorlama Haiku. Config'den override edilebilir.
- Sonuç: `LLM_MODEL_REASONING=claude-sonnet-4-6`, `LLM_MODEL_CHEAP=claude-haiku-4-5` varsayılan.

## 2026-06-13 — HTTP istemcisi: httpx
- Gerekçe: Async uyumu (telegram bot async), timeout/retry kolaylığı.
- Sonuç: httpx benimsendi; testlerde respx ile mock.

## 2026-06-13 — Config: pydantic-settings
- Gerekçe: .env doğrulama + tip güvenliği; eksik zorunlu anahtarda net hata.
- Sonuç: pydantic-settings kullanılacak.
