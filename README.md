# Trend → İş Fikri Ajanı

Her gün güncel trendleri tarayıp **kanıta dayalı**, Claude Code ile kısa sürede
hayata geçirilebilecek iş fikirleri üreten çok ajanlı sistem. Fikirleri doğrular,
Türkçe günlük rapor üretir ve Telegram üzerinden sunar.

## Hızlı Başlangıç

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .       # 'trendidea' paketini kur (python -m trendidea.main için)
cp .env.example .env   # anahtarları doldur (bkz. docs/SETUP.md)
```

### Anahtarsız deneme (dry-run)
Ücretsiz kaynaklardan (Hacker News, GitHub Trending, Google Trends) sinyal çeker
ve iskelet pipeline'ı uçtan uca çalıştırır; LLM/Telegram adımları mock'lanır:

```bash
python -m trendidea.main --dry-run
```

### Tam çalıştırma
`.env` doldurulduktan sonra zamanlayıcı + Telegram botu birlikte çalışır:

```bash
python -m trendidea.main
```

## Geliştirme

```bash
ruff check . && ruff format --check .   # lint
pytest                                  # test (canlı anahtar gerekmez)
```

## Dokümantasyon
- Kurulum & API anahtarları: [docs/SETUP.md](docs/SETUP.md)
- Mimari: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Proje bağlamı: [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md)
- Deploy (Railway): [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Güvenlik
Tüm anahtarlar `.env`'de tutulur ve repoya **asla** girmez. Detay: [docs/SECURITY.md](docs/SECURITY.md).
