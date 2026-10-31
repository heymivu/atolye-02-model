# -*- coding: utf-8 -*-
"""Z3 örnek doğru çözüm (öz-test için; alt ajana verilmez)."""
from datetime import date, timedelta
from decimal import Decimal

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def _kurus(s):
    return int(Decimal(s.replace(".", "").replace(",", ".")) * 100)


def _bicim(kurus):
    isaret = "-" if kurus < 0 else ""
    tl, kr = divmod(abs(kurus), 100)
    return "%s%s,%02d" % (isaret, "{:,}".format(tl).replace(",", "."), kr)


def haftalik_ozet(kayitlar):
    gunler = {}
    for k in kayitlar:
        g = date.fromisoformat(k["tarih"])
        if g.weekday() == 0:
            g = g - timedelta(days=1)
        ad = GUNLER[g.weekday()]
        t = _kurus(k["tutar"])
        gunler[ad] = gunler.get(ad, 0) + (-t if k["tur"] == "iade" else t)
    return {"gunler": {g: _bicim(v) for g, v in gunler.items()}, "toplam": _bicim(sum(gunler.values()))}
