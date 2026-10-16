#!/usr/bin/env python3
"""visual-index: one searchable pool of every still and video frame for a production.

Source media is only ever READ (ffmpeg/sips/PIL open it as input). Everything this
script writes goes under the index folder (and, with --import-to, JPG copies into the pool).

  vindex.py INDEX scan     --src LABEL=PATH [--src ...] [--import-to POOLDIR]
  vindex.py INDEX scenes   VIDEO --label LABEL [--thresh 0.22] [--every 8] [--max 400]
  vindex.py INDEX sheets   [--only untagged|all] [--per 20]
  vindex.py INDEX merge    TAGS.json [TAGS.json ...]
  vindex.py INDEX select   --tags a,b [--any c,d] [--ratio 4:5] [--n 8] [--ring kisi]
                           [--min-q 3] [--allow-used] [--project NAME]
  vindex.py INDEX use      ID [ID ...] --in "PROJECT / slot"
  vindex.py INDEX prefill  --content-root DIR   (ledger from pieces already made)
  vindex.py INDEX sheets   --only all --ids MO-1,MO-2 --name picks_E1   (picks sheet)
  vindex.py INDEX report

Commands rewrite index.csv: run them one at a time per index (no parallel scan + merge).

INDEX is a folder; it holds index.csv, ledger.csv, thumbs/, frames/, sheets/.
Needs: Python 3.9+, Pillow, ffmpeg/ffprobe (videos), sips (macOS, RAW/HEIC thumbs).
"""
import argparse, csv, hashlib, json, os, re, subprocess, sys, tempfile
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat

IMG = {'.jpg', '.jpeg', '.png', '.heic', '.tif', '.tiff', '.webp'}
RAW = {'.arw', '.dng', '.raf', '.cr2', '.cr3', '.nef'}
VID = {'.mp4', '.mov', '.mxf', '.m4v', '.mts'}

COLS = ['id', 'kind', 'source_label', 'source_path', 'timecode', 'pool_path', 'thumb',
        'w', 'h', 'orientation', 'date', 'camera', 'brightness', 'sharpness', 'dhash', 'dup_group',
        # semantic (filled by a vision pass, see SKILL.md)
        'shot_type', 'subject', 'action', 'topic_tags', 'ripple_ring', 'emotion', 'light',
        'quality', 'crop_fit', 'text_safe', 'people', 'consent', 'notes',
        # usage
        'used_in']
SEMANTIC = COLS[COLS.index('shot_type'):COLS.index('used_in')]
RATIOS = {'9:16': 9 / 16, '4:5': 4 / 5, '1:1': 1.0, '16:9': 16 / 9}


# ---------- io ----------
def load(ix):
    p = os.path.join(ix, 'index.csv')
    if not os.path.exists(p):
        return []
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save(ix, rows):
    p = os.path.join(ix, 'index.csv')
    tmp = p + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in COLS})
    os.replace(tmp, p)


def prefix(ix):
    cfg = os.path.join(ix, 'config.json')
    if os.path.exists(cfg):
        return json.load(open(cfg)).get('prefix', 'VX')
    return 'VX'


def next_id(rows, pre):
    n = max([int(r['id'].split('-')[-1]) for r in rows if r['id'].startswith(pre + '-')] or [0])
    return f'{pre}-{n + 1:04d}'


# ---------- image metrics ----------
def metrics(im):
    g = ImageOps.exif_transpose(im).convert('L')
    g.thumbnail((512, 512))
    bright = ImageStat.Stat(g).mean[0]
    sharp = ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).stddev[0]
    small = g.resize((9, 8), Image.LANCZOS)
    d = list(small.get_flattened_data() if hasattr(small, 'get_flattened_data') else small.getdata())
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (d[y * 9 + x] > d[y * 9 + x + 1])
    return round(bright, 1), round(sharp, 1), f'{bits:016x}'


def hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count('1')


def open_any(path, cache):
    """Open image for reading; RAW/HEIC go through a cached sips JPG (source untouched)."""
    ext = os.path.splitext(path)[1].lower()
    if ext in RAW or ext == '.heic':
        out = os.path.join(cache, hashlib.md5(path.encode()).hexdigest() + '.jpg')
        if not os.path.exists(out):
            subprocess.run(['sips', '-s', 'format', 'jpeg', '-Z', '2400', path, '--out', out],
                           capture_output=True)
        return Image.open(out)
    return Image.open(path)


def exif_info(im):
    try:
        ex = im.getexif()
        date = ex.get(36867) or ex.get(306) or ''
        cam = ' '.join(x for x in [ex.get(271, ''), ex.get(272, '')] if x).strip()
        return str(date)[:19], cam
    except Exception:
        return '', ''


def write_thumb(im, dst, size=640):
    t = ImageOps.exif_transpose(im).convert('RGB')
    t.thumbnail((size, size))
    t.save(dst, 'JPEG', quality=82)


def write_pool_copy(im, dst, long_edge=2400):
    t = ImageOps.exif_transpose(im).convert('RGB')
    t.thumbnail((long_edge, long_edge))
    t.save(dst, 'JPEG', quality=85)


def orient(w, h):
    r = w / h
    return 'portrait' if r < 0.95 else 'landscape' if r > 1.05 else 'square'


def crop_fit_auto(w, h):
    """Which target ratios can be cut from this frame at >=1080 px wide without upscaling."""
    fits = []
    for name, r in RATIOS.items():
        cw = min(w, h * r)
        if cw >= 1080 * 0.9:
            fits.append(name)
    return ','.join(fits)


# ---------- scan ----------
def cmd_scan(a):
    ix = a.index
    os.makedirs(os.path.join(ix, 'thumbs'), exist_ok=True)
    rows = load(ix)
    known = {r['source_path'] + '|' + r['timecode'] for r in rows}
    pre = prefix(ix)
    cache = os.path.join(tempfile.gettempdir(), 'vindex_cache')
    os.makedirs(cache, exist_ok=True)
    added = 0
    for spec in a.src:
        label, path = spec.split('=', 1)
        files = []
        for root, dirs, fs in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(('.', '_'))]
            for f in sorted(fs):
                ext = os.path.splitext(f)[1].lower()
                if f.startswith('.') or ext not in IMG | RAW:
                    continue
                stem = os.path.splitext(f)[0]
                # RAW with a sibling JPG: index the JPG only
                if ext in RAW and any(os.path.exists(os.path.join(root, stem + e)) for e in ('.JPG', '.jpg')):
                    continue
                files.append(os.path.join(root, f))
        for fp in files:
            if fp + '|' in known:
                continue
            try:
                im = open_any(fp, cache)
                im.load()
            except Exception as e:
                print('skip', fp, e, file=sys.stderr)
                continue
            iid = next_id(rows, pre)
            date, cam = exif_info(Image.open(fp) if os.path.splitext(fp)[1].lower() in IMG else im)
            t = ImageOps.exif_transpose(im)
            w, h = t.size
            pool_path = fp
            if a.import_to:
                dd = os.path.join(a.import_to, label)
                os.makedirs(dd, exist_ok=True)
                pool_path = os.path.join(dd, os.path.splitext(os.path.basename(fp))[0] + '.jpg')
                if not os.path.exists(pool_path):
                    write_pool_copy(im, pool_path)
            th = os.path.join('thumbs', iid + '.jpg')
            write_thumb(im, os.path.join(ix, th))
            b, s, dh = metrics(im)
            rows.append(dict(id=iid, kind='photo', source_label=label, source_path=fp, timecode='',
                             pool_path=pool_path, thumb=th, w=w, h=h, orientation=orient(w, h),
                             date=date, camera=cam, brightness=b, sharpness=s, dhash=dh,
                             crop_fit=crop_fit_auto(w, h)))
            known.add(fp + '|')
            added += 1
            if added % 50 == 0:
                print(f'{label}: {added}', flush=True)
                save(ix, rows)
    dedupe(rows)
    save(ix, rows)
    print(f'scan: +{added}, total {len(rows)}')


def dedupe(rows, thr=6):
    """Group near-duplicates (bursts, same scene) by dHash; group id = first member id."""
    groups = []
    for r in rows:
        if not r.get('dhash'):
            continue
        for g in groups:
            if hamming(r['dhash'], g[0]['dhash']) <= thr:
                g.append(r)
                break
        else:
            groups.append([r])
    for g in groups:
        gid = g[0]['id'] if len(g) > 1 else ''
        for r in g:
            r['dup_group'] = gid


# ---------- scenes ----------
def ffprobe_dur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def scene_cuts(video, thresh, log=None):
    if log and os.path.exists(log):
        txt = open(log, errors='ignore').read()
    else:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', video, '-vf',
                            f"scale=480:-2,select='gt(scene,{thresh})',showinfo", '-an', '-f', 'null', '-'],
                           capture_output=True, text=True)
        txt = r.stderr
    return sorted(float(x) for x in re.findall(r'pts_time:([\d.]+)', txt))


def grab(video, t, dst, long_edge):
    vf = f"scale='if(gt(iw,ih),{long_edge},-2)':'if(gt(iw,ih),-2,{long_edge})'"
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{t:.3f}', '-i', video,
                    '-frames:v', '1', '-vf', vf, '-q:v', '2', dst], stdin=subprocess.DEVNULL)
    return os.path.exists(dst)


def tc(t):
    return f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:06.3f}'


def cmd_scenes(a):
    ix = a.index
    rows = load(ix)
    pre = prefix(ix)
    known = {r['source_path'] + '|' + r['timecode'] for r in rows}
    fdir = os.path.join(ix, 'frames', a.label)
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(os.path.join(ix, 'thumbs'), exist_ok=True)
    dur = ffprobe_dur(a.video)
    cuts = [0.0] + [c for c in scene_cuts(a.video, a.thresh, a.log) if c > 0.5] + [dur]
    # scenes shorter than min_len merge into the next one
    bounds = []
    for s, e in zip(cuts, cuts[1:]):
        if bounds and e - bounds[-1][0] < a.min_len:
            bounds[-1] = (bounds[-1][0], e)
        elif e - s >= 0.3:
            bounds.append((s, e))
    tmp = tempfile.mkdtemp()
    added = 0
    for si, (s, e) in enumerate(bounds):
        # one pick per scene, extra picks every --every seconds in long scenes
        n = max(1, int((e - s) // a.every)) if a.every else 1
        for k in range(n):
            seg_s = s + (e - s) * k / n
            seg_e = s + (e - s) * (k + 1) / n
            cands = [seg_s + (seg_e - seg_s) * f for f in (0.3, 0.5, 0.7)]
            best, bs = None, -1
            for c in cands:  # best-frame pick: sharpest of three
                p = os.path.join(tmp, f'c{c:.2f}.jpg')
                if grab(a.video, c, p, 480):
                    sh = metrics(Image.open(p))[1]
                    if sh > bs:
                        best, bs = c, sh
            if best is None:
                continue
            key = a.video + '|' + tc(best)
            if key in known:
                continue
            name = f'{a.label}_{tc(best).replace(":", "-")}.jpg'
            dst = os.path.join(fdir, name)
            if not grab(a.video, best, dst, a.long_edge):
                continue
            im = Image.open(dst)
            w, h = im.size
            iid = next_id(rows, pre)
            th = os.path.join('thumbs', iid + '.jpg')
            write_thumb(im, os.path.join(ix, th))
            b, sh, dh = metrics(im)
            rows.append(dict(id=iid, kind='video_frame', source_label=a.label, source_path=a.video,
                             timecode=tc(best), pool_path=dst, thumb=th, w=w, h=h, orientation=orient(w, h),
                             brightness=b, sharpness=sh, dhash=dh, crop_fit=crop_fit_auto(w, h),
                             notes=f'scene {si + 1}/{len(bounds)} {tc(s)}-{tc(e)}'))
            known.add(key)
            added += 1
            if added >= a.max:
                break
        if added >= a.max:
            break
    dedupe(rows)
    save(ix, rows)
    print(f'scenes {a.label}: {len(bounds)} scenes, +{added} frames')


# ---------- contact sheets ----------
def font(sz):
    for f in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc',
              '/Library/Fonts/Arial.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def cmd_sheets(a):
    ix = a.index
    rows = load(ix)
    if a.only == 'untagged':
        rows = [r for r in rows if not r.get('shot_type')]
    if a.label:
        rows = [r for r in rows if r['source_label'] == a.label]
    if a.ids:  # picks sheet: keep the given order
        by = {r['id']: r for r in load(ix)}
        rows = [by[i] for i in a.ids.split(',') if i in by]
    sd = os.path.join(ix, 'sheets')
    os.makedirs(sd, exist_ok=True)
    cols, cw, ch = 5, 400, 300
    per = a.per
    fnt = font(22)
    out = []
    for i in range(0, len(rows), per):
        chunk = rows[i:i + per]
        nrows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cw, nrows * (ch + 30)), 'white')
        d = ImageDraw.Draw(sheet)
        for j, r in enumerate(chunk):
            x, y = (j % cols) * cw, (j // cols) * (ch + 30)
            try:
                t = Image.open(os.path.join(ix, r['thumb']))
                t.thumbnail((cw - 8, ch - 8))
                sheet.paste(t, (x + (cw - t.width) // 2, y + (ch - t.height) // 2))
            except Exception:
                pass
            lab = r['id'] + ('  ' + r['orientation'][0].upper())
            d.text((x + 6, y + ch + 2), lab, fill='black', font=fnt)
        name = (f'{a.name}_{i // per + 1:02d}.jpg' if a.name else
                f'sheet_{i // per + 1:03d}_{chunk[0]["id"]}_{chunk[-1]["id"]}.jpg')
        sheet.save(os.path.join(sd, name), quality=85)
        out.append(name)
    print(f'{len(out)} sheets -> {sd}')


# ---------- merge semantic tags ----------
def cmd_merge(a):
    ix = a.index
    rows = load(ix)
    by = {r['id']: r for r in rows}
    n = 0
    for f in a.files:
        data = json.load(open(f, encoding='utf-8'))
        for t in data:
            r = by.get(t.get('id'))
            if not r:
                print('unknown id', t.get('id'), file=sys.stderr)
                continue
            for k in SEMANTIC:
                if k in t and t[k] not in (None, ''):
                    v = t[k]
                    r[k] = ','.join(v) if isinstance(v, list) else str(v)
            n += 1
    save(ix, rows)
    print(f'merged {n} rows')


# ---------- select ----------
def score(r, want, anyt, ratio):
    tags = set(x.strip() for x in r.get('topic_tags', '').split(',') if x.strip())
    if want and not want <= tags:
        return None
    if anyt and not tags & anyt:
        return None
    s = float(r.get('quality') or 0) * 2
    s += len(tags & anyt)
    if ratio and ratio in r.get('crop_fit', ''):
        s += 1
    elif ratio:
        return None
    s += min(float(r.get('sharpness') or 0) / 40, 1)
    return s


def cmd_select(a):
    ix = a.index
    rows = load(ix)
    want = set(x for x in (a.tags or '').split(',') if x)
    anyt = set(x for x in (a.any or '').split(',') if x)
    used_proj = set()
    cands = []
    for r in rows:
        if not r.get('shot_type'):
            continue
        if float(r.get('quality') or 0) < a.min_q:
            continue
        if r.get('consent', '').startswith('no'):
            continue
        if a.ring and a.ring not in r.get('ripple_ring', ''):
            continue
        uses = [u for u in r.get('used_in', '').split(';') if u.strip()]
        if uses and not a.allow_used:
            continue
        sc = score(r, want, anyt, a.ratio)
        if sc is None:
            continue
        sc -= 1.5 * len(uses)  # used before: allowed only with --allow-used, still penalised
        cands.append((sc, r))
    cands.sort(key=lambda x: -x[0])
    # diversity: max one per dup_group / video scene, no 3 same shot_type in a row,
    # max 2 from the same source clip.
    picked, groups, per_src = [], set(), {}
    for sc, r in cands:
        g = r.get('dup_group') or r['id']
        src = r['source_path']
        if g in groups or per_src.get(src, 0) >= (2 if r['kind'] == 'video_frame' else 99):
            continue
        if len(picked) >= 2 and all(p['shot_type'] == r['shot_type'] for p in picked[-2:]):
            continue
        picked.append(r)
        groups.add(g)
        per_src[src] = per_src.get(src, 0) + 1
        if len(picked) >= a.n:
            break
    for r in picked:
        print(f"{r['id']}\tq{r.get('quality')}\t{r['shot_type']:<7}\t{r['ripple_ring']:<12}\t"
              f"{r['subject'][:40]:<40}\t{r['pool_path']}")
    if a.out:
        with open(a.out, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
            w.writeheader()
            w.writerows(picked)


# ---------- ledger ----------
def cmd_use(a):
    ix = a.index
    rows = load(ix)
    by = {r['id']: r for r in rows}
    led = os.path.join(ix, 'ledger.csv')
    new = not os.path.exists(led)
    with open(led, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['date', 'id', 'used_in', 'pool_path'])
        for i in a.ids:
            r = by.get(i)
            if not r:
                print('unknown', i, file=sys.stderr)
                continue
            uses = [u for u in r.get('used_in', '').split(';') if u.strip()]
            if a.used_in not in uses:
                uses.append(a.used_in)
            r['used_in'] = ';'.join(uses)
            w.writerow([datetime.now().strftime('%Y-%m-%d'), i, a.used_in, r['pool_path']])
    save(ix, rows)
    print(f'ledger: {len(a.ids)} ids -> {a.used_in}')


# ---------- prefill ledger from content already made ----------
STEM = re.compile(r'^(DSCF\d+|_?DSC\d+|DJI_\d+_\d+|C\d{4}|IMG_\d+)', re.I)
FILM = re.compile(r'^film_(\d+)', re.I)


def tc_sec(t):
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def cmd_prefill(a):
    """Every piece folder under --content-root (one level) = one campaign. Image/video files inside it
    (except exports) are matched to index rows by camera stem, or film_<sec> to master-film frames ±3 s."""
    ix = a.index
    rows = load(ix)
    by_stem, secs = {}, []
    for r in rows:
        b = os.path.basename(r['source_path'])
        m = STEM.match(b)
        if m and r['kind'] == 'photo':
            by_stem.setdefault(m.group(1).lstrip('_').upper(), []).append(r['id'])
        m = FILM.match(b)
        if m:
            secs.append((int(m.group(1)), r['id']))
        if r['source_label'] == a.master_label and r['timecode']:
            secs.append((tc_sec(r['timecode']), r['id']))
    for piece in sorted(os.listdir(a.content_root)):
        pd = os.path.join(a.content_root, piece)
        if not os.path.isdir(pd) or piece.startswith(('_', '.')):
            continue
        ids = set()
        for root, dirs, fs in os.walk(pd):
            if re.search(r'/0?4 Export|/05 ', root):
                continue
            for f in fs:
                m = STEM.match(f)
                if m:
                    ids.update(by_stem.get(m.group(1).lstrip('_').upper(), []))
                m = FILM.match(f)
                if m:
                    t = int(m.group(1))
                    ids.update(i for x, i in secs if abs(x - t) <= 3)
        if ids:
            a.ids, a.used_in = sorted(ids), piece
            cmd_use(a)
            rows = load(ix)


# ---------- report ----------
def cmd_report(a):
    rows = load(a.index)
    from collections import Counter
    tagged = [r for r in rows if r.get('shot_type')]
    print(f'total {len(rows)} · tagged {len(tagged)} · photos {sum(r["kind"] == "photo" for r in rows)}'
          f' · video frames {sum(r["kind"] == "video_frame" for r in rows)}')
    for col in ('source_label', 'shot_type', 'ripple_ring', 'light', 'quality', 'orientation'):
        c = Counter(r.get(col) or '-' for r in (rows if col in ('source_label', 'orientation') else tagged))
        print(f'\n{col}: ' + ' · '.join(f'{k} {v}' for k, v in c.most_common()))
    tc_ = Counter(t.strip() for r in tagged for t in r.get('topic_tags', '').split(',') if t.strip())
    print('\ntopic_tags: ' + ' · '.join(f'{k} {v}' for k, v in tc_.most_common()))
    q4 = Counter(t.strip() for r in tagged if float(r.get('quality') or 0) >= 4
                 for t in r.get('topic_tags', '').split(',') if t.strip())
    print('\nq4+ by topic: ' + ' · '.join(f'{k} {v}' for k, v in q4.most_common()))
    print(f'\nused: {sum(bool(r.get("used_in")) for r in rows)} · dup groups: '
          f'{len(set(r["dup_group"] for r in rows if r.get("dup_group")))}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('index')
    sp = p.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('scan'); s.add_argument('--src', action='append', required=True)
    s.add_argument('--import-to')
    s = sp.add_parser('scenes'); s.add_argument('video'); s.add_argument('--label', required=True)
    s.add_argument('--thresh', type=float, default=0.22); s.add_argument('--every', type=float, default=8)
    s.add_argument('--min-len', type=float, default=1.0); s.add_argument('--max', type=int, default=400)
    s.add_argument('--long-edge', type=int, default=2400); s.add_argument('--log')
    s = sp.add_parser('sheets'); s.add_argument('--only', default='untagged'); s.add_argument('--per', type=int, default=20)
    s.add_argument('--label'); s.add_argument('--ids', help='comma list; makes a picks sheet in that order')
    s.add_argument('--name', help='output file stem, e.g. picks_E1')
    s = sp.add_parser('merge'); s.add_argument('files', nargs='+')
    s = sp.add_parser('select'); s.add_argument('--tags'); s.add_argument('--any'); s.add_argument('--ratio')
    s.add_argument('--n', type=int, default=8); s.add_argument('--ring'); s.add_argument('--min-q', type=float, default=3)
    s.add_argument('--allow-used', action='store_true'); s.add_argument('--out')
    s = sp.add_parser('use'); s.add_argument('ids', nargs='+'); s.add_argument('--in', dest='used_in', required=True)
    s = sp.add_parser('prefill'); s.add_argument('--content-root', required=True)
    s.add_argument('--master-label', default='master-film')
    sp.add_parser('report')
    a = p.parse_args()
    os.makedirs(a.index, exist_ok=True)
    {'scan': cmd_scan, 'scenes': cmd_scenes, 'sheets': cmd_sheets, 'merge': cmd_merge,
     'select': cmd_select, 'use': cmd_use, 'prefill': cmd_prefill, 'report': cmd_report}[a.cmd](a)


if __name__ == '__main__':
    main()
