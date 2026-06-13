# AI_AGENT_RULES.md

> Son güncelleme: 2026-06-13 · Bu projede çalışan tüm AI ajanları için bağlayıcı kurallar.

1. Her oturuma `CLAUDE.md` ve `PROJECT_CONTEXT.md` okuyarak başla; sonra `TASKS.md` "Oturum Günlüğü"nden kaldığın yeri al.
2. Mimariye aykırı işlem yapma; gerekiyorsa önce `DECISIONS.md`'e öneri yaz ve onay al.
3. Büyük kararları `DECISIONS.md`'e yaz (tarih, gerekçe, alternatifler, sonuç).
4. Anlamlı değişiklik sonrası `CHANGELOG.md` güncelle.
5. Tamamlanan görevleri `TASKS.md`'de yalnızca testler geçtikten sonra işaretle.
6. Bir görevi bitirmeden yenisine başlama.
7. Teknik borç oluşturma; kaçınılmazsa `TASKS.md`'e "tech-debt" etiketiyle kaydet.
8. Güvenlik standartlarını ihlal etme (`SECURITY.md`).
9. Gereksiz bağımlılık ekleme; yeni paket öncesi gerekçe belirt.
10. Dosya yapısını bozma; yeni klasör gerekiyorsa `ARCHITECTURE.md`'i güncelle.
11. Her işlem sonunda kısa ilerleme raporu ver (yapılan, kalan, sonraki adım).
12. Hata olursa kök neden analizi yap; semptomu değil nedeni düzelt.
13. **Takılma kuralı:** aynı hatada 3 denemeden fazla yapma; dur, denenenleri ve hipotezi raporla, yön iste.
14. Varsayımları açıkça dokümante et (`PROJECT_CONTEXT.md` → Varsayımlar).
15. Yeni özellik öncesi kapsam kontrolü; kapsam dışıysa "Gelecek Özellikler"e yaz.
16. Yıkıcı işlemler (silme, sıfırlama, migration, force push) için önce onay al.
17. Görevle ilgisi olmayan çalışan kodu yeniden yazma (gereksiz refactor yok).
18. Gizli bilgileri (key, şifre, token) asla koda/loga/dokümana yazma.
19. **Oturum devri:** her oturum sonunda `TASKS.md` "Oturum Günlüğü"ne tarihli kayıt ekle (ne bitti, ne yarım, sonraki adım). Son 5 oturum detaylı; eskiler "Geçmiş Özeti"ne sıkıştırılır.

## Gerçeklik Kuralı (mutlak)
- Kanıtsız fikir = geçersiz fikir (≥2 gerçek tarihli kaynak).
- İstatistik/rakip/şirket adı uydurma; doğrulanamayanı "doğrulanamadı" işaretle.
- Bilinmeyene `TBD` yaz; dolgu yapma. Az gerçek fikir, çok sahte fikirden iyidir.
