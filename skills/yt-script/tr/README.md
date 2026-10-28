# yt-script, Türkçe katman

Upstream dosyalar (`hookscore.py`, `hooks.json`) değişmedi. Türkçe için bu klasörü kullan.

```bash
python3 -I tr/hookscore_tr.py hooks.txt              # sırala
python3 -I tr/hookscore_tr.py --hook "tek satır"
python3 -I tr/hookscore_tr.py --facts ~/.claude/FACTS.md hooks.txt
python3 -I tr/hookscore_tr.py --selftest             # gold_tr.txt çiftleri
```

## Ne farklı

| Konu | Upstream (EN) | Bu katman |
|---|---|---|
| Kelime eşleşmesi | tam kelime | kök-önek: `kaybet` → kaybettim, kaybedersin |
| Büyük/küçük harf | `lower()` (İ bozulur) | İ/I doğru çevrilir |
| İkinci tekil | `you` | `-sın/-san/-sınız`, sen/siz ekleri, "belgeselciysen" gibi hitaplar |
| Sayı | rakam | rakam + yüz/bin/milyon/otuz…, ay adları, gün/hafta/kez birimleri |
| Soru | why/how | neden/nasıl/…, soru eki mı/mi/mu/mü, açık döngü ("gösteriyorum") |
| Kısalık bandı | 9-24 kelime | 7-20 kelime (Türkçede kelime daha uzun) |
| Formüller | 21 | 21 Türkçe + 5 yerel: Dalga, Fon Makbuzu, Saha Notu, Sessizlik Bedeli, Yerel Kanıt |

## Skor dışı uyarılar (RS / JB için)

- `KAYNAK?` hook'taki sayı facts dosyasında (varsayılan `~/.claude/FACTS.md`) yoksa uyarır. Uydurma rakam yok.
- `KALIP` yapay zeka kalıpları ve belirsiz yeşil iddialar (GreenSHOUTING).
- `SELF` kendini tanıtan ya da "bu videoda" ile açan hook.

## Sınırlar

Ağırlıklar elle verildi; Türkçe izlenme verisiyle ayarlanmadı. `gold_tr.txt` elle yazılmış çiftlerdir, `--selftest` yalnızca
skorlayıcının Türkçe okuduğunu ve bariz çiftleri doğru sıraladığını gösterir. İzlenmeyi öngörmez. Düşük skor = tekrar bak.
Güçlü hook'lar bile 40-55 aralığında çıkar; bantları (GÜÇLÜ ≥72) gerçek Türkçe veriyle yeniden ayarlamak sıradaki iştir.

Formüllerdeki `[KÖŞELİ]` alanlar doldurulacak boşluklardır; rakam uydurup doldurma.
