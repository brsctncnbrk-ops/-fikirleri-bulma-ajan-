# API.md

> Son güncelleme: 2026-06-13 · Dış servisler ve dahili ajan sözleşmeleri.

## Dış Servisler
| Servis | Erişim | Anahtar | Not |
|---|---|---|---|
| Hacker News | Firebase REST API | Hayır | `topstories`, `item/<id>` |
| GitHub Trending | HTML scrape | Hayır | robots.txt'e uyum, backoff |
| Google Trends | pytrends | Hayır | Resmi olmayan; rate'e dikkat |
| RSS beslemeleri | HTTP | Hayır | Yapılandırılabilir feed listesi (TBD: liste) |
| Reddit | praw | Evet (opsiyonel) | client_id/secret/user_agent |
| Product Hunt | GraphQL | Evet (opsiyonel) | developer token |
| Anthropic | Messages API + web_search tool | Evet (zorunlu) | `web_search_20250305` server tool |
| Telegram | Bot API | Evet (zorunlu) | python-telegram-bot |

## Dahili Ajan Sözleşmeleri (dataclass/JSON)
Ajanlar arası veri `models.py`'deki dataclass'larla taşınır:
- `Signal{source, url, title, summary, published_at, metric}`
- `Cluster{label, score, signals[]}`
- `Idea{title, signal_refs[], target_customer, pain, revenue_model,
  first_revenue_estimate, mvp_scope, dev_time, competitors[], main_risk,
  confidence, validation_notes, status}`
- `Report{date, scanned_sources[], trends[], ideas[], unknowns[]}`

## Telegram Komutları
| Komut | İşlev |
|---|---|
| `/bugun` | Bugünün raporu |
| `/fikir <n>` | n. fikrin detayını derinleştir |
| `/tara` | Manuel anlık tarama tetikle |
| `/kaynaklar` | Taranan kaynakların durumu |
| (serbest mesaj) | O günkü rapor bağlamında soru-cevap |
