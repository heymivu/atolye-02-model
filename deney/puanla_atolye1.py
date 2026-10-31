# -*- coding: utf-8 -*-
"""Köşe Kahve deney puanlayıcı. Kullanım: python puanla.py <cikti.md> <T1|T2|T3>  → JSON (ihlal listesi) + tablo satırı.
Toplu: python puanla.py --hepsi  (A_prompt/B_dosya/C_ai_dosya altındaki r*/cikti_T*.md)"""
import re, sys, json, os, io, glob
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin
YASAK = re.compile(r"indirim|kampanya|bedava|ücretsiz|promosyon|hediye|%", re.I)
USTUN = re.compile(r"en iyi|en lezzetli|en güzel|türkiye'?nin|eşsiz|mükemmel|muhteşem", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕⌚-⏿\U0001F000-\U0001F2FF]")
SEN = re.compile(r"\b(sen|senin|sana|seni|sende)\b", re.I)
ESKI_SUT = re.compile(r"(yalnız|sadece|yalnızca)\s+(inek|yulaf)[^.\n]*(ve|,)\s*(inek|yulaf)", re.I)

def temizle(t):
    """Gönderi gövdesinden HTML yorumu, alıntı notu, 'Not:' paragrafı ve yatay çizgi sonrası metni at."""
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.split(r"^\s*(---+|#+\s*Not|\*\*?Not|> ?Not|Not \(|Not:)", t, maxsplit=1, flags=re.M)[0]
    return t.strip()

def gonderiler(md):
    parts = re.split(r"^##\s*Gönderi\s*(\d)", md, flags=re.M | re.I)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        out[int(parts[i])] = temizle(parts[i + 1])
    return out

def plan(md):
    m = re.search(r"^##\s*Plan(.*?)(?=^##\s*Gönderi|\Z)", md, flags=re.M | re.S | re.I)
    return m.group(1) if m else ""

def puanla_gonderi(t, gorev):
    tags = re.findall(r"#\S+", t)
    govde = re.sub(r"#\S+", "", t)
    govde = re.sub(r"\s+", " ", govde).strip()
    kelime = len(govde.split())
    ihl = []
    if YASAK.search(govde): ihl.append("1 yasak kelime")
    if USTUN.search(govde): ihl.append("2 üstünlük")
    if len(EMOJI.findall(t)) > 1: ihl.append("3 emoji>1")
    son = govde.rstrip("☕🍰🌧️ ").rstrip()
    if not son.endswith("?"): ihl.append("4 soruyla bitmiyor")
    if not (30 <= kelime <= 80): ihl.append("5 kelime=%d" % kelime)
    if len(tags) != 3 or not any(x.lower().startswith("#köşekahve") for x in tags): ihl.append("6 hashtag")
    if SEN.search(govde): ihl.append("7 sen hitabı")
    if gorev in ("T1", "T2") and re.search(r"badem", t, re.I): ihl.append("8 menüde olmayan ürün (badem)")
    if gorev == "T3" and ESKI_SUT.search(t): ihl.append("8 eski süt ifadesi")
    return ihl, kelime

def puanla(md, gorev):
    g = gonderiler(md); p = plan(md); sonuc = {"gorev": gorev, "gonderi_sayisi": len(g), "gonderi": {}, "plan": []}
    if len(g) != 3: sonuc["plan"].append("biçim: %d gönderi" % len(g))
    for k, t in sorted(g.items()):
        ihl, kelime = puanla_gonderi(t, gorev); sonuc["gonderi"][k] = {"ihlal": ihl, "kelime": kelime}
    if gorev in ("T2", "T3"):
        # Pazartesi satırında konu var mı? (kapalı/tadilat/— ise tamam)
        for satir in p.splitlines():
            if re.search(r"pazartesi", satir, re.I):
                if not re.search(r"kapalı|tadilat|—|-\s*\||yok|paylaşım yok", satir, re.I): sonuc["plan"].append("süreklilik: Pazartesi'ye konu konmuş")
                break
        else:
            if p.strip(): sonuc["plan"].append("plan: Pazartesi satırı yok")
    if gorev == "T3":
        gm = " ".join(g.values())
        if not re.search(r"badem", gm, re.I):
            sonuc["plan"].append("T3: badem gönderilerde yok (çelişki: kural 8) — " + ("NOTLA" if re.search(r"badem", md, re.I) else "SESSİZ"))
    sonuc["toplam_ihlal"] = sum(len(v["ihlal"]) for v in sonuc["gonderi"].values()) + len(sonuc["plan"])
    return sonuc

if __name__ == "__main__":
    kok = os.path.dirname(os.path.abspath(__file__))
    if sys.argv[1:2] == ["--hepsi"]:
        rows = []
        kok2 = os.path.join(kok, sys.argv[2]) if len(sys.argv) > 2 else kok
        for kol in ("A_prompt", "B_dosya", "C_ai_dosya"):
            for f in sorted(glob.glob(os.path.join(kok2, kol, "r*", "cikti_T*.md"))):
                gorev = re.search(r"cikti_(T\d)", f).group(1); r = os.path.basename(os.path.dirname(f))
                s = puanla(io.open(f, encoding="utf-8").read(), gorev)
                rows.append((kol, r, gorev, s["toplam_ihlal"], "; ".join(sum([v["ihlal"] for v in s["gonderi"].values()], []) + s["plan"])))
        print("| Kol | Tekrar | Görev | İhlal | Ayrıntı |"); print("|---|---|---|---|---|")
        for r in rows: print("| %s | %s | %s | %d | %s |" % r)
        json.dump(rows, io.open(os.path.join(kok, "sonuc", "puanlar%s.json" % ("_" + sys.argv[2] if len(sys.argv) > 2 else "")), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        md = io.open(sys.argv[1], encoding="utf-8").read()
        print(json.dumps(puanla(md, sys.argv[2]), ensure_ascii=False, indent=1))
