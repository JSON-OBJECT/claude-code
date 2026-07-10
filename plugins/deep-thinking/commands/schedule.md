---
description: Use when creating or refactoring schedule/calendar markdown files into ground-truth indexes — produces month-anchored, bookmark-style documents optimized for grounding, RAG retrieval, and chunk-based parsing instead of narrative-stuffed tables
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git:*), Bash(wc:*), Bash(awk:*), Bash(grep:*), Bash(ls:*), Bash(find:*), Bash(mkdir:*), Bash(mv:*), Bash(rm:*), Bash(diff:*), TodoWrite
argument-hint: [path-to-file-or-directory] [--mode=create|refine|audit] [--scope=year|brand|project]
---

# Writing a Schedule Index

> A calendar. A bookmark. An anchor.
> Not a journal. Not a narrative. Not a place where context goes to die.

---

## The Iron Law

```
A SCHEDULE INDEX HOLDS POINTERS, NOT STORIES.

Every entry is a deeplinkable bookmark.
Every detail lives in the source-of-truth document it points to.
File-change history lives in git — never a manual changelog or the header.
```

**Violating the letter of this rule is violating the spirit of this command.**

If you find yourself writing more than ~7 bullet facts under a single event, stop. The narrative belongs in the source-of-truth document (weekly report, meeting note, ticket, postmortem). The index records *that the event happened, when, who, and where the detail lives*.

---

## When to Use

**Create or refine a schedule index when:**
- A schedule/calendar file has table cells exceeding ~500 characters
- Frontmatter or header is accumulating update history inline (git already records changes)
- The same event appears in multiple files with diverging wording
- An LLM grounding/RAG pipeline can't chunk the file because rows contain prose
- Multiple orthogonal axes (time, brand, project, domain) are mixed in one file
- You are about to add a new schedule/calendar markdown from scratch

**Do NOT use for:**
- Project postmortems or retrospectives (they ARE narrative)
- Single-event meeting notes (use a meeting-notes skill/template)
- Operational runbooks (those need full procedure, not pointers)
- Anything where the prose IS the deliverable

---

## Core Principles

### 1. Index, not journal
The file answers "what happened on date X" with one bookmark, then defers to the source-of-truth document for everything else.

### 2. One event = one heading-anchored sub-section
Every event is a markdown sub-heading (`### YYYY-MM-DD [HH:MM TZ] — Title`). This is the fundamental chunk unit for grounding. Tables hold summary rows only; long-form events get sub-headings.

### 3. Month is a section, year is a file
`## YYYY-MM` H2 anchors create deterministic month-level chunks. Years are separate files. Quarters and "ongoing"/"undated" go into clearly labeled sections at the bottom.

### 4. Time-slot homogeneity per section
Absolute timestamps, weekly windows, conditional triggers, and vague placeholders never share a table. Each gets its own labeled section so chunkers can parse cleanly.

### 5. Cross-ref over copy
When the same event would appear in multiple indexes (events vs launches vs trips), pick one canonical home and have the others link to it. Duplication causes drift.

### 7. Source-of-truth links are mandatory
Every event with non-trivial detail MUST link to where the detail lives: weekly reports, meeting notes, ticket trackers, document IDs. The index promises *the pointer is correct*; it does not promise *to hold the full story*.

---

## Anatomy of a Compliant Entry

```markdown
### 2026-05-13 14:00 KST — Service X v2 Production Release
- **Owner:** Team Alpha (Lead: J. Doe)
- **Status:** ✅ Released
- **Linked items:** PR #1234 · Ticket PROJ-567 · Runbook RBK-89
- **Source-of-truth:** [team-alpha/weekly/2026-W19](../weekly-reports/team-alpha/2026-w19.md) · meeting note `notion://abc123`
- **Cross-ref:** [[2026-launches.md#service-x-v2]] (canonical home)
```

That is the entire entry. Six lines. If you want to know *why* the release was at 14:00 KST instead of 09:00, *who* objected, *what* the rollback plan was — read the source-of-truth document.

---

## Anatomy of a Compliant File

```markdown
---
name: YYYY — [Domain] Schedule Index
description: Chronological bookmark index of [domain] events for YYYY. Pointers + primary-source cross-refs only; narrative lives in source-of-truth docs.
type: schedule-index
timestamp: YYYY-MM-DDT00:00:00+09:00
generated_by: human
human_reviewed: true
tags: [schedule, calendar, index, YYYY]
aliases: []
---

# YYYY [Domain] Index

> **Role:** Calendar · Bookmark · Anchor. Pointers + 1st-source cross-refs only.
>          Detailed narrative lives in source-of-truth documents (linked).
> **Last updated:** YYYY-MM-DD
> **Sibling indexes:** [other-index-1.md] · [other-index-2.md]

---

## 📅 Month Index
- [YYYY-01](#yyyy-01) — one-line theme
- [YYYY-02](#yyyy-02) — one-line theme
- [Standing items (no date)](#standing-items)
- [Recurring meetings](#recurring-meetings)
- [Historical context (~prev period)](#historical-context)

---

## YYYY-01

### YYYY-01-DD — Event 1
- bullets ...

### YYYY-01-DD — Event 2
- bullets ...

## YYYY-02
...

## Standing items
### Trigger: <condition met>
- Event ...

## Recurring meetings
| Cadence | Meeting | Attendees |
|---------|---------|-----------|

## Historical context
### YYYY-MM-DD ~ YYYY-MM-DD — Earlier event for context
- bullets ...

---

## Related documents
- [sibling-index.md] — short purpose
```

---

## Workflow

### Phase 0 — Parse arguments and locate target

1. Determine `--mode`:
   - `create` — no existing file, build from raw notes/transcripts/source documents
   - `refine` — existing file with anti-patterns, refactor in place
   - `audit` — read-only diagnostic, output a problem list and recommended actions
2. Determine `--scope`:
   - `year` (default) — one file per year, months as H2
   - `brand` / `project` — single-domain file, time still as H2 by month
3. Resolve target path. If a directory is given, list all `*.md` candidates and ask which to operate on (or audit all).

### Phase 1 — Diagnose (RED)

Run these measurements **before** writing anything:

```bash
wc -l <target>
awk '{print length}' <target> | sort -n | tail -5     # longest lines = chunk size
grep -c '^### ' <target>                              # H3 anchors (event count)
grep -c '^## ' <target>                               # H2 anchors (month/category)
```

Flag every issue found. Common findings:
- Longest line > 500 chars → "big cell narrative" anti-pattern
- H3 anchor count of 0 → no event-level bookmarks
- Frontmatter keys beyond the standard contract (`name`, `description`, `type`, `timestamp`, `generated_by`, `human_reviewed`, `tags`, `aliases`) → update history accumulating in header (belongs in git). Refresh `timestamp` on every meaningful edit; never append dated history lines.
- Same event found via `grep` in multiple sibling files → duplication drift

Report these findings to the human partner BEFORE proposing edits. In `audit` mode, stop here and output the diagnostic.

### Phase 2 — Plan (GREEN)

Propose a minimal restructuring plan:
1. Map every existing table row to a `### YYYY-MM-DD — Title` sub-section
2. Identify month boundaries — assign each event to a `## YYYY-MM`
3. Separate orthogonal sections: dated events, standing items (undated/conditional), recurring meetings, historical context
4. Identify duplications across sibling indexes — pick canonical home, replace others with cross-ref
5. Strip any accumulated update history from the header — `git log` already records it; do NOT create a CHANGELOG

Surface the plan to the human partner before mass edits. Do not proceed without confirmation when refactoring an existing high-traffic file.

### Phase 3 — Execute

For `refine`:
- Write the new file alongside the original (e.g. `2026-events.md` next to `major-events-2026.md`) — do NOT delete the original until cross-refs are verified
- Strip any accumulated update history from the header — git preserves change history; do NOT keep a manual CHANGELOG
- Update sibling indexes' cross-refs

For `create`:
- Build the file from the template above
- Populate `## Month Index` + month sections from source notes
- Always include the role banner (no changelog pointer — file-change history lives in git)

### Phase 4 — Verify

```bash
# Length budget
awk '{print length}' <new-file> | sort -n | tail -1   # MUST be < 500
grep -c '^### ' <new-file>                            # MUST be > 0
grep -c '^## ' <new-file>                             # SHOULD include all months

# Cross-ref integrity
for link in $(grep -oE '\.\.?/[^)]+\.md' <new-file>); do
  test -f <resolved-path> && echo "✅ $link" || echo "❌ BROKEN: $link"
done

# Duplication check (event titles appearing in multiple sibling files)
grep -oE '^### [^|]+$' <new-file> | sort -u
```

Report metrics in a before/after table:

| Metric | Before | After |
|--------|--------|-------|
| Longest line | N chars | M chars |
| H3 event anchors | N | M |
| H2 month/category anchors | N | M |
| Frontmatter lines | N | M |
| Broken cross-refs | N | 0 |

### Phase 5 — Cutover

When metrics confirm success:
1. Sync any remaining local-modification edits from the original into the new file (run `git diff` on the original)
2. Update sibling indexes' cross-refs to point to the new file
3. Update external references (search the wider repository with `grep -rn`)
4. `git rm` the original (history is preserved by git) — do NOT keep dead originals around as "backup"; ambiguous source of truth is worse than no backup
5. Commit only after the human partner approves

---

## Anti-Patterns

### ❌ Big cell narrative
A single table cell with 1,000–10,000 characters of running prose. Chunkers can't split it. Grounding returns the whole cell as one match — 95% noise.

**Fix:** Convert the row to a `### YYYY-MM-DD — Title` sub-section with bullets.

### ❌ Frontmatter update-history accumulation
"Last updated: 2026-05-22 — added X — also Y — also Z — also W…" growing for months until the header is 5,000 characters of nested update history.

**Fix:** One `Last updated` line in the header. Change history lives in git (`git log`) — never a manual CHANGELOG.

### ❌ Mixed time slots in one table
Absolute dates, week labels, conditional triggers, and "TBD" sharing rows. Algorithmic month extraction breaks.

**Fix:** Separate sections. Dated events under `## YYYY-MM`. Conditional triggers under `## Standing items`. Vague slots under their own labeled section.

### ❌ Same event in 3+ files
Event X is in events.md, launches.md, and trips.md, each with diverging wording. Updates apply to one file and silently drift in others.

**Fix:** Pick one canonical home. Other files cross-ref it via wikilink-style anchor: `[[2026-launches.md#event-x]]`.

### ❌ Multi-axis file
One file mixing year + brand + project + domain history. Readers and chunkers can't tell what's in scope.

**Fix:** One axis per file. Move domain-bound projects (brand-specific timelines, system-history documents) into a `projects/` subdirectory.

### ❌ Detail-in-index instinct
"This event is too important to just bookmark — let me put the full story here."

**Fix:** No. The full story belongs in its source-of-truth document (weekly report / meeting note / ticket / postmortem). The index links to it. If the source-of-truth document does not exist yet, *create that document first*, then link to it from the index.

### ❌ Original-as-backup
Keeping the old narrative-stuffed file around "just in case" after migration.

**Fix:** Delete with `git rm` after cutover. Git history preserves the original. Two files claiming to be the schedule = ambiguous truth.

---

## Rationalizations and Counters

| Rationalization | Reality |
|-----------------|---------|
| "This event is critical and needs the full context inline" | The full context belongs in the source-of-truth document, where it can be maintained. The index records that the event happened. |
| "I'll just add a few more lines to the table cell" | Cell prose grows monotonically. Once you allow it, it never stops. Convert to sub-section now. |
| "The update history in the header is fine — it's only one paragraph" | One paragraph today is twelve paragraphs in three months. Keep one `Last updated` line; `git log` records the rest. |
| "Both files should have the event for findability" | Findability comes from anchors and cross-refs, not duplication. Pick a canonical home. |
| "I'll keep the original file around just in case" | Git history is the backup. Two files that both claim to be the truth produce drift. Delete after cutover. |
| "It's a quick fix — I'll skip the audit phase" | Quick fixes that skip diagnosis create the very anti-pattern this command exists to prevent. Run the audit. |
| "The user only asked to add one event, not refactor" | Adding to a structurally-broken file deepens the brokenness. If audit reveals anti-patterns, surface them before adding. |
| "This file is special and the rules don't apply" | The rules exist precisely because every owner thinks their file is special. Apply them. |

---

## Red Flags — Stop and Reset

Stop and re-read this command if you catch yourself:

- Writing a third bullet of running prose under a single event
- Pasting accumulated change history into the header
- Creating an entry that duplicates one in a sibling file with slightly different wording
- "Adapting" the template instead of following it
- Skipping the diagnostic phase because "the file looks fine"
- Keeping the original file as a fallback after migration

All of these mean: re-anchor on the Iron Law. The index holds pointers, not stories.

---

## Quick Reference

| Need | Pattern |
|------|---------|
| New event | `### YYYY-MM-DD [HH:MM TZ] — Title` with ≤7 bullet facts + source-of-truth link |
| New month section | `## YYYY-MM` H2 + entries underneath, sorted ascending |
| Event spanning days | `### YYYY-MM-DD ~ YYYY-MM-DD — Title` |
| Conditional/undated | Place under `## Standing items` with trigger label |
| Recurring meeting | Single row in `## Recurring meetings` table |
| Cross-file event | Link to canonical home: `[[other-index.md#event-anchor]]` |
| Update history | Lives in git (`git log`) — never the header, never a manual CHANGELOG |
| Past context | `## Historical context` section at the bottom |

---

## Quality Checklist

Use TodoWrite to track each item.

**Diagnostic (RED):**
- [ ] Measured longest line, H3 count, H2 count, frontmatter line count
- [ ] Cross-checked event titles against sibling indexes for duplication
- [ ] Surfaced findings to the human partner before edits

**Restructure (GREEN):**
- [ ] One event = one `### YYYY-MM-DD — Title` sub-section
- [ ] Months as `## YYYY-MM` H2 anchors
- [ ] Orthogonal sections separated (dated · standing · recurring · historical)
- [ ] Every non-trivial event has a source-of-truth link
- [ ] Cross-refs replace duplication across sibling indexes

**Verify (REFACTOR):**
- [ ] Longest line < 500 chars
- [ ] H3 anchor count > 0 and matches event count
- [ ] All cross-ref links resolve to existing files
- [ ] Local modifications from the original synced into the new file
- [ ] External references (`grep -rn` in repo) updated

**Cutover:**
- [ ] Before/after metrics table reported
- [ ] Original file removed via `git rm` after partner confirmation

---

## The Bottom Line

A schedule index that holds narrative is a journal pretending to be an index.
A schedule index that holds pointers is a tool the rest of the knowledge base can rely on.

If a future agent or grounding pipeline can't extract one event cleanly with `awk '/^## YYYY-MM$/,/^## /'` or `grep '^### YYYY-MM-DD'`, the index has failed at its job.

Pointers, not stories.
