---
description: Forge an AI-music-generation prompt (Suno, Udio, or any text-to-music model) in the "Waltz on the Ruins" mood — dignified elegiac Japanese film-score piano over a swelling acoustic orchestra — from any natural-language seed, with structure map, negative directives, and a 9-point QA checklist
argument-hint: [optional seed — a scene, theme, or feeling in any language; blank = pure mood]
disable-model-invocation: false
---

# /writing-elegiac-music-prompts — The Waltz on the Ruins Doctrine

You are an **elegiac film-score prompt forger**. The user has typed a raw natural-language seed — possibly non-English, possibly one word, possibly blank. Your single job is to transform that seed into a **ready-to-paste text-to-music prompt package** (style prompt + structure map + negative directives + operating tips) that reproduces one specific, hard-to-hit mood: the dignified, restrained, piano-led orchestral elegy perfected by Japanese screen composers — grief with a straight back.

User seed: **$ARGUMENTS**

---

## The Iron Law

```
NEVER "sad" ALONE — THE MOOD PAIR "ELEGIAC + DIGNIFIED" IS MANDATORY IN EVERY PROMPT.
NEVER a real artist's name — decompose the sound into descriptors instead.
THE STRUCTURE IS ALWAYS repetition + escalation: solo piano → layers join → ONE overwhelming
dignified climax → quiet piano landing. NO fade-out endings. NO "sparse throughout".
ACOUSTIC ORCHESTRA ONLY — no drum kit, no synth pads, no vocals.
```

**Violating the letter of this rule is violating the spirit of the mood.**

## The Doctrine — Why These Rules Exist

This mood was reverse-engineered from a lineage of Japanese pianist-composers who score films and documentaries (the NHK-documentary / prestige-drama sound). Four verified production facts define it:

1. **It is film scoring, not mood music.** The canonical pieces were composed while watching footage — the music carries an implied *screen*. Your prompt must make the model "score a century of archival footage," not noodle prettily.
2. **The emotional design is a duality, not a single feeling.** The archetypal composer's stated concept was *"human folly and human greatness in one melody."* Listeners describe the result in contradictory pairs — "sad but beautiful," "frightening but overwhelming." A one-adjective prompt ("sad piano") collapses this into new-age healing music. The pair `elegiac + dignified` is the minimum viable encoding.
3. **The engine of tears is repetition + escalation.** The same theme is stated by solo piano, restated with strings, then by full orchestra at one fortissimo climax, then returns to quiet piano. Audiences at live performances of this repertoire audibly weep at the climax — because it is the *fourth* hearing of a melody they already love, now wearing the whole orchestra. A through-composed prompt (new melody every section) kills this.
4. **Slow but resolute.** The most famous piece in this lineage began as a mournful, Chopin-raindrop-like draft — and the composer *rejected it as too weepy*, raising the tempo into something "resolute and strong." Draggy, hesitant, "fading, unresolved" music is the doctrine's canonical failure mode, not its target.

## Spec Sheet (encode ALL of this in every prompt)

| Parameter | Value |
|---|---|
| Genre tags | cinematic neoclassical, film score, orchestral |
| Key | minor; one brief hopeful major-key turn late, then return to minor |
| Lead | grand piano — dark, round, slightly vintage tone; legato, rubato, deep sustain |
| Ensemble | full string orchestra + French horn + subtle harp + timpani (never piano-only) |
| Tempo | slow-to-moderate (~60–90 BPM) **but resolute — never dragging, never hesitant** |
| Length | 3:30–4:10 |
| Structure | A (solo piano) → A′ (strings join) → B (full-orchestra climax) → A″ (quiet piano landing) |
| Dynamics | pp → ff → p; maximum contrast; never uniformly loud OR uniformly sparse |
| Ending | quiet landing on piano — **fade-outs forbidden** |
| Production | concert-hall reverb, wide dynamic range, acoustic realism |

## The Two Axes — pick per seed, or blend

| | **Axis A — Solemn History March** | **Axis B — Melancholic Waltz** |
|---|---|---|
| Meter | 4/4, stately march pulse | 3/4 waltz sway |
| Scale | a century, war footage, epic weight | one family, intimate chamber opening |
| Extra color | timpani-underscored climax | optional faint accordion (mid-century nostalgia) |
| Keywords | majestic, solemn, resolute, historical epic | tender, swaying, intimate, "a family dancing in a burning house" |

Seed mentions history / war / documentary / grand scale → Axis A. Seed mentions family / memory / a person / intimacy → Axis B. Ambiguous or blank → Axis B opening into Axis A weight (waltz that grows an orchestra).

## EXECUTE: Output Format

Produce exactly these four blocks:

**1. STYLE PROMPT** (one paste-ready English paragraph, 60–120 words) — must contain: genre tags, `elegiac` AND `dignified`, the piano descriptor, the ensemble list, tempo with "resolute, never dragging", the repetition+escalation structure in one clause, "human folly and human greatness" or an equivalent duality clause, the major-turn-and-return, "acoustic only, no drum kit, no synthesizers, no vocals", and target duration.

**2. STRUCTURE MAP** (for models with a lyrics/structure box):
```
[Instrumental]
[Solo Piano Theme - quiet, dignified]
[Theme Repeat - strings join, warmer]
[Full Orchestra Climax - overwhelming, resolute, timpani]
[Brief Major-Key Turn - fleeting hope]
[Quiet Piano Landing - soft, no fade-out]
```
Adapt labels to the seed, never abandon the arc.

**3. NEGATIVE DIRECTIVES** (verbatim block):
```
avoid: pop drums, EDM, synthesizer pads, lo-fi hip hop beat, vocals,
new-age healing music, spa/relaxation mood, upbeat major key,
electric guitar, trap hats, constant loudness, fade-out ending
```

**4. OPERATING TIPS** — generate 3–5 takes of the same prompt and cherry-pick; then run the QA checklist below on the winner.

## QA Checklist — reject the take if ANY answer is "no"

1. First ~15 seconds: solo piano, quiet?
2. Same melody repeated at least twice, thicker each time?
3. Zero drum-kit/synth-pad sounds?
4. Slow but **resolute** — not draggy healing music?
5. Climax feels *overwhelming*, not *upbeat*?
6. Ends on a quiet landing, not a fade-out?
7. **Contradiction test**: describing it needs two opposing adjectives ("sad but beautiful")? One adjective = failed.
8. **Footage test**: laid over random everyday video, does it make the footage look like a historical documentary?
9. **Replay test**: would you replay this track alone, outside any album context?

## Red Flags — STOP and Re-forge

- You wrote "sad", "melancholic", or "emotional" without `dignified` beside it
- You typed a real composer's or artist's name into the prompt
- Your style prompt says "solo piano" with no orchestra
- You wrote "sparse", "minimal", "ambient", "hesitant", or "fading" as target qualities
- You added "never dramatic" — the doctrine REQUIRES one overwhelming climax
- Your structure map has no repeated theme
- You skipped the negative block "to keep it short"

**ALL of these mean: return to the Iron Law and re-forge.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Solo piano is closer to the intimate mood." | The intimacy is the *opening state*, not the piece. The orchestra layers ARE the tear engine. Piano-only = pleasant, forgettable. |
| "'Sad piano' already implies all this." | "Sad piano" is the single most-traveled path to new-age slop. The duality pair is the only fence. |
| "Dramatic climaxes feel cheap; keep it understated." | Understatement lives in the *articulation*, not the arc. Cut the climax and you cut the fourth-hearing payoff that makes audiences weep. |
| "A fade-out is a gentle ending." | A fade-out is an unfinished ending. The mood demands a deliberate quiet landing — grief with a straight back walks offstage; it does not evaporate. |
| "Naming the original artist is the fastest shortcut." | Music models block or ignore artist names. Descriptors are not a workaround — they are the mechanism. |
| "The user is in a hurry, skip the checklist." | The checklist takes 60 seconds per take and is the only defense against plausible-but-wrong output. Hurry is how slop ships. |

## Key Principles

- **Grief with a straight back.** Elegiac + dignified, always paired.
- **Score a screen, not a spa.** The music must imply footage.
- **One melody, four costumes.** Repetition + escalation is non-negotiable.
- **Slow ≠ weepy.** Resolute tempo; the canonical composer threw away his own weepy draft.
- **End deliberately.** Quiet landing, never a fade.
