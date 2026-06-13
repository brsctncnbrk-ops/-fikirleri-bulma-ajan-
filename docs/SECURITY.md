# SECURITY.md

> Son güncelleme: 2026-06-13

## Sır Yönetimi
- Tüm API anahtarları yalnızca `.env` (yerel) veya platform secret store'unda (Railway Variables).
- `.env` `.gitignore` ile korunur; repoya asla girmez.
- Anahtarlar loglara yazılmaz; loglarda hassas alanlar maskelenir.

## Yetkilendirme
- Telegram botu yalnızca `TELEGRAM_CHAT_ID` allowlist'indeki sohbetlere yanıt verir.
- Yetkisiz chat_id istekleri reddedilir ve loglanır.

## Dış Çağrı Güvenliği
- Tüm dış istekler timeout + retry/backoff ile sarılır.
- Scraping'de robots.txt/ToS'a uyum; mümkünse resmi API.
- Rate limit aşımında üstel geri çekilme.

## Girdi Doğrulama
- LLM çıktıları şemaya karşı doğrulanır; serbest metin doğrudan DB'ye yazılmaz.
- Telegram kullanıcı girdisi komut yönlendirmede sanitize edilir.

## Veri
- Yalnızca kamuya açık trend verisi işlenir; kişisel veri toplanmaz.
- TBD — Telegram sohbet geçmişi saklama süresi/politikası kullanıcı ile netleşecek (KVKK/GDPR).

## Olay Müdahalesi
- Anahtar sızıntısı şüphesinde: ilgili anahtarı sağlayıcıdan derhal iptal et/yenile, git geçmişini denetle.
