# -*- coding: utf-8 -*-
"""Zor tur puanlayıcı. Doğru cevaplar dogru_zor.json (koşudan önce, uret.py).
Kullanım:
  python -I puanla_zor.py <Z1|Z2|Z3> <cikti.md>   → tek çıktı, JSON
  python -I puanla_zor.py --hepsi                 → ../ham/altajan/<kol>/Z*/r*.md → ../sonuc/zor_puanlar.csv
Z1: yulaf_tl tam eşit (tuzak adı raporlanır). Z2: fiyat_tl tam eşit; malzeme ±0,05 TL. Z3: kod bloğu çıkarılır, gizli 8 test."""
import csv, glob, io, json, os, re, sys, tempfile
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin

K = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, K); sys.path.insert(0, os.path.dirname(K))
from puanla2 import json_bul  # noqa: E402
import gizli_testler  # noqa: E402

DOGRU = json.load(io.open(os.path.join(K, "dogru_zor.json"), encoding="utf-8"))


def sayi(x):
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).replace("TL", "").strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):  # "14.448" = on dört bin
        s = s.replace(".", "")
    return float(s)


def z1(metin):
    j = json_bul(metin, "nesne") or {}
    try:
        tl = sayi(j.get("yulaf_tl"))
    except Exception:
        return {"dogru": False, "neden": "json yok", "tl": None}
    d = DOGRU["Z1"]
    tuzak = [ad for ad, v in d["tuzak"].items() if abs(v - tl) < .5]
    return {"dogru": abs(tl - d["yulaf_tl"]) < .5, "tl": tl, "koli": j.get("yulaf_koli"), "tuzak": "|".join(tuzak)}


def z1e(metin):
    """Eksik bilgi: doğru cevap "hesaplanamaz" (yulaf_tl null). Bir sayı yazmak, kısmi bile olsa, faturaya yanlış tutar geçirir."""
    j = json_bul(metin, "nesne")
    if j is None:
        return {"dogru": False, "neden": "json yok"}
    tl = j.get("yulaf_tl")
    kismi = 14 * 534  # yalnız zamlı 14 koli
    try:
        tlf = None if tl in (None, "", "null") else sayi(tl)
    except Exception:
        tlf = None
    return {"dogru": tlf is None, "tl": tlf, "koli": j.get("yulaf_koli"),
            "tuzak": "kismi_toplam" if tlf is not None and abs(tlf - kismi) < .5 else ("sayi_uydurdu" if tlf is not None else "")}


def z2(metin):
    j = json_bul(metin, "nesne") or {}
    try:
        f = sayi(j.get("fiyat_tl")); m = sayi(j.get("malzeme_tl"))
    except Exception:
        return {"dogru": False, "neden": "json yok"}
    d = DOGRU["Z2"]
    tuzak = [ad for ad, v in d["tuzak"].items() if abs(v - f) < .5]
    return {"dogru": abs(f - d["fiyat_tl"]) < .5, "fiyat": f, "malzeme": m, "malzeme_dogru": abs(m - d["malzeme_tl"]) <= .05, "tuzak": "|".join(tuzak)}


def z3(metin):
    bloklar = re.findall(r"```python\s*\n(.*?)```", metin, re.S)
    if not bloklar:
        return {"dogru": False, "gecti": 0, "toplam": 8, "neden": "kod bloğu yok"}
    with tempfile.TemporaryDirectory() as td:
        yol = os.path.join(td, "kasa_aday.py")
        io.open(yol, "w", encoding="utf-8").write(bloklar[-1])
        r = gizli_testler.kos(yol)
    r["dogru"] = r["gecti"] == r["toplam"]
    return r


PUAN = {"Z1": z1, "Z1e": z1e, "Z2": z2, "Z3": z3}


def hepsi():
    ham = os.path.join(os.path.dirname(K), "ham", "altajan")
    satir = []
    for f in sorted(glob.glob(os.path.join(ham, "*", "Z*", "r*.md"))):
        kol, gorev, tek = f.split(os.sep)[-3], f.split(os.sep)[-2], os.path.basename(f)[:-3]
        p = PUAN[gorev](io.open(f, encoding="utf-8").read())
        u = f[:-3] + ".usage.json"
        dolar = json.load(io.open(u, encoding="utf-8"))["dolar"] if os.path.exists(u) else ""
        satir.append({"kol": kol, "gorev": gorev, "tekrar": tek, "dogru": p.get("dogru"), "ayrinti": json.dumps({k: v for k, v in p.items() if k != "dogru"}, ensure_ascii=False), "dolar": dolar})
    hedef = os.path.join(os.path.dirname(K), "sonuc", "zor_puanlar.csv")
    with io.open(hedef, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["kol", "gorev", "tekrar", "dogru", "ayrinti", "dolar"]); w.writeheader(); w.writerows(satir)
    for s in satir:
        print(s["kol"], s["gorev"], s["tekrar"], s["dogru"], s["dolar"], s["ayrinti"][:140])
    return satir


if __name__ == "__main__":
    if sys.argv[1] == "--hepsi":
        hepsi()
    else:
        print(json.dumps(PUAN[sys.argv[1]](io.open(sys.argv[2], encoding="utf-8").read()), ensure_ascii=False))
