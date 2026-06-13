# RISKS.md

> Son güncelleme: 2026-06-13 · Olasılık/Etki: Düşük / Orta / Yüksek

## Teknik Riskler
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Kaynak API/HTML değişimi parse'ı bozar (GitHub Trending scrape) | Orta | Orta | Resmi API tercihi, parse testleri, graceful skip + log |
| Anthropic web_search sonuçları yetersiz/yanlış rakip döndürür | Orta | Orta | "doğrulanamadı" işaretleme, ≥2 kaynak zorunluluğu, skor düşürme |
| Bu remote ortamda dış ağ kısıtlı → canlı tarama başarısız | Yüksek | Düşük | Testler mock'la geçer; gerçek tarama kullanıcı ortamı/Railway'de |
| LLM çıktısının JSON şemasına uymaması | Orta | Orta | Şema doğrulama + tek yeniden deneme + güvenli fallback |

## Operasyonel Riskler
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Konteyner yeniden başlatınca SQLite kaybı | Orta | Orta | Railway kalıcı volume; DEPLOYMENT'ta belgelenir |
| Zamanlayıcı kaçırılan çalıştırma | Düşük | Düşük | APScheduler misfire_grace_time + manuel /tara |

## Finansal Riskler
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| LLM/web_search token maliyetinin beklenenden yüksek olması | Orta | Orta | Günlük token/maliyet loglama, fikir sayısı sınırı, ucuz model ucuz işlerde |

## Güvenlik Riskleri
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| API anahtarının repoya/loga sızması | Düşük | Yüksek | .gitignore, .env, loglarda maskeleme, secret-scan |
| Yetkisiz Telegram chat'inin botu kullanması | Orta | Orta | TELEGRAM_CHAT_ID allowlist kontrolü |

## Ölçeklenebilirlik Riskleri
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Çoklu kullanıcı/yük artışında SQLite darboğazı | Düşük | Orta | Postgres geçiş planı (Gelecek) |

## Bakım Riskleri
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Bağımlılık eskimesi/kırılma | Orta | Düşük | Sürüm pinleme, testlerle erken tespit |

## Yasal Riskler
| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Scraping'in hedef site ToS/robots.txt ihlali | Orta | Orta | Resmi API tercihi, robots.txt'e uyum, makul rate/backoff |
| Kişisel veri işleme (KVKK/GDPR) | Düşük | Orta | Kişisel veri toplanmıyor; yalnız kamuya açık trend verisi (TBD: Telegram chat logları saklanırsa gözden geçir) |
