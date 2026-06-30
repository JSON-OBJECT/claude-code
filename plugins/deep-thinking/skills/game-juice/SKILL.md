---
name: game-juice
description: Use when building or polishing browser UI that should FEEL like a Japanese gacha/casual mobile game — damage numbers, hit impact, screen shake, springy/alive buttons, combos, "juicy" / "game juice" / "game feel" UI (especially vertical 9:16 mobile). Treats juice as FEEDBACK that communicates game state (not decoration), enforces earned-juice restraint (subtle on frequent actions, full juice reserved for rare/special ones) to avoid the generic AI-mass-produced feel, orchestrates impeccable for visuals and gsap-skills for animation, and carries its own quantitative parameter canon. Forbids uniform max-juice, linear easing, anticipation-less reactions, and silent effects.
---

# Game Juice

Self-contained distillation of a Game Juice / Game Feel implementation canon (verified against Vlambeer *The Art of Screenshake*, GMTK, Steve Swink *Game Feel*, and r/gamedev·r/gamedesign consensus). Everything you need is in this file — no external doc required.

## First principle: juice is FEEDBACK, not decoration

Every effect must answer **"what does this communicate to the player?"** If nothing — cut it. A capable agent already *knows* overshoot/squash/flash; it fails in five predictable ways:

1. **Uniform max-juice** — same full effect on every action → sensory overload → the generic "AI-mass-produced" feel. *This is the #1 cause.*
2. **Reinvents** instead of using the installed skills.
3. **Skips accessibility** (reduced-motion, shake toggle).
4. **Drifting ad-hoc numbers.**
5. **No anticipation / no sound / designs for the screenshot** instead of the hand.

Three implications:
- **Communication, not ornament.** Real juice is *felt, not seen* — raw footage looks chaotic but feels perfect in-hand (Ultrakill). **Validate by playing, never by screenshot.**
- **"Give it mass."** Half of Vlambeer's 30 tricks reduce to: give everything mass/inertia/causality via a **3-beat — anticipation (wind-up) → action → reaction (follow-through).** AI slop does the reaction only and skips anticipation → things "just pop." Bigger action ⇒ more wind-up.
- **Sound is half.** "Audio is half the movie." A silent visual effect is half-finished (see Sound below).

## Workflow (do in order)

0. **Budget the feedback first.** Map each event to a juice tier — this is what prevents the generic feel:
   | Event | Juice |
   |---|---|
   | frequent action (basic tap) | small pop · micro shake · short SFX · **no hit-stop** |
   | occasional (crit / combo) | big pop · color shift · mid shake · 50ms hit-stop |
   | rare (special / defeat / boss) | full: **anticipation** · 120ms hit-stop · slow-mo · camera · strong shake |
   Plus: every relevant event gets *some* small cue (Nuclear Throne rule); reserve the big stuff. **Exaggerate the ONE core verb**, not everything.
1. **Visual + art direction — `impeccable` ALONE.** **REQUIRED SUB-SKILL.** **Do NOT also run `frontend-design`** (impeccable's own rule — they collide & cancel: [impeccable.style](https://impeccable.style/designing/); frontend-design is unmaintained). Run impeccable `init` once for non-throwaway work; treat it as an opinionated partner, not a linter. Avoid the AI tell of **uniform neon glow + default fonts** — give shape/color/sound a distinct identity. Tell it: *Japanese gacha aesthetic (exaggerated · flashy · squishy), vertical 9:16, thick-outlined rounded fonts, crit = yellow/orange. Juice is feedback — restrained on basic hits, full effect only on crit/special.*
2. **Animation — `gsap-skills` (do NOT hand-roll easing).** **REQUIRED SUB-SKILL:** `gsap-timeline` (sequence), `gsap-core` (easing, `gsap.matchMedia`), `gsap-performance` (transforms only), `gsap-plugins` (CustomWiggle/SplitText). GSAP is 100% free since 2025-04-30 (Webflow); all plugins included.
3. **Anchor every number to the Parameter canon below.**
4. **Pick the tier** (see Tech tiers — most UI = T1 GSAP+DOM; ≤tens particles DOM, hundreds canvas).
5. **Apply the Mandatory Floor.**

## Earned juice — the budget that separates real from slop

> *"Put hitstop/zoom/slow-mo on every basic attack and it goes numb fast — sensory overload. Reserve big juice for special/hard actions."* — r/gamedesign (Nioh·Smash Ultimate cited as hitstop-overuse failures)

Strong effects (hit-stop, slow-mo, camera moves, strong shake, full-screen flash) are **only strong when scarce.** Every-tap-the-same IS the generic look. Balance against the Nuclear Throne rule — *some* small cue on every relevant event, big stuff reserved — to get "alive but not overwhelming." **Exaggerate the one core verb** the game is about; painting everything the same makes it featureless.

## Parameter canon (60fps / 16.67ms per frame — starting points, ±tune)

### Buttons — squishy (+ anticipation on big buttons)
```
press:   scale 1 → 0.92            | 90ms       | power2.out
release: scale 0.92 → 1            | 250~400ms  | elastic.out(1,0.4) / back.out(2.5)
special anticipation: hold pulls back (scale 0.9 + y+6px) → fires on release | wind-up 100~200ms
```
**Immediacy:** register input at animation *start*, never wait for it to finish. Input latency < 100ms.

### Damage number pop
```
pop:        scale 0 → 1.3 → 1      | 220ms      | back.out(2)
rise+fade:  y -50px, opacity → 0   | 600~800ms  | power1.in (hang ~0.1s)
crit:       1.5~1.8× + color shift + rotate ±8° + stronger shake
color:      normal=white | crit=yellow/orange | heal=green   (outline/shadow REQUIRED)
multi-hit:  40~80ms stagger
```

### Screen shake — trauma-based (+ MUST be toggleable)
```
trauma:   0~1, +0.3~0.6 per hit
intensity = trauma²                (small impacts barely shake)
displace: mobile 4~10px, rotate ±2~4° (rotation = less nausea)
decay:    trauma -= 1~2 × dt       (dies in 0.5~1s)
noise:    Perlin/Simplex           (pure random = jitter)
```
Shake the **container** (parent wrapper), not individual elements. Provide a 0~100% in-app shake setting — many players turn it off before round one; never make feedback shake-dependent.

### Hit-stop (the weight, but EARNED)
```
crit / combo:    ~50ms freeze (≈3 frames)        ← occasional
heavy / special: 80~150ms freeze (5~9 frames)    ← rare only (boss, defeat, ultimate)
basic tap:       never                           ← overuse = slop
web:             insert empty time in timeline / toggle timeScale(0)
```
A frequent ~20%-rate crit is "occasional," not "rare" — give it ~50ms, and reserve 80~150ms for the genuinely rare events. (Matches the Workflow budget table.)

### Flash · particles · permanence
```
hit flash:  brightness 3→1 | 60~120ms | power1.in   (full-screen = special only)
particles:  8~24 per burst (DOM ceiling), radial+gravity, 300~600ms, spread power2.out / die power1.in
permanence: decals/cracks/debris LINGER seconds or accumulate — "what I did" stays visible (Vlambeer). Pool decal divs, slow fade.
```

### Easing cheatsheet (never linear for feedback)
| Use | Easing |
|---|---|
| enter / move | `power2.out` / `power3.out` |
| squishy overshoot (button·pop) | `back.out(1.7~2.5)` |
| jelly bounce | `elastic.out(1, 0.3~0.5)` |
| heavy impact | `power4.in` / `expo.in` |
| exit / fade | `power1.in` |
| **`linear`/`none`** | ❌ banned for feedback (mechanical motion only) |

> CSS `cubic-bezier()`: back.out ≈ `cubic-bezier(0.34,1.56,0.64,1)`. GSAP/anime provide real elastic/back natively.

## Tech tiers — pick by render layer
| Want | Tier | Tool (current best) | Layer |
|---|---|---|---|
| squishy buttons · damage pop · shake | **T1** | **GSAP** (1st) / anime.js v4 / Motion(React) | DOM + CSS transform |
| stateful "alive" buttons · summon FX | **T2** | **Rive** (interactive) / Lottie (one-shot decor) | `<canvas>` overlay |
| hundreds of flying debris in combat | **T3** | **PixiJS v8** (renderer) / Phaser (full engine) | WebGL/WebGPU `<canvas>` |

**Boundary (Reddit consensus):** particles **≤ tens = DOM**, **hundreds = canvas**. *"GSAP for particles is very inefficient → shaders/canvas."*

## Hit pattern — split light vs heavy (the core of earned juice)

```js
import { gsap } from "gsap";

function hitLight({ target, dmg, popLayer }) {           // frequent: subtle, NO hit-stop
  addTrauma(0.28);
  gsap.fromTo(target, { scaleX: 1.12, scaleY: 0.9 }, { scaleX:1, scaleY:1, duration:0.35, ease:"elastic.out(1,0.4)" });
  popDamage(popLayer, dmg, false); playSfx("hit");
}
function hitHeavy({ target, dmg, popLayer, anticipateEl }) { // rare: full juice
  const tl = gsap.timeline();
  if (anticipateEl) tl.to(anticipateEl, { scale:0.9, y:6, duration:0.14, ease:"power2.in" }); // anticipation
  tl.to({}, { duration: 0.12 });                                                              // hit-stop
  tl.fromTo(target, { filter:"brightness(3)" }, { filter:"brightness(1)", duration:0.14, ease:"power1.in" }, "<");
  addTrauma(0.6); popDamage(popLayer, dmg, true); burst(popLayer, 22); spawnDecal(popLayer); playSfx("crit");
  if (navigator.vibrate) navigator.vibrate(28);
  return tl;
}
```
> Callers only accumulate `trauma`; a ticker renders `trauma²` on the container. When the shake toggle is OFF, make `addTrauma` a no-op.

## Sound — Web Audio (half the feel)

HTMLAudio lags. Pre-decode buffers so the hit and the sound don't drift.
```js
const ctx = new AudioContext(); const buffers = {};
async function loadSfx(name, url){ buffers[name] = await ctx.decodeAudioData(await fetch(url).then(r=>r.arrayBuffer())); }
function playSfx(name, { volume=1, pitchVar=0.06 } = {}){
  if (ctx.state === "suspended") ctx.resume();                 // mobile: resume on first gesture
  const src = ctx.createBufferSource(); src.buffer = buffers[name];
  src.playbackRate.value = 1 + (Math.random()*2-1)*pitchVar;   // ±6% pitch so rapid hits aren't robotic
  const g = ctx.createGain(); g.gain.value = volume;
  src.connect(g).connect(ctx.destination); src.start();
}
```
**Tonal** hit-sounds (like an FPS hit-marker) signal the hit even with no visual — cheapest, highest-value feedback. OscillatorNode + decaying noise works for a single-file demo (no asset).

## Performance — hold 60fps
- Animate **`transform` (translate/scale/rotate) + `opacity` ONLY** → GPU compositor. **Banned:** `width/height/top/left` (reflow), reckless `box-shadow/filter` (paint), per-frame DOM measurement.
- `will-change: transform` only **right before** an effect, then clear it.
- Particles ≤ tens → DOM/GSAP; hundreds → canvas/PixiJS.
- Verify 60fps in DevTools; test on a **mid-range Android** device.

## Accessibility & vertical 9:16 (required)
- **`prefers-reduced-motion`:** weaken/remove shake·big moves·flashing, but **keep essential feedback** (button press). Branch JS via `gsap.matchMedia()`.
- **In-app shake setting** (0~100%), separate from OS settings.
- **Flash-safe:** no >3 strong flashes/sec (WCAG 2.3.1).
- **9:16:** put damage numbers in the top area (avoid the thumb-covered bottom third). Touch targets ≥44×44px. `touch-action: manipulation` (kills double-tap zoom).
- Feedback must read **with sound muted** (visual alone).

## Korean / CJK game fonts (the silent fallback trap)
Latin display/pixel fonts (Fredoka, Baloo, Chakra Petch…) **have no Hangul glyphs** — Korean text silently falls back to `system-ui` (Malgun Gothic) = the "browser, not a game" tell. The fallback throws no error, so **render actual Hangul and check with your eyes.** Mirror your Latin 2-axis pairing onto Hangul (keep **2 roles** — readable body + chunky display — even if family count grows). Free OFL on Google Fonts CDN:

| Role | Font | Identity |
|---|---|---|
| cyberpunk title/display | **Gugi** | angular neon-sign |
| gacha chunky juice·buttons | **Jua** | brush-signboard, round/squishy |
| HUD·body·labels | **Do Hyeon** | acrylic-cut signboard, solid/legible |
| arcade impact title | **Black Han Sans** | thick poster punch |

> **faux-bold caveat:** these are usually **Regular-only** → `font-weight:700` synthesizes a fake bold that smears at small sizes. Want weight? Start with an already-heavy face (Black Han Sans); don't rely on faux-bold.

## Mandatory Floor (verify ALL)
- [ ] **Earned-juice applied** — light vs heavy differentiated; basic actions subtle; hit-stop/slow-mo/camera reserved for rare events.
- [ ] **Invoked `impeccable` (NOT `frontend-design`) + `gsap-skills`** — didn't reinvent, didn't run the two visual skills together; art direction is distinct (not uniform glow).
- [ ] **Anticipation** on big/special actions (wind-up → action → reaction).
- [ ] **Sound paired** (Web Audio, pre-decoded, pitch ±6%, `ctx.resume()` on first gesture). Tonal hit-sounds.
- [ ] **`prefers-reduced-motion`** via `gsap.matchMedia` + **in-app shake toggle**; keep essential feedback.
- [ ] **Flash-safe** (<3/sec), **transform+opacity only**, 60fps mid-Android.
- [ ] **Numbers anchored to the Parameter canon.**
- [ ] **Hangul actually renders** in the chosen game font (no silent system-ui fallback).

## Red flags — you are making AI slop
- **Same full juice on every action** (the big one) · juice for decoration not feedback · reaction without anticipation
- `linear` easing · silent effects · **uniform neon glow + default fonts** (no art direction) · Latin-only font with Hangul left to fall back
- Validating juice by screenshot instead of playing it · no shake toggle / shake-dependent
- Hundreds of particles in DOM · hand-rolled easing · skipped the installed skills · **ran frontend-design alongside impeccable**

**All of these mean: stop — budget the feedback, route to the right skill (impeccable + gsap-skills), anchor to the Parameter canon, add the floor.**
