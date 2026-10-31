# Köşe Kahve deneyi: sonuç

İlk tur 2026-10-30, düzeltme ve zor tur 2026-10-31.

**Nasıl ölçüldü:** Claude Code alt ajanlarıyla, abonelik içinde. Ücretli API çağrısı yapılmadı. Maliyet = kayıttaki token × 2026-10-30 API liste fiyatı. Bu yüzden tutarlar **API liste fiyatıyla hesaplandı**, ödenmiş bir fatura değil. Otomatik tablolar `sonuc/ozet.md` (`analiz.py` üretir), ham çıktılar `ham/altajan/`.

## Ne çalıştırıldı
- 5 kurulum × 5 görev × **3 tekrar** = 75 koşu + 10 taban koşusu (boş görev, G0). Plan 5 tekrardı (Fable 3). Kalite tavanda olduğu için 3'te durduruldu.
- Kurulumlar: Haiku 5.5 (çaba medium), Sonnet 5.5 (high), Opus 5.5 (medium), Opus 5.5 (low), Fable 5.1 (high). Çaba ayarı alt ajana verildi ve kayda yazılmıyor, bu yüzden `.usage.json` dosyalarına ayrıca girildi. Düşük çabalı Opus'un çıkış token'ı belirgin düşük (G3 1.548 ↔ 2.435, G5 1.173 ↔ 1.642), yani ayar uygulanmış.
- Kirlenme kontrolü: 85 alt ajanın 85'i yalnız kendi istem dosyasını okudu ve kendi çıktısını yazdı. Doğru cevap dosyasını açan olmadı. (Kontrol tablosu oturum kimlikleri içerdiği için yayımlanmadı.)
- Alt ajanlara verilen istemler birebir `istemler/` klasöründe.

## Kalite
| Görev | Haiku | Sonnet | Opus | Opus·düşük | Fable |
|---|---|---|---|---|---|
| G1 · 40 yorum, 120 etiket (×3) | 359/360 | 360/360 | 360/360 | 360/360 | 360/360 |
| G1 · alaycı yorumlar (6×3) | 18/18 | 18/18 | 18/18 | 18/18 | 18/18 |
| G2 · teklif tablosu + koli→litre | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| G3 · 8 kural + Pazartesi kapalı | 3/3 | 3/3 | 3/3 | 2/3 (1 gönderi soruyla bitmedi) | 3/3 |
| G4 · süt kararı (Pazartesi tuzağı) | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| G5 · badem: istek sayısı (5) | 2/3 (bir kez 4) | 3/3 | 3/3 | 3/3 | 3/3 |
| G5 · badem: kuralı Ayşe'ye bıraktı | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| G5 · badem tedarikçisi (anahtar: Marmara) | 3/3 | 1/3 ("yok" 2) | 3/3 | 3/3 | 2/3 ("yok" 1) |

- **Ucuz model karar tuzağına düşmedi.** 15 süt kararının 15'i doğru, hepsinde gerekçe Ova Süt'ün Pazartesi teslimatı.
- **Cevap anahtarımızda hata vardı.** Kadıköy Çiftlik koliyle satıyor. 70 + 20 litre tam koliye yuvarlanınca 5.232 TL ediyor ve bütçe (5.000 TL) aşılıyor. Biz litre fiyatıyla 4.810 TL yazmıştık. **15 karar koşusunun 15'i bunu fark etti** (her kurulumda 3/3). Doğru seçim değişmiyor (tek uygulanabilir seçenek), anahtara not düşüldü (`girdiler/dogru.json`).
- G5 tedarikçi ölçütü tartışmalı: "yok" diyen 3 cevap Marmara'yı peşin ödeme ve nakit sıkışıklığı yüzünden elemiş, bu savunulabilir. Katı puanla Sonnet 1/3, Fable 2/3. Esnek puanla hepsi 3/3.
- Haiku'nun tek gerçek kayması **sayma**: bir koşuda 5 badem isteğini 4 saydı, 360 etiketten 1'ini (yorum 38, mocha) yanlış etiketledi.

## Maliyet
API liste fiyatıyla, istek başına. "Ham" = alt ajanın tüm faturası, Claude Code'un kendi sistem metni dâhil. "Görev payı" = ham − taban × 5.

| Kurulum | Taban (boş iş) $ | Bir hafta (G1–G5) ham $ | Görev payı $ |
|---|---|---|---|
| Haiku 5.5 | 0,007 | **0,042** | 0,008 |
| Sonnet 5.5 | 0,104 | 0,834 | 0,316 |
| Opus 5.5 | 0,207 | **1,474** | 0,440 |
| Opus 5.5 · düşük çaba | 0,207 | 1,230 | 0,196 |
| Fable 5.1 | 0,480 | **3,938** | 1,541 |
| Dağıtılmış (Haiku·Haiku·Sonnet·Opus·Opus) | — | 0,722 | 0,191 |

- **Hep Opus ÷ hep Haiku = 35 kat** (ham). İşin kendisinde 54 kat, ama bu sayı alt ajan kurulumuna özel.
- **Planladığımız dağıtım (çırak/kalfa/usta) yalnız 2,0 kat** kazandırdı (fatura yarıya indi), çünkü kararlar Opus'ta kaldı ve Opus 5.5 artık Sonnet'in yalnız iki katı.
- **Fable haftası Opus'un 2,7 katı, Haiku'nun 93 katı.** Kalite daha iyi değil.
- Düşük çabalı Opus haftası %17 ucuz, bir kural ihlaliyle.
- Haiku daha çok yazıyor (G3 çıkış 5.055 token ↔ Opus 2.435), yine de en ucuz, çünkü token'ı 40 kat ucuz.

### Düzeltme (2026-10-31)
Haiku 5.5'in "istem > 100 bin token → 5 kat fiyat" kademesini ilk hesapta alt ajanın **toplam** token'ına uygulamıştık. Kural tek isteğin istemine bakar. Hiçbir Haiku isteği 100 bini geçmedi (en büyüğü 78.819), yani Haiku tutarları tam 5 kat şişkindi. İstek başına fiyatla yeniden hesaplandı: hep Haiku 0,211 → **0,042 $**, hep Opus ÷ hep Haiku 7 → **35 kat**, dağıtılmış 0,786 → 0,722 $ (2,0 kat). Diğer modeller değişmedi. `yonlendir.py` ve `fatura.py` aynı kuralı istek başına uygular.

## Zor görev turu (2026-10-31)
Soru: zor işte çırak tökezler mi? Aynı protokol: alt ajan yalnız kendi istemini okur, cevabı dosyaya yazar. Doğru cevaplar koşudan önce yazıldı (`zor/uret.py` → `zor/dogru_zor.json`). Puanlayıcı öz-testi 19/19 (`zor/test/oz_test_zor.py`). Kirlenme kontrolü 36/36 temiz (Haiku'nun 4 koşusunda işi yazdıktan sonra dosyaya dokunmayan gereksiz araç çağrıları var, biri reddedildi).
Kurulumlar: Haiku 5.5 (medium), Sonnet 5.5 (high), Opus 5.5 (medium). Her görev 3 tekrar, fiyat istek başına.

| Görev | Haiku | Sonnet | Opus | Koşu başı $ (H · S · O) |
|---|---|---|---|---|
| Z1 · iki aylık defter (~55 bin karakter): Kasım yulaf faturası, doğru 28 koli / 14.448 TL (düzeltme, iade, zam, litre→koli, numune, Aralık siparişi, Ekim teslimatı tuzakları) | 3/3 | 3/3 | 3/3 | 0,035 · 0,183 · 0,367 |
| Z1e · aynı defter, eski koli fiyatı YOK: doğru cevap "hesaplanamaz" | **2/3** (1 kez yalnız zamlı kısmı, 7.476 TL, toplam diye yazdı) | 3/3 | 3/3 | 0,035 · 0,252 · 0,491 |
| Z2 · Aralık latte fiyatı (zamlı çekirdek, köpük firesi, KDV, komisyon, %65 marj, 5'e yuvarlama), doğru 140 TL | 3/3 | 3/3 | 3/3 | 0,010 · 0,144 · 0,310 |
| Z3 · kasa betiğinde 4 hata, gizli 8 test | 3/3 (8/8) | 3/3 | 3/3 | 0,011 · 0,161 · 0,323 |

- **Zorlaştırınca da çırak düşmedi:** uzun belge, çok adımlı hesap ve kod düzeltmede her denemede doğru. Z1'de Opus'un ~1/10'u fiyatına.
- **Tek ayrım eksik bilgide.** Z1e bizim kurulum hatamızdan doğdu: ilk koşuda eski fiyatı deftere yazmayı unutmuştuk ve üç model de bunu fark etti. Davranış ayrıldığı için aynı istem ayrı görev yapıldı (bayt bayt aynı, `uret.py` içinde assert), doğru cevap "hesaplanamaz" olarak koşudan önce yazıldı ve 2 tekrar daha koşuldu. Sonnet ve Opus 3/3 "hesaplayamam" dedi. Haiku 3'te 1 kez kısmi tutarı toplam alanına yazdı (metinde "eski fiyatlı kısım dahil değil" notu var, JSON'da yok). Tek örnek: "çırak bilgi eksikken uydurur" genellemesi yapılmaz, "3'te 1" denir.

## Sınırlar
Uydurma kafe, kolay bir hafta artı üç zor iş, tek şirketin modelleri, her iş üç kez. Görevler kısa ve kontrol edilebilir. Uzun ajan işi ölçülmedi. Alt ajan tutarları Claude Code'un sistem metnini de taşır, bu yüzden mutlak tutar doğrudan API çağrısına göre şişkindir; kurulumlar arası kıyas geçerlidir. Anthropic'in kendi kod ölçümünde Opus'a Haiku yardımcıları eklemek maliyeti %32 düşürüp geçme oranını ~4 puan indirdi (https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence, 2026-10-30 okundu).
