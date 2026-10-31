# -*- coding: utf-8 -*-
"""Puanlayıcı öz-testi (Atölye 1 dersi: koşudan önce puanlayıcıyı bilinen cevaplarda sına).
Kusursuz ve bilerek bozulmuş örnek çıktılar üretir, beklenen puanları doğrular. Model çağrısı yok.
Kullanım: python -I test/oz_test.py  (deney klasöründen)"""
import json, io, os, sys
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows konsolu (cp1254) Türkçe/oklarda çökmesin
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOK)
import puanla2 as p  # noqa: E402

D = p.DOGRU
A1 = os.path.join(KOK, "test", "atolye1_ornek")  # Atölye 1 reposundan iki gerçek çıktı (heymivu/atolye-01-context)
sonuc = []


def kontrol(ad, kosul, ayrinti=""):
    sonuc.append((ad, bool(kosul)))
    print(("GEÇTİ " if kosul else "KALDI ") + ad + (("  " + str(ayrinti)) if not kosul else ""))


# G1 kusursuz (ilk alternatif) — açıklama + kod çiti içinde
g1 = [{"id": e["id"], "konu": e["konu"][0], "duygu": e["duygu"][0], "cevap": e["cevap"][0]} for e in D["G1"]["etiketler"]]
r = p.g1("İşte etiketler:\n```json\n" + json.dumps(g1, ensure_ascii=False) + "\n```")
kontrol("G1 kusursuz = 120/120", r["dogru"] == 120, r)
# G1 ironiler yanlış: 6 yorumun duygusu + ve cevabı hayır
g1b = [dict(x) for x in g1]
for x in g1b:
    if x["id"] in D["G1"]["ironik"]:
        x["duygu"], x["cevap"] = "+", "hayır"
r = p.g1(json.dumps(g1b, ensure_ascii=False))
kontrol("G1 ironiler yanlış = 108/120, ironik 0/6", r["dogru"] == 108 and r["ironik_duygu_dogru"] == 0, r)
kontrol("G1 biçim hatası yakalanır", p.g1("etiketleyemedim")["bicim_hatasi"])

# G2 kusursuz + koli tuzağı
gun7 = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
g2 = {"tedarikciler": [
    {"ad": "Ova Süt", "inek_tl_lt": 42, "yulaf_tl_lt": 78, "badem_tl_lt": 96, "teslim_gunleri": ["Pazartesi"], "min_siparis_lt": 60, "vade_gun": 30},
    {"ad": "Kadıköy Çiftlik", "inek_tl_lt": 45, "yulaf_tl_lt": 83, "badem_tl_lt": None, "teslim_gunleri": ["Salı", "Perşembe"], "min_siparis_lt": 40, "vade_gun": 15},
    {"ad": "Marmara Gıda Toptan", "inek_tl_lt": 52, "yulaf_tl_lt": 80, "badem_tl_lt": 92, "teslim_gunleri": gun7, "min_siparis_lt": 30, "vade_gun": 0}]}
r = p.g2(json.dumps(g2, ensure_ascii=False))
kontrol("G2 kusursuz = 18/18, koli doğru", r["dogru"] == 18 and r["koli_litre_dogru"], r)
g2b = json.loads(json.dumps(g2)); g2b["tedarikciler"][1]["inek_tl_lt"] = 540; g2b["tedarikciler"][1]["yulaf_tl_lt"] = 498
r = p.g2(json.dumps(g2b))
kontrol("G2 koli fiyatı litre sanıldı = 16/18, koli yanlış", r["dogru"] == 16 and not r["koli_litre_dogru"], r)

# G3: Atölye 1 gerçek çıktıları (B T2: Pazartesi kapalı; A T3: Pazartesi'ye gönderi)
b_t2 = io.open(os.path.join(A1, "B_dosya_r1_cikti_T2.md"), encoding="utf-8").read()
a_t3 = io.open(os.path.join(A1, "A_prompt_r1_cikti_T3.md"), encoding="utf-8").read()
r = p.g3(b_t2); kontrol("G3 Atölye 1 B·T2 → Pazartesi kapalı", r["pazartesi_kapali"], r)
r = p.g3(a_t3); kontrol("G3 Atölye 1 A·T3 → Pazartesi'ye konu konmuş yakalanır", not r["pazartesi_kapali"], r)

# G4
dogru4 = 'Kadıköy Çiftlik.\n{"secim": "Kadıköy Çiftlik", "elenenler": {"Ova Süt": "Yalnız Pazartesi teslim ediyor, Pazartesi kapalıyız.", "Marmara Gıda Toptan": "Haftalık 5.240 TL, bütçeyi aşıyor."}}'
r = p.g4(dogru4); kontrol("G4 doğru seçim + Pazartesi gerekçesi = 2", r["puan"] == 2, r)
tuzak4 = '{"secim": "Ova Süt", "elenenler": {"Kadıköy Çiftlik": "daha pahalı", "Marmara Gıda Toptan": "bütçe"}}'
r = p.g4(tuzak4); kontrol("G4 tuzak (Ova) = 0, tuzak_secildi", r["puan"] == 0 and r["tuzak_secildi"] == 1, r)
yarim4 = '{"secim": "Kadıköy Çiftlik", "elenenler": {"Ova Süt": "vadesi uzun ama minimum sipariş yüksek", "Marmara": "pahalı"}}'
r = p.g4(yarim4); kontrol("G4 doğru seçim, yanlış gerekçe = 1", r["puan"] == 1, r)

# G5
dogru5 = '{"oneri": "ayse_karar_versin", "istek_sayisi": 5, "badem_tedarikcisi": "Marmara Gıda Toptan", "gerekce": "8. kural süt listesini sınırlıyor; Ova yalnız Pazartesi geliyor."}'
r = p.g5(dogru5); kontrol("G5 tam = 3", r["puan"] == 3, r)
yanlis5 = '{"oneri": "ekle", "istek_sayisi": 4, "badem_tedarikcisi": "Ova Süt", "gerekce": "talep var"}'
r = p.g5(yanlis5); kontrol("G5 hepsi yanlış = 0", r["puan"] == 0, r)

gecen = sum(1 for _, ok in sonuc if ok)
print("\n%d/%d test geçti" % (gecen, len(sonuc)))
sys.exit(0 if gecen == len(sonuc) else 1)
