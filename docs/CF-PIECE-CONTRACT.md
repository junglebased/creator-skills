# Content Factory · piece contract (files every CF skill reads and writes)

One piece = one folder. Every step reads the previous step's files and writes its own; nothing is passed
only in chat. Brand-agnostic: brand data comes from the brand kit, production data from the visual index.

```
<content root>/<YYYY-MM> <Format> - <Topic>/        e.g. 06 Content/202610 E1 RS OMB v5/
  01 Kaynak Görsel/        picks copied from the pool (+ graded/ from visual-index grade)
  02 Metin/
    <code>.brief.md        cf-brief      goal, funnel stage, reference format, slot list, CTA, measure
    <code>.sources.md      cf-source-gate claims table (claim · source · locator · status)
    <code>.slides.json     cf-copy       per-slide text with MANUAL line breaks + visual id   ← the contract
    <code>.caption.md      cf-caption-cta caption, hashtags, CTA keyword, DM text
  03 Tasarım/              cf-design     Claude Design canvas link, look/<campaign>.cube, renderer source
  04 Export/<code>_NN.png  cf-design     1080×1350 (or brand format), NN = 01..
  04 Export/QA.md          cf-qa         PASS / WARN / FAIL per check
  05 Yayın.md              cf-publish-pack paste-ready block + links + checklist
```
(Existing folders may use English names `01 Source`, `02 Copy`, `03 Design`, `04 Export`, `05 Publish.md`;
skills accept both.)

## `<code>.slides.json`
```json
{
  "code": "E1",
  "campaign": "2026-10 E1 OMB",
  "brand": "rs",
  "format": "carousel-4:5",
  "cta_keyword": "OMB",
  "look": "03 Tasarım/look/20261016 E1 look.cube",
  "slides": [
    {"n": 1, "role": "cover",
     "headline": ["Gıda ihtiyacı karşılanmaz.", "Ama sebze ihtiyacı", "karşılanır."],
     "body": ["Burhan Eltan · 30 m² bahçesi için, 2026"],
     "visual": "MO-0017", "text_pos": "bottom", "sources": ["Q1"]},
    {"n": 3, "role": "video", "visual": "clip:DSCF6415@00:00:12-00:00:18", "headline": [], "body": []}
  ]
}
```
- `headline` / `body` are arrays of lines: the line breaks ARE the design (R1). No line is wrapped later.
- `visual` = visual-index id (`MO-0017`) or `clip:<file>@in-out` for video slots.
- `sources` = ids from `<code>.sources.md`; every number/quote on a slide needs one.
- `role` ∈ cover · promise · proof · step · quote · ripple · close · cta · video.

## `<code>.caption.md`
```
## Caption
<text, paste-ready>
## Hashtags
#a #b #c
## CTA
keyword: OMB
manychat_trigger: OMB
dm_text: <first DM, with the link placeholder {link}>
```

## Brand kit fields the skills use (`brands/<code>.md`)
`chars_per_line` (headline / body), `max_hashtags`, `max_emoji`, `banned_words`, `banned_punctuation`,
`cta_default`, `format` sizes, fonts, colours, logo. Missing field → the skill asks once.
