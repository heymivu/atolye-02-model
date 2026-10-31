# Hangi işe hangi model: eşleme tablosu

Kural tek cümle: **en ucuz modelle başla, sonucu kontrol et, tökezlediği yerde bir basamak çık.**

Benzetme üç basamak: **çırak** (en ucuz, en hızlı model), **kalfa** (orta), **usta** (en güçlü model). Bazı şirketlerde bir de **ustaların ustası** var. Bizim deneyde ondan daha iyi sonuç almadık.

> **Fiyatlar değişir. Aşağıdaki her sayı 30 Ekim 2026'da resmî sayfadan okundu. Kullanmadan önce tarihe bak, kaynağı yeniden aç.**

---

## Üç soru

1. **Cevabı kontrol edebiliyor musun?** Etiket, tablo, sayım, testi olan kod kolayca kontrol edilir. Kontrol edebiliyorsan çırakla başla.
2. **Yanlışsa bedeli ne?** Para ya da geri dönüşü olmayan bir karar varsa basamak çık.
3. **Bu iş kaç kez tekrar ediyor?** Günde yüz kez yapılan işte çırağın farkı en büyük, çünkü küçük fark yüz kez birikir.

**Dördüncü not (zor turdan):** asıl soru işin zor olup olmadığı değil, **yanlışın fark edilip edilmeyeceği**. Bilgi eksik olabilecek ve yanlışı kimsenin fark etmeyeceği iş → usta. Deneyde eski fiyatı eksik bir defter verdik. Kalfa ve usta üç denemenin üçünde "eski fiyat olmadan hesaplanamaz" dedi. Çırak üç denemenin birinde yalnız bildiği kısmı toplayıp toplam diye yazdı.

---

## Görev türü → kademe

"Bizim deneyde" sütunu [`deney/`](deney/) klasöründeki ölçümden. Uydurma bir kafe, her iş 3 kez. Senin işinde de önce birkaç örnekle kontrol et.

| İş | Kademe | Neden | Bizim deneyde |
|---|---|---|---|
| Yorum ayıklama, olumlu/olumsuz etiketi, sınıflandırma | çırak | kontrol edilir, çok tekrar eder | 40 yorum × 3 etiket, 3 koşu: çırak 359/360, alaycı yorumlar 18/18 |
| Metinden tablo çıkarma, birim çevirme | çırak | kontrol edilir | teklif tablosu ve koli→litre: her modelde 3/3 |
| Sayma | çırak, ama örneklemle kontrol et | kolay kontrol edilir, kayabilir | çırak bir kez 5 isteği 4 saydı (3'te 2 doğru) |
| Özet, çeviri | çırak | okuması kolay, çok tekrar eder | ölçülmedi |
| Uzun belgeden hesap | çırak, sonucu kontrol et | kontrol edilir; **100 bin token eşiğine dikkat** | iki aylık defter (~55 bin karakter): çırak 3/3, ustanın ~1/10 fiyatına |
| Çok adımlı hesap (zam, fire, KDV, marj) | çırak, sonucu kontrol et | kontrol edilir | latte fiyatı: her modelde 3/3 |
| Testi olan kod düzeltme | çırak | testler cevabı kontrol eder | kasa betiğinde 4 hata, gizli 8 test: her modelde 3/3 |
| Testi olmayan kod | kalfa | yanlış geç fark edilir | ölçülmedi |
| Kurallı, marka sesiyle yazı (gönderi, e-posta) | kalfa | kalite yargısı, kontrolü zor | 8 kural + "Pazartesi kapalı": çırak, kalfa, usta 3/3; düşük çabalı usta 2/3 |
| Para ya da geri dönüşü olmayan karar | usta | yanlışsa bedeli yüksek | süt tedarikçisi kararı: her modelde 3/3, çırak dâhil. Yine de usta, çünkü yanlışın bedeli büyük |
| Bilgi eksik olabilecek, yanlışı fark edilmeyecek iş | usta | uydurmamak gerekiyor | eksik defter: çırak 3'te 1 kısmi toplamı toplam yazdı; kalfa ve usta 3/3 "hesaplanamaz" |

Kod yazmıyorsan sohbet uygulamandaki **model seçici** yeterli. Özeti, çeviriyi ve yorum ayıklamayı hızlı modele ver, önemli kararı en güçlüsüne bırak. Kod yazıyorsan aynı tablo [`yonlendir.py`](yonlendir.py)'nin başında, düzenlenebilir hâlde duruyor.

**Model değiştirmeden önce çabayı da dene.** Anthropic'in model seçme rehberi çaba (effort) ayarını çoğu zaman model değiştirmekten iyi bir kaldıraç sayıyor. Bizim haftada düşük çabalı Opus %17 ucuzdu ve bir kural ihlali yaptı.

---

## Üç şirketin merdiveni (30 Ekim 2026)

1 milyon token başına ABD doları, standart katman.

### Anthropic
Kaynak: https://platform.claude.com/docs/en/about-claude/pricing (sayfada tarih yok; 2026-10-30 okundu)

| Kademe | Model · kimlik | Giriş | Önbellek yazma 5 dk / 1 sa | Önbellekten okuma | Çıkış |
|---|---|---|---|---|---|
| Çırak | Claude Haiku 5.5 · `claude-haiku-5-5` (istem ≤ 100 bin token) | 0,10 | 0,125 / 0,20 | 0,01 | 0,50 |
| Çırak, uzun istem | Claude Haiku 5.5 (istem > 100 bin token) | 0,50 | 0,625 / 1 | 0,05 | 2,50 |
| Kalfa | Claude Sonnet 5.5 · `claude-sonnet-5-5` | 2 | 2,50 / 4 | 0,10 | 10 |
| Usta | Claude Opus 5.5 · `claude-opus-5-5` | 4 | 5 / 8 | 0,20 | 20 |
| Ustaların ustası | Claude Fable 5.1 · `claude-fable-5-1` | 10 | 12,50 / 20 | 0,25 | 50 |

Çıkışta Fable ÷ Haiku = 100 kat, Opus ÷ Haiku = 40 kat, Opus ÷ Sonnet = 2 kat. Büyük tasarruf usta → çırak basamağında.

### OpenAI
Kaynak: https://developers.openai.com/api/docs/pricing (sayfada tarih yok; 2026-10-30 okundu). Kısa bağlam (≤ 272 bin giriş token).

| Kademe | Model | Giriş | Önbellekli giriş | Çıkış |
|---|---|---|---|---|
| Çırak | gpt-6-luna | 0,10 | 0,01 | 0,50 |
| Kalfa | gpt-6.1-terra | 1,00 | 0,05 | 5,00 |
| Usta | gpt-6.1-sol | 2,00 | 0,10 | 10,00 |
| Ustaların ustası | gpt-6-astra | 10,00 | 1,00 | 50,00 |

### Google Gemini
Kaynak: https://ai.google.dev/gemini-api/docs/pricing (sayfada "Last updated 2026-10-28 UTC"; 2026-10-30 okundu). Ücretli katman.

| Kademe | Model · kimlik | Giriş | Çıkış | Not |
|---|---|---|---|---|
| Çırak | Gemini 3.5 Flash-Lite · `gemini-3.5-flash-lite` | 0,30 | 2,50 | |
| Kalfa | Gemini 3.8 Flash · `gemini-3.8-flash` | 0,75 | 3,75 | **1 Ocak 2027'de 1,50 / 7,50'ye çıkıyor (iki kat)** |
| Usta | Gemini 3.1 Pro Preview · `gemini-3.1-pro-preview` | 2,00 (≤ 200 bin) / 4,00 | 12,00 / 18,00 | önizleme |

---

## İki uyarı

- **Uzun belge tuzağı:** Claude Haiku 5.5'te istemi 100 bin token'ı geçen istek 5 kat fiyattan faturalanır (önbellekten okunan token'lar da sayılır). Eşik her isteğe ayrı uygulanır. Çırağa çok uzun bir belgeyi tek seferde okutmak ucuz olmayabilir. `yonlendir.py` ve `fatura.py` bu eşiği istek başına uygular.
- **Toplu gönderim (Batch API):** acele etmeyen işlerde giriş ve çıkış fiyatı %50 iner (Anthropic ve OpenAI sayfalarında). Önbellek indirimiyle birleşebilir.

> Fiyatlar 30 Ekim 2026 tarihli. Değişirler. Kaynağı açmadan bu tablodaki sayıyla karar verme.
