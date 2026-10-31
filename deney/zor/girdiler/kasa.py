# -*- coding: utf-8 -*-
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
