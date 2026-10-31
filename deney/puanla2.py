# -*- coding: utf-8 -*-
"""Atölye 2 puanlayıcı (Köşe Kahve haftası). Doğru cevaplar girdiler/dogru.json'da, koşudan önce yazıldı.
Kullanım:
  python puanla2.py <G1|G2|G3|G4|G5> <cikti.md>     → tek çıktı, JSON puan
  python puanla2.py --hepsi <ham_kök>               → <ham_kök>/<kol>/<Gn>/r*.md hepsini puanlar, sonuc/puanlar.csv
G3 Atölye 1 puanlayıcısıyla (puanla_atolye1.py, T2 kipi: 8 kural + Pazartesi sürekliliği + badem yasağı).
"""
import re, sys, json, os, io, glob, csv
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin

KOK = os.path.dirname(os.path.abspath(__file__))
DOGRU = json.load(io.open(os.path.join(KOK, "girdiler", "dogru.json"), encoding="utf-8"))
sys.path.insert(0, KOK)
import puanla_atolye1 as a1  # noqa: E402

GUN = {"pazartesi": "Pazartesi", "salı": "Salı", "sali": "Salı", "çarşamba": "Çarşamba", "carsamba": "Çarşamba",
       "perşembe": "Perşembe", "persembe": "Perşembe", "cuma": "Cuma", "cumartesi": "Cumartesi", "pazar": "Pazar"}


def kucuk(s):
    return (s or "").replace("İ", "i").replace("I", "ı").lower()


def json_bul(metin, tur):
    """Metindeki son geçerli üst düzey JSON nesnesini/dizisini bul (kod çiti, önündeki açıklama tolere edilir).
    Geçerli bir blok bulununca içine girilmez: iç içe nesnede en dıştaki alınır."""
    metin = re.sub(r"```(?:json)?", "", metin)
    acik, kapa = ("[", "]") if tur == "dizi" else ("{", "}")
    son = None
    i = 0
    while i < len(metin):
        if metin[i] != acik:
            i += 1
            continue
        derinlik = 0; bulundu = False
        for j in range(i, len(metin)):
            if metin[j] == acik:
                derinlik += 1
            elif metin[j] == kapa:
                derinlik -= 1
                if derinlik == 0:
                    try:
                        son = json.loads(metin[i:j + 1]); bulundu = True
                    except ValueError:
                        pass
                    break
        i = j + 1 if bulundu else i + 1
    return son


def g1(metin):
    veri = json_bul(metin, "dizi")
    if not isinstance(veri, list):
        return {"bicim_hatasi": True, "dogru": 0, "toplam": 120, "oran": 0.0}
    cevap = {int(x.get("id", 0)): x for x in veri if isinstance(x, dict)}
    dogru = 0; ironik_dogru = 0; hatalar = []
    for e in DOGRU["G1"]["etiketler"]:
        c = cevap.get(e["id"], {})
        ok_k = kucuk(c.get("konu")) in e["konu"]
        ok_d = str(c.get("duygu", "")).strip() in e["duygu"]
        ok_c = kucuk(c.get("cevap")).replace("hayir", "hayır") in e["cevap"]
        dogru += ok_k + ok_d + ok_c
        if e["id"] in DOGRU["G1"]["ironik"] and ok_d:
            ironik_dogru += 1
        if not (ok_k and ok_d and ok_c):
            hatalar.append(e["id"])
    return {"bicim_hatasi": False, "dogru": dogru, "toplam": 120, "oran": round(dogru / 120, 4),
            "ironik_duygu_dogru": ironik_dogru, "ironik_toplam": len(DOGRU["G1"]["ironik"]),
            "hatali_yorumlar": hatalar}


def tedarikci_esle(ad):
    for t in DOGRU["G2"]["tedarikciler"]:
        if re.search(t["anahtar"], kucuk(ad)):
            return t
    return None


def gunler(liste):
    out = set()
    for g in liste or []:
        k = kucuk(str(g)).strip()
        if k in GUN:
            out.add(GUN[k])
    return out


def g2(metin):
    veri = json_bul(metin, "nesne")
    satirlar = (veri or {}).get("tedarikciler") if isinstance(veri, dict) else None
    if not isinstance(satirlar, list):
        return {"bicim_hatasi": True, "dogru": 0, "toplam": 18, "oran": 0.0}
    dogru = 0; hatalar = []; birim_tuzagi = None
    for s in satirlar:
        t = tedarikci_esle(s.get("ad", ""))
        if not t:
            continue
        for alan in ("inek_tl_lt", "yulaf_tl_lt", "badem_tl_lt", "min_siparis_lt", "vade_gun"):
            beklenen, gelen = t[alan], s.get(alan)
            try:
                ok = (beklenen is None and gelen in (None, "", 0)) or (beklenen is not None and abs(float(gelen) - beklenen) < 0.01)
            except (TypeError, ValueError):
                ok = False
            dogru += ok
            if not ok:
                hatalar.append("%s.%s=%s" % (t["anahtar"][:8], alan, gelen))
        ok = gunler(s.get("teslim_gunleri")) == set(t["teslim_gunleri"])
        dogru += ok
        if not ok:
            hatalar.append("%s.teslim=%s" % (t["anahtar"][:8], s.get("teslim_gunleri")))
        if t["inek_tl_lt"] == 45:  # Kadıköy Çiftlik: koli → litre tuzağı
            try:
                birim_tuzagi = abs(float(s.get("inek_tl_lt")) - 45) < .01 and abs(float(s.get("yulaf_tl_lt")) - 83) < .01
            except (TypeError, ValueError):
                birim_tuzagi = False
    return {"bicim_hatasi": False, "dogru": dogru, "toplam": 18, "oran": round(dogru / 18, 4),
            "koli_litre_dogru": bool(birim_tuzagi), "hatalar": hatalar}


def g3(metin):
    s = a1.puanla(metin, "T2")
    pzt = not any("süreklilik" in p or "Pazartesi satırı yok" in p for p in s["plan"])
    return {"bicim_hatasi": s["gonderi_sayisi"] != 3, "toplam_ihlal": s["toplam_ihlal"], "pazartesi_kapali": pzt,
            "ayrinti": sum([v["ihlal"] for v in s["gonderi"].values()], []) + s["plan"]}


def g4(metin):
    veri = json_bul(metin, "nesne")
    if not isinstance(veri, dict) or "secim" not in veri:
        return {"bicim_hatasi": True, "secim_dogru": 0, "tuzak_secildi": 0, "pazartesi_gerekcesi": 0, "puan": 0}
    secim_dogru = int(bool(re.search(DOGRU["G4"]["dogru"], kucuk(veri.get("secim")))))
    tuzak_secildi = int(bool(re.search(DOGRU["G4"]["tuzak"], kucuk(veri.get("secim")))))
    gerekce = ""
    for ad, neden in (veri.get("elenenler") or {}).items():
        if re.search(DOGRU["G4"]["tuzak"], kucuk(ad)):
            gerekce = kucuk(neden)
    pzt = int(DOGRU["G4"]["tuzak_neden"] in gerekce)
    return {"bicim_hatasi": False, "secim": veri.get("secim"), "secim_dogru": secim_dogru, "tuzak_secildi": tuzak_secildi,
            "pazartesi_gerekcesi": pzt, "puan": secim_dogru + (pzt if secim_dogru else 0)}


def g5(metin):
    veri = json_bul(metin, "nesne")
    if not isinstance(veri, dict) or "oneri" not in veri:
        return {"bicim_hatasi": True, "puan": 0}
    try:
        istek = int(veri.get("istek_sayisi")) == DOGRU["G5"]["istek_sayisi"]
    except (TypeError, ValueError):
        istek = False
    ted = bool(re.search(DOGRU["G5"]["badem_tedarikcisi"], kucuk(veri.get("badem_tedarikcisi"))))
    oneri = kucuk(veri.get("oneri")).strip()
    kural = oneri != "ekle" and (oneri in DOGRU["G5"]["oneri_dogru"] or bool(re.search(r"kural|8\.|ayşe", kucuk(veri.get("gerekce")))))
    return {"bicim_hatasi": False, "oneri": veri.get("oneri"), "istek_sayisi": veri.get("istek_sayisi"), "istek_dogru": int(istek),
            "tedarikci_dogru": int(ted), "kurali_ayseye_birakti": int(kural), "puan": int(istek) + int(ted) + int(kural)}


PUAN = {"G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5}


def hepsi(ham):
    satirlar = []
    for f in sorted(glob.glob(os.path.join(ham, "*", "G*", "r*.md"))):
        kol, gorev = f.replace("\\", "/").split("/")[-3:-1]
        if gorev not in PUAN:  # G0 = taban ölçümü, puanlanmaz
            continue
        s = PUAN[gorev](io.open(f, encoding="utf-8").read())
        satirlar.append({"kol": kol, "gorev": gorev, "tekrar": os.path.basename(f)[:-3], "puan": json.dumps(s, ensure_ascii=False)})
    os.makedirs(os.path.join(KOK, "sonuc"), exist_ok=True)
    with io.open(os.path.join(KOK, "sonuc", "puanlar.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["kol", "gorev", "tekrar", "puan"]); w.writeheader(); w.writerows(satirlar)
    print(len(satirlar), "çıktı puanlandı → sonuc/puanlar.csv")


if __name__ == "__main__":
    if sys.argv[1] == "--hepsi":
        hepsi(sys.argv[2])
    else:
        print(json.dumps(PUAN[sys.argv[1]](io.open(sys.argv[2], encoding="utf-8").read()), ensure_ascii=False, indent=1))
