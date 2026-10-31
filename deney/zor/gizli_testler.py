# -*- coding: utf-8 -*-
"""Z3 gizli testleri (alt ajana verilmez). Kullanım: python -I gizli_testler.py <kasa_modulu.py>  → JSON {"gecti": n, "toplam": 8, "ayrinti": {...}}
Her test ayrı; biri çökerse diğerleri yine koşar. Modül ayrı süreçte değil, importlib ile yüklenir (yalnız standart kütüphane bekleniyor)."""
import importlib.util, json, sys
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin


def yukle(yol):
    spec = importlib.util.spec_from_file_location("kasa_aday", yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.haftalik_ozet


def k(tarih, tutar, tur="satis"):
    return {"tarih": tarih, "tur": tur, "tutar": tutar}


# 2026-11-03 Salı, 04 Çarşamba, 05 Perşembe, 06 Cuma, 07 Cumartesi, 08 Pazar, 09 Pazartesi
TESTLER = {
    "gun_adi_sali": ([k("2026-11-03", "100,00")], lambda r: r["gunler"] == {"Salı": "100,00"}),
    "gun_adi_hafta": ([k("2026-11-04", "10,00"), k("2026-11-06", "20,00"), k("2026-11-07", "30,00")],
                      lambda r: r["gunler"] == {"Çarşamba": "10,00", "Cuma": "20,00", "Cumartesi": "30,00"}),
    "pazartesi_pazara": ([k("2026-11-08", "200,00"), k("2026-11-09", "50,00")], lambda r: r["gunler"] == {"Pazar": "250,00"} and r["toplam"] == "250,00"),
    "binlik_okuma": ([k("2026-11-05", "1.234,50")], lambda r: r["gunler"].get("Perşembe") == "1.234,50"),
    "binlik_yazma": ([k("2026-11-05", "6.000,00"), k("2026-11-07", "6.000,00")], lambda r: r["toplam"] == "12.000,00"),
    "iade": ([k("2026-11-03", "300,00"), k("2026-11-04", "40,00", "iade"), k("2026-11-04", "100,00")],
             lambda r: r["gunler"] == {"Salı": "300,00", "Çarşamba": "60,00"} and r["toplam"] == "360,00"),
    "kurus": ([k("2026-11-06", "0,10")] * 3 + [k("2026-11-06", "0,05", "iade")], lambda r: r["gunler"] == {"Cuma": "0,25"} and r["toplam"] == "0,25"),
    "karisik": ([k("2026-11-08", "1.999,99"), k("2026-11-09", "0,01"), k("2026-11-03", "12.345,67"), k("2026-11-03", "345,67", "iade")],
                lambda r: r["gunler"] == {"Pazar": "2.000,00", "Salı": "12.000,00"} and r["toplam"] == "14.000,00"),
}


def kos(yol):
    ayrinti = {}
    try:
        f = yukle(yol)
    except Exception as e:  # modül yüklenmiyor → hepsi kalır
        return {"gecti": 0, "toplam": len(TESTLER), "ayrinti": {"yukleme": repr(e)[:200]}}
    for ad, (girdi, kontrol) in TESTLER.items():
        try:
            r = f([dict(x) for x in girdi])
            ayrinti[ad] = bool(kontrol(r))
        except Exception as e:
            ayrinti[ad] = "hata: " + repr(e)[:120]
    return {"gecti": sum(1 for v in ayrinti.values() if v is True), "toplam": len(TESTLER), "ayrinti": ayrinti}


if __name__ == "__main__":
    print(json.dumps(kos(sys.argv[1]), ensure_ascii=False))
