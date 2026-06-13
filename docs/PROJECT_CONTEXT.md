# PROJECT_CONTEXT.md

> Son güncelleme: 2026-06-13 · Projenin "Single Source of Truth" dosyası.

# Proje Özeti
Çok ajanlı bir sistem her gün güncel trendleri tarar, tekrarlayan talep/acı
sinyallerini tespit eder, bunlardan Claude Code ile hayata geçirilebilecek somut
iş fikirleri üretir, fikirleri gerçek kaynaklarla doğrular ve Türkçe günlük rapor
olarak Telegram üzerinden sunar. Sistemin tek değeri **gerçekliktir**.

# İş Hedefleri
- Kullanıcıya her gün, uygulanabilir ve kanıtlı iş fikirleri sunmak.
- Fikirden ilk gelire giden yolu somutlaştırmak (model + ilk müşteri + süre).
- TBD — uzun vadeli ticari hedef (kişisel kullanım / ürünleştirme) kullanıcıdan bekleniyor.

# Başarı Metrikleri
- Günde en az 1 doğrulanmış (≥2 kaynaklı, güven skoru ≥ eşik) fikir.
- Üretilen fikirlerin kaynak doğrulama oranı %100 (kanıtsız fikir yayınlanmaz).
- Pipeline günlük başarı oranı (hatasız çalıştırma) ≥ %95.
- TBD — kullanıcı tarafından "işe yarar" bulunan fikir oranı (geri bildirimle ölçülecek).

# Hedef Kitle
Tek kişi/küçük ekip olarak Claude Code ile hızlı MVP çıkarıp gelir aramak isteyen
indie geliştirici/girişimci. Birincil kullanıcı: proje sahibi.

# Kullanıcı Problemleri
- "Ne yapsam?" belirsizliği: bol trend, az somut/uygulanabilir fikir.
- Fikirlerin çoğu kanıtsız ve hayal ürünü; pazar/rakip doğrulaması zahmetli.
- Trendleri her gün manuel takip etmek zaman alıcı.

# Çözüm Tanımı
Otomatik günlük pipeline: Tarama → Sinyal işleme → Fikir üretimi → Doğrulama →
Raporlama → Telegram. Her fikir Gerçeklik Kuralı'nın 5 testinden geçer.

# Kullanıcı Akışları
1. Sistem her gün belirlenen saatte raporu Telegram'a yollar.
2. Kullanıcı `/bugun`, `/fikir <n>`, `/tara`, `/kaynaklar` komutlarıyla etkileşir.
3. Serbest mesajla o günkü rapor bağlamında soru-cevap yapar.

# Fonksiyonel Gereksinimler
- Çoklu kaynaktan son 24-72 saat verisi toplama (graceful degrade).
- Sinyal kümeleme + skorlama.
- Şablonlu fikir üretimi (LLM).
- 5 testlik doğrulama + web_search ile rakip doğrulama + 0-100 güven skoru.
- Markdown + Telegram raporu, dünkü raporla karşılaştırma.
- Telegram komutları + oturum bağlamı.
- Her çalıştırmanın denetlenebilir kaydı (`runs/`).

# Fonksiyonel Olmayan Gereksinimler
- Hata toleransı: timeout + retry + graceful degrade.
- Maliyet kontrolü: günlük LLM token/maliyet loglama.
- Rate limit'lere saygı (backoff), robots.txt/ToS uyumu, resmi API tercihi.
- Test edilebilirlik: canlı anahtar olmadan tüm testler geçer.

# Teknik Mimari
Bkz. `docs/ARCHITECTURE.md`. Tek konteyner; içeride APScheduler + Telegram bot
+ orchestrator. Depolama SQLite.

# Kullanılacak Teknolojiler
Python 3.11+, anthropic SDK, python-telegram-bot, APScheduler, pydantic-settings,
httpx, praw, pytrends, beautifulsoup4, SQLite, ruff, pytest, Docker, Railway.

# Sistem Bileşenleri
Orchestrator, Scanner (+kaynak fetcher'ları), Signal Processor, Idea Generator,
Validator/Gatekeeper, Reporter, Telegram Bot. Bkz. ARCHITECTURE.

# Entegrasyonlar
Hacker News API, Reddit (praw), Product Hunt GraphQL, GitHub Trending (scrape),
Google Trends (pytrends), Anthropic API (+web_search tool), Telegram Bot API.

# API Gereksinimleri
Dış API anahtarları: Anthropic (zorunlu), Telegram (zorunlu), Reddit & Product
Hunt (opsiyonel). Bkz. `docs/API.md` ve `docs/SETUP.md`.

# Veritabanı Gereksinimleri
SQLite tablolar: signals, clusters, ideas, reports, runs, sessions. Bkz. ARCHITECTURE.

# Güvenlik Gereksinimleri
Anahtarlar yalnızca `.env`; repoya/loga asla yazılmaz. Bkz. `docs/SECURITY.md`.

# Performans Gereksinimleri
Günlük tek çalıştırma; gerçek zamanlı SLA yok. Kaynak çağrıları paralel/timeout'lu.

# Ölçeklenebilirlik Gereksinimleri
Başlangıçta tek kullanıcı/tek konteyner. Çoklu kullanıcı = Gelecek Özellik.

# SEO Gereksinimleri
Uygulanamaz (web sitesi değil).

# Test Stratejisi
Bkz. `docs/TESTING.md`. Birim testler + uçtan uca dry-run; HTTP `respx`, LLM/Telegram mock.

# Yayınlama Stratejisi
Docker imajı → Railway. Bkz. `docs/DEPLOYMENT.md`.

# Risk Analizi
Bkz. `docs/RISKS.md`.

# Karar Günlüğü
Bkz. `docs/DECISIONS.md`.

# Kapsam Dışı (Out of Scope)
- Çoklu kullanıcı/SaaS arayüzü.
- Fikirlerin otomatik olarak koda dönüştürülüp deploy edilmesi.
- Ödeme/abonelik altyapısı.

# Gelecek Özellikler
- Web tabanlı dashboard.
- Fikir başına otomatik MVP iskeleti üretimi.
- Çoklu kullanıcı ve kişiselleştirilmiş niş takibi.

# Varsayımlar
- Kullanıcının makinesinde/Railway'de dış ağ erişimi vardır (bu remote ortamda kısıtlı olabilir).
- Global trendler İngilizce ağırlıklıdır; rapor Türkçe sunulur.
- Tek birincil kullanıcı (proje sahibi) hedefleniyor.

# AI Ajan Kuralları
Bkz. `docs/AI_AGENT_RULES.md`.
