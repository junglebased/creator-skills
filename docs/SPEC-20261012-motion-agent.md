# SPEC: Motion agent (Claude skill for animated carousels and reels, RS + JB)

Date: 2026-10-12 · Status: draft for Berkay's review · Branch: `claude/motion-agent-spec` (not merged)
Reference analysis: `docs/ANALYSIS-20261012-ig-DeZYQm2iPvw.md`

## Assumptions (Berkay was on his phone, so no questions were asked)

- A1. The skill lives in this repo as `skills/motion/` (next to dl, formula, transcribe) and installs to `~/.claude/skills/motion`.
- A2. Berkay's Claude plan is not confirmed as Team/Enterprise. Claude Motion (Team/Enterprise only at launch) is therefore treated as optional, not as the core renderer.
- A3. Language: on-screen copy is EN-first for RS reels, with a TR variant per post. JB is EN.
- A4. RS brand kit values come from `~/.claude/profile/06-brand-voice.md` §9. Fonts are Fontshare (Clash Display, Satoshi, Boska, Expose), self-hosted inside each render.
- A5. Footage comes from Berkay's own RS/JB archives only. No stock, no AI-generated people.

## 1. Role

A motion designer agent that turns **one sourced fact or one story beat** into a 6-12 s looping motion piece in RS or JB identity. Like the reference post, it follows a **locked brief per brand** plus **one scene line**, so every output looks like the same studio made it. It writes HTML/CSS/JS compositions, renders MP4s, assembles carousels and reels, and runs a QA pass (craft + Greenshouting) before handing over drafts. It never publishes.

## 2. Inputs

| Input | Required | Example |
|---|---|---|
| `brand` | yes | `rs` or `jb` |
| `preset` | yes | one id from §4 |
| `scene` | yes | one line: "<object> → <change>", e.g. "30 m² bed → feeds a family" |
| `facts[]` | for RS, yes | each with value, unit, scope, date, source (URL/Notion/transcript timecode), wording |
| `footage[]` | optional | clip path + in/out timecode (documentary plate) |
| `quote` | optional | verbatim line + speaker + transcript timecode |
| `format` | yes | `carousel-4x5` (1080×1350) and/or `reel-9x16` (1080×1920) |
| `slides` | carousel only | 3-10 scene lines |

## 3. Outputs

- `out/<YYYYMMDD>-<slug>/` containing:
  - `scene-NN.html` (the source composition, re-renderable)
  - `scene-NN-1080x1350.mp4` and/or `scene-NN-1080x1920.mp4`, H.264, 30 fps, yuv420p, loop-safe
  - `cover.png` (first frame, for the carousel thumbnail and the grid)
  - `reel.mp4` (concatenated scenes + optional music bed + burnt-in captions for 9:16)
  - `caption.md` (EN + TR, one CTA, sources block)
  - `qa.md` (checklist result + Greenshouting report)
- Safe zones: 9:16 keeps text inside y 220-1520 (above the IG reel UI). 4:5 keeps 64 px side margins.

## 4. Style preset library (v1)

Every preset is a locked brief in the shape of the reference: BAR · FORMAT · ONE RULE · LOOK · TYPE · MOTION · NEVER + SCENE.

| Id | Brand | Look | Motion signature | Use for |
|---|---|---|---|---|
| `rs-field-glass` | RS | humus #181715 to mist #F3F1EB gradient, frosted "field card" over a blurred documentary still, sprout-500 #4A7A2E primary, gold #F6BF26 for one word only | springs with low bounce (damping ~0.8), slow holds (1.5 s), particles move like seeds or soil (gravity, settle) | single numbers: area, yield (attributed), views, years |
| `rs-ripple-rings` | RS | concentric rings on humus: person → family/neighbour → village/cooperative → ecosystem | each ring draws on with stroke-dasharray, one sourced number lands per ring, gentle radial pulse | the "dalga etkisi" layer, the signature RS format |
| `rs-footage-to-data` | RS | documentary plate (hands, soil) that match-cuts into a diagram of the same shape | mask reveal from footage to vector (bed outline → grid → count), lower-third quote in Boska | 10x layer, see §6 |
| `rs-map-tr` | RS | tilted, light 3D map of Türkiye, terrain relief, clay #CC7A59 pins | pin drop with squash, route or region draw-on, glass label | "where": Kaz Dağları, Tekirdağ, Istanbul; film locations |
| `jb-process-mono` | JB | ink #101417 / mist, Space Mono labels, Playfair headline, 12% grain | timeline scrubbing, frame counters, before/after wipe on a real frame | behind-the-scenes, "how this shot was built" |
| `jb-keynote-glass` | JB | the reference look re-skinned: mist background, warm-gold accent, one hero object | the full reference vocabulary (odometer, morph, snap, magnify) | tool and workflow posts, the JB lead magnet |

Shared motion tokens (in `skills/motion/tokens.css`): `--spring-soft` (stiffness 120, damping 20), `--spring-snap` (260/22), `--hold-min: 1.2s`, `--loop: 6s` (carousel) or `8s` (reel beat), per-digit odometer component, stroke draw-on, mask wipe, particle-to-target, variable-weight text.

## 5. Ripple FX: best-in-class references and what we borrow

| # | Who | Evidence | Signature technique | RS/JB adaptation |
|---|---|---|---|---|
| 1 | Apple design / keynote motion | WWDC23 "Animate with springs" https://developer.apple.com/videos/play/wwdc2023/10158/ | Springs described by duration + bounce instead of curves; one hero object; material depth (glass, shadow) | Tokens `--spring-soft/snap`; RS bounce kept low (calm, "quietly urgent") |
| 2 | Emil Kowalski (Sonner, Vaul, animations.dev) | https://animations.dev · https://emilkowal.ski | Purposeful, short motion; enter from scale 0.95 not 0; origin-aware transforms; interruptible | Every element enters from 0.95/opacity 0; labels scale from their anchor (pin, ring) |
| 3 | Rauno Freiberg (Vercel, "Invisible Details of Interaction Design") | https://rauno.me/craft/interaction-design | Motion as a physical metaphor (momentum, lag, snap); details hold up under stress | Seeds fall with gravity, soil settles, water flows: physical metaphors from the field, not from UI |
| 4 | The Pudding | https://pudding.cool | Unit visualisation (one dot = one real thing), annotation-led reveal, human-scale units | "1 dot = 1 person fed / 1 m²"; numbers always shown at human scale with scope in small text |
| 5 | Kurzgesagt | https://kurzgesagt.org | Strict palette per film, explanatory loops, rhythm locked to narration, character as entry point | One palette per RS film; reels cut on Burhan's voice (no narrator), data enters on his words |

What the reference does that none of these do: **one locked brief + one variable line** as a production system. We keep that.

**10x layer (what none of them do together):** real documentary footage of the practitioner + sourced data animated in the same frame + the ripple structure (person → community → land). Our motion explains *his* proof, not a product's metric. Each number carries its source in the frame (small, legible), so a Greenshouting-compliant post becomes a design feature, not a disclaimer.

## 6. Production pipeline recommendation

| Option | What Claude automates | 1080×1350 / 1080×1920 | Quality ceiling | Cost (approx., Oct 2026) | Verdict |
|---|---|---|---|---|---|
| **HyperFrames (HeyGen, Apache-2.0)** HTML + GSAP → headless Chrome → FFmpeg; MCP + CLI + agent skills | everything: write HTML, render, batch, re-render on fact change | any size, set per composition | high (GSAP, Three.js, Lottie, video plates) | $0 + local render time | **Primary.** Claude writes HTML best, renders are deterministic, MCP already connected in this setup (`compose`, `render_video`, `import-claude-motion-from-url`) |
| Remotion (React) | everything, same as above | any size | high; mature ecosystem, Lambda rendering | free for individuals/companies up to 3 people (JB/RS qualifies); company licence above that | **Fallback** if HyperFrames blocks on a feature; same HTML skills carry over |
| Claude Motion (claude.ai) | prompt → animation → MP4 in chat, refine by chat | 1080p presets; custom sizes by prompt | high for UI/chart explainers; no real footage | needs Team/Enterprise seat | **Ideation / one-offs.** Prototype a scene, then import into HyperFrames for brand lock and batch |
| Claude Design artifacts | static frames, covers, storyboards | yes (static) | static only | included in plan | Covers and storyboard frames only |
| After Effects template + script (ExtendScript / nexrender) | fill text/data into a hand-built template, render | yes | highest for hand-crafted motion | ~US$23-35/month Creative Cloud + build time | Only if a human motion designer joins; poor fit for agent iteration |
| Blender (MCP connected) | scene setup, camera, terrain via Python | yes | highest for 3D (terrain, map flyovers) | $0, heavy render | **Special shots only:** a Kaz Dağları terrain flyover plate rendered once, then used as a footage layer in HyperFrames |
| Canva | template fill via MCP | yes | low for motion (preset animations) | Pro ~US$15/month | Not for this goal; fine for static team use |

**Recommendation:** HyperFrames as the renderer, with a brand-locked brief per preset (the reference's trick), GSAP for springs and timelines, real footage plates and Blender only for hero 3D plates. Claude Motion is the sketchpad when a seat is available. Remotion stays the documented fallback.

## 7. QA checklist (run on every scene before hand-off)

Craft
- [ ] One hero object at 60-70% of the frame; one change; reset to the first frame (loop seam invisible).
- [ ] After-state held ≥1.2 s; total length matches the preset (6 s carousel / 8 s reel beat).
- [ ] Every movement uses spring or physics easing; no linear tweens except progress bars and counters.
- [ ] Key number ≥120 px; ≤5 words of headline per scene; text inside safe zones (9:16: y 220-1520).
- [ ] Brand palette only (≤2 colours + neutrals); gold used for one word maximum (RS).
- [ ] Fonts embedded and rendering (no fallback font on any frame); Turkish diacritics correct (ğ ş ı İ ç ö ü).
- [ ] Contrast WCAG AA for all text over footage (humus gradient behind the lower third).
- [ ] Rendered at 30 fps H.264 yuv420p, under 30 MB per scene; first frame exported as the cover.

Truth (RS Greenshouting, run `rs-greenshouting-check`)
- [ ] Every number has value, scope, date and source in `facts[]`, and a short source line is visible on screen.
- [ ] Yield, health, carbon and "feeds N people" claims are attributed to the practitioner ("Burhan's observation") unless two independent sources exist.
- [ ] Views are written as views ("viewed 250,000+ times"), never as people or "viewers reached".
- [ ] Numbers re-checked against FACTS.md within 7 days of publishing; `~` values re-read at the source.
- [ ] No banned words (06-brand-voice §5), no exclamation marks, no countdown/doom rhetoric, no em dashes in public copy.
- [ ] Quotes are verbatim with a transcript timecode.

Rights
- [ ] Only own footage, own fonts (licensed) and own logos. Nothing from reference posts.

## 8. Out of scope (v1)

- Publishing or scheduling (drafts only; Berkay posts).
- AI-generated footage or people; voice cloning; music generation (use licensed library tracks picked by Berkay).
- Long-form explainers over 60 s; YouTube 16:9 masters (later preset).
- Defrost Club and FundPilot presets (their design systems exist; add after RS/JB v1 works).
- A UI for non-technical users; the CLI/skill is the interface.

## 9. MVP: 1 template in 1 week

Done = one preset (`rs-field-glass`) renders a 5-slide RS carousel (1080×1350) and a 20-25 s reel (1080×1920) from a single `scene.yaml`, passes QA, and Berkay says "gönderilebilir".

| Day | Work | Output |
|---|---|---|
| 1 | Install HyperFrames CLI/skills; lock the `rs-field-glass` brief; tokens.css; self-host the fonts | brief + tokens committed |
| 2 | Build 3 components: odometer number, stroke draw-on area outline, particle-to-target "people" dots | components with a test render |
| 3 | Footage plate layer (blurred still + humus gradient + lower third); 4:5 and 9:16 layouts | 2 test MP4s |
| 4 | `scene.yaml` → HTML generator in the skill; batch render; cover export | first full carousel |
| 5 | QA automation (frame-0 = last-frame diff, safe-zone check, font check) + Greenshouting pass | `qa.md` |
| 6 | Mikro Onarım prototype (below), EN + TR | draft post folder |
| 7 | Buffer, Berkay's review, fixes | v0.1 tag on branch |

## 10. First prototype: Mikro Onarım

Story line: "30 m² → 4-6 people → 250K+ views". Three scenes, `rs-field-glass` (+ `rs-ripple-rings` for scene 2).

| Scene | Object → change | Motion | On-screen text (EN) | Source line |
|---|---|---|---|---|
| 1 | Burhan's hands in the bed (footage still) → the bed outline lifts off as a vector square that fills to "30 m²" | mask reveal footage → vector, stroke draw-on, odometer 0 → 30 | "30 m²" · "one garden, Kaz Dağları" | film, 2026 |
| 2 | One dot (Burhan) → ripple ring → 4-6 dots settle into the ring | ripple ring draws on, dots fall with gravity and settle | "feeds 4-6 people" · "Burhan's observation" | transcript timecode (to fill in) |
| 3 | Film frame → view counter rolls up | per-digit odometer, sprout-green progress arc | "viewed 250,000+ times" | YouTube Studio, read on DD.MM.2026 |
| CTA | Static end frame | none | "Watch the film: Rebuilt from the Ground Up" | link in bio |

Greenshouting notes for this prototype:
- "4-6 people" is not in FACTS.md as a sourced number. Show it as Burhan's observation with the transcript timecode, or drop it.
- "~250K viewers" in the brief must become "viewed 250,000+ times" and needs a fresh YouTube Studio read first (FACTS: 225,349 on 7 Oct; ~250K per Berkay on 12 Oct).
- Do not use the YouTube clickbait title in the end frame; use the locked credit title "Burhan: Rebuilt from the Ground Up".
