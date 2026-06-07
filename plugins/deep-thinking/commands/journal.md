---
description: Turn a raw thought-dump into a clean, lineage-aware, ground-searchable entry in the monthly insight log — and refine past entries
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git:*), Bash(wc:*), Bash(awk:*), Bash(grep:*), Bash(ls:*), Bash(find:*), Bash(mkdir:*), Bash(sqlite3:*), Bash(python3:*), Bash(date:*), mcp__time__get_current_time, TodoWrite
argument-hint: "<raw thoughts>" [--mode=add|refine|promote|review]
---

# Writing a Journal Entry

You are turning the user's raw thought-dump — **"$ARGUMENTS"** — into one or more clean, restrained, deeplinkable entries in the month-anchored insight log at `journal/journal-YYYY-MM.md`.

> An incubator. A capture net. A fermenter.
> The complementary **opposite** of `/schedule`: there, prose is forbidden; here, the insight **is** the deliverable — but it stays terse, structured, and chunkable.

---

## The Iron Law

```
CAPTURE THE INSIGHT IN ITS LINEAGE — STRUCTURE AND SITUATE, NEVER FABRICATE.

Lose no detail the user gave. Fabricate no conclusion the user did not.
Find the past thought this insight extends, updates, or reverses — and link it.
One day = one H3 chunk. The entry is human-authored ground truth.
```

An insight is never born from nothing — it is the continuation of an earlier thought (yesterday's, or a year ago's) that it **supplements, updates, or completely reverses.** So you do NOT take the dump at face value. You search the local vault — *including past journal entries* — to recover that antecedent, grasp its context and background, and **situate the new insight against it with brilliant-but-minimal elaboration and source links.**

**Elaborate the context, not the conclusion.** You MAY add background, lineage, and a terse grounded note drawn from linked local sources. You MAY NOT invent the user's opinion, finish their half-thought, or fuse separate thoughts into a thesis. Situating ≠ synthesizing.

**Violating the letter of this rule is violating the spirit of `/journal`.**

If you find yourself writing a conclusion the user did not voice, a "common structure" across separate thoughts, copying a source instead of linking it, or more than ~7 substance bullets — STOP. You crossed from situating into fabricating.

---

## When to Use

Use `/journal` when:
- The user dumps a loose, unordered stream of thoughts/realizations and wants them recorded
- A daily/weekly insight needs to land in the searchable archive
- A past entry is inaccurate or stale and needs a faithful fix (`--mode=refine`)
- A matured insight should graduate to its own canonical doc (`--mode=promote`)

**Use this ESPECIALLY when (most tempting to freelance):**
- The dump is two or three unrelated thoughts at once → you will be tempted to weave them into one narrative. **Don't.** Split into separate entries.
- The insight connects to a deep-research doc → you will be tempted to copy that doc's facts in. **Don't.** Link, never copy.
- The thought feels half-baked → you will be tempted to "finish the thought" for the user. **Don't.** Capture it as a 🌱 fragment exactly as far as they took it.

**Do NOT use for:**
- Calendar events / purchases / activities → that is `/schedule` (pointers, no narrative)
- Answering a question from the archive → that is `/ground`

---

## The Complementary Pair

| | `/schedule` | **`/journal`** |
|---|---|---|
| Holds | pointers (bookmarks) | **the insight itself (prose)** |
| Source-of-truth | elsewhere | **is its own source — `human_reviewed: true`** |
| >7 bullets means | move detail out | **promote to a canonical doc** |
| Failure mode | narrative creep | **synthesis creep / verbosity** |

Both: **month = file, day = `### YYYY-MM-DD` H3 chunk.** Identical chunking so `/ground` retrieves a single day cleanly.

---

## The 2-Tier Incubator Model

```
Tier 1 — CAPTURE   journal/journal-YYYY-MM.md   (default --mode=add)
                   raw dump → 🌱 fragment entry, terse, grounded, filed by day

Tier 2 — PROMOTE   engineering/… finance/… philosophy/…   (--mode=promote)
                   a 🌿 recurring insight matures → its own canonical .md
                   the journal entry shrinks to a 🌳 pointer
```

Maturity markers (greppable pipeline — `rg '🌿' journal/` surfaces promotion candidates):

| Marker | Meaning |
|--------|---------|
| 🌱 `fragment` | first capture (default for every new entry) |
| 🌿 `recurring` | the theme has resurfaced ≥2× — promotion candidate |
| 🌳 `promoted → [link]` | graduated to a canonical doc; entry is now a pointer |

---

## EXECUTE: The 4 Phases (default `--mode=add`, sequential, no skipping)

### Phase 1 — Intake & Decode (the signature step)

**GATE: You cannot write anything until the dump is segmented and decoded without loss or invention.**

1. **Get today's date.** Call `mcp__time__get_current_time` (system timezone). Derive `YYYY-MM-DD` (entry anchor) and `YYYY-MM` (target file). If the user names a date ("yesterday", "last Tuesday"), use that instead.

2. **Segment into distinct insights.** Topic shifts and explicit signals ("and", "separately", "unrelated", "also") mark boundaries. **Each distinct insight = its own `### YYYY-MM-DD — title` entry.** If the user says two things are separate, they are separate. NEVER fuse them under a synthesized meta-thesis.

3. **Decode each segment into the user-substance fields — using ONLY what the user gave:**
   - **Insight** — the core realization, 1–2 sentences, conclusion-first
   - **Trigger** — what prompted it (if stated)
   - **Reasoning** — the logic or the *real variable* the user identified (preserve their sharp specifics: numbers, names, the actual lever — this is the detail you must NOT drop)
   - **So-what** — implication / open question (if stated)
   (The grounded fields — Lineage, Context, Links, Tags — are filled in Phase 2. Maturity defaults to 🌱.)

4. **Anti-loss / anti-fabrication double-check:**
   - **Lose nothing:** every concrete the user said (amounts, names, the precise insight) survives.
   - **Fabricate no conclusion:** no invented opinion, no "common structure" fusing separate thoughts, no finished half-thought. Unsure whether the user implied it? Leave it out or phrase it as their open question.
   - **Grounded context is allowed and wanted** (Phase 2) — but it must be sourced from a linked local doc, not from your own reasoning.

### Phase 2 — Ground & Trace the Lineage (Don't Take the Dump at Face Value)

**GATE: Before filing, you have (a) resolved every entity to its canonical vault anchor, and (b) found the antecedent thought this insight extends/updates/reverses.**

1. **Find canonical docs AND prior journal entries** for each topic/person/concept. Reuse `/ground` Stage 1 discovery — lightweight, no full read. **Search `journal/journal-*.md` too**, not just topic dirs — yesterday's or last year's entry is often the antecedent.
   ```bash
   sqlite3 vault.fts5.db -separator $'\t' "
     SELECT rel_path, bm25(notes_fts) AS s FROM notes_fts
     WHERE notes_fts MATCH '<keyword>'
       AND (human_reviewed != 'false' OR human_reviewed IS NULL)
     ORDER BY s LIMIT 3;"
   ```
   Quote hyphenated/multi-word terms: `MATCH '"context-switch" OR "context switch"'`. Fallback: `Grep` / `rg -l -t md`, `Glob`. Try EN/synonym/abbreviation variants.

2. **Identify the antecedent and classify the relationship:**
   - 🔗 **extends** — adds to / sharpens the prior thought
   - 🔄 **revises** — changes part of it with new information
   - ↩️ **reverses** — contradicts / overturns it
   Record a **Lineage** field linking the antecedent with the relationship verb. When the antecedent is another journal entry, link it fully-qualified: `[[journal/journal-YYYY-MM.md#anchor]]` (not a bare in-file anchor — `/ground` resolves file-qualified links across months). If none exists, say so: `Lineage: (new seed — no antecedent found)`.

3. **Add brilliant-but-minimal elaboration** (`Context`). One or two terse lines that situate the insight against the linked source's background — the context that makes the entry legible a year later. **Elaborate the context, not the conclusion:** background and lineage are grounded in the linked doc; the *opinion* stays the user's. Never exceed a couple of lines, never copy a passage — link and say "see [[…]]".

4. **Attach `Links`** (relative link + heading anchor when known) and inline `Tags` (`#tag`, trigram-searchable) drawn from the entities found.

### Phase 3 — File (Month File, Day Chunk, Human Provenance)

**GATE: The entry lands in the correct monthly file with provenance that survives `/ground`.**

1. **Resolve the target file** `journal/journal-YYYY-MM.md`.
   - **This is a living tracker named by subject (the month) — NOT a per-event dated file.** All of a month's day-entries accumulate here as H3 chunks. Do not create one file per day.
   - If `journal/` or the month file is missing → scaffold from the template below.
2. **Append each decoded entry** as a `### YYYY-MM-DD — title` section, sorted ascending. Same date, multiple distinct insights → multiple H3 entries.
3. **Update the `## Index` TOC** with an anchor line per new entry.
4. **Frontmatter provenance is NON-NEGOTIABLE:** `generated_by: human` + `human_reviewed: true`.
   - The insight is the user's; you only transcribed and filed it. It must be citable as a **primary `[H]` source** and must pass `/ground`'s `human_reviewed != 'false'` filter. `generated_by: claude-*` / `human_reviewed: false` would make the user's own journal **invisible and untrusted** to grounding — a catastrophic failure.
   - This provenance is honest ONLY because you obeyed the Iron Law (transcribe, don't synthesize). The moment you inject your own claims, this frontmatter becomes a lie. Don't.

### Phase 4 — Verify & Reindex

**GATE: Confirm chunkability, restraint, and link integrity; then refresh the search index.**

```bash
awk '{print length}' journal/journal-YYYY-MM.md | sort -n | tail -1   # longest line < ~400
grep -c '^### ' journal/journal-YYYY-MM.md                            # H3 day-chunks present
```
- **Substance budget:** the user-substance bullets (Insight · Reasoning · So-what) stay ≤ ~5; the grounded scaffold (Lineage · Context · Links · Tags · Maturity) does not count. If the *insight itself* needs more, it is no longer a fragment — flag it 🌿 and suggest `--mode=promote`.
- All `Links`/`Lineage` references resolve to existing files.
- TOC anchors match the new `### ` headings.
- Frontmatter shows `generated_by: human` / `human_reviewed: true`.
- Run `python3 fts5-reindex.py` so the new entry is BM25-searchable.

Report back: file path, entries added (titles + 🌱/🌿), lineage + links attached, reindex result.

---

## Modes

### `--mode=refine` — Seamlessly Correct or Update a Past Entry

The user points at an existing entry (from a few days ago or older) that is inaccurate, incomplete, or stale. Fix the **record** faithfully and invisibly — do not rewrite history into something it never was.

**GATE: You have located the exact target entry and understood it fully before changing one word.**

1. **Locate the target.** Use the date, quoted text, or topic the user gives. Search the right month file (and older months if needed): `grep -rn '^### ' journal/`, then `Read` the full entry in surrounding context. Confirm the exact `### YYYY-MM-DD — title` before editing.
2. **Understand it fully.** What did it claim? What are its Lineage, Links, Maturity? What exactly is wrong or stale per the user's request?
3. **Classify the change — this dictates the method:**
   - **Correction** (the entry recorded the thought wrong; a fact/typo is off) → edit in place, minimal diff, no trace. The goal is an accurate record.
   - **Enrichment** (a missing link, tag, or one clarifying line) → add it surgically; keep restraint.
   - **Change of mind** (the user now thinks differently — the old entry was a *faithful record of what they thought then*) → this is NOT a silent rewrite. It is a **new dated entry** whose **Lineage** 🔄 revises / ↩️ reverses the old one. Preserving the superseded thought is the entire point of a thinking-over-time log. If intent is ambiguous between "the record was wrong" and "I changed my mind," **ASK which.**
4. **Edit seamlessly.** Preserve structure, voice, and every still-correct part. Touch only what must change. If the title changes, update the H3 heading AND its TOC anchor. Never reformat or reorder unrelated entries.
5. **Re-ground if the change touches a topic** — re-resolve Links/Lineage for the edited content.
6. **Record & reindex.** Bump `Last updated` and run `python3 fts5-reindex.py`. File-change history lives in git — do NOT keep a manual changelog.

### `--mode=promote` — Graduate a Matured Insight

A 🌿 entry matured. Create a canonical doc in the right topic dir (deep-research-style frontmatter), move the substance there, and **replace the journal entry body with a 🌳 pointer**: `🌳 promoted → [[topic/…md]]`. The journal stops holding the story.

### `--mode=review` — Weekly Review Pass

List this month's 🌱/🌿 entries, surface anything that resurfaced (promotion candidate), fix tags/links. No new content invented.

---

## Anatomy of a Compliant Entry

```markdown
### 2026-06-07 — More tests on a god-object cement bad design, not quality
- **Insight:** Piling unit tests onto a class with five responsibilities locks in the bad design — cohesion is the lever, not coverage.
- **Trigger:** Reviewing a teammate's PR.
- **Reasoning:** Tests pin behavior in place; covering a god-object makes the wrong shape *harder* to change later. Split responsibilities first, then cover.
- **Lineage:** 🔄 revises [[engineering/testing-strategy-deep-research.md]] — the "raise coverage everywhere" stance now has a precondition: refactor for cohesion first.
- **So-what (open):** Where is the line — when is low coverage acceptable because the module is about to be split?
- **Links:** [[engineering/testing-strategy-deep-research.md]]
- **Tags:** #testing #refactoring #cohesion #code-review
- **Maturity:** 🌱 fragment
```

Substance = Insight · Reasoning · So-what (3 bullets, the user's own). Scaffold = Lineage · Links · Tags · Maturity (grounded, not counted). Conclusion-first, every concrete preserved, zero invented thesis, lineage traced to a prior doc.

**Two separate thoughts in one dump → two entries, no "common theme" section:**

```markdown
### 2026-06-07 — The cost of chat is the context-switch tax, not message count
- **Insight:** Defaulting to chat for quick questions is death by a thousand interrupts — the hidden variable is context-switch cost, not how many messages.
- **Trigger:** Caught my own habit of pinging instead of writing it down.
- **Reasoning:** Async docs batch the interrupt; chat distributes it across everyone's focus time.
- **Lineage:** 🔗 extends [[engineering/async-communication-deep-research.md]] with a personal failure mode.
- **Tags:** #async #focus #communication #deep-work
- **Maturity:** 🌱 fragment
```

## Anatomy of a Compliant File

```markdown
---
name: 2026-06 — Insight Journal
description: Chronological capture log of insights/realizations during 2026-06. Matured insights graduate to topic-dir canonical docs; pointers remain here.
type: journal-log
generated_by: human
human_reviewed: true
generated_at: 2026-06-07
tags: [journal, insight, log, 2026-06]
aliases: ["June 2026 journal", "2026-06 insight log"]
---

> **Role:** Incubator · capture net · fermenter. The opposite of `/schedule` — here prose is the deliverable (but restrained).
> **Chunk unit:** one insight = one `### YYYY-MM-DD — title` H3 anchor. Partial retrieval works at this granularity.
> **Promotion:** 🌳 = graduated to a canonical doc; body is a pointer only.
> **Last updated:** 2026-06-07
> **Siblings:** [journal-2026-05.md](journal-2026-05.md) · schedule [../schedules/schedule-2026-06.md](../schedules/schedule-2026-06.md)

---

## Index — This Month's Insights
- [2026-06-07 — More tests on a god-object cement bad design, not quality](#2026-06-07--more-tests-on-a-god-object-cement-bad-design-not-quality)

---

### 2026-06-07 — ...
- ...
```

---

## Red Flags — STOP and Re-read the Iron Law

If you catch yourself:
- Taking the dump at face value without searching for its antecedent → **you missed the lineage. Search `journal/` and topic docs first.**
- Writing a "common structure" / "what these two thoughts share" section across separate thoughts → **the user said they were separate. Split, don't synthesize.**
- Copying facts from a canonical doc into the entry → **link, don't copy.**
- Writing a Context note longer than ~2 lines → **over-elaborating. Trim and link.**
- Writing an 8th substance bullet or a second paragraph → **promotion signal, not a bigger fragment.**
- "Finishing" a half-formed thought the user trailed off on → **capture it half-formed as 🌱.**
- Setting `generated_by: claude-*` or `human_reviewed: false` → **you'd erase the entry from `/ground`. It's the user's insight: `human` / `true`.**
- Creating `journal/journal-2026-06-07-….md` (per-day file) → **wrong. Month file, day chunk.**
- (refine) Silently rewriting a past entry when the user actually changed their mind → **that erases the thinking-over-time record. New entry with Lineage instead.**
- (refine) Reformatting or reordering unrelated entries → **minimal diff only; touch one entry.**

**ALL of these mean: STOP. Situate and structure only what the user gave; file it by day in the month file.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "These two thoughts clearly connect — I'll add a synthesis note." | The user said they were separate. Forcing a thesis is inventing content. Two entries, no meta-section. |
| "The dump stands on its own; no need to search the past." | Every insight extends a prior thought. Search `journal/` + docs and classify it extends/revises/reverses. Missing the lineage loses the point. |
| "Adding context means I'm synthesizing — the Iron Law forbids it." | Elaborate the *context* (grounded, linked, minimal), not the *conclusion*. Situating is required; fabricating opinion is forbidden. |
| "It's my synthesis, so `generated_by: claude` is honest." | The *insight* is the user's; you transcribed it. `human` / `true` is correct AND required — otherwise `/ground` filters out the user's own journal. |
| "More detail = more useful. Let me expand it." | Verbosity kills chunk precision and buries the signal. ≤5 substance bullets. Over budget = promote, don't bloat. |
| "This canonical doc has great context — I'll fold it in." | Link, don't copy. Duplication drifts. The journal points; the doc holds the story. |
| "A per-day file is cleaner and more atomic." | Then partial month-level retrieval and the schedule-parallel break. Month = file, day = H3 chunk. Not negotiable. |
| "The thought is half-baked, I'll complete it." | A captured fragment is the point. Finishing it puts words in the user's mouth. Mark 🌱 and move on. |
| "(refine) The user wants it fixed, so I'll rewrite the old entry." | If they changed their mind, that's a NEW entry with Lineage; a silent rewrite destroys the record. Correction vs change-of-mind — ask. |
| "(refine) I'll rewrite the whole entry cleanly while I'm in there." | Minimal diff. Preserve the still-correct parts and the anchor. Refine one entry; never reformat the file. |
| "No need to reindex for one entry." | `python3 fts5-reindex.py` is ~7s. Without it the entry isn't BM25-searchable — defeating the entire purpose. |

---

## Quick Reference

| Mode / Phase | Activity | Tool | Success Criterion |
|--------------|----------|------|-------------------|
| **add · 1. Decode** | Date + segment dump into distinct insights; fill substance fields from user's words only | `mcp__time__*` | No detail lost, no conclusion invented, "separate" respected |
| **add · 2. Ground** | Resolve entities + find antecedent in docs AND `journal/`; classify extends/revises/reverses; minimal Context | `sqlite3 vault.fts5.db` / `Grep` / `Glob` | Lineage + cross-refs resolve; context links, not copies |
| **add · 3. File** | Append `### YYYY-MM-DD —` to month file; update TOC; `human` / `true` frontmatter | `Read`/`Write`/`Edit` | Month file, day chunk, provenance survives `/ground` |
| **add · 4. Verify** | ≤5 substance bullets, longest line <400, links resolve; reindex | `awk`/`grep`/`python3 fts5-reindex.py` | Chunkable, restrained, BM25-searchable |
| **refine** | Locate exact entry, classify correction vs change-of-mind, edit seamlessly | `Grep`/`Read`/`Edit` | Minimal diff; record stays faithful; reindexed |
| **promote** | Graduate 🌿 → canonical doc; entry becomes 🌳 pointer | `Write`/`Edit` | Story moved out; pointer left behind |

---

## Key Principles

- **Transcribe, don't synthesize.** Structure the user's words; never add your own conclusion. This is what makes `human` / `true` provenance honest.
- **Every insight has an ancestor.** Find the prior thought it extends/revises/reverses — in docs and in past journal entries — and link it.
- **Elaborate the context, not the conclusion.** Grounded, linked, minimal background is wanted; invented opinion is forbidden.
- **Month = file, day = chunk.** `journal/journal-YYYY-MM.md`, `### YYYY-MM-DD —` H3 anchors enable partial retrieval — mirrors `/schedule`.
- **Restraint is the format.** ≤5 substance bullets, conclusion-first. Over budget = promotion signal, not a bigger entry.
- **Refine the record, don't rewrite history.** Fix what was wrong in place; a change of mind is a new entry with lineage, not an erasure.
- **Human-authored ground truth.** `generated_by: human`, `human_reviewed: true` — or `/ground` erases the user's own journal.
- **Capture beats polish.** A terse 🌱 fragment filed today > a perfect essay never written. Low friction sustains the habit.

---

## Integration with Other Commands

- **`/schedule`** — the complementary opposite. Activities/purchases go there as pointers; insights come here as prose. Entries may cross-ref each other.
- **`/ground`** — consumes this log. Entries with `human_reviewed: true` are citable as primary `[H]` sources; the `### YYYY-MM-DD` H3 anchors are its Stage-2 chunk units.
- **`fts5-reindex.py`** — run after every `add` / `refine` / `promote` so the change enters `vault.fts5.db` for BM25 search.
- **Global `~/.claude/CLAUDE.md`** — modern-CLI mapping (`rg`, `fd`) and `mcp__time__*` for timestamps apply to all shell/date steps here.

---

Now act on the mode for: **"$ARGUMENTS"** (default `--mode=add` if no mode given).
