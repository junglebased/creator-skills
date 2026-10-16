---
name: cf-publish-pack
description: Packs one approved Content Factory piece for publishing, for any brand: writes 05 Yayın.md with status (from QA), links (Claude Design canvas, Swipe view with launch=focused, exports), the paste-ready caption + hashtags, the DM-tool keyword and first DM, slide order with visual ids, a pre-publish checklist and the visual-index ledger command to run once the post is live. Nothing is posted or scheduled. Use when the user says "/cf-publish-pack", "yayın paketi", "paste-ready", "yayına hazırla", or after cf-qa passes.
---

# cf-publish-pack

Pipeline: `… → caption/CTA → QA → **publish-pack**` (→ measure).
Contract: `docs/CF-PIECE-CONTRACT.md` · rules: `docs/CF-PRODUCTION-RULES.md`.

## Run
```bash
python3 <skill>/scripts/publish_pack.py "<piece folder>" \
  --design-url <Claude Design canvas link> --viewer-url "<link>?launch=focused" \
  --index "<pool>/_Visual Index" [--channel instagram] [--when "2026-10-16 19:00"]
```
- Status comes from the newest `04 Export/QA*.md`: `READY` only with 0 FAIL. `BLOCKED` packs are still written
  (so the user sees what is missing) but say so in the first line.
- Writes `05 Yayın.md` (never overwrites: `05 Yayın-v2.md`…).

## Rules
- Agents never post, schedule, DM or upload. The pack is for the human (or an Outbox the human triggers).
- One link for review: the Swipe view of the Claude Design canvas (R2), opened with `launch=focused`.
- The ledger command is run only after the user says the post is live (then: `vindex.py use … --in
  "<campaign>"`, which also updates the cross-project ledger).
- Content Factory app Outbox (if used): copy the caption block and status into the draft; state flow
  ready → copied → posted is the user's.
- After publishing: note the post URL and time under `## Yayında` in the same file; 48 h metrics go to
  cf-measure (`_performance.csv` of /formula).
