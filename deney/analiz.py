# -*- coding: utf-8 -*-
"""Atölye 2 sonuç tablosu: kalite (puanla2) + maliyet (token_topla, liste fiyatı) + taban (G0) düşülmüş görev maliyeti
+ haftalık düzenler. Kullanım (deney klasöründen): python -I analiz.py  → sonuc/ozet.md, sonuc/kol_gorev.csv"""
import csv, glob, io, json, os, statistics as st, collections
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin

KOK = os.path.dirname(os.path.abspath(__file__))
KOLLAR = ["H", "S", "O", "O-", "F"]
AD = {"H": "Haiku 5.5", "S": "Sonnet 5.5", "O": "Opus 5.5", "O-": "Opus 5.5 · düşük çaba", "F": "Fable 5.1"}
GOREV = ["G1", "G2", "G3", "G4", "G5"]
GAD = {"G1": "40 yorum etiketi", "G2": "teklif tablosu", "G3": "plan + 3 gönderi", "G4": "süt tedarikçisi kararı", "G5": "badem sütü kararı"}

P = collections.defaultdict(list)
for r in csv.DictReader(io.open(os.path.join(KOK, "sonuc", "puanlar.csv"), encoding="utf-8")):
    P[(r["kol"], r["gorev"])].append(json.loads(r["puan"]))
U = collections.defaultdict(list)
for f in glob.glob(os.path.join(KOK, "ham", "altajan", "*", "G*", "*.usage.json")):
    p = f.replace("\\", "/").split("/")
    U[(p[-3], p[-2])].append(json.load(io.open(f, encoding="utf-8")))


def ort(x):
    return st.mean(x) if x else float("nan")


def kalite(kol, g):
    ps = P[(kol, g)]
    if not ps:
        return float("nan"), ""
    if g == "G1":
        v = ort([x["oran"] for x in ps]); return v, "%%%.1f etiket doğru" % (100 * v)
    if g == "G2":
        v = ort([x["oran"] for x in ps]); return v, "%%%.0f hücre, koli %d/%d" % (100 * v, sum(x["koli_litre_dogru"] for x in ps), len(ps))
    if g == "G3":
        ok = [x["toplam_ihlal"] == 0 and x["pazartesi_kapali"] for x in ps]
        return ort(ok), "%d/%d kusursuz (ihlal %d)" % (sum(ok), len(ps), sum(x["toplam_ihlal"] for x in ps))
    if g == "G4":
        ok = [x["puan"] == 2 for x in ps]
        return ort(ok), "%d/%d doğru + Pazartesi gerekçesi (tuzağa düşen %d)" % (sum(ok), len(ps), sum(x["tuzak_secildi"] for x in ps))
    ok = [x["puan"] == 3 for x in ps]
    return ort(ok), "%d/%d tam (istek sayısı doğru %d/%d)" % (sum(ok), len(ps), sum(x["istek_dogru"] for x in ps), len(ps))


taban = {k: ort([u["dolar"] for u in U[(k, "G0")]]) for k in KOLLAR}
satir, tablo = [], {}
for k in KOLLAR:
    for g in GOREV:
        us = U[(k, g)]
        ham = ort([u["dolar"] for u in us])
        cikis = ort([u["usage"]["output_tokens"] for u in us])
        q, qs = kalite(k, g)
        net = ham - taban[k] if taban[k] == taban[k] else float("nan")
        tablo[(k, g)] = (ham, net, q)
        satir.append({"kol": k, "model": AD[k], "gorev": g, "n": len(us), "kalite": round(q, 4), "kalite_metin": qs,
                      "ham_dolar": round(ham, 5), "taban_dolar": round(taban[k], 5), "gorev_dolar": round(net, 5), "cikis_token": round(cikis)})
with io.open(os.path.join(KOK, "sonuc", "kol_gorev.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(satir[0])); w.writeheader(); w.writerows(satir)

DUZEN = {"hep usta (Opus)": {g: "O" for g in GOREV},
         "dağıtılmış (Haiku·Haiku·Sonnet·Opus·Opus)": {"G1": "H", "G2": "H", "G3": "S", "G4": "O", "G5": "O"},
         "hep çırak (Haiku)": {g: "H" for g in GOREV},
         "hep Fable": {g: "F" for g in GOREV}}
out = ["# Atölye 2 — ölçüm özeti (otomatik, `analiz.py`)", "",
       "Yol: Claude Code alt ajanları (abonelik içinde, ücretli API çağrısı yok). Maliyet = kayıttaki token × 2026-10-30 liste fiyatı.",
       "**Ham** = alt ajanın tüm faturası (Claude Code sistem metni dâhil). **Taban** = aynı modelde boş görev (G0). **Görev** = ham − taban (işin kendisi).", "",
       "| Model | Taban $ |", "|---|---|"] + ["| %s | %.4f |" % (AD[k], taban[k]) for k in KOLLAR] + [""]
for g in GOREV:
    out += ["## %s · %s" % (g, GAD[g]), "", "| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |", "|---|---|---|---|---|---|"]
    for s in satir:
        if s["gorev"] == g:
            out.append("| %s | %d | %s | %.4f | %.4f | %d |" % (s["model"], s["n"], s["kalite_metin"], s["ham_dolar"], s["gorev_dolar"], s["cikis_token"]))
    out.append("")
out += ["## Bir hafta (G1–G5 birer kez), düzenlere göre", "", "| Düzen | Ham $ | Görev $ | Ortalama kalite (0–1) |", "|---|---|---|---|"]
ref = None
for ad, d in DUZEN.items():
    ham = sum(tablo[(d[g], g)][0] for g in GOREV); net = sum(tablo[(d[g], g)][1] for g in GOREV)
    q = ort([tablo[(d[g], g)][2] for g in GOREV])
    out.append("| %s | %.3f | %.3f | %.3f |" % (ad, ham, net, q))
    ref = ref or (ham, net)
out += ["", "Oran (hep usta ÷ düzen):"]
for ad, d in DUZEN.items():
    ham = sum(tablo[(d[g], g)][0] for g in GOREV); net = sum(tablo[(d[g], g)][1] for g in GOREV)
    out.append("- %s: ham ×%.1f · görev ×%.1f" % (ad, ref[0] / ham, ref[1] / net if net > 0 else float("nan")))
io.open(os.path.join(KOK, "sonuc", "ozet.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
