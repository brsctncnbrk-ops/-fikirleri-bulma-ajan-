# TASKS.md

> Son güncelleme: 2026-06-13 · Yaşayan görev günlüğü. Durumlar: Bekliyor / Devam Ediyor / Test Ediliyor / Tamamlandı.

---

ID: TASK-001
Görev: Proje iskeleti + build/lint/test altyapısı ve örnek geçen test
Öncelik: Yüksek
Bağımlılıklar: —
Etkilenen Dosyalar: pyproject.toml, requirements*.txt, .gitignore, src/trendidea/__init__.py, tests/test_smoke.py
Tamamlanma Kriteri: ruff temiz, pytest yeşil, paket import edilebilir
Test Gereksinimi: Var (smoke test)
Durum: Tamamlandı

ID: TASK-002
Görev: Tam dokümantasyon seti (CLAUDE.md, README, .env.example, /docs/*)
Öncelik: Yüksek
Bağımlılıklar: TASK-001
Etkilenen Dosyalar: CLAUDE.md, README.md, .env.example, docs/*
Tamamlanma Kriteri: Tüm doküman dosyaları gerçek içerikle oluşturuldu, TBD'ler işaretli
Test Gereksinimi: Yok (saf dokümantasyon)
Durum: Tamamlandı

ID: TASK-003
Görev: Config (pydantic-settings) + logging + LLM maliyet sayacı iskeleti
Öncelik: Yüksek
Bağımlılıklar: TASK-001
Etkilenen Dosyalar: src/trendidea/config.py, logging_conf.py, tests/test_config.py
Tamamlanma Kriteri: .env yüklenir, eksik anahtar net şekilde raporlanır; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-004
Görev: SQLite şema + repository katmanı + dataclass modeller
Öncelik: Yüksek
Bağımlılıklar: TASK-001
Etkilenen Dosyalar: src/trendidea/db.py, models.py, tests/test_db.py
Tamamlanma Kriteri: Tablolar oluşur, CRUD round-trip testi geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-005
Görev: Scanner base + Hacker News fetcher (anahtarsız)
Öncelik: Yüksek
Bağımlılıklar: TASK-004
Etkilenen Dosyalar: src/trendidea/agents/scanner.py, agents/sources/hackernews.py, tests/test_scanner_hn.py
Tamamlanma Kriteri: HN yanıtı parse edilir (mock), Signal üretilir; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-006
Görev: GitHub Trending + Google Trends + RSS fetcher'ları + graceful skip
Öncelik: Orta
Bağımlılıklar: TASK-005
Etkilenen Dosyalar: agents/sources/github_trending.py, google_trends.py, rss.py, tests/*
Tamamlanma Kriteri: Her kaynak parse testi geçer, erişilemezlikte atlama loglanır
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-007
Görev: Reddit + Product Hunt fetcher'ları (anahtar varsa gerçek, yoksa atla)
Öncelik: Orta
Bağımlılıklar: TASK-005
Etkilenen Dosyalar: agents/sources/reddit.py, producthunt.py, tests/*
Tamamlanma Kriteri: Anahtar yoksa zarifçe atlar; mock yanıt parse testi geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-008
Görev: Signal Processor (kümeleme, gürültü ayıklama, skorlama)
Öncelik: Yüksek
Bağımlılıklar: TASK-005
Etkilenen Dosyalar: agents/signal_processor.py, tests/test_signal_processor.py
Tamamlanma Kriteri: Tekrarlayan sinyaller birleşir, skor üretilir; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-009
Görev: LLM wrapper + Anthropic web_search entegrasyonu + token sayacı
Öncelik: Yüksek
Bağımlılıklar: TASK-003
Etkilenen Dosyalar: src/trendidea/llm.py, tests/test_llm.py
Tamamlanma Kriteri: Mock'lu çağrı çalışır, token sayacı toplar; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-010
Görev: Idea Generator (şablonlu fikir üretimi)
Öncelik: Yüksek
Bağımlılıklar: TASK-008, TASK-009
Etkilenen Dosyalar: agents/idea_generator.py, tests/test_idea_generator.py
Tamamlanma Kriteri: Skorlu sinyalden şablon dolu Idea üretir (mock LLM); test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-011
Görev: Validator/Gatekeeper (5 test + web_search rakip doğrulama + skor)
Öncelik: Yüksek
Bağımlılıklar: TASK-010
Etkilenen Dosyalar: agents/validator.py, tests/test_validator.py
Tamamlanma Kriteri: Kanıtsız fikir elenir, geçenlere 0-100 skor; eleme mantığı testi geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-012
Görev: Reporter (markdown + Telegram özeti + dünle karşılaştırma)
Öncelik: Yüksek
Bağımlılıklar: TASK-011
Etkilenen Dosyalar: agents/reporter.py, tests/test_reporter.py
Tamamlanma Kriteri: Bölüm 5 formatında Türkçe rapor üretir; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-013
Görev: Telegram bot (komutlar + serbest sohbet + oturum bağlamı)
Öncelik: Yüksek
Bağımlılıklar: TASK-012
Etkilenen Dosyalar: telegram/bot.py, handlers.py, tests/test_telegram_handlers.py
Tamamlanma Kriteri: /bugun /fikir /tara /kaynaklar yönlendirme testi geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-014
Görev: Orchestrator + APScheduler + runs/ kaydı + retry/backoff + uçtan uca dry-run
Öncelik: Yüksek
Bağımlılıklar: TASK-012
Etkilenen Dosyalar: orchestrator.py, main.py, tests/test_orchestrator_dryrun.py
Tamamlanma Kriteri: --dry-run uçtan uca çalışır, runs/ altına rapor yazar; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-015
Görev: Dockerfile + railway.json + DEPLOYMENT/SETUP tamamlanması + kuru çalıştırma
Öncelik: Orta
Bağımlılıklar: TASK-014
Etkilenen Dosyalar: Dockerfile, railway.json, docs/DEPLOYMENT.md, docs/SETUP.md
Tamamlanma Kriteri: Dockerfile + railway.json hazır, deploy adımları belgelendi
Test Gereksinimi: Yok (config + dokümantasyon)
Not: `pip install .` (paket kurulumu) editable kurulumla doğrulandı; `docker build`
bu geliştirme ortamında Docker daemon olmadığından çalıştırılamadı — Railway/daemonlı
ortamda doğrulanmalı (tech-debt: CI'da docker build adımı eklenebilir).
Durum: Tamamlandı

ID: TASK-016
Görev: LLM token kullanımı + opsiyonel maliyet tahminini raporda göster (Bölüm 9)
Öncelik: Orta
Bağımlılıklar: TASK-012, TASK-014
Etkilenen Dosyalar: config.py, logging_conf.py, models.py, agents/reporter.py, orchestrator.py, tests/test_cost.py
Tamamlanma Kriteri: Rapor token kullanımını gösterir; fiyat girilmişse $ tahmini; fiyat uydurulmaz
Test Gereksinimi: Var
Durum: Tamamlandı

ID: TASK-017
Görev: RSS besleme listesini yapılandırılabilir yap (RSS_FEEDS env)
Öncelik: Düşük
Bağımlılıklar: TASK-006
Etkilenen Dosyalar: config.py, agents/sources/rss.py, .env.example, tests/test_rss_config.py
Tamamlanma Kriteri: Feed listesi env'den okunur, boşsa varsayılana düşer; test geçer
Test Gereksinimi: Var
Durum: Tamamlandı

---

## Oturum Günlüğü

### 2026-06-13
- Tamamlandı: Proje analizi, kullanıcı Q&A (anahtar yok / web_search / global+TR / Railway), plan onayı.
- Tamamlandı: TASK-001 → TASK-015 (tüm pipeline + dokümantasyon + Docker/Railway config).
- Doğrulama: 61 test geçti, ruff temiz; `--dry-run` uçtan uca çalıştı (GitHub Trending
  gerçek tarandı, diğer kaynaklar bu ortamda 403 → zarifçe atlandı), rapor `runs/` altına yazıldı.
- Yarım kalan / açık: API anahtarları kullanıcıda yok → tam çalıştırma (LLM fikir üretimi +
  Telegram) anahtarlar girilince doğrulanacak. `docker build` daemon olmadığından doğrulanamadı.
- Sonraki adım: Kullanıcı anahtarları girer (docs/SETUP.md), `python -m trendidea.main` ile
  tam akış denenir; Railway deploy (docs/DEPLOYMENT.md). Faz 2: Reddit/PH tam entegrasyon, RSS feed listesi.

### 2026-06-13 (devam)
- Tamamlandı: TASK-016 (raporda token/maliyet görünürlüğü — Bölüm 9 boşluğu kapatıldı),
  TASK-017 (yapılandırılabilir RSS beslemeleri).
- Doğrulama: 69 test geçti, ruff temiz, dry-run raporunda "💸 LLM kullanımı" satırı görünüyor.
- Sonraki adım: değişmedi — kullanıcı anahtarlarıyla tam akış + Railway deploy.
