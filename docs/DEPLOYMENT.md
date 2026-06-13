# DEPLOYMENT.md

> Son güncelleme: 2026-06-13 · Hedef: Railway (tek konteyner).

## Yerel Docker
```bash
docker build -t trendidea .
docker run --env-file .env -v $(pwd)/data:/app/data trendidea
```
(SQLite kalıcılığı için `DATABASE_PATH=/app/data/trendidea.db` önerilir.)

## Railway
1. Railway hesabı aç, **New Project → Deploy from GitHub repo** ile bu repoyu bağla.
2. Railway `Dockerfile`'ı otomatik algılar (`railway.json` ile servis ayarlanır).
3. **Variables** sekmesinde `.env.example`'daki tüm değişkenleri gir
   (ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, opsiyoneller, TIMEZONE...).
4. SQLite kalıcılığı için bir **Volume** ekle ve `DATABASE_PATH`'i o volume yoluna ayarla.
5. Deploy et; loglardan zamanlayıcının ve botun başladığını doğrula.

## Doğrulama
- Bot'a `/kaynaklar` yaz → kaynak durumları dönmeli.
- `/tara` ile manuel tarama tetikle → kısa süre sonra rapor özeti gelmeli.

TBD — Railway proje adı/region ve volume boyutu kullanıcı tarafından belirlenecek.
