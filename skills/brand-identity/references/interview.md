# Stage 1 — Discovery

## A. Harvest (before any question)
Look for, in this order, and tag each finding with its source:
1. Folders/URLs the user named. 2. `~/.claude/FACTS.md`, `~/.claude/profile/00-INDEX.md` (own brands). 3. Site: CSS tokens (`--var` colours, font-family), About/Services copy, meta descriptions. 4. Email signatures, decks, one-pagers, proposals. 5. Past work list, testimonials, press, awards (only with sources). 6. Competitors/references the user admires (links). 7. Connected platforms via `brand-voice:discover-brand` (Notion, Drive, Box) when the client uses them.
Do not scrape private accounts; public pages only.

## B. Known / gap table (write to `brand/01-discovery.md`)
| Topic | Known | Source | Confidence (H/M/L) | Gap? |
Topics: who they are · what they make · who for · why they exist (belief) · how they differ · proof · current look · current voice samples · competitors · constraints (language, budget, legal) · goals for the next 12 months · what must NOT change.

## C. Interview — only rows marked Gap or L
Rules: 2 rounds max, ≤12 questions total, batch each round in one message, give choices where you can, accept "skip" and mark `TODO(ask)`.
Question bank (pick, don't ask all):
- Belief: "What do you think is wrong with how your field works today?"
- Audience: "Name one real person who is your ideal client. What did they say before hiring you?"
- Difference: "What do clients say you do that others don't? Quote them if possible."
- Proof: "Three results, numbers or names you can show (with source)."
- Enemy/contrast: "What do you refuse to be?"
- Feeling: "After meeting the brand, a person should feel ___ and do ___."
- Taste: "Three brands or films you admire (any field) and the one thing you steal from each."
- Voice: "Paste 3 things you wrote that sound most like you. One you cringe at."
- Visual: "Colours, fonts, textures you love or hate. Anything that must stay."
- Language: "Which languages does the brand speak, with whom?"
- Constraints: "Deadlines, budget for design/print, tools (Canva, Figma, none)?"
- Future: "Where should the brand be in 12 months?"
For a person-brand add: what work they want more of / less of; what they are famous for by accident.
For a client brand add: who approves, who uses the guidelines day to day.

## D. Close
Summarise in 5 lines, list remaining `TODO(ask)`, log decisions in `decisions.md`.
