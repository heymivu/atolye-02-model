# Görevler (her kola aynı cümlelerle verilir)

Her çağrıda sistem notu aynı: "Köşe Kahve'nin sahibi Ayşe için çalışıyorsun. Ekteki dosyalar işletmenin güncel bilgisidir. Türkçe yaz." Ekler her görevin altında. Her görev ayrı ve yeni bir sohbet (önceki görevin çıktısı verilmez; G4–G5 kendi girdilerini ham dosyalardan okur).

## G1 — Yorum etiketleme (ekler: YORUMLAR.md)
Ekteki 40 yorumun her birini etiketle.
- konu (tek): kahve | hizmet | fiyat | ortam | urun_istegi (menüye yeni ürün isteği)
- duygu: + (memnun) | - (şikâyet) | 0 (ne övgü ne şikâyet: soru, istek)
- cevap: evet (şikâyet, soru ya da istek varsa) | hayır (yalnız övgü)
Yalnız JSON dizi ver, başka metin yazma: [{"id": 1, "konu": "...", "duygu": "...", "cevap": "..."}, ...]

## G2 — Teklif tablosu (ekler: TEKLIFLER.md)
Ekteki üç teklifi tek tabloya dök. Fiyatları litre başına TL olarak ver (gerekirse çevir); verilmeyen ürün null.
Yalnız JSON ver: {"tedarikciler": [{"ad": "...", "inek_tl_lt": 0, "yulaf_tl_lt": 0, "badem_tl_lt": null, "teslim_gunleri": ["..."], "min_siparis_lt": 0, "vade_gun": 0}]}
teslim_gunleri: Türkçe gün adları; her gün teslim ediyorsa yedi günü yaz. Peşin ödeme vade_gun = 0.

## G3 — Instagram planı (ekler: TALIMAT.md, ORNEKLER.md, ISLETME.md)
Bu haftanın Instagram planını ve 3 gönderiyi yaz.

## G4 — Tedarikçi kararı (ekler: ISLETME.md, TEKLIFLER.md)
Bu ay sütü hangi tedarikçiden alalım? Tek tedarikçi seç ve kısa gerekçe yaz.
Son satırda yalnız şu JSON olsun: {"secim": "<tedarikçi adı>", "elenenler": {"<ad>": "<neden>", "<ad>": "<neden>"}}

## G5 — Badem sütü (ekler: ISLETME.md, TEKLIFLER.md, YORUMLAR.md)
Müşteriler badem sütü istiyor. Badem sütü menüye girsin mi? Önerini kısa yaz.
Son satırda yalnız şu JSON olsun: {"oneri": "ekle | ekleme | ayse_karar_versin", "istek_sayisi": 0, "badem_tedarikcisi": "<ad ya da yok>", "gerekce": "..."}
