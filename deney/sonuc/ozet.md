# Atölye 2 — ölçüm özeti (otomatik, `analiz.py`)

Yol: Claude Code alt ajanları (abonelik içinde, ücretli API çağrısı yok). Maliyet = kayıttaki token × 2026-10-30 liste fiyatı.
**Ham** = alt ajanın tüm faturası (Claude Code sistem metni dâhil). **Taban** = aynı modelde boş görev (G0). **Görev** = ham − taban (işin kendisi).

| Model | Taban $ |
|---|---|
| Haiku 5.5 | 0.0068 |
| Sonnet 5.5 | 0.1035 |
| Opus 5.5 | 0.2069 |
| Opus 5.5 · düşük çaba | 0.2070 |
| Fable 5.1 | 0.4795 |

## G1 · 40 yorum etiketi

| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |
|---|---|---|---|---|---|
| Haiku 5.5 | 3 | %99.7 etiket doğru | 0.0093 | 0.0024 | 3917 |
| Sonnet 5.5 | 3 | %100.0 etiket doğru | 0.1755 | 0.0720 | 3219 |
| Opus 5.5 | 3 | %100.0 etiket doğru | 0.3292 | 0.1222 | 2349 |
| Opus 5.5 · düşük çaba | 3 | %100.0 etiket doğru | 0.2648 | 0.0578 | 2265 |
| Fable 5.1 | 3 | %100.0 etiket doğru | 0.8247 | 0.3452 | 3040 |

## G2 · teklif tablosu

| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |
|---|---|---|---|---|---|
| Haiku 5.5 | 3 | %100 hücre, koli 3/3 | 0.0067 | -0.0001 | 1572 |
| Sonnet 5.5 | 3 | %100 hücre, koli 3/3 | 0.1442 | 0.0407 | 802 |
| Opus 5.5 | 3 | %100 hücre, koli 3/3 | 0.2877 | 0.0807 | 777 |
| Opus 5.5 · düşük çaba | 3 | %100 hücre, koli 3/3 | 0.2236 | 0.0167 | 705 |
| Fable 5.1 | 3 | %100 hücre, koli 3/3 | 0.6790 | 0.1994 | 793 |

## G3 · plan + 3 gönderi

| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |
|---|---|---|---|---|---|
| Haiku 5.5 | 3 | 3/3 kusursuz (ihlal 0) | 0.0091 | 0.0023 | 5055 |
| Sonnet 5.5 | 3 | 3/3 kusursuz (ihlal 0) | 0.1809 | 0.0774 | 3624 |
| Opus 5.5 | 3 | 3/3 kusursuz (ihlal 0) | 0.3321 | 0.1251 | 2435 |
| Opus 5.5 · düşük çaba | 3 | 2/3 kusursuz (ihlal 1) | 0.2477 | 0.0407 | 1548 |
| Fable 5.1 | 3 | 3/3 kusursuz (ihlal 0) | 0.8922 | 0.4127 | 4090 |

## G4 · süt tedarikçisi kararı

| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |
|---|---|---|---|---|---|
| Haiku 5.5 | 3 | 3/3 doğru + Pazartesi gerekçesi (tuzağa düşen 0) | 0.0091 | 0.0023 | 4381 |
| Sonnet 5.5 | 3 | 3/3 doğru + Pazartesi gerekçesi (tuzağa düşen 0) | 0.1633 | 0.0599 | 2612 |
| Opus 5.5 | 3 | 3/3 doğru + Pazartesi gerekçesi (tuzağa düşen 0) | 0.2689 | 0.0619 | 2427 |
| Opus 5.5 · düşük çaba | 3 | 3/3 doğru + Pazartesi gerekçesi (tuzağa düşen 0) | 0.2493 | 0.0423 | 1642 |
| Fable 5.1 | 3 | 3/3 doğru + Pazartesi gerekçesi (tuzağa düşen 0) | 0.7723 | 0.2928 | 2200 |

## G5 · badem sütü kararı

| Model | n | Kalite | Ham $ | Görev $ | Çıkış token |
|---|---|---|---|---|---|
| Haiku 5.5 | 3 | 2/3 tam (istek sayısı doğru 2/3) | 0.0080 | 0.0012 | 3389 |
| Sonnet 5.5 | 3 | 1/3 tam (istek sayısı doğru 3/3) | 0.1700 | 0.0665 | 2489 |
| Opus 5.5 | 3 | 3/3 tam (istek sayısı doğru 3/3) | 0.2566 | 0.0496 | 1642 |
| Opus 5.5 · düşük çaba | 3 | 3/3 tam (istek sayısı doğru 3/3) | 0.2449 | 0.0379 | 1173 |
| Fable 5.1 | 3 | 2/3 tam (istek sayısı doğru 3/3) | 0.7701 | 0.2905 | 1878 |

## Bir hafta (G1–G5 birer kez), düzenlere göre

| Düzen | Ham $ | Görev $ | Ortalama kalite (0–1) |
|---|---|---|---|
| hep usta (Opus) | 1.474 | 0.440 | 1.000 |
| dağıtılmış (Haiku·Haiku·Sonnet·Opus·Opus) | 0.722 | 0.191 | 0.999 |
| hep çırak (Haiku) | 0.042 | 0.008 | 0.933 |
| hep Fable | 3.938 | 1.541 | 0.933 |

Oran (hep usta ÷ düzen):
- hep usta (Opus): ham ×1.0 · görev ×1.0
- dağıtılmış (Haiku·Haiku·Sonnet·Opus·Opus): ham ×2.0 · görev ×2.3
- hep çırak (Haiku): ham ×35.0 · görev ×54.1
- hep Fable: ham ×0.4 · görev ×0.3
