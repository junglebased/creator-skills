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

## Kalibrasyon (29 Eki 2026)

`calibrate.py`: yt-dlp ile çekilmiş Türkçe videoların ilk 15 saniyelik otomatik altyazısını skorlar, izlenmeyle kanal içi yüzdelik üzerinden karşılaştırır.
Örneklem: @regenerative_stories'in takip ettiği hesaplardan 12 Türkçe kanal, 119 video (çoğu STK / çiftlik / kurum; YouTube 429 verdi, kanal başına 20 hedeflenmişti).

- Skor ile kanal-içi izlenme yüzdeliği: Spearman **+0.22** (zayıf ama pozitif). Üst üçte bir 34.0, alt üçte bir 32.3 ortalama.
- Özellik bazında: STAKES +0.12, BREVITY +0.15, SPECIFICITY +0.08, CURIOSITY 0.00, ADDRESS -0.08. Yani ADDRESS ve CURIOSITY şu veride izlenmeyi ayırt etmiyor.
- Gerçek açılışlar p50 34, p90 40, max 47 puan aldı. Upstream'in 72/55 bantları Türkçede hiç görülmedi, bu yüzden bantlar geçici olarak **GÜÇLÜ ≥50, İDARE EDER 40-49, ZAYIF <40** yapıldı.
- Örneklemin açılışları ağırlıkla "Merhaba…" ve webinar girişleri. En çok izlenen açılış (667 bin) "Merhaba, ben X. 51 yaşındayım. Üç çocuk annesiyim…" tanıklığıydı. Bu yüzden `SELF` uyarısı rakamlı kişisel açılışta susar ve yeni **Tanıklık** formülü eklendi.

Bu bir sağlama, ayar değil. Ağırlıkları bu veriye göre oynatma; önce seçilmiş (iyi hook'lu) kanallardan daha büyük, ayrı bir örneklem lazım.
Otomatik altyazıda noktalama ve büyük harf yok; `?`, `ADDRESS` ve özel isim sinyalleri bu yüzden gerçek açılışlarda eksik ölçülür.

## Sınırlar

Ağırlıklar elle verildi; Türkçe izlenme verisiyle ayarlanmadı. `gold_tr.txt` elle yazılmış çiftlerdir, `--selftest` yalnızca
skorlayıcının Türkçe okuduğunu ve bariz çiftleri doğru sıraladığını gösterir. İzlenmeyi öngörmez. Düşük skor = tekrar bak.
Güçlü hook'lar bile 40-55 aralığında çıkar; bantları (GÜÇLÜ ≥72) gerçek Türkçe veriyle yeniden ayarlamak sıradaki iştir.

Formüllerdeki `[KÖŞELİ]` alanlar doldurulacak boşluklardır; rakam uydurup doldurma.
