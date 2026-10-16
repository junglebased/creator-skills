---
name: visual-index
description: Brand- and project-agnostic visual pool for any content (films, client work, brand posts, LinkedIn, decks). Index ALL visual material of a production (photos + frame grabs cut from videos at scene changes, on the Mac, external disks or a synced Drive folder) into one searchable pool, tag every still (shot type, subject, topic, ripple ring, emotion, light, cinematic quality 1–5, crop fit, text-safe area), then pick visuals for a carousel/reel/cover by topic fit with no-repeat + diversity rules and a used-in ledger. Use BEFORE producing any content from a film or shoot, and whenever the user says "/visual-index", "görsel havuz", "görsel indeksle", "kare çıkar", "frame grab", "hangi görseli kullanayım", "aynı görseller tekrar ediyor", "görsel seç", "contact sheet", or hands over a production folder and asks for visuals for a post.
---

# visual-index

Principle (Berkay, 16 Oct 2026): **index everything first, then choose.** No content is produced from a
handful of familiar shots. Every quality cinematic image is seen once, scored, tagged by topic, and
every use is written to a ledger so the same frame does not carry five posts.

Works for any brand and any production: one index per production (a film, a client shoot, a brand
library), parameters = project root, sources, brand, target formats. One **cross-project ledger** is
shared by all indexes, so a frame used in a client deck is also "used" for the brand's own posts.

Pipeline position (Content Factory): `brief → source-gate → **visual-index → visual-select** → copy → design → caption/CTA → QA → publish-pack`.

## Hard rules
1. **Source media is read-only.** Never move, rename, re-encode in place or delete originals. Premiere/Resolve
   project folders and camera cards are read-only. The script only opens sources as input.
2. Everything written goes to the production's index folder (`<pool>/_Visual Index/`) or, for imports from
   external disks, to JPG copies (long edge 2400, q85) inside the pool. English `YYYYMMDD` names for new files.
   Never overwrite: new version = new file.
3. Heavy work (vision tagging, scanning many folders) runs in **Sonnet/Haiku subagents**, ≤6 contact sheets
   (≈120 stills) per agent. Main thread only merges and decides.
4. Consent: people and files on the production's no-go list (write it at the top of `topics.md`; also
   licence-unclear media) get `consent: no` and are never selected.
5. A frame is never chosen without being in the index. If a needed topic has no q≥3 frame, say so (gap) and
   propose a shoot or a frame grab; do not stretch a weak image.

## Files (per production)
```
<pool>/_Visual Index/
  config.json         {"prefix": "MO", "production": "..."}
  topics.md           production topic tags (on top of the generic ones)
  index.csv           one row per still (schema below)
  ledger.csv          date, id, used_in, pool_path  (append-only)
  TAGGING-PROMPT.md   the exact prompt given to tagging subagents
  thumbs/<id>.jpg     640 px previews
  frames/<label>/     frame grabs from video, <label>_<HH-MM-SS.mmm>.jpg, long edge 2400
  sheets/             contact sheets, 20 per sheet, labelled with ids
  tags/*.json         raw tagging output per batch (merged into index.csv)
```
Script: `scripts/vindex.py` (Python 3 + Pillow + ffmpeg; no numpy). Run with `python3`.

### index.csv columns
`id, kind (photo|video_frame), source_label, source_path, timecode, pool_path, thumb, w, h, orientation,
date, camera, brightness, sharpness, dhash, dup_group` (automatic) ·
`shot_type, subject, action, topic_tags, ripple_ring, emotion, light, quality, crop_fit, text_safe, people,
consent, notes` (vision pass, vocabulary in `references/tagging-vocab.md`) · `used_in` (ledger, `;`-separated).

## Step 0 · Init (once per production)
```bash
python3 $V "<pool>/_Visual Index" init --prefix MO --production "Mikro Onarım" --brand rs \
  --formats 4:5,9:16 --global-ledger "<content-factory>/Visual Ledger/used-in.csv" [--look series.cube]
```
Creates `config.json`, folders and a `topics.md` template. Fill `topics.md` (what each topic must show + the
no-go list) before tagging. Prefix = short code per production (MO, SF, DC01…); ids stay stable forever.
The global ledger path is the same for every production of the user.

## Step 1 · Inventory (5 min, before anything else)
List every place the production's visuals live and write it into the audit: pool folders, existing contact
sheets/indexes (improve them, don't replace), master film export, interview + b-roll clips, external disks
(check `/Volumes`, and footage manifests in `Agentic OS/03 Reports/*Footage Manifest.csv`). Count per source.
Note which sources are NOT yet in the pool (typical gap: workshop/event photos left on the SSD).

## Step 2 · Build the index
```bash
V=<skill>/scripts/vindex.py; IX="<pool>/_Visual Index"
echo '{"prefix":"MO"}' > "$IX/config.json"
# photos already on the Mac
python3 $V "$IX" scan --src "macro-2026=<pool>/2026-10-02 Makro Bahçe" --src "archive-2023=<pool>/Arşiv 2023-24 Foto - Fuji"
# photos on an external disk -> JPG copies into the pool
python3 $V "$IX" scan --import-to "<pool>/Archive 2024 Workshop" --src "workshop-fuji=/Volumes/SSD/.../Photos - Fuji"
# master film: scene detection + best-of-3 sharpness pick per scene, extra pick every 8 s in long scenes
python3 $V "$IX" scenes "<master>.mp4" --label master-film --thresh 0.22 --every 8
# b-roll clips: fewer frames per clip (one clip, or a whole card/folder with skips)
python3 $V "$IX" scenes "<clip>.MP4" --label broll-<name> --every 20 --max 6
python3 $V "$IX" scenes-dir "/Volumes/SSD/<shoot>/DJIOSMO3" --label broll-2026 --skip "*0294*" --skip "*0302*"
```
- Scene threshold 0.22 suits edited films with dissolves; raw single-take clips: rely on `--every`.
- Skip interview A-roll (one static frame) except 1–2 portrait grabs; skip no-go clips.
- `dup_group` (dHash ≤6 bits) clusters bursts and repeated scenes automatically.
- Long scans: run in background (`run_in_background`), they print progress every 50 files.

## Step 3 · Contact sheets + vision tagging
```bash
python3 $V "$IX" sheets --only untagged      # 20 per sheet, ids printed under each tile
```
Spawn Sonnet subagents in parallel (Agent tool, background), each with ≤6 sheets and the prompt in
`TAGGING-PROMPT.md` (template: `references/tagging-prompt.md`). Each writes `tags/tags_<first>-<last>.json`.
Then merge and check coverage:
```bash
python3 $V "$IX" merge "$IX"/tags/*.json
python3 $V "$IX" report      # counts by source, shot type, ring, light, quality, topic; q4+ per topic
```
Spot-check 10 random rows against thumbs. If an agent was lenient (many 5s), re-rate that batch.

**Pre-fill the ledger** from content already made, otherwise "no repeat" starts blind:
```bash
python3 $V "$IX" prefill --content-root "<film>/06 Content"   # each piece folder = one campaign
```
It matches camera stems (DSCF6458…, _DSC4198…, DJI_…) and `film_<seconds>` stills to master-film frames
(±3 s). Exports are ignored (they are the same images). Check the result with `report` (`used:` line).

## Step 4 · Select for a piece (visual-select)
Write the slot list first (from the brief): slot → what the slide must SHOW (topic tags), ratio, text area.
```bash
python3 $V "$IX" select --tags burhan-portrait --ratio 4:5 --min-q 4 --n 5          # cover candidates
python3 $V "$IX" select --any layer-carbon,layer-compost,omb-bed-build --ratio 4:5 --n 6
python3 $V "$IX" select --any workshop,participants --ring aile-komsu --ratio 4:5 --n 4
```
Ranking = quality×2 + topic matches + ratio fit + sharpness; already-used frames are excluded
(`--allow-used` re-admits them with a penalty).

**Diversity rules (apply across the whole piece, not per slot):**
- Max 1 frame per `dup_group` and max 2 frames per source video clip in one piece.
- Never 3 consecutive slides with the same `shot_type`; a carousel mixes at least 3 shot types
  (e.g. wide/aerial for place, medium for person, detail/macro for proof).
- Max 40% of slides from one shoot/source_label; at least one archive (film era) and one recent frame
  when the story spans time ("3 years later").
- Cover = q5 (q4 only if no q5 fits); face or hands, `text_safe` matching the headline position.
- Ripple slide uses the ring it talks about (`kisi` → `aile-komsu` → `koy-ekosistem`), never the cover image.
- A frame used in the last 30 days on the same channel is not reused; a HERO may appear at most once per
  campaign (E1–E5 = one campaign).
- Prefer text_safe areas over adding dark gradients; if `text_safe: none`, use it as a video/full-bleed slide
  without text.

Output a selection table: `slot · id · thumb · why (topic/quality/ratio) · crop note · alternates (2 ids)`.
Show it to the user as a contact sheet of the picks, in slot order:
`vindex.py "$IX" sheets --only all --ids MO-0319,MO-0013,... --name 20261016_picks_E1`.
Look at the sheet yourself before sending (tags can be wrong; the eye decides).
After the user approves, copy picks into the piece's `01 Kaynak Görsel/` (crop with `RS/_Araçlar/merkez_kirp.py`
or the design step) and **write the ledger**:
```bash
python3 $V "$IX" use MO-0123 MO-0456 --in "2026-10 E1 OMB carousel"
```

## Step 4b · Series look (one grade for the whole piece)
All frames of one carousel/reel (photos, video frames, film stills) pass through **one series look**: the same
`.cube`, white-balance target, contrast and saturation. Mixed sources without it look like a collage
(e.g. an ungraded pale tomato next to a graded film still).
1. Log sources (Fuji F-Log2, S-Log, D-Log) first get their technical conversion LUT (`--pre-lut ID=...`),
   Rec709 sources (film masters, JPGs) do not. Never put a log LUT on a Rec709 image.
2. Then the series look (`--lut look.cube`, or `look` in config.json). The look belongs to the piece or
   campaign; save it next to the piece (`03 Tasarım/look/<campaign>.cube`) and reuse it for every slide and
   the video slot (Resolve/ffmpeg use the same file).
3. `vindex.py "$IX" grade <ids in slot order> --lut <look.cube> [--pre-lut MO-0042=flog2_to_709.cube] --out "<piece>/01 Kaynak Görsel/graded"`
   writes graded JPGs (never overwrites) and `compare_<time>.jpg`: before row / after row, side by side.
4. Check the compare grid before design: skin tones, greens, blacks consistent across all slides; one outlier
   = adjust that frame's exposure/WB first, not the look.

## Step 5 · Audit report (what to send the user)
Short, in their language: counts per source; coverage per topic (q3+/q4+); gaps (topics with 0–2 good frames);
quality issues (soft, burnt-in subtitles, low-res, consent); top candidates for the piece in hand.

## Gotchas
- HEIC via `sips` can fail inside the sandbox; such files are skipped with a message — convert them outside or
  ignore if they are phone screenshots.
- Film master frames may carry burnt-in subtitles/titles → tagged `burnt-in text`, quality 1, never selected.
- Vertical clips (1728×3072) yield portrait frames; they fit 9:16 and 4:5 without cropping.
- `crop_fit` from the scan is resolution-only; the vision pass replaces it with subject-aware fit.
- Thumbnails are for choosing; design always uses `pool_path` (2400 px or source).
- Every subcommand rewrites `index.csv`: never run two at once on the same index (a long `scenes` run
  and a `merge` would overwrite each other). To work while a build runs, copy the index to a scratch
  folder, merge/select there, and redo the merge on the real index when the build ends.
- `scenes` on a 4K master is slow (~4 seeks per pick): ~15 s per frame. Start it first, in background.
- Vision agents are lenient on consent and sometimes on quality: spot-check q5s and every frame with people.
