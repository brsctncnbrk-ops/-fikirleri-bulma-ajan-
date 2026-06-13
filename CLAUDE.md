# CLAUDE.md

> Son güncelleme: 2026-06-13

## Proje Özeti
Her gün otomatik olarak güncel trendleri tarayıp, Claude Code ile hayata
geçirilebilecek ve kısa sürede gelir üretebilecek **kanıta dayalı** iş fikirleri
üreten çok ajanlı bir sistem. Fikirler doğrulanır, raporlanır ve Telegram
üzerinden sunulur. Global trend taraması, Türkçe rapor.

## Komutlar
- Kurulum: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt`
- Dry-run (anahtarsız test): `python -m trendidea.main --dry-run`
- Servis (zamanlayıcı + bot): `python -m trendidea.main`
- Test: `pytest`
- Lint/Format: `ruff check .` ve `ruff format .`

## Teknoloji Yığını
Python 3.11+ · anthropic SDK (Claude) · python-telegram-bot · APScheduler ·
pydantic-settings · httpx · praw · pytrends · beautifulsoup4 · SQLite (stdlib).
Kalite: ruff + pytest. Deploy: Docker + Railway.

## Dosya Yapısı
- `src/trendidea/` — uygulama kodu (`agents/`, `telegram/`, `config.py`, `db.py`, `llm.py`, `orchestrator.py`, `main.py`)
- `tests/` — birim ve uçtan uca testler
- `docs/` — tüm dokümantasyon
- `runs/` — zaman damgalı çalıştırma çıktıları (gitignore'lu)

## Kodlama Standartları
- Kod dili: İngilizce (değişken/fonksiyon/dosya isimleri)
- Yorum/dokümantasyon dili: Türkçe (kullanıcı tercihi)
- İsimlendirme: snake_case (Python)
- Formatter/Linter: ruff (line-length 100)

## Zorunlu Dokümanlar
- Detaylı bağlam: `docs/PROJECT_CONTEXT.md`
- Mimari: `docs/ARCHITECTURE.md`
- Görevler ve durum: `docs/TASKS.md`
- Kararlar: `docs/DECISIONS.md`
- Ajan kuralları: `docs/AI_AGENT_RULES.md`
- Kurulum & anahtarlar: `docs/SETUP.md`

## Kritik Kurallar
1. Her oturuma `docs/PROJECT_CONTEXT.md` ve `docs/TASKS.md` (Oturum Günlüğü) okuyarak başla.
2. Görev tamamlanmadan önce build + lint + test çalıştır ve geçtiğini doğrula.
3. Yıkıcı işlemler (dosya silme, db sıfırlama, force push) için önce kullanıcı onayı al.
4. `.env` ve gizli anahtarları asla commit'leme, asla koda gömme.
5. **Gerçeklik Kuralı:** kanıtsız fikir geçersizdir; istatistik/rakip uydurma, bilinmeyene `TBD` yaz.
6. Aynı hatada 3 başarısız denemeden sonra dur ve kullanıcıya raporla.
