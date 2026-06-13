# SETUP.md

> Son güncelleme: 2026-06-13 · Kurulum + API anahtarı edinme rehberi.

## 1. Yerel kurulum
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## 2. API anahtarlarını edinme

Şu an hiçbir anahtarın yok; adım adım nasıl alacağın aşağıda. Sadece **Anthropic**
ve **Telegram** zorunlu; Reddit/Product Hunt opsiyonel (yoksa o kaynaklar atlanır).

### 2.1 Anthropic Claude API (ZORUNLU)
1. https://console.anthropic.com adresine kaydol/giriş yap.
2. Sağ üstten **Settings → API Keys → Create Key**.
3. Anahtarı kopyala, `.env` içine `ANTHROPIC_API_KEY=` satırına yapıştır.
4. Faturalandırma için **Billing** bölümünden küçük bir kredi yükle (kullandıkça öde).
   Maliyet sistem tarafından loglanır; başlangıç için birkaç dolar yeterli.

### 2.2 Telegram bot token + chat id (ZORUNLU)
1. Telegram'da **@BotFather**'a yaz → `/newbot` → bot adı ve kullanıcı adı ver.
2. BotFather sana bir **token** verir → `.env` içine `TELEGRAM_BOT_TOKEN=`.
3. Chat id'ni öğren: yeni botuna `/start` yaz, sonra tarayıcıda
   `https://api.telegram.org/bot<TOKEN>/getUpdates` aç; `chat.id` değerini
   `.env` içine `TELEGRAM_CHAT_ID=` olarak gir.

### 2.3 Reddit API (OPSİYONEL)
1. https://www.reddit.com/prefs/apps → **create another app** → tür: **script**.
2. `client_id` (uygulama adının altındaki kısa kod) ve `secret`'i al.
3. `.env`: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` doldur.

### 2.4 Product Hunt API (OPSİYONEL)
1. https://www.producthunt.com/v2/oauth/applications → yeni uygulama oluştur.
2. **Developer token** üret → `.env`: `PRODUCTHUNT_TOKEN`.

## 3. Çalıştırma
```bash
python -m trendidea.main --dry-run   # anahtarsız iskelet testi
python -m trendidea.main             # tam servis (zamanlayıcı + bot)
```

## 4. Deploy
Railway adımları için bkz. `docs/DEPLOYMENT.md`.

## Notlar
- `.env` dosyası asla commit edilmez (`.gitignore` ile korunur).
- Eksik zorunlu anahtar varsa uygulama başlatılırken net bir hata verir.
