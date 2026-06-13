# TESTING.md

> Son güncelleme: 2026-06-13

## İlkeler
- **Testler canlı API anahtarı gerektirmez.** Dış çağrılar mock'lanır.
- HTTP: `respx` ile httpx çağrıları stub'lanır.
- Anthropic & Telegram: `unittest.mock` ile sahte istemci/yanıt.
- Her ajan için en az bir birim testi; pipeline için bir uçtan uca dry-run testi.

## Kritik akış kapsamı (Bölüm 6 Kalite Kapısı)
- Tarayıcı parse: HN/GitHub/Trends yanıtından `Signal` üretimi.
- Doğrulayıcı eleme: kanıtsız fikir elenir, geçenlere 0-100 skor.
- Rapor üretimi: Bölüm 5 formatında Türkçe çıktı.
- Telegram komut yönlendirme: `/bugun /fikir /tara /kaynaklar`.

## Çalıştırma
```bash
pytest            # tüm testler
ruff check .      # lint
ruff format --check .
```

## Kalite Kapısı
build (import/çalışır) + lint (ruff temiz) + test (pytest yeşil) üçü birden
geçmeden commit yapılmaz. Geçmeyen test silinmez/skip edilmez; assertion zayıflatılmaz.
