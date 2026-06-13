# Changelog

> "Keep a Changelog" (keepachangelog.com) standardı · Semantic Versioning.

## [Unreleased]
### Added
- Proje iskeleti: ruff + pytest altyapısı, src/ paket düzeni, smoke test (TASK-001).
- Tam dokümantasyon seti: CLAUDE.md, README.md, .env.example ve /docs/* (TASK-002).
- Config (pydantic-settings) + JSON loglama + LLM maliyet sayacı (TASK-003).
- SQLite şema + repository katmanı + dataclass modeller (TASK-004).
- Scanner altyapısı + Hacker News, GitHub Trending, Google Trends, RSS, Reddit,
  Product Hunt kaynakları (anahtarsız çalışanlar + anahtar gerektirenlerde graceful skip) (TASK-005–007).
- Signal Processor: deterministik kümeleme + talep skorlaması (TASK-008).
- Anthropic LLM wrapper + server-side web_search + JSON yardımcısı (TASK-009).
- Idea Generator (şablonlu fikir üretimi) (TASK-010).
- Validator/Gatekeeper: Gerçeklik Kuralı 5 testi + web_search rakip doğrulama + 0-100 skor (TASK-011).
- Reporter: Türkçe günlük rapor (Markdown + Telegram özeti + dünle karşılaştırma) (TASK-012).
- Telegram komut yönlendirme + bot adaptörü (TASK-013).
- Orchestrator + APScheduler + Telegram servisi + `--dry-run`; `runs/` denetim artefaktları (TASK-014).
- Dockerfile + railway.json + dağıtım/kurulum dokümantasyonu (TASK-015).
- Raporda LLM token kullanımı + opsiyonel USD maliyet tahmini (fiyat uydurulmaz) (TASK-016).
- Yapılandırılabilir RSS besleme listesi (RSS_FEEDS env) (TASK-017).

### Fixed
- Railway deploy sağlamlaştırma (TASK-018): `tzdata` eklendi (slim imajda zaman dilimi
  çökmesini önler), `pyproject.toml`'a `[build-system]` ve `[project.dependencies]` eklendi
  (`pip install .` artık kendi kendine yeterli), python-telegram-bot 22.x için `post_init`
  builder üzerinden veriliyor.
