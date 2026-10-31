# -*- coding: utf-8 -*-
"""Zor tur puanlayıcı öz-testi: doğru cevap tam puan, her tuzak yanlış ve adıyla; hatalı kasa.py düşer, örnek çözüm 8/8."""
import io, json, os, sys
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin

T = os.path.dirname(os.path.abspath(__file__)); K = os.path.dirname(T)
sys.path.insert(0, K)
import puanla_zor as p  # noqa: E402

D = p.DOGRU; sonuc = []


def bak(ad, kosul):
    sonuc.append(kosul); print(("OK  " if kosul else "HATA"), ad)


bak("Z1 doğru", p.z1('hesap...\n{"yulaf_koli": 28, "yulaf_tl": %d}' % D["Z1"]["yulaf_tl"])["dogru"])
bak("Z1 TR biçimli sayı", p.z1('{"yulaf_koli": 28, "yulaf_tl": "14.448"}')["dogru"])
for ad, v in D["Z1"]["tuzak"].items():
    r = p.z1('{"yulaf_koli": 0, "yulaf_tl": %d}' % v)
    bak("Z1 tuzak " + ad, (not r["dogru"]) and ad in r["tuzak"])
bak("Z1 json yok", not p.z1("bilmiyorum")["dogru"])
bak("Z1e null doğru", p.z1e('Eski fiyat yok.\n{"yulaf_koli": 28, "yulaf_tl": null}')["dogru"])
r = p.z1e('{"yulaf_koli": 28, "yulaf_tl": 7476}'); bak("Z1e kısmi toplam yanlış", (not r["dogru"]) and r["tuzak"] == "kismi_toplam")
r = p.z1e('{"yulaf_koli": 28, "yulaf_tl": 14448}'); bak("Z1e uydurma yanlış", (not r["dogru"]) and r["tuzak"] == "sayi_uydurdu")
bak("Z1e json yok", not p.z1e("bilmiyorum")["dogru"])
bak("Z2 doğru", p.z2('{"malzeme_tl": 41.51, "fiyat_tl": 140}')["dogru"])
bak("Z2 malzeme ±0,05", p.z2('{"malzeme_tl": "41,53", "fiyat_tl": 140}')["malzeme_dogru"])
for ad, v in D["Z2"]["tuzak"].items():
    r = p.z2('{"malzeme_tl": 1, "fiyat_tl": %d}' % v)
    bak("Z2 tuzak " + ad, (not r["dogru"]) and ad in r["tuzak"])
dogru_kod = io.open(os.path.join(T, "kasa_dogru.py"), encoding="utf-8").read()
hatali_kod = io.open(os.path.join(K, "girdiler", "kasa.py"), encoding="utf-8").read()
r = p.z3("Düzelttim.\n```python\n" + dogru_kod + "```\n"); bak("Z3 örnek çözüm 8/8 (%d)" % r["gecti"], r["dogru"])
r = p.z3("```python\n" + hatali_kod + "```"); bak("Z3 hatalı kod düşer (%d/8)" % r["gecti"], (not r["dogru"]) and r["gecti"] <= 2)
r = p.z3("kod yok"); bak("Z3 kod bloğu yok", not r["dogru"])
print("%d/%d" % (sum(sonuc), len(sonuc)))
sys.exit(0 if all(sonuc) else 1)
