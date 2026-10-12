# Analysis: Instagram post DeZYQm2iPvw ("16 Claude Motion animations")

Date: 2026-10-12 · Analyst: Claude (motion-agent spec work, branch `claude/motion-agent-spec`)
Source: https://www.instagram.com/p/DeZYQm2iPvw/ · author @charliehills · posted 2026-10-12
Local media (gitignored, never committed or republished): `research/20261012-ig-DeZYQm2iPvw/`

> Reference content is for technical analysis only. Do not reuse its assets, fonts, logos, prompt text or layout 1:1.
> We take the *mechanism* (rules, timing, structure) and rebuild it in RS/JB identity.

## 1. What was downloaded

- 19 carousel slides. Every slide is a silent MP4: 1080×1350, 30 fps, exactly 6.0 s, H.264, no audio track.
- Caption saved as `DeZX1n-CCEH.txt`. The dl engine names files by media id, not by shortcode.
- The engine fetched the carousel twice (yt-dlp and gallery-dl). The 19 byte-identical duplicates were moved to `_dupes/`.
- Contact sheets (9 frames per slide at 1.5 fps) are in `sheets/`. Engagement metrics were not captured; the caption file has none.
- Method: the formula codebook fields (hook / structure / visual / copy / viral elements), applied by hand. No full `/formula` account run, because this is one post and the token budget is tight.

## 2. Post-level codebook

| Field | Value |
|---|---|
| Hook text (cover) | "Claude Motion [Graphics → Charts → Logos → Apps]" (the last word cycles) + "16 examples, one prompt each" |
| Hook type | list-promise + newsjacking (Claude Motion beta launched 8-9 Oct 2026) |
| Hook mechanism | A live 4×4 wall of 16 moving thumbnails proves the claim before you read a word |
| Structure | hook → process-how (the brief) → proof ×16 → CTA |
| First frame | screen (grid of UI animations) |
| Typography | bold-sans headings, mono for the brief/prompt text |
| Accent | colored-word (second word of each title) |
| Palette mood | pastel / bright clean (off-white, system blue, green, purple, one orange accent) |
| Density | 0-10 words in the title zone; 30-60 in the small "what is in this scene" prompt block |
| Branding | identical template on every slide: tag line, title, card, prompt, footer avatar + "NN / 19" + "SWIPE" |
| Caption formula | personal test → result count → "slide 2 is the brief" → what failed first → 4 numbered steps → constraint line → availability → comment-keyword CTA |
| CTA | comment-keyword (lead magnet: "BRIEF") |
| Emotion | curiosity, then competence ("I could do this") |
| Viral elements | newsjacking, series-counter, repeated-composition, save-worthy-info, live-demo, open-loop (full prompts only via comment) |
| Do not copy | his title template, the "Comment BRIEF" wording, the Apple-device UI subjects, the brief text itself |

## 3. Slide by slide

Timing comes from contact sheets with one frame every 0.67 s. All scenes share one loop: **rest (= first frame) 0-0.7 s → action 0.7-3.5 s → hold ≥1.2 s → reset ~0.8 s back to the first frame**. Each slide therefore loops seamlessly on Instagram.

| # | Scene ("A → b") | Hero object | The one change | Motion techniques | Colour |
|---|---|---|---|---|---|
| 1 | Cover | 4×4 grid of all 16 scenes, live | title word cycles Graphics/Charts/Logos/Apps | grid of synced loops, word swap with spring | white, blue, orange accent |
| 2 | The brief | `motion-brief.md` window | THE SCENE field types a new scene name | typewriter swap in a highlighted chip; everything else stays still for contrast | white card, mono black, orange |
| 3 | Bars → trend | glass chart widget | 7 bars spring up staggered, trend line draws, "+200%" pops | staggered spring scale-Y, stroke draw-on, glowing end dot, number pop with overshoot | blue bars, green line |
| 4 | Monthly → yearly | pricing card + segmented control | pill slides, £29 rolls to £290, badge appears | odometer digit roll with motion blur, pill slide spring, badge scale-in | blue, green badge |
| 5 | Dots → logo | ~150 glossy spheres | particles swirl and converge into an app-icon logo, then scatter | particle convergence to target positions, 3D shading, staggered arrival | blue |
| 6 | Island → live | phone top + island pill | pill grows, 3-2-1 flips, red LIVE pulses, shrinks back | shape morph (pill → card), flip numerals, pulse loop | warm gradient, red |
| 7 | Visits → sales | 3D glass funnel | particles pour through, counter 0 → 600 | particle stream with gravity, counter roll, glass refraction | pale blue |
| 8 | Click → done | "Publish" button | cursor clicks → circle + progress ring → green tick → "Published" | button morph (pill ↔ circle), ring progress, success ripple, cursor squash on click | blue → green |
| 9 | Card → paid | wallet card + pay button | card rises from pocket, progress fills, "Paid" tick | Y slide with spring, masked "pocket" occlusion, fill wipe, depth blur | blue, green |
| 10 | 0 → 12,480 | lock-screen widget | each digit rolls on its own to the final number | per-digit odometer, vertical motion blur, staggered settle, "+18%" pill in | white, green |
| 11 | Weight → bold | "Make it move." headline | variable font 100 → 900; the full stop becomes a bouncing blue dot | variable-font axis animation, per-letter breathing, object handoff (glyph → dot) | black, blue |
| 12 | Sketch → app | phone wireframe | a vertical handle sweeps and reveals the finished UI | wipe/mask reveal (before/after slider), ring fills to 86% | grey sketch → blue |
| 13 | Drag → booked | calendar glass window | cursor drags an event, it snaps into a slot and turns purple with an avatar | drag with lag/inertia, magnetic snap, colour state change | blue → purple |
| 14 | Alerts → stack | lock screen | notifications drop one by one, collapse into a pile, "12 new orders" | stacked spring entrances, collapse with depth offsets, count-up | blue, green |
| 15 | Rings → closed | activity ring | ring sweeps closed, burst, "Goal hit" lands | arc sweep with ease-out, particle burst, text scale-in | green |
| 16 | Dock → open | 6-icon dock | cursor magnifies, icon bounces, window zooms out "+32% → +38%" | dock magnification (fisheye), bounce, scale-from-origin window, number tick | multi-colour icons |
| 17 | Card → 360° | product card (headphones £129) | card turns 360° in Y, back lists 3 ticked features, lands facing front | 3D Y rotation with perspective, specular sweep, staggered ticks | blue, green |
| 18 | Map → route | tilted 3D light map | pins drop with bounce, glowing route draws, "4 new stores" label | pin drop with squash, path draw-on with glow, glass label, camera tilt | white map, blue |
| 19 | CTA | "Comment BRIEF" | the keyword types into a comment field | typewriter, blinking caret, 3-line "what you get" list | white, orange |

### The brief (slide 2), paraphrased

The whole carousel comes from one fixed brief plus one variable line. Its rules, in our words:
- **Bar:** keynote-grade, or it is not done.
- **Format:** a fixed canvas (a 1080×960 card inside a 1080×1350 slide), exactly 6 s, last frame = first frame.
- **One rule:** one hero object at 60-70% of the frame, one satisfying change, then reset.
- **Look:** bright, frosted glass, soft shadows, real depth, one or two colours.
- **Type:** heavy weights, 5 words at most, key number at least 120 px.
- **Motion:** springs on everything; hold the after-state for at least 1.2 s.
- **Never:** grey placeholder bars, stock icons, emoji, dark backgrounds.
- Variable line: "THE SCENE: <object> → <change>".

Per the caption, his first attempt used his own brand kit and gave generic results. Quality jumped only when the brief named a concrete quality bar and hard constraints.

### Template anatomy (every proof slide)

1. Tiny tag line at top left ("THE SCENE · NN OF 16").
2. Title "Noun → noun" in a heavy grotesk at ~70 px, with the second word in the scene colour.
3. A one-line subtitle in grey.
4. The 1080×960 animation card (the actual Claude Motion export), centred.
5. "What is in this scene" prompt in mono at ~22 px, with variables highlighted in blue, then an "I used: …" line.
6. Footer: avatar + handle, "NN / 19", "SWIPE →".

## 4. Why it works

1. **Constraint = consistency.** One brief fixes format, palette, type and motion; only the scene line changes. That is why 16 outputs look like one designer made them. This is the most transferable idea.
2. **One object, one change, reset.** Each loop has a clear before and after inside 6 s. The eye always knows where to look, and the loop makes it rewatchable, which raises watch time per slide.
3. **Proof before promise.** The cover is the results wall, not a claim. Slide 2 hands over the "how", so the next 16 slides are proof. That drives saves and swipe-through.
4. **Physics, not tweens.** Spring overshoot, motion blur on rolling digits, squash on clicks and magnetic snaps make the motion read as material. That is the "keynote" feel.
5. **Numbers as heroes.** 6 of the 16 scenes end on a big number (+200%, £290, 600, 12,480, +38%, 4). A large numeral at the end of the motion is the payoff frame.
6. **Repeatable template + series counter.** "NN / 19" and an identical layout lower the reading cost, so the viewer swipes on autopilot.
7. **Lead-magnet CTA.** The full prompts are held back for a comment keyword. That raises comments while the post is already complete enough to save.

## 5. Limits for RS / JB (what not to transfer)

- The look is SaaS/Apple UI on white. RS lives in humus/mist with documentary stills, so "never dark backgrounds" does not apply to RS.
- There are no people, no place and no sensory anchor. The RS rule is a person, a hand, soil or a dated number first. Swap the UI-object vocabulary for field objects: seed, bed, water, a map of Türkiye, ripple rings.
- Abstract demo numbers (+200%) would break the Greenshouting rules. Every RS number must be sourced, scoped and dated.
- The comment-keyword lead magnet suits JB (process, tools) better than RS (films). The RS CTA is "watch the film".
