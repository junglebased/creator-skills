#!/usr/bin/env python3
"""cf-publish-pack: build 05 Yayın.md (paste-ready block + links + checklist) for one piece.

  publish_pack.py PIECE_DIR [--code E1] [--design-url URL] [--viewer-url URL]
                  [--channel instagram] [--when "2026-10-16 19:00"] [--index VISUAL_INDEX_DIR]

Reads slides.json, caption.md, latest QA*.md, 04 Export/*.png. Never overwrites (05 Yayın-v2.md ...).
With --index it prints the visual-index `use` command for the ledger (it does not write the ledger itself:
that happens after the user confirms the post is live).
"""
import argparse, glob, json, os, re
from datetime import datetime


def find(piece, *names):
    for n in names:
        p = os.path.join(piece, n)
        if os.path.exists(p):
            return p
    return None


def section(md, name):
    m = re.search(rf'^## {name}\s*\n(.*?)(?=^## |\Z)', md, re.S | re.M)
    return m.group(1).strip() if m else ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('piece'); ap.add_argument('--code'); ap.add_argument('--design-url', default='')
    ap.add_argument('--viewer-url', default=''); ap.add_argument('--channel', default='instagram')
    ap.add_argument('--when', default=''); ap.add_argument('--index')
    a = ap.parse_args()
    piece = a.piece.rstrip('/')
    txt = find(piece, '02 Metin', '02 Copy') or piece
    sj = sorted(glob.glob(os.path.join(txt, f'{a.code or "*"}.slides.json')))
    data = json.load(open(sj[0], encoding='utf-8')) if sj else {}
    code = a.code or data.get('code', 'piece')
    capf = sorted(glob.glob(os.path.join(txt, f'{code}.caption.md')) or glob.glob(os.path.join(txt, '*.caption.md')))
    cap = open(capf[0], encoding='utf-8').read() if capf else ''
    exp = find(piece, '04 Export') or piece
    pngs = sorted(glob.glob(os.path.join(exp, f'{code}_*.png'))) or sorted(glob.glob(os.path.join(exp, '*.png')))
    qas = sorted(glob.glob(os.path.join(exp, 'QA*.md')), key=os.path.getmtime)
    qa = open(qas[-1], encoding='utf-8').read() if qas else ''
    m = re.search(r'\*\*(\d+) FAIL · (\d+) WARN', qa)
    fails, warns = (int(m.group(1)), int(m.group(2))) if m else (None, None)

    caption = section(cap, 'Caption')
    tags = section(cap, 'Hashtags')
    cta = section(cap, 'CTA')
    kw = re.search(r'keyword:\s*(\S+)', cta)
    dm = re.search(r'dm_text:\s*(.+)', cta)
    status = ('READY' if fails == 0 else f'BLOCKED: {fails} FAIL in QA') if fails is not None else 'NO QA RUN'

    lines = [f'# Yayın · {code} · {data.get("campaign", "")}', '',
             f'**Durum:** {status}' + (f' · {warns} WARN' if warns else ''),
             f'**Kanal:** {a.channel}' + (f' · **Zaman:** {a.when}' if a.when else ''), '',
             '## Linkler',
             f'- Claude Design canvas: {a.design_url or "[DESIGN URL?]"}',
             f'- Swipe görünümü (launch=focused): {a.viewer_url or "[VIEWER URL?]"}',
             f'- Export klasörü: {exp} ({len(pngs)} PNG)',
             f'- QA: {qas[-1] if qas else "[QA yok: cf-qa çalıştır]"}', '',
             '## Yapıştır · caption', '```', caption + ('\n\n' + tags if tags else ''), '```', '',
             '## DM aracı (ManyChat vb.)',
             f'- Tetikleyici kelime: **{kw.group(1) if kw else "[KEYWORD?]"}**',
             f'- İlk DM: {dm.group(1).strip() if dm else "[DM?]"}', '',
             '## Slayt sırası']
    for s in data.get('slides', []):
        head = ' / '.join(s.get('headline') or [])
        lines.append(f'{s.get("n")}. {s.get("role", "")} · {s.get("visual", "")} · {head}')
    lines += ['', '## Kontrol listesi (yayından hemen önce)',
              '- [ ] QA 0 FAIL; WARN\'lar okundu',
              '- [ ] Telefonda Swipe görünümünde baştan sona kaydırıldı',
              '- [ ] Görsellerdeki kişilerin izni teyitli (QA consent satırları)',
              '- [ ] DM aracında tetikleyici kelime ve link canlı test edildi (kendi hesabından yorum)',
              '- [ ] Caption\'daki rakamlar sources.md ile aynı',
              '- [ ] Collab ise ortak hesap daveti / ortak caption hazır',
              '- [ ] Yayından sonra: ledger yazıldı (aşağıdaki komut), 48 saat ölçüm notu']
    if a.index and data.get('slides'):
        ids = [s['visual'] for s in data['slides'] if s.get('visual', '').startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) and '-' in s.get('visual', '') and not s['visual'].startswith('clip:')]
        lines += ['', '## Ledger (yayın canlı olunca)', '```',
                  f'python3 <visual-index>/scripts/vindex.py "{a.index}" use {" ".join(ids)} --in "{data.get("campaign", code)}"',
                  '```']
    out = os.path.join(piece, '05 Yayın.md')
    k = 1
    while os.path.exists(out):
        k += 1
        out = os.path.join(piece, f'05 Yayın-v{k}.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(out, '·', status)


if __name__ == '__main__':
    main()
