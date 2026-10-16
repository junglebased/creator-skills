# Vision tagging prompt (reuse per batch; replace {SHEETS})

You are tagging stills for a documentary visual index (film "Mikro Onarım", protagonist Burhan Eltan, regenerative micro-garden (OMB), Kaz Dağları, Türkiye).

Read first: ~/code/creator-skills/.claude/worktrees/visual-index/skills/visual-index/references/tagging-vocab.md (field rules + quality rubric) and <pool>/_Visual Index/topics.md (production topic tags). Use ONLY those values.
Then use <pool>/_Visual Index/index.csv only for id, kind, source_label, source_path, timecode (filenames often carry hints like "burhan-patlican-hasat_HERO" or "kompost"; trust them for subject names). Do not print the whole CSV; grep the ids you need.

Your contact sheets (in <pool>/_Visual Index/sheets/): {SHEETS}. Each sheet = up to 20 thumbnails labelled id + orientation letter. View every sheet with the Read tool. If a tile is too small to judge, open <pool>/_Visual Index/thumbs/<id>.jpg (640px).

For EVERY id on your sheets write one JSON object (schema in vocab). Be strict on quality (most frames are 3; 5 only for true cover-grade). Burhan = man ~50, often flat cap, plaid shirt, sometimes glasses; in older archive may appear without cap. Unsure who → unknown:N. Workshop 2024 = group of participants building beds together in Ayvalık. Note burnt-in text, near-duplicates ("near-dup of MO-xxxx"), soft focus.

Write with the Write tool to <pool>/_Visual Index/tags/tags_<first>-<last>.json as a JSON array (valid JSON only). Return ≤6 lines: count, #q5/#q4, best cover candidates (ids + why), gaps seen.
