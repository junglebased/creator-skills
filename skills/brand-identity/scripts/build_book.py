#!/usr/bin/env python3
"""brand.json -> brand-book.html (A4, one section per page) + brand-kit.md. Usage: build_book.py brand.json outdir/"""
import json, os, sys, html

def e(x): return html.escape(str(x or ""))
def ul(items): return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>" if items else ""

def table(head, rows):
    if not rows: return ""
    return "<table><tr>" + "".join(f"<th>{e(h)}</th>" for h in head) + "</tr>" + \
        "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) + "</table>"

def build(d):
    p, a, v, vis = d.get('positioning', {}), d.get('archetype', {}), d.get('voice', {}), d.get('visual', {})
    cols = vis.get('colors', [])
    C = {c['token']: c['hex'] for c in cols}
    ink = C.get('ink', '#111'); paper = C.get('paper', '#fff')
    accent = next((c['hex'] for c in cols if c['token'] not in ('ink', 'paper')), '#c00')
    types = vis.get('type', [])
    head_font = next((t['font'] for t in types if t['layer'].startswith('head')), 'Georgia')
    body_font = next((t['font'] for t in types if t['layer'].startswith('body')), 'system-ui')
    secs = []  # (title, body)
    def add(title, body):
        if body.strip(): secs.append((title, body))

    add("Story and belief", (f"<p class='lead'>{e(d.get('belief'))}</p>" if d.get('belief') else "") + (f"<p>{e(d.get('story'))}</p>" if d.get('story') else ""))
    add("Positioning", (f"<p class='lead'>{e(p.get('plain'))}</p>" if p.get('plain') else "") + (f"<p>{e(p.get('statement'))}</p>" if p.get('statement') else "") +
        (f"<h3>Promise</h3><p>{e(p.get('promise'))}</p>" if p.get('promise') else "") +
        (f"<h3>Frame</h3><p>{e(p.get('frame'))}</p>" if p.get('frame') else ""))
    ar = d.get('architecture')
    if ar: add("Brand architecture", f"<p class='lead'>Model: {e(ar.get('model'))}</p><h3>Shared</h3>{ul(ar.get('shared'))}<h3>Differs</h3>{ul(ar.get('differs'))}<p>{e(ar.get('usage'))}</p>")
    add("Audience and proof", (f"<h3>Best-fit audience</h3><p>{e(p.get('audience'))}</p>" if p.get('audience') else "") +
        (f"<h3>Alternatives today</h3>{ul(p.get('alternatives'))}" if p.get('alternatives') else "") +
        (f"<h3>Proof</h3>" + table(["Claim", "Evidence", "Source"], [[x.get('claim'), x.get('evidence'), x.get('source')] for x in p.get('proof', [])]) if p.get('proof') else ""))
    add("Values and personality", (table(["Value", "Behaviour"], [[x.get('name'), x.get('behaviour')] for x in p.get('values', [])]) if p.get('values') else "") +
        (f"<h3>Archetype</h3><p><b>{e(a.get('primary'))}</b> with shadow {e(a.get('shadow'))}. {e(a.get('why'))}</p>{ul(a.get('example_lines'))}" if a else "") +
        (f"<h3>Not</h3>{ul(p.get('not'))}" if p.get('not') else ""))
    add("Voice", table(["Word", "Means", "Do", "Don't"], [[x.get('word'), x.get('meaning'), x.get('do'), x.get('dont')] for x in v.get('adjectives', [])]) + ul(v.get('habits')))
    add("Tone map", table(["Context", "Tone", "Opening line"], [[x.get('context'), x.get('tone'), x.get('opening')] for x in v.get('tone_map', [])]))
    pt = v.get('pitches', {})
    add("Messaging", (f"<h3>Tagline</h3><p class='lead'>{e(d.get('tagline'))}</p>" if d.get('tagline') else "") +
        (f"<h3>Alternatives</h3>{ul(d.get('tagline_alts'))}" if d.get('tagline_alts') else "") +
        "".join(f"<h3>{n}</h3><p>{e(pt.get(k))}</p>" for k, n in (("s10", "10 seconds"), ("s30", "30 seconds"), ("s60", "60 seconds")) if pt.get(k)) +
        (table(["Pillar", "Message", "Proof"], [[x.get('theme'), x.get('message'), x.get('proof')] for x in v.get('pillars', [])]) if v.get('pillars') else "") +
        (f"<h3>Banned</h3><p>{e(', '.join(v.get('banned', [])))}</p>" if v.get('banned') else ""))
    lg = vis.get('logo', {})
    add("Logo brief", (table(["Route", "Expresses"], [[x.get('idea'), x.get('expresses')] for x in lg.get('routes', [])]) if lg.get('routes') else "") +
        (f"<h3>Rules</h3>{ul(lg.get('rules'))}" if lg.get('rules') else "") + (f"<h3>Misuse</h3>{ul(lg.get('misuse'))}" if lg.get('misuse') else "") +
        (f"<h3>Deliverables</h3>{ul(lg.get('deliverables'))}" if lg.get('deliverables') else ""))
    sw = "".join(f"<div class='sw'><div class='chip' style='background:{e(c['hex'])}'></div><b>{e(c['token'])}</b><br>{e(c['hex'])}<br><small>{e(c.get('role'))} {e(c.get('share'))}</small></div>" for c in cols)
    add("Colour", f"<div class='swatches'>{sw}</div>" if cols else "")
    add("Type", table(["Layer", "Font", "Fallback", "Note"], [[t.get('layer'), t.get('font'), t.get('fallback'), t.get('note')] for t in types]) +
        (f"<p class='spec' style='font-family:\"{e(head_font)}\",serif;font-size:30pt'>{e(d.get('name'))}</p><p class='spec' style='font-family:\"{e(body_font)}\",sans-serif'>The quick brown fox jumps over the lazy dog.</p>" if types else ""))
    add("Imagery, motion, layout", "".join(f"<h3>{t}</h3>{ul(vis.get(k))}" for k, t in (("imagery", "Imagery"), ("motion", "Motion"), ("layout", "Layout")) if vis.get(k)))
    add("Do and don't", (f"<h3>Do</h3>{ul(d.get('dos'))}" if d.get('dos') else "") + (f"<h3>Don't</h3>{ul(d.get('donts'))}" if d.get('donts') else ""))
    add("Next steps", ul(d.get('next_steps')) + (f"<h3>Open (TODO)</h3>{ul(d.get('todo'))}" if d.get('todo') else "") + (f"<h3>Sources</h3>{ul(d.get('sources'))}" if d.get('sources') else ""))

    toc = "".join(f"<li>{e(t)}</li>" for t, _ in secs)
    pages = [f"<section class='page cover'><div><p class='kicker'>Brand book · {e(d.get('date'))}</p><h1>{e(d.get('name'))}</h1><p class='lead'>{e(d.get('tagline'))}</p></div></section>",
             f"<section class='page'><h2>Contents</h2><ol>{toc}</ol><p class='small'>One section per page. Facts carry source tags. Draft items are marked TODO.</p></section>"]
    pages += [f"<section class='page'><h2>{e(t)}</h2>{b}</section>" for t, b in secs]
    fonts = "&family=".join(f.replace(' ', '+') for f in {head_font, body_font})
    css = f"""@page{{size:A4;margin:0}}
:root{{--ink:{ink};--paper:{paper};--accent:{accent}}}
*{{box-sizing:border-box}}html,body{{margin:0;background:#888}}
body{{font:11pt/1.5 "{body_font}",system-ui,sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:210mm;height:297mm;padding:20mm;background:var(--paper);overflow:hidden;break-after:page;break-inside:avoid;margin:0 auto 8mm;position:relative}}
.page:last-child{{break-after:auto}}
.page:before{{content:"";position:absolute;left:20mm;top:12mm;width:16mm;height:2mm;background:var(--accent)}}
h1,h2,h3{{font-family:"{head_font}",Georgia,serif;font-weight:400;margin:0}}
h1{{font-size:44pt;line-height:1.05;margin:0 0 8mm}}h2{{font-size:26pt;margin:6mm 0 8mm}}h3{{font-size:13pt;margin:6mm 0 2mm;color:var(--accent)}}
.lead{{font-size:15pt;line-height:1.35}}.kicker,.small,small{{opacity:.65;font-size:9pt}}
.cover{{display:flex;align-items:flex-end;background:var(--ink);color:var(--paper)}}.cover .lead{{opacity:.85}}
table{{width:100%;border-collapse:collapse;font-size:10pt;break-inside:avoid}}th,td{{text-align:left;vertical-align:top;padding:2.5mm 3mm;border-bottom:.3mm solid rgba(128,128,128,.4)}}
th{{font-size:8.5pt;text-transform:uppercase;letter-spacing:.06em;opacity:.7}}
ul,ol{{padding-left:5mm}}li{{margin:1mm 0}}
.swatches{{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}}.chip{{height:24mm;border:.3mm solid rgba(128,128,128,.4);margin-bottom:2mm}}
@media screen{{.page{{box-shadow:0 2px 12px rgba(0,0,0,.3)}}body{{padding:8mm 0}}}}"""
    doc = f"<!doctype html><html lang='{e(d.get('language', 'en'))}'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{e(d.get('name'))} Brand Book</title><link rel='stylesheet' href='https://fonts.googleapis.com/css2?family={fonts}&display=swap'><style>{css}</style></head><body>{''.join(pages)}</body></html>"
    return doc

def kit(d):
    p, a, v, vis = d.get('positioning', {}), d.get('archetype', {}), d.get('voice', {}), d.get('visual', {})
    L = [f"# Brand kit — {d.get('name')}   (generated by brand-identity, {d.get('date')})", "", "## Identity",
         f"- What you make / for whom: {p.get('audience') or 'TODO(ask)'}",
         f"- Positioning (one sentence): {p.get('plain') or p.get('statement') or 'TODO(ask)'}",
         f"- Content pillars + mix: {'; '.join(x.get('theme','') for x in v.get('pillars', [])) or 'TODO(ask)'}",
         f"- Your 10x layer: {p.get('promise') or 'TODO(ask)'}",
         "- Facts the model may use (story beats, awards, numbers WITH sources): " + ("; ".join(f"{x.get('claim')} [{x.get('source')}]" for x in p.get('proof', [])) or "TODO(ask)"),
         "", "## Voice", f"- 3 adjectives: {', '.join(x.get('word','') for x in v.get('adjectives', [])) or 'TODO(ask)'}",
         f"- Language(s): {d.get('language') or 'TODO(ask)'}",
         f"- Banned words / punctuation: {', '.join(v.get('banned', [])) or 'TODO(ask)'}",
         f"- Emoji policy: {next((h for h in v.get('habits', []) if 'emoji' in h.lower()), 'TODO(ask)')}",
         "", "## CTA per pillar", "| pillar | comment keyword | lead magnet / destination |", "|---|---|---|"]
    L += [f"| {x.get('theme')} | TODO(ask) | TODO(ask) |" for x in v.get('pillars', [])]
    L += ["", "## Color", "| token | hex | use |", "|---|---|---|"] + [f"| {c['token']} | {c['hex']} | {c.get('role','')} |" for c in vis.get('colors', [])]
    L += ["", "## Type", "| layer | font | note |", "|---|---|---|"] + [f"| {t['layer']} | {t['font']} | {t.get('note','')} |" for t in vis.get('type', [])]
    L += ["", "## Visual rules", f"- Logo / handle badge: {'; '.join(vis.get('logo', {}).get('rules', [])) or 'TODO(ask)'}",
          f"- Photo style (and what's banned): {'; '.join(vis.get('imagery', [])) or 'TODO(ask)'}",
          f"- Grain / overlays / counters: {'; '.join(vis.get('motion', [])) or 'TODO(ask)'}", ""]
    return "\n".join(L)

if __name__ == '__main__':
    d = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'brand-book.html'), 'w', encoding='utf-8').write(build(d))
    open(os.path.join(out, 'brand-kit.md'), 'w', encoding='utf-8').write(kit(d))
    print("wrote brand-book.html, brand-kit.md in", out)
