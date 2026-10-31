# -*- coding: utf-8 -*-
"""Zor görev turu (Z1–Z3) girdileri, doğru cevaplar ve alt ajan istemleri. Koşudan ÖNCE çalıştırılır (2026-10-31).
Z1 uzun defter: bir aylık işletme defterinden yulaf faturası (düzeltme, iade, zam, litre↔koli, numune ve sipariş tuzakları).
Z2 çok adımlı hesap: Aralık latte fiyatı (zamlı çekirdek, köpürtme firesi, KDV, kart komisyonu, %65 marj, 5 TL'ye yukarı yuvarlama).
Z3 kod: kasa betiğindeki hatalar; gizli testlerle puanlanır (testler alt ajana verilmez).
Kullanım: python -I uret.py  → girdiler/, dogru_zor.json, ../istemler/Z1–Z3.md
Rastgelelik sabit tohumlu (defterdeki gürültü satırları); cevaplar aşağıdaki olay listesinden hesaplanır."""
import io, json, os, random
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin
from datetime import date, timedelta
from decimal import Decimal, ROUND_CEILING

K = os.path.dirname(os.path.abspath(__file__))
GIR = os.path.join(K, "girdiler"); os.makedirs(GIR, exist_ok=True)
IST = os.path.join(os.path.dirname(K), "istemler")
GUN = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
R = random.Random(20261031)

# ---------- Z1: Kasım defteri ----------
# Kadıköy Çiftlik Salı/Perşembe teslim eder. (gün, defterde yazan yulaf ifadesi, faturaya giren koli, inek kolisi)
TESLIM = [
    (3, "4 koli yulaf", 4, 6), (5, "3 koli yulaf", 3, 5), (10, "4 koli yulaf", 4, 6),
    (12, "4 koli yulaf", 3, 5),          # 27 Kasım'da düzeltilir: irsaliyede 3
    (17, "4 koli yulaf", 4, 7), (19, "5 koli yulaf", 3, 6),  # 20 Kasım: 2 koli bozuk, iade
    (24, "24 litre yulaf (koliler 6'lık)", 4, 7), (26, "3 koli yulaf", 3, 6),
]
ESKI, YENI = 498, 534  # koli fiyatı (6 × 1 L, KDV dahil); 17 Kasım ve sonrası teslimatlar YENI
OZEL = {
    15: ["Selin'den (Kadıköy Çiftlik) e-posta geldi, aynen yapıştırıyorum: \"Ayşe Hanım merhaba, maliyetler nedeniyle 17 Kasım ve sonrasındaki "
         "teslimatlarda yulaf sütü kolisi 534 TL, inek sütü kolisi 560 TL olacaktır. Önceki teslimatlar eski fiyattan faturalanır.\""],
    20: ["Dünkü (19 Kasım) yulaf kolilerinden 2'si şişmiş, açınca ekşi kokuyordu. Selin'e geri verdik; o iki koli faturadan düşülecek."],
    21: ["Marmara Gıda'dan bir temsilci geldi, denemek için 2 litre yulaf sütü numune bıraktı. Ücretsiz, faturası yok."],
    27: ["Selin aradı: 12 Kasım irsaliyesinde yulaf 3 koli yazıyormuş. Defterime 4 yazmışım, yanlışmış; faturada 3 olacak."],
    29: ["1 Aralık Salı teslimatı için Selin'e 5 koli yulaf siparişi geçtim (Aralık faturasına girecek)."],
}
z1_koli = sum(t[2] for t in TESLIM)
z1_tl = sum(t[2] * (YENI if t[0] >= 17 else ESKI) for t in TESLIM)
TUZAK_Z1 = {  # yanlış yolların vereceği tutarlar (puanlayıcı öz-testi ve analiz için)
    "duzeltme_kacti": z1_tl + ESKI, "iade_kacti": z1_tl + 2 * YENI, "zam_kacti": sum(t[2] for t in TESLIM) * ESKI,
    "aralik_siparisi_eklendi": z1_tl + 5 * YENI, "hepsi_kacti": (z1_tl + ESKI + 2 * YENI),
}

PERSONEL = ["Emre", "Deniz", "Zeynep", "Can"]
HAVA = ["Yağmurlu, öğlene kadar sakindi.", "Güneşli, dışarıdaki masalar doldu.", "Lodos vardı, kapı sürekli açıldı.", "Soğuk ve kapalı.",
        "Hafif yağmur, akşamüstü kalabalık.", "Rüzgârlı ama açık.", "Sisli sabah, sonra güneş."]
MUSTERI = [
    "Köşedeki masada iki kişi üç saat ders çalıştı, iki kez filtre kahve tazeledik.", "Bir müşteri yulaflı latte'yi çok beğendi, fotoğrafını çekti.",
    "Çocuklu bir aile geldi, bebek sandalyesi istediler; ikinci bir tane almamız lazım.", "Düzenli müşterimiz Hakan Bey yine americano + kurabiye aldı.",
    "Biri kartla ödeme yapamadı, POS bir dakika bağlantı kaybetti.", "Turist bir çift menünün İngilizcesini sordu.",
    "Bir müşteri kekte ceviz olup olmadığını sordu; alerji listesini tezgâha asmalıyız.", "Öğrenci indirimi soruldu, şimdilik yok dedik.",
    "Biri prizin yanındaki masayı sordu, uzatma kablosu verdik.", "Kahvesini unutup giden bir müşteri yarım saat sonra döndü.",
    "Bir müşteri badem sütü sordu; yok dedik, yulaf önerdik.", "İki arkadaş doğum günü için pasta getirdi, tabak verdik.",
    "Mahalleden yeni taşınan biri kendini tanıttı, hafta sonları geleceğini söyledi.", "Biri Wi-Fi şifresini üç kez sordu; kartı masalara koymalıyız.",
    "Bir müşteri tuvaletin kapısının sıkıştığını söyledi.", "Yaşlı bir hanım her zamanki gibi çay ve simit istedi; simidimiz yok, kek aldı.",
    "Bir grup toplantı için altı kişilik masa istedi, iki masayı birleştirdik.", "Biri soğuk demleme sordu, kışın yapmıyoruz dedik.",
]
ISLER = [
    "Espresso makinesinin grup contaları kontrol edildi, sağ grup hafif kaçırıyor.", "Değirmen ayarı bir tık inceltildi, akış 28 saniyeye geldi.",
    "Bulaşık makinesinin tuzu eklendi.", "Vitrin camı ve tezgâh altı temizlendi.", "Çöp konteyneri dolu kaldı, belediyeyi aradık.",
    "Instagram'a yeni kek fotoğrafı kondu, 140 beğeni.", "Fırın termostatı 5 derece fazla gösteriyor, not aldım.",
    "Kahve çekirdeği stoku sayıldı: 6 kg var.", "Su filtresinin değişim tarihi yaklaşıyor (Aralık başı).",
    "Kurabiye hamuru iki tepsi hazırlandı.", "Kasa açılışta 500 TL bozuklukla başladı.", "Peçeteler bitmek üzere, siparişe eklendi.",
    "Menü tahtasına günün keki yazıldı: havuçlu.", "Buzdolabı sıcaklıkları kaydedildi: 3 °C ve 4 °C.", "Dış tabela ışığı yanmıyor, ampul alınacak.",
    "Kağıt bardak 8 oz stok sayıldı: 3 koli.", "Fincanların ikisi kırıldı, yenisi alınacak.", "Zeynep latte art pratiği yaptı, lale oturdu.",
]


def satis():
    return ("Satış: latte %d, americano %d, filtre %d, flat white %d, çay %d, kek %d dilim, kurabiye %d."
            % (R.randint(28, 55), R.randint(12, 30), R.randint(10, 24), R.randint(6, 16), R.randint(25, 60), R.randint(10, 26), R.randint(15, 40)))


def gun_yaz(s, g, ay_adi, tes, ozel):
    d = g.day; ad = GUN[g.weekday()]
    s.append("## %d %s %s" % (d, ay_adi, ad))
    if ad == "Pazartesi":
        s.append("Kapalı. " + R.choice(["Ben gelip faturaları düzenledim.", "Kimse yoktu.", "Tadilattan kalan boyayı hallettim, dükkân kapalıydı."]))
        s.append("")
        return
    acan, kapatan = R.sample(PERSONEL, 2)
    s.append("Bugün %s açtı, %s kapattı. %s" % (acan, kapatan, R.choice(HAVA)))
    if d in tes:
        s.append("Kadıköy geldi (sabah 08.10): %d koli inek, %s. İrsaliye imzalandı." % (tes[d][1], tes[d][0]))
    s.append(satis())
    s.append("Gün sonu sayım: inek sütü %s L, yulaf sütü %s L kullanıldı."
             % (str(round(R.uniform(8, 13), 1)).replace(".", ","), str(round(R.uniform(2, 4.5), 1)).replace(".", ",")))
    for x in R.sample(MUSTERI, 6):
        s.append("- " + x)
    for x in R.sample(ISLER, 5):
        s.append("- " + x)
    for x in ozel.get(d, []):
        s.append("- " + x)
    s.append("Kasa: nakit %d TL, kart %d TL." % (R.randint(1800, 4200), R.randint(5200, 11800)))
    s.append("")


def defter(eski_fiyat_yaz=True):
    """eski_fiyat_yaz=False → Z1e (eksik bilgi): eski koli fiyatı defterde yok. Gürültü aynı tohumdan, iki defter yalnız o satırda ayrışır.
    (2026-10-31: ilk Z1 koşusunda bu satır unutulmuştu; üç model de fark etti → ayrı görev oldu.)"""
    R.seed(20261031)
    ekim_ozel = {31: ["Ekim faturası Kadıköy'e ödendi, makbuz klasörde."]}
    if eski_fiyat_yaz:
        ekim_ozel[1] = ["Selin'le (Kadıköy Çiftlik) yıllık fiyatı konuştuk: inek kolisi 540 TL, yulaf kolisi %d TL, KDV dahil. Zam olursa e-postayla haber verecek." % ESKI]
    s = ["# Köşe Kahve — Ekim–Kasım 2026 defteri (Ayşe'nin günlük notları, olduğu gibi)", "",
         "Not: Pazartesileri kapalıyız. Kadıköy Çiftlik Salı ve Perşembe sabahı teslim eder (inek kolisi 12 × 1 L, yulaf kolisi 6 × 1 L).", ""]
    # Ekim: aynı tedarikçi, aynı biçim, Kasım faturasına girmez (tuzak)
    ekim = {}
    for d in range(1, 32):
        if date(2026, 10, d).weekday() in (1, 3):
            ekim[d] = ("%d koli yulaf" % R.randint(3, 5), R.randint(5, 7))
    s.append("# EKİM"); s.append("")
    for d in range(1, 32):
        gun_yaz(s, date(2026, 10, d), "Ekim", ekim, ekim_ozel)
    s.append("# KASIM"); s.append("")
    tes = {t[0]: (t[1], t[3]) for t in TESLIM}
    for d in range(1, 31):
        gun_yaz(s, date(2026, 11, d), "Kasım", tes, OZEL)
    return "\n".join(s) + "\n"


# ---------- Z2: Aralık latte fiyatı ----------
FIYAT_MD = """# Köşe Kahve — maliyet notu (Ayşe, Kasım sonu)

## Malzeme fiyatları (hepsi KDV dahil, alış)
- Kahve çekirdeği (Moda Kavurma): Kasım'da kilosu 1.150 TL. Kavurucunun e-postası: "1 Aralık'tan itibaren kilo fiyatı 1.290 TL."
- İnek sütü (Kadıköy Çiftlik): 12 × 1 litre koli 540 TL.
- Kağıt bardak + kapak (12 oz): adedi 7,40 TL.

## Latte reçetesi
- Çift shot espresso: toplam 18 gram çekirdek.
- Süt: bardağa 220 ml süt girer. Köpürtürken pitcher'da kalan ve dökülen kısım yüzünden çekilen süt bunun %10 fazlasıdır.
- Şeker, peçete, karıştırıcı maliyete katılmıyor.

## Satış tarafı
- Menü fiyatı KDV dahildir; kafede satışta KDV %10.
- Satışların neredeyse hepsi kartla; banka, KDV dahil satış tutarının %1,8'ini komisyon olarak kesiyor.
- Hedef: KDV hariç satış tutarından kart komisyonu ve malzeme maliyeti düşüldükten sonra kalan brüt kâr, KDV hariç satış tutarının en az %65'i olsun.
- Menü fiyatları 5 TL'nin katıdır.
"""
D = Decimal
cekirdek = D(18) * D(1290) / D(1000)
sut = D(220) * D("1.10") / D(1000) * (D(540) / D(12))
bardak = D("7.40")
malzeme = (cekirdek + sut + bardak)
# P/1,10 − 0,018·P − malzeme ≥ 0,65 · P/1,10  →  P ≥ malzeme / (0,35/1,10 − 0,018)
p_min = malzeme / (D("0.35") / D("1.10") - D("0.018"))
fiyat = (p_min / 5).to_integral_value(rounding=ROUND_CEILING) * 5


def z2_yan(cek_kg=1290, fire=D("1.10"), kom_kdvsiz=False):
    m = D(18) * D(cek_kg) / D(1000) + D(220) * fire / D(1000) * D(45) + bardak
    pay = D("0.35") / D("1.10") - (D("0.018") / D("1.10") if kom_kdvsiz else D("0.018"))
    return int((m / pay / 5).to_integral_value(rounding=ROUND_CEILING) * 5)


TUZAK_Z2 = {"eski_cekirdek": z2_yan(cek_kg=1150), "fire_yok": z2_yan(fire=D(1))}  # komisyonu KDV hariçten almak da 140 verir: ayırt etmez

# ---------- Z3: kasa betiği (hatalı) ----------
KASA = '''# -*- coding: utf-8 -*-
"""Köşe Kahve kasa özeti.

haftalik_ozet(kayitlar) bir haftanın kasa kayıtlarını gün gün toplar.
kayitlar: [{"tarih": "2026-11-03", "tur": "satis" | "iade", "tutar": "1.234,50"}, ...]
  tutar Türkçe biçimde yazılır (binlik ayraç nokta, ondalık virgül) ve her zaman pozitiftir.

Kurallar:
1. Satış toplama eklenir, iade düşülür. İade, iadenin yapıldığı günün toplamından düşülür.
2. Pazartesileri kapalıyız. Pazartesi tarihli bir kayıt, önceki Pazar'ın geç girilmiş kaydıdır ve Pazar'a yazılır.
3. Tutarlar kuruşu kuruşuna toplanır; yuvarlama hatası olmaz.
4. Dönüş: {"gunler": {"Salı": "1.234,50", ...}, "toplam": "9.876,00"}
   - gunler yalnız kaydı olan günleri içerir; gün adları Türkçe (Salı, Çarşamba, Perşembe, Cuma, Cumartesi, Pazar).
   - Para Türkçe biçimde: binlik ayraç nokta, ondalık virgül, her zaman iki hane ("0,50", "12.000,00").
"""
from datetime import date

GUNLER = ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"]


def _tl(s):
    return float(s.replace(",", "."))


def _bicim(x):
    return ("%.2f" % x).replace(".", ",")


def haftalik_ozet(kayitlar):
    gunler = {}
    for k in kayitlar:
        g = GUNLER[date.fromisoformat(k["tarih"]).weekday()]
        t = _tl(k["tutar"])
        if k["tur"] == "iade":
            t = -t
        gunler[g] = gunler.get(g, 0) + t
    toplam = sum(gunler.values())
    return {"gunler": {g: _bicim(v) for g, v in gunler.items()}, "toplam": _bicim(toplam)}
'''

ORTAK = "SİSTEM NOTU (rolün): Köşe Kahve'nin sahibi Ayşe için çalışıyorsun. Ekteki dosyalar işletmenin güncel bilgisidir. Türkçe yaz.\n\n"


def main():
    df = defter()
    io.open(os.path.join(GIR, "DEFTER_KASIM.md"), "w", encoding="utf-8").write(df)
    io.open(os.path.join(GIR, "FIYAT_ARALIK.md"), "w", encoding="utf-8").write(FIYAT_MD)
    io.open(os.path.join(GIR, "kasa.py"), "w", encoding="utf-8").write(KASA)
    dogru = {"not": "Doğru cevaplar koşudan önce yazıldı (2026-10-31), uret.py olay listesinden hesaplandı.",
             "Z1": {"yulaf_tl": z1_tl, "koli": z1_koli, "tuzak": TUZAK_Z1},
             "Z2": {"malzeme_tl": float(malzeme.quantize(D("0.01"))), "fiyat_tl": int(fiyat), "p_min": float(p_min.quantize(D("0.01"))), "tuzak": TUZAK_Z2},
             "Z1e": {"yulaf_tl": None, "koli": z1_koli, "not": "eski koli fiyatı defterde yok: doğru cevap 'hesaplanamaz' (yulaf_tl null). Kısmi tutarı toplam diye yazmak yanlış."},
             "Z3": {"test": "gizli_testler.py (8 test)"}}
    json.dump(dogru, io.open(os.path.join(K, "dogru_zor.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def z1_istem(metin):
        return (ORTAK + '<dosya ad="DEFTER_KASIM.md">\n' + metin + "</dosya>\n\n"
                "Kasım ayında Kadıköy Çiftlik'ten teslim alınan yulaf sütü için Kasım faturasına toplam kaç TL yazılmalı? Hesabını kısaca göster.\n"
                'Son satırda yalnız şu JSON olsun: {"yulaf_koli": <sayı>, "yulaf_tl": <sayı>}\n')
    z1 = z1_istem(df)
    z1e = z1_istem(defter(eski_fiyat_yaz=False))
    yol_e = os.path.join(IST, "Z1e.md")  # ilk koşuda kullanılan istemle birebir aynı olmalı
    if os.path.exists(yol_e):
        assert io.open(yol_e, encoding="utf-8").read() == z1e, "Z1e istemi ilk koşudakinden farklı"
    z2 = (ORTAK + '<dosya ad="FIYAT_ARALIK.md">\n' + FIYAT_MD + "</dosya>\n\n"
          "Aralık ayında latte'nin menü fiyatı en az kaç TL olmalı ki hedef tutsun? Hesabını adım adım göster.\n"
          'Son satırda yalnız şu JSON olsun: {"malzeme_tl": <bir latte malzeme maliyeti, kuruşlu>, "fiyat_tl": <menü fiyatı>}\n')
    z3 = (ORTAK + '<dosya ad="kasa.py">\n' + KASA + "</dosya>\n\n"
          "Ayşe: \"Haftalık kasa özetinde Pazartesi diye bir satır çıkıyor, binlik tutarlarda betik çöküyor ve rakamlar tutmuyor. "
          "Betiği docstring'deki kurallara tam uyacak şekilde düzelt.\"\n"
          "Düzeltilmiş kasa.py'nin TAMAMINI tek bir ```python kod bloğu içinde ver (yalnız standart kütüphane, fonksiyon adı ve imzası aynı kalsın). "
          "Kod bloğundan önce en fazla üç satırla neyi düzelttiğini yaz.\n")
    for ad, metin in (("Z1", z1), ("Z1e", z1e), ("Z2", z2), ("Z3", z3)):
        io.open(os.path.join(IST, ad + ".md"), "w", encoding="utf-8").write(metin)
    print("Z1", z1_koli, "koli", z1_tl, "TL", TUZAK_Z1)
    print("Z2 malzeme", malzeme.quantize(D("0.01")), "p_min", p_min.quantize(D("0.01")), "fiyat", fiyat, TUZAK_Z2)
    print("Z1 istem", len(z1), "karakter")


if __name__ == "__main__":
    main()
