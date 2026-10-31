# -*- coding: utf-8 -*-
"""fatura.py: Claude Code kullanımının API liste fiyatıyla faturası, kendi bilgisayarında.

Claude Code her oturumu ~/.claude/projects/ altına .jsonl kayıt olarak yazar. Bu betik o kayıtlarda
yalnız SAYILARA bakar: model adı, usage alanları (giriş, önbellek yazma, önbellekten okuma, çıkış),
mesaj kimliği, istek kimliği ve zaman damgası. Yazışmaların içeriğini kullanmaz, yazdırmaz, hiçbir
yere göndermez; ağ bağlantısı yok, yalnız Python standart kütüphanesi.

Kullanım:
  python fatura.py                                          # tüm kayıtlar
  python fatura.py --baslangic 2026-10-10 --bitis 2026-10-29
  python fatura.py --proje Projeler-blog                    # yalnız klasör adında bu metin geçen projeler
  python fatura.py --kok D:/baska/yer/projects              # kayıtlar başka yerdeyse

Çıkan tutar ödediğin para değildir: aboneliğin varsa aynı kullanımın API'de liste fiyatıyla ne
tutacağıdır. Batch indirimi, fast mode gibi çarpanlar hesaba girmez.
"""
import argparse, collections, datetime, glob, json, os, sys

for _akis in (sys.stdout, sys.stderr):
    if hasattr(_akis, "reconfigure"):
        _akis.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolunda Türkçe harfler bozulmasın

# ---------------------------------------------------------------------------------------------
# FİYAT TABLOSU: fiyatlar değişir, kullanmadan önce kaynağa bak ve gerekirse güncelle.
FIYAT_TARIHI = "2026-10-30"
FIYAT_KAYNAGI = "https://platform.claude.com/docs/en/about-claude/pricing"
# 1 milyon token başına ABD doları: (giriş, önbellek yazma 5 dk, önbellek yazma 1 sa, önbellekten okuma, çıkış)
FIYAT = {
    "claude-fable-5-1":  (10.00, 12.50, 20.00, 0.25, 50.00),
    "claude-opus-5-5":   (4.00, 5.00, 8.00, 0.20, 20.00),
    "claude-sonnet-5-5": (2.00, 2.50, 4.00, 0.10, 10.00),
    "claude-haiku-5-5":  (0.10, 0.125, 0.20, 0.01, 0.50),
}
# Eşikli fiyat: istemi (giriş + önbellek okuma + önbellek yazma) eşiği geçen İSTEK pahalı fiyattan faturalanır.
# Eşik her isteğe ayrı uygulanır, toplam token'a değil.
UZUN_ISTEM = {
    "claude-haiku-5-5": (100_000, (0.50, 0.625, 1.00, 0.05, 2.50)),
}
# ---------------------------------------------------------------------------------------------

KALEMLER = ("giris", "yazma_5dk", "yazma_1sa", "okuma", "cikis")


def kayit_koku(verilen):
    if verilen:
        return verilen
    ayar = os.environ.get("CLAUDE_CONFIG_DIR")
    return os.path.join(ayar if ayar else os.path.join(os.path.expanduser("~"), ".claude"), "projects")


def sayilar(usage):
    """usage nesnesinden beş kalemi çıkarır. Önbellek yazma 5 dk / 1 sa ayrımı yoksa hepsi 5 dk sayılır."""
    cc = usage.get("cache_creation") or {}
    y5 = cc.get("ephemeral_5m_input_tokens") or 0
    y1 = cc.get("ephemeral_1h_input_tokens") or 0
    toplam_yazma = usage.get("cache_creation_input_tokens") or 0
    y5 += max(toplam_yazma - y5 - y1, 0)
    return {"giris": usage.get("input_tokens") or 0, "yazma_5dk": y5, "yazma_1sa": y1,
            "okuma": usage.get("cache_read_input_tokens") or 0, "cikis": usage.get("output_tokens") or 0}


def istek_dolari(model, s):
    """Tek isteğin kalem kalem doları. Eşikli fiyat bu isteğin kendi istemine göre seçilir."""
    fiyat = FIYAT[model]
    if model in UZUN_ISTEM:
        esik, pahali = UZUN_ISTEM[model]
        if s["giris"] + s["okuma"] + s["yazma_5dk"] + s["yazma_1sa"] > esik:
            fiyat = pahali
    return {k: s[k] * f / 1e6 for k, f in zip(KALEMLER, fiyat)}


def oku(kok, bas, bit, proje):
    """Kayıtları tarar; her istek (message.id, requestId) için alan alan en büyük değeri tutar.
    Claude Code bir mesajı birden çok satıra yazar ve ilk satırda çıkış sayısı çoğu zaman eksiktir
    (akış başındaki geçici değer). Toplamak iki kez saydırır, ilk satırı almak eksik saydırır."""
    istekler, dosya_sayisi = {}, 0
    for yol in glob.glob(os.path.join(kok, "**", "*.jsonl"), recursive=True):
        if proje:
            ust = os.path.relpath(yol, kok).replace("\\", "/").split("/")[0]
            if proje.lower() not in ust.lower():
                continue
        dosya_sayisi += 1
        try:
            f = open(yol, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with f:
            for no, satir in enumerate(f):
                if '"usage"' not in satir:  # usage taşımayan satırlar hiç çözümlenmez
                    continue
                try:
                    d = json.loads(satir)
                except ValueError:
                    continue
                gun = str(d.get("timestamp", ""))[:10]  # kayıttaki zaman UTC
                if (bas and gun < bas) or (bit and gun > bit):
                    continue
                m = d.get("message")
                if not isinstance(m, dict) or not isinstance(m.get("usage"), dict):
                    continue
                anahtar = (m.get("id"), d.get("requestId"))
                if anahtar == (None, None):
                    anahtar = (yol, no)  # kimliksiz satır: tek başına bir istek
                s = sayilar(m["usage"])
                e = istekler.get(anahtar)
                if e is None:
                    istekler[anahtar] = [m.get("model") or "?", s]
                else:
                    for k in KALEMLER:
                        e[1][k] = max(e[1][k], s[k])
    return istekler, dosya_sayisi


def tr(x, ondalik=2):
    """1234567.891 → 1.234.567,89"""
    return ("{:,.%df}" % ondalik).format(x).replace(",", "_").replace(".", ",").replace("_", ".")


def main():
    ap = argparse.ArgumentParser(description="Claude Code kayıtlarından API liste fiyatıyla fatura (yalnız sayılar okunur).")
    ap.add_argument("--baslangic", help="ilk gün, YYYY-AA-GG (dahil, UTC)")
    ap.add_argument("--bitis", help="son gün, YYYY-AA-GG (dahil, UTC)")
    ap.add_argument("--proje", help="yalnız klasör adında bu metin geçen projeler (ör. Projeler-blog)")
    ap.add_argument("--kok", help="kayıt klasörü (varsayılan ~/.claude/projects)")
    a = ap.parse_args()

    for ad, gun in (("--baslangic", a.baslangic), ("--bitis", a.bitis)):
        if gun:
            try:
                datetime.date.fromisoformat(gun)
            except ValueError:
                raise SystemExit("%s tarihi YYYY-AA-GG biçiminde olmalı (ör. 2026-10-10): %s" % (ad, gun))
    kok = kayit_koku(a.kok)
    if not os.path.isdir(kok):
        raise SystemExit("Kayıt klasörü yok: %s\nClaude Code hiç çalışmadıysa ya da kayıtlar başka yerdeyse --kok ile göster." % kok)
    istekler, n_dosya = oku(kok, a.baslangic, a.bitis, a.proje)

    model_top = collections.defaultdict(lambda: {"istek": 0, "uzun": 0, **{k: 0 for k in KALEMLER},
                                                 **{"$" + k: 0.0 for k in KALEMLER}})
    fiyatsiz = collections.Counter()
    for model, s in istekler.values():
        if model not in FIYAT:
            if sum(s.values()):
                fiyatsiz[model] += 1
            continue
        t = model_top[model]
        t["istek"] += 1
        for k in KALEMLER:
            t[k] += s[k]
        if model in UZUN_ISTEM and s["giris"] + s["okuma"] + s["yazma_5dk"] + s["yazma_1sa"] > UZUN_ISTEM[model][0]:
            t["uzun"] += 1
        for k, v in istek_dolari(model, s).items():
            t["$" + k] += v

    pencere = "%s → %s" % (a.baslangic or "en eski kayıt", a.bitis or "en yeni kayıt")
    print("Claude Code faturası · API liste fiyatıyla HESAPLANDI (ödenen tutar değil)")
    print("Pencere: %s (UTC, tam gün) · %d kayıt dosyası%s" % (pencere, n_dosya, (" · proje: " + a.proje) if a.proje else ""))
    print("Fiyat: %s, %s\n" % (FIYAT_TARIHI, FIYAT_KAYNAGI))
    if not model_top:
        print("Bu pencerede fiyatı bilinen modelle istek yok.")
        return

    genel = sum(sum(t["$" + k] for k in KALEMLER) for t in model_top.values())
    sirali = sorted(model_top.items(), key=lambda x: -sum(x[1]["$" + k] for k in KALEMLER))
    bas = "%-18s %8s %13s %13s %13s %13s %11s %7s"
    print("Token (milyon)")
    print(bas % ("Model", "İstek", "Giriş", "Önb. yazma", "Önb. okuma", "Çıkış", "$", "Pay"))
    for model, t in sirali:
        d = sum(t["$" + k] for k in KALEMLER)
        print(bas % (model, tr(t["istek"], 0), tr(t["giris"] / 1e6), tr((t["yazma_5dk"] + t["yazma_1sa"]) / 1e6),
                     tr(t["okuma"] / 1e6), tr(t["cikis"] / 1e6), tr(d), "%" + tr(100 * d / genel, 1)))
    print(bas % ("TOPLAM", tr(sum(t["istek"] for t in model_top.values()), 0), "", "", "", "", tr(genel), ""))

    print("\nDolar, kalem kalem")
    print("%-18s %13s %13s %13s %13s" % ("Model", "Giriş", "Önb. yazma", "Önb. okuma", "Çıkış"))
    kalem = {"giris": 0.0, "yazma": 0.0, "okuma": 0.0, "cikis": 0.0}
    for model, t in sirali:
        y = t["$yazma_5dk"] + t["$yazma_1sa"]
        kalem["giris"] += t["$giris"]; kalem["yazma"] += y; kalem["okuma"] += t["$okuma"]; kalem["cikis"] += t["$cikis"]
        print("%-18s %13s %13s %13s %13s" % (model, tr(t["$giris"]), tr(y), tr(t["$okuma"]), tr(t["$cikis"])))
    print("Pay: giriş %%%s · önbellek yazma %%%s · önbellekten okuma %%%s · çıkış %%%s" % tuple(
        tr(100 * kalem[k] / genel, 1) for k in ("giris", "yazma", "okuma", "cikis")))

    uzun = {m: t["uzun"] for m, t in model_top.items() if t["uzun"]}
    if uzun:
        print("\nUzun istem fiyatından faturalanan istek: " + ", ".join("%s %d" % kv for kv in uzun.items()))
    if fiyatsiz:
        print("\nFiyat tablosunda olmayan model (toplama girmedi; tabloya ekleyebilirsin): "
              + ", ".join("%s (%d istek)" % kv for kv in fiyatsiz.most_common()))


if __name__ == "__main__":
    main()
