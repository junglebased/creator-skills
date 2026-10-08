# Codebook — per-post analysis schema

One file per post: `analysis/<id>.json` (written by the analysis agent). Fields are short and enums are fixed so `formula.py synth` can count them.

```json
{
  "id": "", "format_code": "",              // format_code is assigned during synthesis (F1..)
  "hook": {
    "text": "",                            // cover / first-3-seconds on-screen text, verbatim
    "spoken": "",                          // first spoken sentence from the transcript ("" if music/no speech)
    "type": "",                            // one of HOOK TYPES
    "mechanism": ""                        // why it stops the scroll, <=12 words
  },
  "structure": ["hook", "context", "..."], // list of ARC BEATS
  "visual": {
    "first_frame": "",                     // face | object | text-card | landscape | screen | product
    "text_position": "",                   // top | middle | lower-third | full-screen | none
    "typography": "",                      // editorial-serif | bold-sans | handwritten | meme | captions
    "type_scale": "",                      // huge | large | medium
    "accent": "",                          // colored-word | box | underline | none
    "palette_mood": "",                    // warm-natural | high-contrast-neon | pastel | mono | dark-cinematic
    "density": "",                         // words per frame/slide: 0-10 | 10-30 | 30-60 | 60+
    "branding": "",                        // logo placement / template consistency
    "motion": ""                           // video: seconds per shot, caption style, b-roll share
  },
  "copy": {
    "caption_formula": "",                 // e.g. "hook -> 3 news paragraphs -> quote -> question -> CTA -> credits"
    "length_words": 0,
    "voice": "",                           // 3 adjectives
    "cta": {"type": "", "text": ""},       // CTA TYPES
    "hashtags": 0
  },
  "emotion": "",                           // curiosity | awe | anger | hope | humor | nostalgia | fear | belonging
  "viral_elements": [],                    // from VIRAL ELEMENTS
  "why_it_worked": "",                     // <=2 sentences, tie to the metrics (or "why it flopped")
  "adaptable_for": [],                     // brand codes from brands/*.md that this fits
  "do_not_copy": ""                        // account-specific things that must not be imitated
}
```

## HOOK TYPES
paradox · question-curiosity · danger-risk · number-shock · quote · meet-the-character · this-is-x · before-after · list-promise · myth-busting · secret-unknown · personal-confession · newsjacking · celebrity · POV · challenge · humor-absurd · visual-shock (no text) · career-timeline

## ARC BEATS
hook · context · character · problem · tension · process-how · proof-number · turn · outcome · emotional-close · question · CTA · credits

## CTA TYPES
follow · save · share-tag · comment-keyword (lead magnet) · comment-question · link-in-bio · DM · product-sale · newsletter · none

## VIRAL ELEMENTS
face-in-first-frame · weird-object · series-counter · repeated-composition · contrast-color · karaoke-captions · pattern-interrupt · open-loop (answer at the end) · save-worthy-info · debate-trigger · community-identity · trending-audio · collab · repost · news-timing · human-scale-number · me-too-feeling · live-demo (shows the technique while explaining it)
