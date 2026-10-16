#!/usr/bin/env python3
"""cf-qa: pre-publish checks for one Content Factory piece (see docs/CF-PIECE-CONTRACT.md).

  cfqa.py PIECE_DIR [--code E1] [--index VISUAL_INDEX_DIR] [--brand-kit brands/rs.md]
          [--size 1080x1350] [--chars-headline 24] [--chars-body 40] [--max-lines 3]
          [--max-hashtags 5] [--max-emoji 1] [--manychat OMB]

Reads only. Writes <PIECE>/04 Export/QA.md (new file per run if one exists: QA-v2.md ...).
Exit code 1 if any FAIL.
"""
import argparse, csv, glob, json, os, re, sys, unicodedata
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    Image = None

DEFAULT_BANNED = ['tutkulu', 'ilham verici', 'yolculuk', 'inanılmaz', 'özverili', 'günümüzde', 'keşfet',
                  'büyüleyici', 'kurtarır', 'mucize', '%100', 'sıfır atık',
                  'passionate', 'journey', 'inspiring', 'game-changer', 'unlock', 'delve']
RISK_WORDS = ['sigara', 'cigarette', 'alkol', 'alcohol', 'logo', 'brand', 'marka', 'plate', 'plaka']


def find(piece, *names):
    for n in names:
        p = os.path.join(piece, n)
        if os.path.exists(p):
            return p
    return None


def emoji_count(s):
    return sum(1 for ch in s if unicodedata.category(ch) == 'So' or 0x1F300 <= ord(ch) <= 0x1FAFF)


def brand_limits(path):
    """Pull numbers from a brand kit line like: chars_per_line: headline Boska 76 px ≈ 22–24, body ... ≈ 38–40"""
    out = {}
    if not path or not os.path.exists(path):
        return out
    txt = open(path, encoding='utf-8').read()
    m = re.search(r'chars_per_line[^\n]*', txt)
    if m:
        nums = [int(x) for x in re.findall(r'(\d+)\s*(?:chars|karakter|\)|,|$|·)', m.group(0))]
        rng = re.findall(r'≈\s*(\d+)\s*[–-]\s*(\d+)', m.group(0))
        if len(rng) >= 2:
            out['headline'], out['body'] = int(rng[0][1]), int(rng[1][1])
        elif len(nums) >= 2:
            out['headline'], out['body'] = nums[0], nums[1]
    m = re.search(r'banned[_ ]words[^:]*:\s*(.+)', txt, re.I)
    if m:
        out['banned'] = [w.strip().lower() for w in re.split(r'[,·;]', m.group(1)) if w.strip()]
    return out


class Report:
    def __init__(self):
        self.rows = []

    def add(self, status, check, detail=''):
        self.rows.append((status, check, detail))

    def md(self, title):
        n = {s: sum(r[0] == s for r in self.rows) for s in ('FAIL', 'WARN', 'PASS')}
        out = [f'# QA · {title} · {datetime.now():%Y-%m-%d %H:%M}', '',
               f'**{n["FAIL"]} FAIL · {n["WARN"]} WARN · {n["PASS"]} PASS**', '',
               '| status | check | detail |', '|---|---|---|']
        order = {'FAIL': 0, 'WARN': 1, 'PASS': 2}
        for s, c, d in sorted(self.rows, key=lambda r: order[r[0]]):
            out.append(f'| {s} | {c} | {d.replace("|", "/")} |')
        return '\n'.join(out) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('piece')
    ap.add_argument('--code')
    ap.add_argument('--index')
    ap.add_argument('--brand-kit')
    ap.add_argument('--size', default='1080x1350')
    ap.add_argument('--chars-headline', type=int)
    ap.add_argument('--chars-body', type=int)
    ap.add_argument('--max-lines', type=int, default=3)
    ap.add_argument('--max-hashtags', type=int, default=5)
    ap.add_argument('--max-emoji', type=int, default=1)
    ap.add_argument('--manychat', help='ManyChat trigger keyword actually configured')
    a = ap.parse_args()
    piece = a.piece.rstrip('/')
    R = Report()
    bl = brand_limits(a.brand_kit)
    ch_h = a.chars_headline or bl.get('headline', 24)
    ch_b = a.chars_body or bl.get('body', 40)
    banned = DEFAULT_BANNED + bl.get('banned', [])

    txt_dir = find(piece, '02 Metin', '02 Copy') or piece
    sj = sorted(glob.glob(os.path.join(txt_dir, f'{a.code or "*"}.slides.json')))
    if not sj:
        R.add('FAIL', 'slides.json', f'no <code>.slides.json in {txt_dir} (contract: docs/CF-PIECE-CONTRACT.md)')
        data = {'slides': []}
    else:
        data = json.load(open(sj[0], encoding='utf-8'))
        R.add('PASS', 'slides.json', os.path.basename(sj[0]))
    code = a.code or data.get('code') or 'piece'
    slides = data.get('slides', [])
    kw = (data.get('cta_keyword') or '').strip()

    # ---- R1 text: line limits, balance, banned, punctuation, open placeholders
    for s in slides:
        n = s.get('n')
        for part, lim in (('headline', ch_h), ('body', ch_b)):
            lines = s.get(part) or []
            if isinstance(lines, str):
                R.add('FAIL', f'S{n} {part}', 'string, not a list of lines: line breaks must be manual (R1)')
                lines = lines.split('\n')
            maxl = a.max_lines + (1 if part == 'headline' else 0)
            if len(lines) > maxl:
                R.add('FAIL', f'S{n} {part} lines', f'{len(lines)} > {maxl}')
            elif len(lines) > a.max_lines:
                R.add('WARN', f'S{n} {part} lines', f'{len(lines)} lines (4 only if unavoidable)')
            for ln in lines:
                if len(ln) > lim:  # up to +15 % = WARN (renders, but check), beyond = FAIL
                    R.add('WARN' if len(ln) <= lim * 1.15 else 'FAIL', f'S{n} {part} length',
                          f'"{ln}" {len(ln)} > {lim} chars')
            if len(lines) >= 2:
                lens = [len(x) for x in lines]
                if min(lens) and max(lens) / min(lens) > 1.8:
                    R.add('WARN', f'S{n} {part} balance', f'line lengths {lens}')
                if len(lines[-1].split()) == 1 and len(lines[-1]) < 10:
                    R.add('WARN', f'S{n} {part} widow', f'one-word last line "{lines[-1]}"')
            for ln in lines:
                low = ln.lower()
                for w in banned:
                    if w and w in low:
                        R.add('FAIL', f'S{n} banned word', f'"{w}" in "{ln}"')
                if '!' in ln:
                    R.add('WARN', f'S{n} punctuation', f'exclamation in "{ln}"')
                if '—' in ln:
                    R.add('WARN', f'S{n} punctuation', f'em dash in "{ln}"')
                if re.search(r'\[(SOURCE|KAYNAK|DETAIL|YEAR)\?\]', ln, re.I):
                    R.add('FAIL', f'S{n} open placeholder', ln)
                if emoji_count(ln):
                    R.add('WARN', f'S{n} emoji on slide', ln)
        if re.search(r'\d', ' '.join((s.get('headline') or []) + (s.get('body') or []))) and not s.get('sources') \
                and s.get('role') not in ('cta',):
            R.add('FAIL', f'S{n} number without source', 'every number/quote on a slide needs a sources id')

    if slides and not any(r[1].startswith('S') and r[0] != 'PASS' for r in R.rows):
        R.add('PASS', 'R1 text', f'{len(slides)} slides within {a.max_lines} lines, {ch_h}/{ch_b} chars')

    # ---- CTA keyword consistency (slide = caption = ManyChat)
    cap_p = None
    for pat in (f'{code}.caption.md', '*.caption.md'):
        g = glob.glob(os.path.join(txt_dir, pat))
        if g:
            cap_p = g[0]
            break
    caption = open(cap_p, encoding='utf-8').read() if cap_p else ''
    if not cap_p:
        R.add('FAIL', 'caption', 'no <code>.caption.md')
    cta_slides = [s for s in slides if s.get('role') == 'cta']
    if kw:
        on_slide = any(kw in ' '.join((s.get('headline') or []) + (s.get('body') or [])) for s in cta_slides)
        R.add('PASS' if on_slide else 'FAIL', 'CTA keyword on CTA slide', kw)
        R.add('PASS' if re.search(rf'\b{re.escape(kw)}\b', caption) else 'FAIL', 'CTA keyword in caption', kw)
        trig = re.search(r'manychat_trigger:\s*(\S+)', caption)
        mc = a.manychat or (trig.group(1) if trig else '')
        if mc:
            R.add('PASS' if mc.upper() == kw.upper() else 'FAIL', 'CTA keyword = ManyChat trigger', f'{kw} / {mc}')
        else:
            R.add('WARN', 'ManyChat trigger', 'not stated: confirm in ManyChat before publishing')
    elif cta_slides:
        R.add('FAIL', 'cta_keyword', 'CTA slide but no cta_keyword in slides.json')

    # ---- caption hygiene
    if caption:
        body = caption.split('## Hashtags')[0]
        tags = re.findall(r'(?<!\w)#\w+', caption)
        R.add('PASS' if len(tags) <= a.max_hashtags else 'FAIL', 'hashtags', f'{len(tags)} (max {a.max_hashtags})')
        e = emoji_count(body)
        R.add('PASS' if e <= a.max_emoji else 'FAIL', 'emoji in caption', f'{e} (max {a.max_emoji})')
        for w in banned:
            if w and w in body.lower():
                R.add('FAIL', 'caption banned word', w)
        if body.count('—') > 1:
            R.add('WARN', 'caption em dashes', str(body.count('—')))
        if '!' in body:
            R.add('WARN', 'caption exclamation', 'brand voice: none')
        if re.search(r'\[(SOURCE|KAYNAK|DETAIL|YEAR)\?\]', caption, re.I):
            R.add('FAIL', 'caption open placeholder', '')
        if re.search(r'link in bio|linke tıkla|bio\'daki link', caption, re.I) and kw:
            R.add('WARN', 'caption', 'link-in-bio next to a comment-keyword CTA: pick one')

    # ---- exports: size, count, naming
    exp = find(piece, '04 Export')
    pngs = sorted(glob.glob(os.path.join(exp, f'{code}_*.png'))) if exp else []
    if not pngs and exp:
        pngs = sorted(glob.glob(os.path.join(exp, '*.png')))
    if not pngs:
        R.add('WARN', 'exports', 'no PNG exports yet')
    else:
        W, H = (int(x) for x in a.size.lower().split('x'))
        bad = []
        for p in pngs:
            if Image:
                with Image.open(p) as im:
                    if im.size != (W, H):
                        bad.append(f'{os.path.basename(p)} {im.size[0]}x{im.size[1]}')
        R.add('FAIL' if bad else 'PASS', 'export size', ', '.join(bad) or f'{len(pngs)} × {a.size}')
        still_slides = [s for s in slides if s.get('role') != 'video']
        if slides and len(pngs) < len(still_slides):
            R.add('WARN', 'export count', f'{len(pngs)} PNG for {len(still_slides)} still slides')
        if len(pngs) > 20:
            R.add('FAIL', 'export count', f'{len(pngs)} > 20 (Instagram limit)')

    # ---- visuals: index, consent, risk, repeats, diversity
    if a.index and os.path.exists(os.path.join(a.index, 'index.csv')):
        rows = {r['id']: r for r in csv.DictReader(open(os.path.join(a.index, 'index.csv'), encoding='utf-8'))}
        camp = data.get('campaign', '')
        groups, shots, srcs = {}, [], {}
        for s in slides:
            v = s.get('visual', '')
            if not v or v.startswith('clip:'):
                continue
            r = rows.get(v)
            if not r:
                R.add('FAIL', f'S{s.get("n")} visual', f'{v} not in index')
                continue
            if r.get('consent') == 'no':
                R.add('FAIL', f'S{s.get("n")} visual consent', f'{v}: {r.get("notes", "")[:80]}')
            elif r.get('consent') == 'check':
                R.add('WARN', f'S{s.get("n")} visual consent', f'{v}: {r.get("people")} — confirm release')
            if any(w in (r.get('notes', '') + r.get('subject', '')).lower() for w in RISK_WORDS):
                R.add('WARN', f'S{s.get("n")} brand/risk', f'{v}: {r.get("notes", "")[:80]}')
            base = lambda u: u.split(' (')[0].strip()  # "2026-10 E1 OMB (taslak)" -> "2026-10 E1 OMB"
            other = [u for u in r.get('used_in', '').split(';') if u.strip() and base(u) != base(camp)]
            if other:
                R.add('FAIL', f'S{s.get("n")} repeat', f'{v} already used in: {"; ".join(other)}')
            g = r.get('dup_group') or v
            if g in groups:
                R.add('FAIL', f'S{s.get("n")} same shot', f'{v} same dup_group as S{groups[g]}')
            groups[g] = s.get('n')
            shots.append(r.get('shot_type', ''))
            srcs[r['source_label']] = srcs.get(r['source_label'], 0) + 1
            if float(r.get('quality') or 0) < 3:
                R.add('WARN', f'S{s.get("n")} quality', f'{v} q{r.get("quality")}')
        if shots:
            kinds = len(set(shots))
            R.add('PASS' if kinds >= 3 else 'WARN', 'shot-type diversity', f'{kinds} types: {shots}')
            for i in range(2, len(shots)):
                if shots[i] == shots[i - 1] == shots[i - 2]:
                    R.add('WARN', 'shot-type run', f'3× {shots[i]} in a row')
            top = max(srcs.values())
            if top / len(shots) > 0.4 and len(shots) >= 5:
                R.add('WARN', 'source mix', f'{top}/{len(shots)} from one source: {srcs}')
        cover = next((s for s in slides if s.get('role') == 'cover'), None)
        if cover and rows.get(cover.get('visual', '')):
            q = float(rows[cover['visual']].get('quality') or 0)
            R.add('PASS' if q >= 5 else 'WARN', 'cover quality', f'{cover["visual"]} q{q:g} (target 5)')
    else:
        R.add('WARN', 'visual checks', 'no --index given: repeats/consent/diversity not checked')

    # ---- R3 look
    look = data.get('look')
    if look:
        lp = look if os.path.isabs(look) else os.path.join(piece, look)
        R.add('PASS' if os.path.exists(lp) else 'FAIL', 'series look (R3)', look)
        grids = glob.glob(os.path.join(piece, '**', 'compare_*.jpg'), recursive=True)
        R.add('PASS' if grids else 'WARN', 'compare grid (R3)', grids[0] if grids else 'none found: run visual-index grade')
    else:
        R.add('WARN', 'series look (R3)', 'no "look" in slides.json')

    out_dir = exp or piece
    os.makedirs(out_dir, exist_ok=True)
    qp = os.path.join(out_dir, 'QA.md')
    k = 1
    while os.path.exists(qp):
        k += 1
        qp = os.path.join(out_dir, f'QA-v{k}.md')
    open(qp, 'w', encoding='utf-8').write(R.md(code))
    fails = sum(r[0] == 'FAIL' for r in R.rows)
    print(f'{qp}\n{fails} FAIL · {sum(r[0] == "WARN" for r in R.rows)} WARN · {sum(r[0] == "PASS" for r in R.rows)} PASS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
