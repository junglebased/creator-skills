#!/usr/bin/env python3
"""hookscore_tr.py - Turkish layer for hookscore.py. The upstream file is untouched.

Same five properties and the same verdict (60% mean, 40% weakest), but read through Turkish:
agglutinative suffixes (stem-prefix matching, not whole words), the second person that lives in
verb endings (-sın, -san, -sınız), Turkish number words and money, I/İ casing, and a band of 7-20
words (Turkish packs more into a word than English).

On top of the five scores it prints WARNINGS, which are the part built for RS / JB work:
  KAYNAK?   a number that is not in the facts file (default ~/.claude/FACTS.md) - no invented figures
  KALIP     AI-tell phrases (anti-AI list) and unspecific green claims (GreenSHOUTING)
  SELF      the hook opens with who you are / "bu videoda" / a subscribe pitch

    python3 hookscore_tr.py hooks.txt            # ranked
    python3 hookscore_tr.py --hook "bir satir"   # one hook
    python3 hookscore_tr.py --json hooks.txt
    python3 hookscore_tr.py --facts FILE ...     # facts file for the KAYNAK? check
    python3 hookscore_tr.py --selftest           # runs gold_tr.txt, prints pair accuracy

HONEST LIMITS. The weights are hand-set, not fitted to Turkish view data. gold_tr.txt is written
by hand (strong vs weak pairs on the same idea), so --selftest proves the scorer reads Turkish and
orders deliberate pairs sensibly; it does not predict views. A low score = look again.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORMULAS = json.load(open(os.path.join(HERE, "hooks_tr.json"), encoding="utf-8"))["hooks"]
DEFAULT_FACTS = os.path.expanduser("~/.claude/FACTS.md")

W = r"[\wçğıöşüÇĞİÖŞÜ]"          # one letter of a Turkish word

def tl(t):
    """Turkish-aware lower(): İ->i, I->ı (plain lower() turns İ into i + combining dot)."""
    return t.replace("İ", "i").replace("I", "ı").lower()

def words(t): return re.findall(r"[a-zçğıöşü0-9%₺]+", tl(t))

def stem(*stems):
    """Word-START match for each stem, so 'kaybet' also catches kaybettim, kaybedersin, kaybediyor."""
    return re.compile(r"(?<!" + W + r")(?:" + "|".join(stems) + r")" + W + r"*")

NUMWORD = stem("yüz", "bin", "milyon", "milyar", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz",
               "dokuz", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan",
               "yarım", "çeyrek", "ilk", "son", "tek")
NUMWORD_STRICT = re.compile(r"(?<!" + W + r")(yüz|bin|milyon|milyar|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan)(?!" + W + r"{4})")
DIGITS = re.compile(r"(\d[\d.,]*)\s?(%|k\b|bin|milyon|milyar|tl\b|₺|kez|kere|gün|hafta|ay|yıl|saat|dakika|saniye|kişi|film|video)?", re.I)
MONTH = stem("ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık")
UNIT = stem("gün", "hafta", "ay\\b", "yıl", "saat", "dakika", "saniye", "kez", "kere", "kişi")

VAGUE = stem("inanılmaz", "muhteşem", "harika", "efsane", "müthiş", "şok", "çılgın", "devasa", "mükemmel",
             "süper", "sır", "gizli", "kesin", "kusursuz", "devrim", "oyun değiştir", "bomba", "korkunç")
FILLER = stem("yani", "işte", "şey", "arkadaşlar", "merhaba", "selam", "hoş geldin", "bugün", "abone",
              "kanal", "beğen", "videoya", "evet")
# self-intro / summary openers: never earned in the first sentence
SELF = re.compile(r"^\W*(merhaba|selam|ben\s+\w+|bu videoda|bugün size|bugünkü|hoş geldin|kanalıma)", re.I)

# --- second person lives in the verb ending ---
YOU_PRON = stem("sen", "siz", "senin", "sizin", "sana", "size", "seni", "sizi", "sende", "sizde")
YOU_VERB = re.compile(r"(?<!" + W + r")" + W + r"{3,}(?:sın|sin|sun|sün|sınız|siniz|sunuz|sünüz|san|sen|sanız|seniz)(?!" + W + r")")
YOU_VOC = stem("belgesel(?:ci|ler)", "yönetmen", "kameraman", "kurgucu", "yapımcı", "film yapan", "çekiyor",
               "başvuru", "fon ", "hibe")

STAKE = stem("kaybet", "kaybol", "kaçır", "boşa", "boşuna", "israf", "zarar", "bedel", "ödeyeceksin", "ödersin",
             "ödedi", "pahalı", "batır", "hata", "yanlış", "risk", "tehlike", "vazgeç", "bırak", "çöpe",
             "unutul", "hatırlanma", "sessizl", "ölü", "ölmek", "son bul", "bitir", "tükeni", "geç kal",
             "reddedil", "elen", "eleme", "düşer", "düşme", "kapıda kal", "yarısını", "hiçbir işe")
STAKE_FRAME = re.compile(r"(?<!" + W + r")(?:yoksa|aksi halde|aksi takdirde|olmazsa|etmezsen|yapmazsan|değilse)(?!" + W + r")")

CURIO_Q = stem("neden", "niçin", "niye", "nasıl", "ne ", "nedir", "nerede", "kim", "kimse", "hangi", "kaç",
               "peki", "ama", "oysa", "meğer", "aslında", "sadece", "yalnızca", "hiç", "tek bir", "bir tek",
               "sonra ne", "ne oldu", "hâlâ", "hala", "bile", "fakat",
               # an open loop the video promises to close
               "göster", "açıyorum", "anlat", "okuyorum", "sırayla")
CURIO_PART = re.compile(r"(?<!" + W + r")(?:mı|mi|mu|mü)(?!" + W + r")", re.I)   # question particle
CLOSED = re.compile(r"(?<!" + W + r")(?:çünkü|bu yüzden|yani|dolayısıyla|demek ki|sebebi)(?!" + W + r")", re.I)

# --- warnings (not scored) ---
AI_TELL = re.compile(r"(derinlemesine|yolculuğa çık|keşfedeceğiz|keşfe çık|hazır mısınız|gelin birlikte|"
                     r"gelin\s+\w+\s+bakalım|dijital çağda|günümüzün hızlı|bir dünya|sınırları zorla|"
                     r"oyun değiştirici|devrim niteliğinde|büyüleyici|sihirli değnek|bir kez daha|"
                     r"hepimizin bildiği|unutmamak gerekir|önemli bir rol oyna|ele alacağız|göz atacağız|"
                     r"adım adım rehber|her şeyi değiştir)", re.I)
GREEN = re.compile(r"(?<!" + W + r")(sürdürülebilir\w*|çevre dostu|yeşil|doğa dostu|iklimi kurtar\w*|"
                   r"gezegeni kurtar\w*|karbon nötr\w*|net sıfır|doğal)(?!" + W + r")", re.I)

# ------------------------------------------------------------------ properties
def specificity(t):
    w = words(t)
    if not w: return 0
    nums = len(DIGITS.findall(t)) + len(NUMWORD_STRICT.findall(tl(t)))
    units = len(UNIT.findall(tl(t)))
    dates = len(MONTH.findall(tl(t)))
    vague = len(VAGUE.findall(tl(t)))
    filler = len(FILLER.findall(tl(t)))
    s = 34 + min(2, nums) * 20 + min(2, units) * 5 + min(1, dates) * 8 - vague * 16 - filler * 5
    # named things: capitalised mid-sentence words (Mikro Onarım'da, Eceabat, COP31, Dijital Detaylar)
    caps = [x for x in re.findall(r"[A-ZÇĞİÖŞÜ][\wçğıöşüÇĞİÖŞÜ]+(?:'\w+)?|[A-Z]{2,}\d*", t)]
    s += min(18, 6 * max(0, len(caps) - (1 if t[:1].isupper() else 0)))
    return max(0, min(100, s))

def address(t):
    low = tl(t)
    first6 = " ".join(low.split()[:6])
    n = len(YOU_PRON.findall(low)) + len(YOU_VERB.findall(low))
    first = 30 if (YOU_PRON.search(first6) or YOU_VERB.search(first6) or YOU_VOC.search(first6)) else 0
    return max(0, min(100, 26 + min(n, 3) * 18 + first))

def stakes(t):
    low = tl(t)
    n = len(STAKE.findall(low)) + len(STAKE_FRAME.findall(low))
    return max(0, min(100, 22 + min(n, 3) * 26 + (14 if DIGITS.search(t) else 0)))

def curiosity(t):
    low = tl(t)
    n = len(CURIO_Q.findall(low)) + len(CURIO_PART.findall(low))
    q = 18 if t.strip().endswith("?") else 0
    closed = -18 if CLOSED.search(low) else 0
    return max(0, min(100, 24 + min(n, 4) * 17 + q + closed))

def brevity(t):
    n = len(words(t))
    if n == 0: return 0
    if 7 <= n <= 20: return 100            # Turkish: fewer, longer words than English
    if n < 7:  return max(30, 100 - (7 - n) * 12)
    return max(10, 100 - (n - 20) * 7)

PROPS = [("SPECIFICITY", specificity), ("ADDRESS", address), ("STAKES", stakes),
         ("CURIOSITY", curiosity), ("BREVITY", brevity)]

FIX = {
 "SPECIFICITY": "sıfatı bir sayı, bir isim ya da tarihle değiştir (kaynaklı olsun)",
 "ADDRESS": "ilk altı kelimede izleyiciye seslen: 'çekiyorsan', 'sen', 'belgeselciysen'",
 "STAKES": "mevcut yolda devam etmenin bedelini söyle: kaybettiğin ne, kaçırdığın ne",
 "CURIOSITY": "kendi kendini cevaplayan yarıyı at; açık bir boşluk bırak",
 "BREVITY": "7-20 kelime. Sesli oku, nefesin bittiği yerde dur",
}

# ------------------------------------------------------------------ facts / warnings
def load_facts(path):
    try:
        return tl(open(path, encoding="utf-8").read())
    except OSError:
        return None

def norm_num(s): return re.sub(r"[.,\s]", "", s)

def warnings(t, facts):
    out = []
    low = tl(t)
    if SELF.search(t):
        out.append("SELF     açılış kendini tanıtıyor / özetliyor; izleyicinin bedeliyle aç")
    for m in AI_TELL.finditer(low):
        out.append(f"KALIP    yapay zeka kalıbı: '{m.group(0)}'")
    for m in GREEN.finditer(low):
        out.append(f"KALIP    belirsiz yeşil iddia: '{m.group(0)}' (GreenSHOUTING: kaynaklı, somut ya da çıkar)")
    if facts is not None:
        known = {norm_num(x.strip(".,")) for x in re.findall(r"\d[\d.,]*", facts)}
        for m in re.finditer(r"\d[\d.,]*", t):
            raw = m.group(0).strip(".,")
            if len(norm_num(raw)) >= 2 and norm_num(raw) not in known:
                out.append(f"KAYNAK?  '{raw}' facts dosyasında yok; kaynak göster ya da çıkar")
    return out

# ------------------------------------------------------------------ scoring
def classify(t):
    best, hits = None, 0
    for f in FORMULAS:
        n = sum(1 for p in f["match"] if re.search(p, t, re.I))
        if n > hits: best, hits = f, n
    return (best["name"] if best else "Sınıflanmadı"), hits

def score(t):
    parts = {n: fn(t) for n, fn in PROPS}
    vals = list(parts.values())
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    name, hits = classify(t)
    return parts, verdict, name, hits

def band(v): return "GÜÇLÜ" if v >= 72 else "İDARE EDER" if v >= 55 else "ZAYIF"

def report(r):
    t = r["hook"]
    print(f"\n  {t}")
    print(f"  {'-' * min(72, max(20, len(t)))}")
    for k, v in r["properties"].items():
        print(f"    {k:<12} {v:3d}  {'#' * (v // 5)}")
    print(f"    {'KARAR':<12} {r['verdict']:3d}  {r['band']}")
    print(f"    formül       {r['formula']}" + (f"  ({r['matched']} kalıp)" if r["matched"] else "  (kalıp yok: genelde özettir, hook değil)"))
    low = min(r["properties"], key=r["properties"].get)
    print(f"    en zayıf     {low} - {FIX[low]}")
    for w in r["warnings"]:
        print(f"    ! {w}")

def run(lines, facts):
    out = []
    for t in lines:
        parts, verdict, name, hits = score(t)
        out.append({"hook": t.strip(), "properties": parts, "verdict": verdict, "band": band(verdict),
                    "formula": name, "matched": hits, "warnings": warnings(t, facts)})
    return out

def selftest():
    """gold_tr.txt: blocks separated by a blank line; first line of a block is STRONG, the rest WEAK."""
    path = os.path.join(HERE, "gold_tr.txt")
    blocks = [b.strip().splitlines() for b in open(path, encoding="utf-8").read().split("\n\n") if b.strip()]
    blocks = [[l for l in b if l.strip() and not l.startswith("#")] for b in blocks]
    blocks = [b for b in blocks if len(b) > 1]
    ok = total = 0
    for b in blocks:
        s = score(b[0])[1]
        for weak in b[1:]:
            w = score(weak)[1]
            total += 1; ok += s > w
            print(f"  {'OK ' if s > w else 'MISS'} {s:3d} > {w:3d}  {b[0][:48]}  |  {weak[:40]}")
    print(f"\n  pair accuracy: {ok}/{total} = {round(100 * ok / max(1, total))}%  (hand-written pairs, not view data)")
    return 0 if ok / max(1, total) >= 0.8 else 1

def main():
    a = sys.argv[1:]
    if "--selftest" in a: sys.exit(selftest())
    as_json = "--json" in a
    facts_path = DEFAULT_FACTS
    if "--facts" in a:
        i = a.index("--facts"); facts_path = a[i + 1]; del a[i:i + 2]
    a = [x for x in a if x != "--json"]
    facts = load_facts(facts_path)
    if "--hook" in a:
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        lines = [l for l in open(a[0], encoding="utf-8").read().splitlines() if l.strip()]
    else:
        print(__doc__); sys.exit(1 if not a else 0)
    out = sorted(run(lines, facts), key=lambda r: -r["verdict"])
    if as_json:
        print(json.dumps([{k: v for k, v in r.items() if k != "matched"} for r in out], indent=1, ensure_ascii=False)); return
    for r in out: report(r)
    if len(out) > 1:
        print(f"\n  kazanan: {out[0]['hook']}  ({out[0]['verdict']}, {out[0]['band']})\n")

if __name__ == "__main__":
    main()
