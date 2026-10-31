# -*- coding: utf-8 -*-
"""yonlendir.py: her işi etiketine göre doğru modele gönderir, her çağrıdan sonra kaç sent tuttuğunu yazar.

Kullanım:
  python yonlendir.py yorum "Bu yorumu olumlu/olumsuz diye etiketle: Latte soğuktu ama kasiyer çok iyiydi."
  python yonlendir.py ozet --dosya rapor.txt
  python yonlendir.py --isler ornek-isler.jsonl          # birçok iş, her satır {"etiket": ..., "metin": ...}
  python yonlendir.py --isler ornek-isler.jsonl --kuru   # API çağırmaz: hangi modele gider, tahmini kaç $
  python yonlendir.py --liste                            # etiket → kademe → model tablosu

Gerçek çağrı için: pip install anthropic ve ANTHROPIC_API_KEY ortam değişkeni (anahtarı dosyaya yazma).
--kuru kipi ne anahtar ne kütüphane ister.
"""
import argparse, io, json, os, sys

for _akis in (sys.stdout, sys.stderr):
    if hasattr(_akis, "reconfigure"):
        _akis.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolunda Türkçe harfler bozulmasın

# ---------------------------------------------------------------------------------------------
# YÖNLENDİRME TABLOSU: kendi işlerine göre düzenle. Etiket → kademe.
# Ölçüt üç soru: cevabı kontrol edilebilir mi, yanlışsa bedeli ne, kaç kez tekrar ediyor?
# Bilgi eksik olabilecek ve yanlışı fark edilmeyecek iş → usta. Ayrıntı: esleme-tablosu.md
ROTA = {
    "yorum":       "cirak",   # yorum ayıklama, olumlu/olumsuz etiketi
    "etiket":      "cirak",   # sınıflandırma
    "tablo":       "cirak",   # e-postadan/metinden tablo çıkarma
    "ozet":        "cirak",
    "ceviri":      "cirak",
    "hesap":       "cirak",   # sonucu kontrol edilen hesap
    "kod-testli":  "cirak",   # testleri olan kod düzeltme (testler cevabı kontrol eder)
    "yazi":        "kalfa",   # marka sesiyle gönderi, e-posta taslağı
    "kod":         "kalfa",   # testi olmayan kod
    "karar":       "usta",    # para ya da geri dönüşü olmayan karar
    "eksik-bilgi": "usta",    # bilgi eksik olabilir, yanlışı fark edilmeyebilir
}
# Kademe → (model, çaba). Çaba (effort): low | medium | high | xhigh | max
KADEME = {
    "cirak": ("claude-haiku-5-5", "medium"),
    "kalfa": ("claude-sonnet-5-5", "high"),
    "usta":  ("claude-opus-5-5", "medium"),
}
KADEME_AD = {"cirak": "çırak", "kalfa": "kalfa", "usta": "usta"}

# FİYAT: 2026-10-30, https://platform.claude.com/docs/en/about-claude/pricing (değişir, kaynağa bak)
# 1 milyon token başına $: (giriş, önbellek yazma 5 dk, önbellek yazma 1 sa, önbellekten okuma, çıkış)
FIYAT = {
    "claude-opus-5-5":   (4.00, 5.00, 8.00, 0.20, 20.00),
    "claude-sonnet-5-5": (2.00, 2.50, 4.00, 0.10, 10.00),
    "claude-haiku-5-5":  (0.10, 0.125, 0.20, 0.01, 0.50),
}
# Haiku 5.5: istemi 100 bin token'ı geçen İSTEK 5 kat fiyattan faturalanır (eşik her isteğe ayrı uygulanır)
UZUN_ISTEM = {"claude-haiku-5-5": (100_000, (0.50, 0.625, 1.00, 0.05, 2.50))}
# ---------------------------------------------------------------------------------------------

KARAKTER_BASINA_TOKEN = 1 / 3.2  # --kuru için kaba tahmin (Türkçe metin); gerçek sayı çağrıdan sonra yazılır


def dolar(model, giris, yazma_5dk, yazma_1sa, okuma, cikis):
    """Tek isteğin doları. Eşikli fiyat bu isteğin kendi istemine (giriş + önbellek) bakar."""
    fiyat = FIYAT[model]
    if model in UZUN_ISTEM and giris + yazma_5dk + yazma_1sa + okuma > UZUN_ISTEM[model][0]:
        fiyat = UZUN_ISTEM[model][1]
    return sum(n * f for n, f in zip((giris, yazma_5dk, yazma_1sa, okuma, cikis), fiyat)) / 1e6


def uzun_mu(model, istem):
    return model in UZUN_ISTEM and istem > UZUN_ISTEM[model][0]


def para(x):
    """0.00463 → '0,0046 $ (0,46 sent)'"""
    return "%s $ (%s sent)" % (("%.4f" % x).replace(".", ","), ("%.2f" % (100 * x)).replace(".", ","))


def model_sec(etiket):
    if etiket not in ROTA:
        raise SystemExit("Bilinmeyen etiket: %r. Var olanlar: %s\nYeni etiketi yonlendir.py başındaki ROTA tablosuna ekle."
                         % (etiket, ", ".join(sorted(ROTA))))
    kademe = ROTA[etiket]
    model, caba = KADEME[kademe]
    return kademe, model, caba


def isleri_oku(a):
    if a.isler:
        isler = []
        for no, satir in enumerate(io.open(a.isler, encoding="utf-8"), 1):
            if not satir.strip() or satir.lstrip().startswith("#"):
                continue
            try:
                d = json.loads(satir)
            except ValueError:
                raise SystemExit("%s satır %d geçerli JSON değil" % (a.isler, no))
            metin = d.get("metin") or ""
            if d.get("dosya"):  # dosya yolu JSONL dosyasının klasörüne göre; metin varsa dosyanın arkasına eklenir
                ek = io.open(os.path.join(os.path.dirname(os.path.abspath(a.isler)), d["dosya"]), encoding="utf-8").read()
                metin = ek + ("\n\n" + metin if metin else "")
            if not d.get("etiket") or not metin:
                raise SystemExit("%s satır %d: 'etiket' ve 'metin' (ya da 'dosya') gerekli" % (a.isler, no))
            isler.append((d["etiket"], metin))
        return isler
    if not a.etiket:
        raise SystemExit("Etiket ver (ör. python yonlendir.py yorum \"...\") ya da --isler dosya.jsonl kullan. Yardım: --help")
    if a.dosya:
        metin = io.open(a.dosya, encoding="utf-8").read()
    elif a.metin:
        metin = a.metin
    else:
        raise SystemExit("Metin ver: tırnak içinde ya da --dosya ile.")
    return [(a.etiket, metin)]


def kuru(isler, cikis_tahmini):
    toplam = 0.0
    for etiket, metin in isler:
        kademe, model, caba = model_sec(etiket)
        giris = int(len(metin) * KARAKTER_BASINA_TOKEN) + 10
        d = dolar(model, giris, 0, 0, 0, cikis_tahmini)
        toplam += d
        print("%-12s → %-5s · %s (çaba %s) · ~%d giriş + ~%d çıkış token · tahmini %s%s"
              % (etiket, KADEME_AD[kademe], model, caba, giris, cikis_tahmini, para(d),
                 " · UZUN İSTEM: 5 kat fiyat" if uzun_mu(model, giris) else ""))
    print("\nKURU KİP: API çağrılmadı. %d iş, tahmini toplam %s" % (len(isler), para(toplam)))
    print("Tahmin kabadır: giriş karakter/3,2; çıkış --cikis-tahmini (şu an %d). Gerçek sayı çağrıdan sonra yazılır." % cikis_tahmini)


def gercek(isler, max_tokens):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY ortam değişkeni yok. Anahtarı ortam değişkenine koy (README.md › Kurulum), dosyaya yazma.\n"
                         "API'ye gitmeden denemek için: --kuru")
    try:
        import anthropic
    except ImportError:
        raise SystemExit("anthropic kütüphanesi yok: pip install anthropic  (ya da önce --kuru ile dene)")
    istemci = anthropic.Anthropic()  # anahtarı ANTHROPIC_API_KEY ortam değişkeninden okur
    toplam = 0.0
    for etiket, metin in isler:
        kademe, model, caba = model_sec(etiket)
        try:
            yanit = istemci.messages.create(
                model=model,
                max_tokens=max_tokens,
                output_config={"effort": caba},
                messages=[{"role": "user", "content": metin}],
            )
        except anthropic.AuthenticationError:
            raise SystemExit("Anahtar geçersiz (401). ANTHROPIC_API_KEY'i kontrol et.")
        except anthropic.PermissionDeniedError:
            raise SystemExit("Yetki ya da bakiye sorunu (403). Console'da hesabını kontrol et.")
        except anthropic.RateLimitError:
            raise SystemExit("Hız sınırı (429). Biraz bekleyip yeniden dene.")
        except anthropic.APIStatusError as e:
            raise SystemExit("API hatası %s: %s" % (e.status_code, e.message))
        except anthropic.APIConnectionError:
            raise SystemExit("Ağ hatası: API'ye ulaşılamadı.")

        for blok in yanit.content:
            if blok.type == "text":
                print(blok.text)
        if yanit.stop_reason == "max_tokens":
            print("[uyarı: cevap max_tokens sınırında kesildi, --max-tokens'ı artır]")
        elif yanit.stop_reason == "refusal":
            print("[uyarı: model bu isteği reddetti]")

        u = yanit.usage
        cc = getattr(u, "cache_creation", None)
        y5 = (getattr(cc, "ephemeral_5m_input_tokens", 0) or 0) if cc else 0
        y1 = (getattr(cc, "ephemeral_1h_input_tokens", 0) or 0) if cc else 0
        y5 += max((u.cache_creation_input_tokens or 0) - y5 - y1, 0)
        okuma = u.cache_read_input_tokens or 0
        d = dolar(model, u.input_tokens, y5, y1, okuma, u.output_tokens)
        toplam += d
        print("── %s → %s · %s · giriş %d · önbellek %d · çıkış %d token · %s%s\n"
              % (etiket, KADEME_AD[kademe], model, u.input_tokens, y5 + y1 + okuma, u.output_tokens, para(d),
                 " · UZUN İSTEM: 5 kat fiyat" if uzun_mu(model, u.input_tokens + y5 + y1 + okuma) else ""))
    if len(isler) > 1:
        print("Toplam %d iş: %s (API liste fiyatıyla)" % (len(isler), para(toplam)))


def main():
    ap = argparse.ArgumentParser(description="Etikete göre model seçer, her çağrının token ve $ tutarını yazar.")
    ap.add_argument("etiket", nargs="?", help="işin etiketi (ROTA tablosundaki adlardan biri)")
    ap.add_argument("metin", nargs="?", help="modele gidecek metin")
    ap.add_argument("--dosya", help="metni dosyadan oku")
    ap.add_argument("--isler", help="JSONL dosyası: her satır {\"etiket\": ..., \"metin\": ...} ya da {\"etiket\": ..., \"dosya\": ...}")
    ap.add_argument("--kuru", action="store_true", help="API çağırma; hangi modele gideceğini ve tahmini tutarı göster")
    ap.add_argument("--cikis-tahmini", type=int, default=800, help="--kuru'da iş başına çıkış token tahmini (varsayılan 800)")
    ap.add_argument("--max-tokens", type=int, default=16000, help="çağrı başına en çok çıkış token'ı")
    ap.add_argument("--liste", action="store_true", help="yönlendirme tablosunu göster")
    a = ap.parse_args()

    if a.liste:
        for etiket, kademe in ROTA.items():
            model, caba = KADEME[kademe]
            i, _, _, _, o = FIYAT[model]
            print("%-12s → %-5s · %-18s çaba %-6s · giriş %s $/M, çıkış %s $/M" % (etiket, KADEME_AD[kademe], model, caba, i, o))
        return
    isler = isleri_oku(a)
    if a.kuru:
        kuru(isler, a.cikis_tahmini)
    else:
        gercek(isler, a.max_tokens)


if __name__ == "__main__":
    main()
