---
name: verdict
description: Distil a finished thread into verdict cards — compact, binding conclusions a future session reads instead of re-researching the topic. Builds the layer on first run.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[optional: path to an _answers/ file — blank harvests this conversation]"
---

# Verdict

A **verdict** is a settled conclusion a future session obeys instead of re-researching. It states the ruling, the branch rules, the **rejects**, and the **appeal** conditions that would overturn it. How the deliberation went stays in the source.

**Why this runs at all:** a session reaches a genuinely good answer and then ends before anyone files it. The reasoning evaporates and the next session pays for the same investigation again. This is the intake valve.

**Why a card is replaced rather than extended.** Under full reversal, append-only memory and last-write-wins both score **0.210 against 0.309 for having no memory at all**; the same store with an explicit revocation state scores **0.950** (TEPA, arXiv 2608.07429). A layer that keeps superseded conclusions retrievable is worse than an empty one, because the stale text still enters the prompt as evidence. Every rule below — amend the owning card, rewrite the slot, one ruling in one place, `stale_after` as an explicit validity state — exists to keep this layer out of the 0.210 column. **Growth is the symptom of drifting back into it.**

**It takes no instruction.** Invoked bare, it harvests the conversation it is running inside, rules on what was **settled**, finds the cards that own those questions, and **lands** the facts there — building the layer itself on the first run. `$ARGUMENTS`, when given, names an `_answers/` file to harvest instead.

**Read `ANATOMY.md` now** — it holds the slot template, the frontmatter contract, and the retrieval mechanics that decide how a card gets written. Everything below assumes it.

## The inversion

Default summarising keeps the narrative and drops the numbers. A verdict does the opposite.

**Carry** every number, proper noun, version string, parameter value, price, rejected option with its reason, and recorded dissent.
**Leave behind** the research narrative, the comparison tables that produced the ruling, and the story of who found what.

---

## Step 0 — Bootstrap the layer

Decide the location yourself: locate the root, then create what is missing.

```bash
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"   # vault root; prefer the dir holding fts5-reindex.py
mkdir -p "$root/verdicts/<domain>"
```

**Domain** is the subject area the decision belongs to, one word, lowercase (`ai-cinema`, `infrastructure`, `fashion`). Mirror the vault's existing topic folders when they exist — cards at `verdicts/<topic>/` and prose at `<topic>/` put the same axis on two layers. When no folder fits, name the domain after the decision's field, not after the session.

Seed these once, only if absent:

| Path | Purpose | Seed when absent |
|---|---|---|
| `verdicts/<domain>/` | where cards live | always |
| `verdicts.md` | root router, one row per **domain** | `type: index`, a table: domain · what it decides · card count · earliest expiry |
| `verdicts/CHARTER.md` | the genre contract | copy the joining conditions, slot skeleton, and maintenance rules from `ANATOMY.md` |
| `verdict-lookup.sh` | the query every session runs first, and the layer's `--lint` | the script in Step 2 |

**Done when** `verdicts/<domain>/` and the router both exist, each either newly seeded or left exactly as found.

---

## Step 1 — Harvest, and rule on what is settled

Read the whole source in order. Later turns correct earlier ones — a licence term restated from a primary source, a model that turned out to be omitted, a price that moved.

When the source is an `_answers/` file, first prove it is whole; a file read at 40 % yields cards that are wrong on arrival:

```bash
head -20 <source>              # the header usually declares the total ("9 rounds", "full thread")
grep -nE "^#{1,2} " <source>   # enumerate what is actually present
stat -c '%s %y' <source>       # a file touched minutes ago may still be growing
```

Then build a ledger of every fact, and rule on each one. **This ruling is the whole job** — a card is only as good as this classification.

| Verdict on the fact | Test | Where it lands |
|---|---|---|
| **Settled** | Measured first-hand, or read from a primary source **in this thread**, and nothing later reversed it | The ruling, branch table, or rejects table |
| **Reversed** | An earlier claim this thread overturned | One line in the correction ledger — never in the body |
| **Unresolved** | Awaiting legal, vendor, or a measurement not yet taken | Open items, or one bullet under appeal |
| **Narrative** | How the investigation went, who found what, the comparison that produced the ruling | **Nowhere — `git log -p` and `distilled_from` already own it.** This is what compression means |

> 🔴 **"Nowhere" is refused unless you name who already owns it.** Told to discard the narrative, an operator builds it a house next door instead: measured on one vault, a session log inside `verdicts/` was folded to a table, regrew to **60 KB in six days**, was folded again, and stood at **36.7 KB eight days after that**. It is already recoverable from `git log -p -- <card>` and the `_answers/` file in `distilled_from`. **Any file under `verdicts/` that accumulates per-session or per-date sections is a bypass, whatever it is named** — banning `log.md` by name does not catch `LANDING-LOG.md`.

**Explored but not concluded is not settled.** An option weighed mid-thread and dropped belongs in **rejects** with its reason, not in the ruling. Confidence that varied stays marked — verified against the primary source / secondary only / actively disputed.

### Collapse the churn — the rule that makes long threads survivable

A real session is not a clean investigation. It circles, repeats itself, and overturns its own findings three times as fresh research lands. Handled naively, every one of those flips becomes a line in some card, and the layer inherits the mess instead of the conclusion.

**A claim's ledger entry is its *final* state in the thread, not its history.** Fold every flip of the same claim into one entry before routing anything.

| Kind of reversal | Belongs in the card? |
|---|---|
| The thread contradicted **itself** — an early guess corrected by later research | **No.** Only the final state lands. The intermediate versions are narrative |
| The thread's final state contradicts **what a card currently asserts** | **Yes** — rewrite that card's line, and log one correction-ledger entry |
| The thread confirmed what the card already says | **No.** Nothing lands. Confirmation is not news; at most it moves `timestamp` |

Otherwise the correction ledger becomes the patchwork the body was protected from. **The ledger records where the vault was wrong, not where the conversation wandered.**

### Then sweep for omissions

Before routing, re-read the source **once more against the ledger** and ask what is in the thread that the ledger does not carry. Long sessions bury settled numbers inside digressions, and a fact that survives in no card is a fact the next session pays to rediscover. This second pass is where completeness is actually won — the first pass follows the thread's own emphasis, which under-weights anything settled early and never revisited.

**Done when** every fact in the source carries one of the four verdicts, every claim appears once in its final state, and the second pass surfaced nothing new.

---

## Step 2 — Route each fact to the card that owns it

**Amend is the default. Mint is the exception.** A new card is correct only when a genuinely *new decision* arrived, not when new facts arrived about an old one. Facts split across a new card and a stale old one lose, because the old card owns the question the user will actually ask, and retrieval hands that one over.

```bash
./verdict-lookup.sh <keyword> [keyword2 ...]
```

When the script does not exist yet, this is its body — a query, not a read, because locating one card never justifies loading a whole domain:

```bash
sqlite3 vault.fts5.db -separator $'\t' "
  SELECT DISTINCT rel_path, description, stale_after FROM notes_fts
  WHERE rel_path IN (SELECT rel_path FROM notes_fts
                     WHERE notes_fts MATCH '<keyword>'
                       AND (instr(rel_path,'verdicts/')=1 OR instr(rel_path,'z/verdicts/')=1))
    AND description != '' AND stale_after != ''
  ORDER BY stale_after;"
```

> 🔴 **The card predicate must cover every card root the vault has.** `instr()` anchored at position 1 matches only the top-level root, so a vault that also keeps a second axis of cards under a prefix — a private or scoped root — silently drops all of them and answers as though no card owned the question. Enumerate the roots once and OR them, here and anywhere else the pipeline filters for cards.

Three things it must handle: warn on query terms under three characters (see `ANATOMY.md`), fall back to the main checkout's index when run from a git worktree where the gitignored DB is absent, and carry `--lint` (Step 6) so the layer's rules have an observer.

> 🔴 **Zero rows does not mean no card owns this.** It also means the keyword missed — a two-character term is not indexed at all, and a multi-word phrase matches literally. Retry with a different compound term, and check the domain folder listing, **before** concluding that minting is correct. A wrong zero here mints a duplicate card, which is the most expensive failure this layer has.

**Done when** every settled fact names the card that owns its question, or is flagged as a new decision that needs Mint.

---

## Step 3 — Land it

### The card is **state**. Git is the **log**.

A model editing a document narrates its own edit by reflex. Fifty amendments later the ruling is still correct and nobody can find it: the card has become a log of its own revisions. So every amendment rewrites, and **nothing in the card records that it rewrote.**

- A line that changed reads exactly like a line that never did — no `🆕`, no `🔄`, no `updated`, no *as of this session*.
- A section that is now wrong gets **rewritten in place**, where `2026-08-06 addendum:` would have gone.
- The one place a change is recorded is the **correction ledger**, and it names the overturned claim, not the act of editing.
- 🔴 **A heading names a decision, a situation, or a subject — never a date, a meeting, or an event.** Same prohibition one level up, and the one that actually gets breached: blocked from writing `2026-08-06 addendum:` inside a slot, a session opens `## 2026-08-06 <vendor> PT — …` instead and the ban never fires. Measured on one vault, the two largest cards — **95 KB and 92 KB** — were dated sections end to end, and had become negotiation diaries. Facts arriving in waves are reorganised **by what decides the outcome**, never by when each wave landed.

Measured on one vault: **1,000 edit markers across 954 KB of cards — one per kilobyte —** with the 15 KB ceiling at 78 % violation.

### Every fact lands *in a slot the card already has*, by rewriting that slot

| Incoming fact | Where it lands | What you rewrite |
|---|---|---|
| Changes the ruling | Ruling | **The ruling line itself.** Replace the sentence |
| A new candidate | Rejects table, or branch table if adopted | One row. The body does not grow |
| A new way the ruling could fail | Appeal | One bullet |
| Overturns something the card asserts | Correction ledger | One line: what it used to claim, what is true, where the wrong version came from |
| Deeper detail on something already ruled | The linked source | Nothing — the card's line stands |

### The size gate — two questions, not one

```bash
before=$(stat -c%s <card>)   # …amend…
after=$(stat -c%s <card>);  echo "Δ $((after-before)) bytes for <N> new facts"
[ "$after" -gt 15360 ] && echo "⛔ $((after/1024))KB — over the ceiling. Split now, per Step 4."
```

The **delta** asks whether you replaced or appended. A card that absorbed three facts by replacement moves by hundreds of bytes, in either direction; **if it grew by thousands, you appended.** Go back and rewrite the slot instead.

The **absolute** check asks whether the card is still under the ceiling, and it is the one that gets skipped: the ceiling is written into Step 4 where cards are born small, and never re-asked in Step 3 where they grow. **A relative gate passes forever** — 300 bytes × 40 amendments is a 12 KB card built entirely from individually justified, individually passing edits. Measured on one vault: **56 % of cards over the ceiling, the ten largest holding 17 % of the layer.** A card that crossed the line during *this* amendment is split during *this* session, not queued.

> **Why the ceiling is a per-question price, not a style preference.** When a live card covers the question, the grounding pipeline stops and **reads that card whole** — that is the short-circuit the layer exists to provide. So the card's size *is* the cost of every question it answers: ~5 K tokens at the ceiling, ~30 K for a 92 KB card. Oversize cards do not merely rank badly; they tax the exact path the layer was built to make cheap.

**Done when** every fact occupies a slot, the card reads as pure **state**, the byte delta is consistent with replacement, and the card is still under the ceiling.

---

## Step 4 — Mint, when the decision really is new

### Cut into decisions

Four axes, applied together:

- **Decision unit** — "which image model" is a topic and grows forever; "which image model do we use" is a decision and ends when the answer settles. Name each card with the question it closes.
- **Retrieval moment** — budgeting, sitting at the tool, and asking legal are three moments. One card per moment.
- **Decay rate** — model rankings and prices decay in ~2 months; craft principles and statute in ~6–12. Mixing rates forces the slow half through the fast half's review cycle.
- **Size ceiling** — ~15 KB per card. Over it, split along the three axes above.

> The reindex contract report will **not** catch this. Its oversize threshold is 80 K chars, five times the card ceiling — a 40 KB card passes it silently. Measure cards yourself: `find verdicts -name '*.md' -size +15k`.

**The domain splits too.** Cards have four axes and domains have none, so one subject quietly swallows the layer: measured on one vault, a single domain reached **57 cards and 1.24 MB — a third of everything**, which forced its generated index to 19 KB and its router row to 809 characters. **Past ~20 cards or ~300 KB, cut the domain into subdomains along the same four axes.** The router row is the gauge: a row you cannot state in one line is a domain that has stopped being one decision area.

**Only cards live in `verdicts/`.** The folder's genre marker is its path prefix, so anything else parked there is retrieved as if it were a ruling. Admit `type: canon` cards and the generated `INDEX.md`, nothing else — a deep-research report, a how-to guide, or a running tracker belongs in its theme folder with the card linking to it in one line. Measured on one vault: **9 non-card files totalling 356 KB** had accumulated inside the card roots, one of them a 72 KB report still carrying its Executive Summary and Sources — precisely the narrative Step 1 rules to leave behind.

Then write the card against the slot template in `ANATOMY.md`, and **spread the expiry**. `stale_after` comes from the fastest-decaying claim, but when a session mints six cards they inherit the same date and expire as one unreviewable batch. Scatter them across ±10 days so review arrives as a queue, not an avalanche.

**Done when** every card answers one question, asked at one moment, under one `stale_after`, within the ceiling — and every number, proper noun, parameter value, rejected option, dissent, and reversal from Step 1 appears in exactly one card.

### Close the loop minting opens

**A new card almost always overturns something an existing card asserts**, because the research that produced it went looking where the old cards were thin. For each card minted, ask what existing card owns each question it touches, and run Step 3 on that card now — rewrite its ruling line, cross-link both directions, log the reversal.

---

## Step 5 — Wire the router, and keep it a router

`verdicts.md` at the vault root is read on **every** question, so its byte count is a fixed cost charged to questions that have nothing to do with any card. The failure is gradual: rulings get richer, each row grows from one line to a paragraph, and one domain quietly takes a third of the file. Measured on one vault, a hub reached **155 KB — roughly 44 K tokens, 4.4 % of a 1 M context window, spent before the question was even read.**

**So the router holds one row per _domain_, not per card** — what the domain decides, how many cards, the earliest expiry, the link. Card-level routing is what `verdict-lookup.sh` is for. Split at ~12 KB.

> 🔴 **"One row per domain" is a count, and a count does not bound size.** Rows obey it and become paragraphs instead: measured on one vault, a compliant 13-row router still reached 15.7 KB, its longest row **1,019 characters**, carrying 18 edit markers and a section of work-in-progress. Three rules bound the row:
>
> - **≤160 characters.** A row says *what the domain decides*, never *what it decided* — the moment a ruling appears in the router it is a **mirror**, and the router is the copy nobody reindexes.
> - **No edit markers.** The router is state for the same reason a card is.
> - **No queues.** A "not yet landed" list is work in progress; it is charged to every question that will never care about it. Park it outside the hot path, or land the items.
>
> Better still, **generate the rows** — domain, card count, earliest expiry and link all exist in card frontmatter, so an `--emit-router` sibling to `--emit-index` cannot drift. Derived state is the only state that survives this layer's edit rate.

| Tier | Holds | Read when |
|---|---|---|
| `verdicts.md` — router | One row per domain | Every question |
| `verdict-lookup.sh` | Path · ruling · expiry, by keyword | To locate a card — **the normal path** |
| `verdicts/CHARTER.md` | The genre contract | Minting or restructuring a card |

### A ruling lives in exactly one card

Every extra copy is a **mirror**, and mirrors **drift** — the copy that goes stale is the one nobody reindexes, and it is what retrieval hands over. Any listing of cards is therefore **generated** from frontmatter and marked generated, because derived state cannot drift.

> 🔴 **A hand-maintained per-card index is this layer's strongest attractor and its worst investment.** Path, ruling and expiry already live in each card's frontmatter, so the index buys nothing a query does not return for free. Measured on one vault: a 99 KB domain index cost **63 hand edits across 200 commits**, went **last in BM25 on every query it matched** (length normalisation buries a file indexed as three giant sections), and still advertised a table its owning card had transferred away six days earlier. Reach for `--emit-index`-style generation instead, and an index that is *only* a mirror can be deleted outright.

**Done when** the router has a row per domain, every row resolves, and every ruling exists in exactly one card.

---

## Step 6 — Reindex, probe, promote

```bash
./reindex.sh          # or: python3 fts5-reindex.py
sqlite3 vault.fts5.db "SELECT rel_path, heading FROM notes_fts
  WHERE notes_fts MATCH '<question a future session would ask>'
    AND status != 'deprecated' ORDER BY bm25(notes_fts) LIMIT 3"
```

Probe with one realistic question per touched card. **A card that does not surface is a card that does not exist.** When a probe misses, sharpen the `description` and restate the subject noun inside the body of the section that should have matched — the retrieval unit is a section, not a file.

### Then check the slots, because surfacing is the easy half

```bash
for c in <touched cards>; do
  grep -q '^## Rejects' "$c" || echo "⛔ $c — no Rejects"
  grep -q '^## Appeal'  "$c" || echo "⛔ $c — no Appeal"
done
```

Surfacing is the easy half. Memory systems resolve *what the current state is* at **91 %** and then act on it in open-ended work at **32 %**, with the correct value already visible in **67.8 %** of those failures (Stale benchmark, via arXiv 2608.01619). Finding the card is the 91 %; the answer obeying it is the 32 %, and **the slots are what closes that gap** — a branch table turns an unstated assumption into a stated rule, and `Rejects` pre-empts the option the next session would re-litigate. `Appeal` is load-bearing twice over: without it an expired card collapses back into full re-investigation, the exact cost it was minted to avoid. Measured on one vault, **~31 % of cards were missing each.**

### Run the layer's lint before you finish

```bash
./verdict-lookup.sh --lint     # exits 1 on violations
```

Ceiling, edit markers, dated headings, missing slots, non-card files, domain size, router hygiene — one pass. **Every rule in this skill that shipped without a check has decayed, and every rule with a machine behind it has not:** on a 178-card vault, `stale_after` coverage stood at 100 %, generated-index drift at zero, and `type` violations at zero, while the prose-only rules sat at 30–56 % breach. Writing the rule more forcefully does not close that gap. Add the check.

Then settle promotion **in this session**, because a later session will not come. A card left at `status: draft` / `human_reviewed: false` is filtered out of the grounding pipeline it exists to short-circuit, so the next session re-researches the topic anyway. Report the open items, then ask outright whether to promote, naming what a human would be signing off on.

**Done when** every touched card surfaces in the top 3 on a realistic question, carries `Rejects` and `Appeal`, adds no new `--lint` violation, and is either promoted (`status: stable`, `human_reviewed: true`) with that decision recorded, or left draft with the reason stated.
