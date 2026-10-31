# Köşe Kahve deneyi: dosyalar ve yeniden koşma

Uydurma bir kafenin (Köşe Kahve) bir haftalık işleri, beş model kurulumuna üçer kez verildi. Sonra üç zor iş daha, üç kuruluma. Sonuç ve sınırlar: [`SONUC.md`](SONUC.md).

## Ne nerede

| Yol | Ne |
|---|---|
| `girdiler/` | Haftanın girdileri: 40 yorum, 3 tedarikçi teklifi, işletme notu, talimat ve örnekler (Atölye 1'den), görev cümleleri |
| `girdiler/dogru.json` | Doğru cevaplar, **koşudan önce** yazıldı (G4 notunda bizim anahtar hatamız da var) |
| `istemler/` | Alt ajanlara verilen istemlerin birebir metni: G0 (boş taban), G1–G5, Z1, Z1e, Z2, Z3 |
| `puanla2.py` | G1–G5 puanlayıcı. G3 için `puanla_atolye1.py`'yi kullanır |
| `test/oz_test.py` | Puanlayıcı öz-testi: kusursuz ve bilerek bozulmuş çıktılar, 12 test |
| `zor/uret.py` | Zor tur girdilerini, doğru cevapları ve Z istemlerini üretir (sabit tohum, tekrar koşunca aynı dosyalar) |
| `zor/girdiler/`, `zor/dogru_zor.json` | Zor tur girdileri (iki aylık defter, Aralık fiyatları, hatalı kasa betiği) ve doğru cevaplar |
| `zor/puanla_zor.py`, `zor/gizli_testler.py` | Zor tur puanlayıcı. Kod görevi modele gösterilmeyen 8 testle puanlanır |
| `zor/test/oz_test_zor.py` | Zor tur puanlayıcı öz-testi, 19 test |
| `ham/altajan/<kurulum>/<görev>/rN.md` | Modellerin cevapları, olduğu gibi. Kurulum: H Haiku, S Sonnet, O Opus, O- Opus düşük çaba, F Fable |
| `ham/altajan/.../rN.usage.json` | O koşunun token sayıları, istek sayısı ve liste fiyatıyla $ |
| `analiz.py` | `sonuc/ozet.md` ve `sonuc/kol_gorev.csv`'yi üretir |
| `sonuc/` | `ozet.md` (otomatik tablo), `puanlar.csv`, `kol_gorev.csv`, `zor_puanlar.csv` |

## Kendin kontrol et

Python 3.10+, ek kütüphane yok, model çağrısı yok. Bu klasörden:

```
python test/oz_test.py              # 12/12 test geçti
python zor/test/oz_test_zor.py      # 19/19
python puanla2.py --hepsi ham/altajan   # sonuc/puanlar.csv yeniden
python zor/puanla_zor.py --hepsi        # sonuc/zor_puanlar.csv yeniden
python analiz.py                    # sonuc/ozet.md yeniden
python zor/uret.py                  # zor tur girdileri yeniden (aynı çıkmalı)
```

Tek bir cevabı puanlamak: `python puanla2.py G4 ham/altajan/H/G4/r1.md` ya da `python zor/puanla_zor.py Z1 ham/altajan/H/Z1/r1.md`.

## Kendi modellerinle tekrar koş

`istemler/` içindeki metni olduğu gibi modele ver (sohbet uygulaması, API ya da başka bir şirketin modeli), cevabı bir `.md` dosyasına kaydet ve yukarıdaki tek-cevap komutuyla puanla. Cevap biçimi istemin sonunda yazıyor (çoğu görevde son satırda JSON).

Maliyet bizim tabloyla doğrudan kıyaslanmaz: bizim tutarlar Claude Code alt ajanının kendi sistem metnini de taşır. API'den tek çağrıyla koşarsan istek daha kısa olur, tutar daha düşük çıkar.
