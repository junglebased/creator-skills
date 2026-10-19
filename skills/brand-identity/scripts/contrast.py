#!/usr/bin/env python3
"""WCAG contrast check for brand.json. Usage: contrast.py brand.json  (exit 1 on failure)."""
import json, sys

def lum(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c*2 for c in h)
    r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    f = lambda c: c/12.92 if c <= .03928 else ((c+.055)/1.055)**2.4
    return .2126*f(r) + .7152*f(g) + .0722*f(b)

def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la+.05)/(lb+.05)

def main(p):
    d = json.load(open(p))
    v = d.get('visual', {})
    col = {c['token']: c['hex'] for c in v.get('colors', [])}
    bad = 0
    for pr in v.get('pairs', []):
        fg, bg = col.get(pr['fg']), col.get(pr['bg'])
        if not fg or not bg:
            print(f"MISSING token in pair {pr}"); bad += 1; continue
        need = 3.0 if pr.get('size') == 'large' else 4.5
        r = ratio(fg, bg)
        ok = r >= need
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'} {pr['fg']} on {pr['bg']}: {r:.2f}:1 (need {need})")
    if not v.get('pairs'): print("no pairs declared: add visual.pairs")
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main(sys.argv[1])
