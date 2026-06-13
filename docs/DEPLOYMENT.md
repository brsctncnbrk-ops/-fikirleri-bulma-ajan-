# DEPLOYMENT.md

> Son güncelleme: 2026-06-13 · Hedef: Railway (tek konteyner, worker servisi).

## Genel mimari notu
Uygulama bir **worker** olarak çalışır (Telegram long-polling + APScheduler).
Dışarıya HTTP portu açmaz; bu yüzden Railway'de **public domain / port gerekmez**.
SQLite verisi kalıcı bir **Volume**'de tutulmalıdır, aksi halde her deploy'da sıfırlanır.

## Yerel Docker ile deneme (opsiyonel)
```bash
docker build -t trendidea .
docker run --env-file .env -v "$(pwd)/data:/app/data" trendidea
```
İmaj `DATABASE_PATH=/app/data/trendidea.db` ile gelir; volume'u `/app/data`'ya bağla.

## Railway adım adım

### 1. Projeyi bağla
1. https://railway.app → **New Project → Deploy from GitHub repo**.
2. `brsctncnbrk-ops/-fikirleri-bulma-ajan-` reposunu seç.
3. Deploy edilecek branch'i seç: `claude/merhaba-yvv48l` (ya da önce `main`'e merge et).
4. Railway kökteki `Dockerfile`'ı ve `railway.json`'u otomatik algılar (builder = DOCKERFILE).

### 2. Ortam değişkenlerini gir (Variables sekmesi)
Zorunlu:
- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Önerilen:
- `TIMEZONE=Europe/Istanbul`
- `DAILY_REPORT_HOUR=9`
- `DATABASE_PATH=/app/data/trendidea.db`  ← volume yoluyla aynı olmalı

Opsiyonel (varsa kaynakları açar):
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`
- `PRODUCTHUNT_TOKEN`
- `LLM_PRICE_INPUT_PER_MTOK`, `LLM_PRICE_OUTPUT_PER_MTOK` (maliyet tahmini için)
- `RSS_FEEDS` (virgülle ayrılmış feed URL'leri)

> Tam liste için `.env.example`. Anahtarları nasıl alacağın: `docs/SETUP.md`.

### 3. Kalıcı SQLite için Volume ekle
1. Servis → **Settings → Volumes → New Volume**.
2. Mount path: `/app/data` (DATABASE_PATH ile uyumlu).
3. Kaydet; Railway servisi yeniden deploy eder.

### 4. Deploy ve doğrulama
- Deploy loglarında şunları görmelisin:
  - `{"message": "scheduler started", "hour": 9}`
  - `{"message": "bot starting"}`
- Telegram'da botuna yaz:
  - `/kaynaklar` → kaynak durumları dönmeli.
  - `/tara` → kısa süre sonra rapor özeti gelmeli (tam tarama + LLM çalışır).
  - `/bugun` → en son raporu gösterir.
- Her gün `DAILY_REPORT_HOUR` saatinde otomatik rapor `TELEGRAM_CHAT_ID`'ye düşer.

## Güncelleme akışı
Branch'e yeni commit push'ladığında Railway otomatik yeniden deploy eder
(GitHub entegrasyonu açıksa).

## Sorun giderme
- **Açılışta timezone hatası:** `tzdata` paketi requirements'ta; eksikse yeniden build et.
- **Veri her deploy'da sıfırlanıyor:** Volume mount path'i `DATABASE_PATH` ile aynı mı?
- **Bot yanıt vermiyor:** `TELEGRAM_CHAT_ID` doğru mu (bot yalnız o sohbete yanıt verir)?
- **Fikir üretilmiyor / "anahtar yok" notu:** `ANTHROPIC_API_KEY` Variables'ta tanımlı mı?
- **Maliyet:** Günlük token kullanımı raporda ve `runs/.../run.json`'da görünür.

TBD — Railway proje adı/region kullanıcı tarafından belirlenecek.
