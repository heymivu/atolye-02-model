# Hangi işe hangi model: çırak, kalfa, usta

**Mivu Atölye 2** · Video: [YouTube, @heymivu](https://www.youtube.com/@heymivu)

Yapay zekâya verdiğin her işi en pahalı modele gönderiyorsan, faturanın çoğu gereksiz olabilir. Bizim ölçtüğümüz haftada en ucuz model aynı işleri doğru yaptı ve **35 kat ucuza** geldi. Bu repo üç şey veriyor: hangi işin hangi basamağa gittiğini gösteren bir tablo, işleri otomatik dağıtan küçük bir betik ve Claude Code faturanı kendi bilgisayarında çıkaran bir betik. Bir de deneyin bütün dosyaları.

Kural tek cümle: **en ucuz modelle başla, sonucu kontrol et, tökezlediği yerde bir basamak çık.**

| Dosya | Ne işe yarar |
|---|---|
| [`esleme-tablosu.md`](esleme-tablosu.md) | Görev türü → kademe (çırak / kalfa / usta), üç soru, üç şirketin fiyat merdiveni (30 Ekim 2026, kaynak linkli) |
| [`yonlendir.py`](yonlendir.py) | Her işi etiketine göre doğru modele gönderir, her çağrıdan sonra kaç sent tuttuğunu yazar |
| [`fatura.py`](fatura.py) | Claude Code kullanıyorsan faturanı yerel kayıtlarından çıkarır. İçeriğe bakmaz, yalnız sayıları toplar |
| [`ornek-isler.jsonl`](ornek-isler.jsonl) | `yonlendir.py` için beş örnek iş |
| [`deney/`](deney/) | Köşe Kahve deneyi: girdiler, doğru cevaplar, puanlayıcılar, modellerin ham cevapları, sonuç |

---

## Hangisi senin için?

### Kod yazmıyorum → [`esleme-tablosu.md`](esleme-tablosu.md)
Sohbet uygulamandaki **model seçici** yeterli. Tabloya bak, işin hangi basamakta olduğunu üç soruyla bul:

1. Cevabı kontrol edebiliyor musun?
2. Yanlışsa bedeli ne?
3. Bu iş kaç kez tekrar ediyor?

Özeti, çeviriyi ve yorum ayıklamayı hızlı modele ver, önemli kararı en güçlüsüne bırak. Bilgi eksik olabilecek ve yanlışı fark edilmeyecek işi de ustaya bırak.

### Kod yazıyorum → [`yonlendir.py`](yonlendir.py)
Betiğin başında düzenlenebilir bir tablo var: etiket → kademe → model. Her çağrıdan sonra şöyle bir satır yazar:

```
── yorum → çırak · claude-haiku-5-5 · giriş 1200 · önbellek 0 · çıkış 350 token · 0,0003 $ (0,03 sent)
```

(Bu satırdaki sayılar örnek. Gerçek sayıyı API'nin döndürdüğü token sayısından hesaplar.)

### Claude Code kullanıyorum → [`fatura.py`](fatura.py)
Claude Code her oturumu bilgisayarında `~/.claude/projects/` altına kayıt dosyası olarak yazar. `fatura.py` bu kayıtlardan model başına istek sayısını, token kalemlerini (giriş, önbellek yazma, önbellekten okuma, çıkış), dolar tutarını ve yüzdesini çıkarır. Videodaki 1.015 dolar, bu betiğin önceki bir sürümüyle kanalın kendi klasöründeki 20 günlük kayıttan çıktı.

---

## Kurulum

Gereken: **Python 3.10 veya üstü** (`python --version` ile bak).

### fatura.py
Yalnız Python'un standart kütüphanesi, başka bir şey kurulmaz. Ağa bağlanmaz.

```
python fatura.py
python fatura.py --baslangic 2026-10-01 --bitis 2026-10-31
python fatura.py --proje blog        # yalnız klasör adında "blog" geçen projeler
```

- Tarihler tam gün ve dahil. Kayıttaki saat UTC olduğu için gün sınırı Türkiye saatinden 3 saat kayar.
- Okuduğu alanlar: model adı, `usage` sayıları, mesaj kimliği, istek kimliği, zaman damgası. Yazışmaların içeriğini kullanmaz, ekrana basmaz, hiçbir yere göndermez.
- Aynı istek kayıtta birden çok satırda geçer ve ilk satırdaki çıkış sayısı çoğu zaman eksiktir. Betik her isteği (mesaj kimliği, istek kimliği) ile bir kez sayar ve her alanın en büyük değerini alır. Biz ilk sürümde ilk satırı almıştık, çıkış token'ları eksik çıkmıştı.
- Fiyat istek başına uygulanır: Haiku 5.5'in 100 bin token eşiği her isteğin kendi istemine bakar.
- Claude Code eski kayıtları kendiliğinden siler (varsayılan olarak yaklaşık 30 gün). Daha eski bir dönem görünmüyorsa sebebi bu.
- Kayıtlar başka bir yerdeyse `--kok <klasör>` ile göster.

### yonlendir.py
Önce API'ye hiç gitmeden dene. Bunun için ne anahtar ne kütüphane gerekir:

```
python yonlendir.py --liste
python yonlendir.py --isler ornek-isler.jsonl --kuru
python yonlendir.py yorum "Latte soğuktu ama kasiyer çok iyiydi." --kuru
```

`--kuru` her işin hangi modele gideceğini ve **tahmini** tutarını gösterir (giriş token'ı karakter sayısından kabaca tahmin edilir).

Gerçek çağrı için:

1. Kütüphaneyi kur: `pip install anthropic`
2. Anthropic Console'dan bir API anahtarı al. Anahtarı **ortam değişkenine** koy, hiçbir dosyaya yazma. Aşağıdaki komutlar anahtarı sorar ve komut geçmişine yazmaz; değişken terminal kapanınca silinir:
   - Windows PowerShell: `$env:ANTHROPIC_API_KEY = Read-Host "Anahtar"`
   - macOS / Linux: `read -s ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY`
3. Çalıştır: `python yonlendir.py --isler ornek-isler.jsonl`

Gerçek çağrı API hesabından ücretlendirilir. Tutarı her çağrının altında görürsün. Kendi işlerin için `ornek-isler.jsonl`'u kopyala: her satır `{"etiket": "...", "metin": "..."}`, istersen `"dosya": "yol"` da ekleyebilirsin.

---

## İki uyarı

- **Çırağa çok uzun belge verme.** Haiku 5.5'te istemi 100 bin token'ı geçen istek 5 kat fiyattan faturalanır. İki betik de bunu istek başına hesaplar ve satırda "UZUN İSTEM" diye yazar.
- **Acele etmeyen işleri toplu gönder.** Batch API'de giriş ve çıkış fiyatı yarıya iner. Bu betikler toplu gönderim yapmaz.

Fiyatlar **30 Ekim 2026** tarihli ve değişir. İki betikte de fiyat tablosu dosyanın başında, tarihiyle duruyor. Kullanmadan önce [resmî fiyat sayfasına](https://platform.claude.com/docs/en/about-claude/pricing) bak.

---

## Deneyde ne bulduk?

Uydurma bir kafe (Köşe Kahve) için bir haftalık iş: 40 yorumu etiketlemek, tedarikçi tekliflerini tabloya dökmek, kurallara uyan gönderi yazmak, süt tedarikçisi seçmek, badem sütü kararı. Beş kurulum (Haiku, Sonnet, Opus, düşük çabalı Opus, Fable), her iş 3 kez. Sonra üç zor iş daha: iki aylık dağınık defterden fatura hesabı, çok adımlı fiyat hesabı ve hatalı bir kasa betiğini düzeltmek. Ayrıntı: [`deney/SONUC.md`](deney/SONUC.md) · dosyalar ve yeniden koşma: [`deney/README.md`](deney/README.md)

| | Çırak (Haiku 5.5) | Kalfa (Sonnet 5.5) | Usta (Opus 5.5) | Ustaların ustası (Fable 5.1) |
|---|---|---|---|---|
| Bir haftanın tutarı (API liste fiyatıyla) | **0,042 $** | 0,834 $ | **1,474 $** | 3,938 $ |
| Süt kararı (Pazartesi tuzağı) | 3/3 | 3/3 | 3/3 | 3/3 |
| 120 etiket × 3 | 359/360 | 360/360 | 360/360 | 360/360 |
| Zor tur: defter, fiyat hesabı, kod | 3/3, 3/3, 3/3 | 3/3, 3/3, 3/3 | 3/3, 3/3, 3/3 | koşulmadı |
| Zor tur: eski fiyatı eksik defter | **2/3** | 3/3 | 3/3 | koşulmadı |

- Hep usta ÷ hep çırak = **35 kat**. İşleri çırak, kalfa, usta diye dağıtınca hafta 0,722 $ tuttu: yalnız 2 kat ucuz, çünkü kararlar ustada kaldı ve Opus 5.5 artık Sonnet'in yalnız iki katı.
- Ustaların ustası ustanın 2,7 katı tuttu, sonuç daha iyi değildi.
- Çırağın kayması sayma (bir kez 5 isteği 4 saydı) ve eksik bilgi (3'te 1 kez yalnız bildiği kısmı toplam diye yazdı) oldu.
- Beş kurulumun beşi de **bizim cevap anahtarımızdaki hatayı** yakaladı (koli fiyatıyla bütçe aşılıyordu).

> **Sınırlar:** uydurma bir kafe, tek şirketin modelleri (Anthropic, Ekim 2026), her iş 3 kez. Görevler kısa ve kontrol edilebilir; uzun ajan işi ölçülmedi. Ücretli API çağrısı yapılmadı: işler abonelik içinde Claude Code alt ajanlarıyla koşuldu, tutarlar kayıttaki token sayısı × API liste fiyatıyla **hesaplandı**. Bunlar ödenmiş bir fatura değil. Alt ajan tutarları Claude Code'un kendi sistem metnini de taşır, bu yüzden mutlak tutar doğrudan API'ye göre yüksektir; kurulumlar arası kıyas geçerlidir.

---

## Lisans

Kod ve betikler (`*.py`) [MIT](LICENSE). Metinler (bu dosya, `esleme-tablosu.md`, `deney/` içindeki girdiler, istemler ve sonuç metinleri) [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): kullan, değiştir, kaynak göster. Fiyat tabloları resmî sayfalardan aktarılmış olgulardır; kaynakları yanlarında yazıyor.

*Mivu, yapay zekâyı anlatan küçük bir robot.* · YouTube / Instagram / TikTok / X: **@heymivu**
