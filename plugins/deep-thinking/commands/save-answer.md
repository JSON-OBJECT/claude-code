---
description: Use when the user asks to save/preserve the previous answer ("이 답변 저장해", "이거 저장해", "save this answer", "이 답변 보관해") right after a grounded or researched answer — archives the question-answer pair VERBATIM as one md file in the vault's `_answers/` folder, which is permanently excluded from FTS5 indexing and /ground's default search (retrievable only on explicit user opt-in, as an `[A-crystal]` event record — never as topic evidence) so LLM-synthesized answers never feed back into LLM sources
allowed-tools: Read, Write, Bash, Grep, Glob
argument-hint: [optional slug override]
---

# Save-Answer Command — Save the Previous Q&A Pair

You are permanently archiving the **previous question-answer pair from THIS conversation** into the vault's `_answers/` folder. Optional slug override: **"$ARGUMENTS"**.

This implements the crystallization half of the wiki loop: good answers should not evaporate into chat history. But crystallized answers are **keepsakes for the human, never sources for the machine.**

---

## The Iron Law

```
SAVE INTO _answers/ ONLY — SAVING INTO A TOPIC FOLDER POISONS THE GROUNDING CORPUS.
THE ANSWER IS PRESERVED VERBATIM — NOT ONE CHARACTER OF Q OR A MAY CHANGE.
NEVER INDEX, NEVER PROMOTE — _answers/ IS OUTSIDE /ground's DEFAULT SEARCH.
OPT-IN RETRIEVAL IS EVENT-RECORD ONLY ([A-crystal]) — NEVER TOPIC EVIDENCE.
```

**Empirical baseline (recorded before this command existed):** an unguided agent asked to "save this answer" saved it into a topic directory (`software-engineering/`), ran the FTS5 reindex and proudly verified the answer now ranked #1 in BM25 search, "corrected" the answer's citations in place before saving, committed without staging discipline, and closed by recommending promotion to `human_reviewed: true` so /ground could cite it as primary evidence — the complete cognitive-debt loop (LLM output re-ingested as LLM source), executed in a single well-meaning pass. Every gate below exists because that actually happened.

**Violating the letter of this rule is violating the spirit of this command.**

---

## EXECUTE: The 4 Steps

### Step 1 — Capture (verbatim or abort)

- The **question** = the user's message that prompted the answer, verbatim.
- The **answer** = the full answer text you delivered, verbatim — including the Grounding summary, inline `file:line` citations, and the Sources list if present.
- **GATE:** both MUST be recoverable exactly from this conversation. If context compaction has destroyed the exact text, STOP and tell the user — NEVER reconstruct an approximation from memory. A crystallized answer that differs from what the user actually read is a forgery.

### Step 2 — File

- Path: `_answers/YYYY-MM-DD-<slug>.md` — today's date (the Q&A is a fixed event, so the date belongs in the filename), slug = 3–6 kebab-case words from the question (or `$ARGUMENTS` if given). On collision append `-2`, `-3`.
- If `_answers/` does not exist, create it.
- Template:

  ```markdown
  ---
  type: crystallized-answer
  generated_by: <your model id>
  human_reviewed: false
  asked_at: YYYY-MM-DD
  source_command: /ground   # or whatever produced the answer
  ---

  # <질문 한 줄 요약>

  ## 질문

  <verbatim>

  ## 답변

  <verbatim>
  ```

- `human_reviewed: false` is **permanent** for this type — see Step 3.

### Step 3 — Guard Verification

Before writing, verify the containment infrastructure is intact:

```bash
rg -n '"_answers"' fts5-reindex.py
```

- Hit → containment intact, proceed.
- No hit → **WARN the user in the report** and add `"_answers",` to `EXCLUDE_DIRS` before saving (this is the only permitted edit outside `_answers/`).
- Do **NOT** run `fts5-reindex.py` after saving — there is nothing to index; the folder is excluded by design. Running it anyway "to check" is the baseline failure.

### Step 4 — Commit and Report

- Stage ONLY the new file: `git add _answers/<file>` (NEVER `git add -A` — other sessions may have work in flight).
- Commit with a one-line message naming the question topic.
- Report: saved path, filename, and one sentence reminding that this file is outside /ground's default search by design — findable via `eza _answers/` or `rg` directly, or by explicitly asking /ground to `"include answers in search"` (retrieved as an `[A-crystal]` event record, never as topic evidence).

---

## Red Flags — STOP, You Are About to Poison the Corpus

If you catch yourself thinking:

- "A topic folder would make it easier to find later." — That folder IS the grounding corpus. `_answers/` only.
- "I'll reindex so it shows up in search." — Search visibility is the failure condition, not the goal.
- "The answer has a wrong citation — I'll fix it before saving." — You are archiving what the user read and approved, not an improved edition. Verbatim.
- "I'll polish/distill the answer for posterity." — Journals distill; crystals photocopy. Preservation is the entire point.
- "Once reviewed, this could be promoted to human_reviewed: true." — Crystallized answers are NEVER promotable. If the content deserves canon status, that is a NEW document authored through the normal ingest path (deep-research, journal) — never a flag flip on LLM chat output.
- "The exact answer text is gone, but I remember the gist." — Abort and say so. A reconstructed crystal is a forgery.
- "git add -A is faster." — You will sweep another session's in-flight work into your commit.

**ALL of these mean: STOP. Return to the Iron Law.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Making it searchable helps the user." | The user's explicit design goal is the opposite: LLM answers must never become LLM sources by default. The sanctioned path already exists — /ground's explicit opt-in retrieves crystals as `[A-crystal]` event records. Indexing adds nothing but poisoning risk. |
| "It cites real files, so it's as good as a source." | It is synthesis OVER sources. Citing it later means citing your own output as evidence — compounding hallucination with a provenance costume. |
| "Fixing the citation line numbers improves the record." | It silently changes what the user approved. If a citation is wrong, that's worth MENTIONING in the report — never editing into the saved text. |
| "This answer is so good it belongs in the topic folder." | Quality is not provenance. However good, it remains unreviewed LLM output; topic folders are for curated knowledge. |
| "human_reviewed: false is meant to be promoted eventually." | For ingest documents, yes. For type: crystallized-answer it is a permanent marker, because the quarantine is structural (folder), not procedural (flag). |
| "One reindex won't hurt — the folder is excluded anyway." | Then it is also pointless. The baseline agent's reindex is how an un-excluded save would silently succeed. Don't normalize the motion. |

---

## Quick Reference

| Step | Activity | Success Criterion |
|------|----------|-------------------|
| **1. Capture** | Q + A verbatim from this conversation | Exact text or explicit abort |
| **2. File** | `_answers/YYYY-MM-DD-<slug>.md` + frontmatter | Date in filename; `human_reviewed: false`; verbatim body |
| **3. Guard** | `rg '"_answers"' fts5-reindex.py` | Containment confirmed (or restored + warned); NO reindex |
| **4. Commit** | `git add <that file only>` + one-line message | Only the new file in the commit; path reported |

---

## Key Principles

- **Crystals are keepsakes, not sources.** The human rereads them; the machine retrieves them only on explicit user opt-in, and then only as `[A-crystal]` event records ("this was answered on that date") — never as evidence about the topic.
- **Photocopy, don't distill.** The value is "exactly what I was told that day" — the opposite of journal distillation.
- **Quarantine is structural.** The folder exclusion (fts5-reindex.py `EXCLUDE_DIRS` + /ground Stage 1) does the enforcement; no flag or good intention substitutes for it.
- **Date in filename.** A Q&A pair is a fixed event; `YYYY-MM-DD-` prefix follows the vault's filename convention.
- **Abort beats approximate.** No verbatim text, no crystal.

---

## Integration with Other Instructions

- **`fts5-reindex.py`** — `"_answers"` MUST remain in `EXCLUDE_DIRS`; Step 3 verifies on every run.
- **`/ground`** — Stage 1 default-excludes `_answers/` alongside `_inbox/` and `_archive/`. On explicit user opt-in (`"include answers in search"` / `"답변 포함해서 검색"`), /ground searches the folder via `Glob`/`Grep` (never the FTS5 index) and cites hits as `[A-crystal]` event records only — crystallized answers are never citable as topic evidence at any stage.
- **`/lint`** — mechanical link checks skip `_answers/` (its citation strings reference vault files as text, not as live links to validate).
- **`_answers/README.md`** in the vault documents the convention for human readers.

---

Now save the previous Q&A pair. Slug override: **"$ARGUMENTS"**
