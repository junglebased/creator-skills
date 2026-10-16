# Tagging vocabulary (vision pass)

One JSON object per still. Use ONLY these values (topic tags: add a production-specific
list in the index folder's `topics.md`; the generic ones below always apply).

```json
{"id": "MO-0042",
 "shot_type": "close",
 "subject": "Burhan's hands lifting compost",
 "action": "turning compost",
 "topic_tags": ["compost-make", "soil-hands"],
 "ripple_ring": "kisi",
 "emotion": "focus",
 "light": "golden",
 "quality": 4,
 "crop_fit": ["4:5", "1:1"],
 "text_safe": "top",
 "people": "burhan",
 "consent": "ok",
 "notes": "slight motion blur on left hand"}
```

| field | values |
|---|---|
| shot_type | `aerial` · `wide` · `medium` · `close` · `detail` · `macro` |
| subject | free text, ≤8 words, concrete nouns (who/what is in frame) |
| action | free text, ≤5 words, verb first; `-` if static |
| topic_tags | 1–4 from the topic list (generic + production `topics.md`) |
| ripple_ring | `kisi` (one person / own garden) · `aile-komsu` (family, neighbours, workshop group, people taught) · `koy-ekosistem` (village, landscape, soil life, biodiversity, region) · `none` (textures, objects) |
| emotion | `calm` · `joy` · `focus` · `pride` · `curiosity` · `warmth` · `contemplative` · `neutral` |
| light | `golden` · `daylight-soft` · `daylight-hard` · `overcast` · `shade` · `indoor` · `blue-hour` · `night` |
| quality | 1–5, see rubric |
| crop_fit | ratios where the SUBJECT survives a centred or shifted crop: `9:16` · `4:5` · `1:1` · `16:9` |
| text_safe | where clean negative space for a headline sits: `top` · `bottom` · `left` · `right` · `center` · `none` |
| people | `burhan`, `burhan+family`, `participants:N`, `unknown:N`, `none`; name known people only if visible context makes it certain |
| consent | `ok` (consented protagonist, crowd from behind, no faces) · `check` (identifiable third party, children) · `no` (known refusal list) |
| notes | defects (soft focus, blur, overexposed, text/logo in frame, watermark, duplicate of X) or a strong use idea |

## Quality rubric (cinematic, for social stills)
- **5 cover**: strong composition + intentional light + sharp subject + emotion or story in one frame. Stops the scroll alone.
- **4 slide**: clearly good; one of the above slightly weaker. Can carry a slide with text.
- **3 support**: usable, informative (shows a step), plain light or composition.
- **2 weak**: soft, cluttered, flat, awkward moment. Only if nothing else shows that step.
- **1 reject**: out of focus, motion-smeared, eyes closed, lens flare ruin, accidental frame, transition frame.

Video frames: judge the still, not the clip. Transition/dissolve frames, title cards and frames with burnt-in subtitles = 1 (note `burnt-in text`).

## Generic topic tags
`portrait` · `working` · `teaching` · `group` · `landscape` · `aerial-site` · `hands` · `tools` · `food` · `table` · `texture-bg` · `home` · `archive` · `before` · `after` · `season-spring` · `season-summer` · `season-autumn` · `season-winter`
