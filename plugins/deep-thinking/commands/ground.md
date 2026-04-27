---
description: Generate grounded answers from local markdown archive (5-Stage pipeline)
allowed-tools: Glob, Grep, Read, Bash, Agent, Edit, Write
argument-hint: <question or topic>
---

# Markdown Source Grounding Command

You are answering **"$ARGUMENTS"** using ONLY the local `.md` archive as primary source.

---

## The Iron Law

```
NO ANSWER WITHOUT LOCAL .md SOURCE GROUNDING FIRST.
NO FULL-FILE READ WITHOUT HEADING SCAN FIRST — CONTEXT IS A FINITE BUDGET.
EVERY CLAIM MUST CITE file:line.
```

This repository is a curated archive of long-form deep-research `.md` files. Your training data does NOT include the user's curated angle. The local archive is ground truth; web is a supplement for gaps only.

A 150K-char file consumes ~42K tokens — 4.2% of a 1M context window. Three such files cold-read simultaneously trigger compaction and lose prior work context. This is why **every stage exists**: narrow first, read last, read only what you need.

**Violating the letter of this rule is violating the spirit of this command.**

---

## EXECUTE: The 5 Stages (Sequential, No Skipping)

### Stage 0 — Tool Layer Awareness

**GATE: Before any search, distinguish the three layers.**

1. **Claude Code internal tools** (preferred for in-agent grounding)
   - `Glob` — filename/path patterns
   - `Grep` — content search (ripgrep-backed; respects `.gitignore`)
   - `Read` — verified, line-numbered file reading
   - `Agent` with `subagent_type=Explore` — multi-round, parallel exploration that protects the main context window

2. **Shell modern CLI** (via `Bash`, when a pipeline is required)
   - `fd` (NEVER `find`), `rg` (NEVER `grep`), `bat`, `sd`, `fzf`, `scc`/`tokei`
   - **`mq`** — jq for Markdown: AST-level heading/link/code-block extraction (`mq '.h2' file.md`)
   - **`yq --front-matter="extract"`** — YAML frontmatter field extraction from `.md` files
   - **`glow`** — terminal markdown renderer for visual verification
   - **`lychee`** — async link validator for archive maintenance (`lychee "**/*.md"`)
   - If `~/.ripgreprc` exists with `--type-add=research:*.md`, use `rg --type research` for markdown-only searches

3. **MCP semantic search** (for natural-language queries when keyword search fails)
   - `qmd` (MCP server) — BM25 + vector semantic search over markdown archives
   - `markdown-vault-mcp` — frontmatter-aware indexed search
   - `mq-mcp` — markdown AST queries via MCP

**Rule:** Default to internal tools. Drop to shell for pipelines (`rg -l … | xargs sd …`) or features internal tools lack. Use MCP semantic search only when Stage 1 keyword search returns zero after synonym/multilingual attempts.

### Stage 1 — Discovery (Narrow the Candidate Set)

**GATE: You cannot read anything until you know which files are candidates.**

1. **Filename / path match** (cheapest, always first)
   - Internal: `Glob` with `pattern="**/*<keyword>*.md"`
   - Shell: `fd -e md <keyword>`
   - **ALWAYS try multi-language variants in the same step:** e.g., a drug's brand name / its Korean transliteration / its generic chemical name. Empirical: EN+KR+generic-name triple search expanded 4→8 files in testing.
   - **Default exclude `_inbox/`, `_archive/`** — `_inbox/` holds Web-Clipper-ingested unreviewed notes (prompt injection surface), `_archive/` is explicit burial. Include only when user explicitly asks (`"include inbox in search"`).

2. **Content match** (only files that actually mention the keyword)
   - **Preferred when `vault.fts5.db` exists at repo root — BM25-ranked file list:**
     ```bash
     sqlite3 vault.fts5.db -separator $'\t' "
       SELECT rel_path, bm25(notes_fts) AS score
       FROM notes_fts
       WHERE notes_fts MATCH '<keyword>'
         AND (human_reviewed != 'false' OR human_reviewed IS NULL)
       ORDER BY score LIMIT 10;"
     ```
     BM25 returns files **ranked by keyword density** (TF-IDF), not alphabetical. The top 5 of a 30-file match are the ones to read; the rest are passing mentions. This is the single biggest context-budget saver Stage 1 offers.
   - **Fallback when DB absent or returns 0** (DB may be stale; run `python3 fts5-reindex.py` — 3s for 200 files):
     - Internal: `Grep` with `pattern=<keyword>`, `output_mode="files_with_matches"`, `type="md"`
     - Shell: `rg -l -t md '<keyword>'`
   - Try synonym/abbreviation variants in this step: brand names, abbreviations, synonyms
   - **FTS5 supports phrase + NEAR queries** that ripgrep cannot: `MATCH '"Series B funding"'` (exact phrase), `MATCH 'NEAR("brand-name" "investment", 20)'` (within 20 tokens). Use these for compound/relational questions.

3. **Frontmatter-based filtering** (when files have YAML frontmatter)
   - Shell: `fd -e md -x yq --front-matter="extract" '.tags[]' {} \; -print | rg '<keyword>'`

4. **Absence determination** (CRITICAL)
   - **Distinguish "no dedicated file" from "merely mentioned in passing."**
   - `Glob` = 0 AND `Grep` results only contain passing mentions (keyword NOT in H1~H3 headings) → topic absent, Stage 5 authorized
   - `Glob` = 0 BUT `Grep` results have keyword in headings → adopt as candidate
   - Verification method: extract headings with `mq '.h2'` from Grep result files and check if keyword appears in **H1~H3 headings**

5. **Directory structure as coverage signal**
   - Check if `Glob` results reveal a **dedicated subdirectory** (e.g., `topic-area/person-name/` = 6+ file archive on that subject)
   - Dedicated directory exists → treat entire directory as candidate pool
   - No dedicated directory, files scattered across folders → adopt only files where keyword appears in H1~H3 headings

6. **Question-type-aware filtering** (CRITICAL for interpretive questions)
   - Factual questions ("price of X?") → data/spec files first
   - Interpretive questions ("define X as a person?") → philosophy/archetype/analysis files first, raw meeting notes as support
   - Comparative questions ("X vs Y?") → both sides' dedicated files needed
   - Empirical: an interpretive question about a person → 24 Grep results filtered to 4 (philosophy, archetype, meeting notes, public record) for cross-synthesis

7. **Candidate volume triage**
   - 1–4 candidates → proceed directly to Stage 2–4
   - 5+ candidates → delegate to `Agent(subagent_type=Explore, thoroughness="very thorough")` to protect main context. Empirical: vintage fashion search hit 15 files — direct processing would exhaust context budget

### Stage 2 — Map (Heading Scan, Never Read Cold)

**GATE: Files >500 lines MUST be mapped before they are read.**

Long-form `.md` files in this repo routinely exceed 2,000 lines. Reading top-to-bottom wastes context.

1. Extract the table of contents:
   - **Preferred — `mq` (AST-level, zero false positives):**
     `mq '.h2' <candidate>.md` — extracts real H2 headings, ignoring `##` inside code blocks
   - Internal fallback: `Grep` with `pattern="^#{1,3}\s"`, `path=<candidate>`, `output_mode="content"`, `-n=true`
   - Shell fallback: `rg -n '^#{1,3}\s' <candidate>.md`

2. Identify the 1–3 sections most likely to answer the question. Record their line ranges.

**Why mq over rg (empirical):** `rg '^## '` matches `## comment` inside code blocks (false positive). Empirical test: in a tech doc with code blocks, rg returned 10 headings vs mq returned 6 — **4 false positives (40% error rate)** from `## Project`, `## Commands` etc. inside a markdown code block. In pure prose files (fashion, health, places), mq = rg (identical results). **Since you cannot know whether code blocks exist before opening the file, use mq as default.**

### Stage 3 — Pinpoint (Context Extraction)

**GATE: Cite-grade answers require line-anchored context, not paraphrased recall.**

Pull the exact passages with surrounding context for citation:

- Internal: `Grep` with `output_mode="content"`, `-C=5`, `-n=true` (line numbers are required for `file:line` citations)
- Shell: `rg -n -C 5 '<keyword>' <candidate>.md`

**Multi-file cross-reference:** For interpretive/synthetic questions, a single file NEVER completes the answer. Pinpoint across ALL candidate files and synthesize at intersection points. Empirical: an interpretive question about a person → 4 files each provided a different layer (aesthetic conviction, structural loneliness, future-reverse thinking, personal philosophy) — cross-synthesized into one answer.

**Concept-level search:** For interpretive questions, search **related concepts**, not just the question's literal keywords. Example: question about "essence as a human" → search `loneliness`, `conviction`, `yearning`, `DNA`, `archetype`, not just "essence."

Every claim in your final answer MUST be traceable to a `file:line` from this stage.

### Stage 4 — Verify (Targeted Read)

**GATE: Never quote a passage you have not Read in full surrounding context.**

- Use `Read` with `offset` and `limit` to load only the identified section.
- For very large sweeps across many files or naming conventions, delegate to `Agent(subagent_type=Explore, thoroughness="very thorough")` and consume only the summary — this preserves the main context window.
- **Frontmatter provenance gate (CRITICAL — closes the cognitive-debt loop):** before quoting a passage as a primary source, check the file's frontmatter:
  ```bash
  yq --front-matter=extract '.generated_by, .human_reviewed' <candidate>.md
  ```
  - `generated_by: claude-*` AND `human_reviewed: false` → **the file is LLM-synthesized and unreviewed.** Do NOT cite as primary evidence. Use only as boilerplate context, and surface a warning in the Grounding summary that human review is required.
  - `human_reviewed: true` OR no `generated_by` field → human-authored or human-validated, citable as a primary source.
  - **Why:** if the agent cites its own past synthesis as truth, every subsequent answer compounds prior hallucinations. The MIT Kosmyna cognitive-debt mechanism is exactly this closed loop. The gate breaks it.
- **Detail vs Summary rule:** When **detailed entries** (date/place/item per individual row) AND **summary paragraphs** (compressed into one block) coexist in the same file, the **detailed entries are the canonical source.** Summaries compress and merge entities. Empirical: "Store A → Item X, Store B → Item Y" (2 stores, 2 items) were merged into "found in [district]" in the summary — causing incorrect store attribution.
- **Human verification:** `glow <file>.md` renders the markdown in-terminal — use to visually confirm tables, links, and heading structure are intact.

### Stage 5 — Augment (Web/Social, Only the Gaps)

**GATE: Web search is authorized ONLY for facts the local corpus demonstrably lacks or for explicit freshness needs.**

- Use `mcp__brave-search__*` (sequential, never parallel — rate limits).
- Use `mcp__reddit__*` for community signal, `mcp__fetch__fetch` for page extraction.
- Cite web sources by URL alongside the local `file:line` citations from Stages 3–4.

---

## Output Format

### Structure your answer as:

1. **Grounding summary**: Which files were found (Glob/Grep counts), which sections were relevant
2. **Answer**: The substantive answer with inline `file:line` citations for every claim
3. **Sources**: List all cited `file:line` references at the end

### Citation format:

Mark every citation with provenance so the reader (and future you) can distinguish human authorship from LLM synthesis:

> `[H] filename.md:123` — human-authored note (no `generated_by` field, OR `human_reviewed: true`)
> `[A-reviewed] filename.md:123` — LLM-synthesized but human-reviewed (`generated_by: claude-*`, `human_reviewed: true`)
> `[A-unreviewed] filename.md:123` — LLM-synthesized, NOT yet reviewed — supporting context only, never as primary evidence

If `[A-unreviewed]` appears in the Sources list, the Grounding summary MUST flag *"This answer references unreviewed synthesis notes as supporting context only — they cannot be cited as primary sources until promoted to `human_reviewed: true`."*

### Default Voice — Narrative, Not Inventory

The **Answer** section MUST be written as **flowing narrative prose with metaphor**, not a bullet-point data dump. This is the default voice when the user does not specify one.

- **Easy, friendly tone.** Plain sentences a non-expert can read without stopping. No jargon without an inline gloss.
- **Narrative arc.** Lead with tension or a scene. Move cause → consequence → meaning. Connect facts with connective tissue ("however", "right at this point", "this is where the story twists").
- **Metaphor as cognitive anchor.** For every abstract claim (philosophy, strategy, relational dynamic), embed a concrete analogy so the reader's brain can grip it. A well-placed metaphor > three bullet points.
- **Insight over inventory.** Each paragraph MUST deliver a "so what" — why this fact matters, what it reveals, how it connects. A fact without interpretation is a failed paragraph.
- **Citations stay inline.** `file:line` references embed inside the prose, not at the end of bullet points. Narrative flow is not an excuse to drop provenance.

**Override clause:** If the user explicitly requests a different format (table, checklist, terse bullets, technical spec), follow that request. Otherwise this narrative-metaphor voice is the default — do NOT wait to be asked.

**Red flag in output:** If your draft Answer reads like a Wikipedia infobox or a bulleted fact list, STOP and rewrite as prose. Bullets are for the Grounding summary and Sources sections, NEVER for the Answer body (unless explicitly requested).

---

## Context Budget — Why Every Stage Exists

| File size | Tokens (est.) | 1M context % | Risk |
|-----------|--------------|--------------|------|
| 30K chars | ~8K tokens | 0.8% | Safe |
| 80K chars | ~22K tokens | 2.2% | Caution |
| 150K chars | ~42K tokens | 4.2% | Dangerous — Lost in the Middle effect |
| 3 files × 100K | ~84K tokens | 8.4% | Compaction triggers, prior work lost |

File reads consume **~96% of context** in typical sessions. The 5 Stages exist to ensure you read **only the 200–500 lines that matter**, not the 2,000+ that don't.

---

## Red Flags — STOP and Restart at Stage 1

If you catch yourself thinking:

- "I already know this brand/item, I'll just answer."
- "It's faster to search the web than grep the repo."
- "The user only wants a quick opinion."
- "This file is too long to map — I'll skim from the top."
- "I'll cite from memory; the file probably says the same thing."
- "No need for line numbers, the user trusts me."
- "This case is different — it's general knowledge."
- "I'll do the local search after I draft the answer."
- "I'll just Read the whole file — it's only 2,000 lines."
- "mq is overkill for heading extraction — rg '^##' is fine."
- "I searched in one language and found nothing — topic is absent."
- "Grep returned 8 files, so I should read them all."
- "This single file completes the answer." — Interpretive questions almost always require multi-file cross-synthesis.
- "The question's exact words are sufficient search terms." — Expand to related concepts.
- "This summary paragraph has everything — no need to check the detailed rows." — Summaries merge entities. Detailed entries are canonical.

**ALL of these mean: STOP. Return to Stage 1 and run `Glob` / `Grep`.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "The local archive probably doesn't have this." | You have not run `Glob`/`Grep` yet. "Probably" is not evidence. Run Stage 1 first; absence must be proven, not assumed. |
| "The file is 2,000 lines — too big to use." | That is exactly why Stage 2 exists. `mq '.h2'` takes milliseconds and turns 2,000 lines into a 10-line map. |
| "Web search will be more current." | Currency is Stage 5, not Stage 1. The user's curated take is the baseline; web only fills gaps. |
| "I remember what's in that file from a prior session." | Memories decay; files change. Re-`Grep`. Citations without re-verification are hallucinations with line numbers. |
| "Citing `file:line` is overkill for a chat answer." | This repo's value is provenance. Without `file:line`, the user cannot audit you and the answer is unfalsifiable. |
| "ast-grep would be more powerful." | `sg` is for code AST, not Markdown prose. For Markdown AST, use `mq`. |
| "I'll just `cat` the whole file into context." | Burns context budget. A 150K file = 42K tokens = 4.2% of context gone. Use `Read offset/limit` after mapping. |
| "I ran one `Grep` and it returned nothing — moving to web." | One query is not Stage 1. Try synonyms, brand variants (EN/KR/JP), and `Glob` on filenames before declaring absence. |
| "rg '^##' is good enough for heading extraction." | Empirical: rg=10 vs mq=6 in a code-block-heavy doc (4 false positives, 40% error rate). `mq` is correct. |
| "Grep returned 0 results, so the topic doesn't exist." | You may have searched in only one language. Try EN/KR/generic-name/abbreviation variants. Empirical: single-language search = 4 files → triple-language search = 8 files. |
| "15 candidates — I'll read them all directly." | 5+ → delegate to `Agent(Explore)`. 15 files processed directly = context budget blown. |
| "Grep returned 8 files, so all are topic files." | Glob=0 + Grep returning only passing mentions = **topic absent**. Adopt only files where keyword appears in headings. |
| "This one file completes the answer." | Interpretive questions ("define X?") require multiple files providing different layers (facts/philosophy/archetype/impression). Single-file answers are one-dimensional. |
| "Searching the question's exact words is sufficient." | Searching "essence as a human" with only the word "essence" misses half the results. Expand to `loneliness`, `conviction`, `yearning`, `DNA`, `archetype`. |
| "This summary paragraph settles the facts." | Summaries compress places, dates, and entities. Empirical: "found in [district]" summary → actually 2 different stores with 2 different items. Detailed rows are canonical. |
| "The DB might be stale, just use ripgrep." | `python3 fts5-reindex.py` takes 3 seconds. Reindex and get BM25 ranking — ripgrep only gives alphabetical order, it does not know which file is most relevant. |
| "I made this file with deep-research, so I can trust it." | If `human_reviewed: false`, citing it as truth is the **closed loop of citing your own synthesis as ground truth.** That is the definition of cognitive debt. Do not cite as primary evidence. |
| "The answer might be in `_inbox/` too, let's just search there." | `_inbox/` holds unreviewed external input — a prompt injection surface. Exclude from indexing AND searching unless the user explicitly says *"include inbox"*. |
| "BM25 score differences are small, the ripgrep order is fine." | Even when BM25 scores are close, the *order* is meaningful. Reading the top 5 saves ~70% of context. Reading all 30 matches is budget waste. |

---

## Quick Reference

| Stage | Activity | Primary Tool | Shell Fallback | Success Criterion |
|-------|----------|-------------|----------------|-------------------|
| **0. Awareness** | Choose tool layer | — | — | Internal tools chosen unless pipeline needed |
| **1. Discovery** | Narrow + rank candidates (multi-lang) | `Glob`, **`sqlite3 vault.fts5.db ... ORDER BY bm25`** (when DB exists), `Grep` fallback | `fd -e md`, `rg -l -t md` | Candidates produced + BM25-ranked; EN/KR/JP variants tried; `_inbox`/`_archive` excluded; ≥5 → Explore delegation |
| **2. Map** | Heading scan of long files | `Grep ^#{1,3}\s` | **`mq '.h2'`** (preferred), `rg -n '^#{1,3}\s'` | Section line ranges identified |
| **3. Pinpoint** | Extract cited context | `Grep -n -C 5` | `rg -n -C 5` | `file:line` citations captured |
| **4. Verify** | Targeted read | `Read offset/limit`, `Agent(Explore)` | `glow` (render check) | Passage read in surrounding context |
| **5. Augment** | Fill gaps from web/social | `mcp__brave-search__*`, `mcp__reddit__*` | — | Gap-only URLs added; local citations preserved |

---

## Golden One-Liner

> **`Glob` → `FTS5 BM25` (or `Grep` fallback) → `mq` (headings) → `Grep -n -C` (context) → `Read` + frontmatter gate → `glow` (verify) → web only for gaps.**
> Narrow → Rank → Map → Pinpoint → Verify (provenance!) → Augment. Never reverse the order.

---

## Key Principles

- **Local first, web last.** The curated `.md` corpus is the ground truth; the web is a supplement.
- **Prove absence before assuming it.** "I didn't find it" requires a Stage 1 search with multi-language variants, not a hunch.
- **Map before reading.** Long files demand a heading scan; cold reads burn context budget.
- **Cite by `file:line`.** Provenance is non-negotiable. No line number = no claim.
- **Right tool, right layer.** Internal tools by default; `mq` for markdown AST; shell pipelines only when justified.
- **Delegate breadth, not depth.** Multi-file sweeps belong to `Agent(Explore)`; the main agent reads what matters.
- **Context is finite.** Every Read costs tokens. The 5 Stages are a token budget optimizer, not bureaucracy.
- **Detail over summary.** When both exist, detailed entries are canonical. Summaries merge entities.
- **Narrative by default.** The Answer flows as prose with metaphor and insight, never as a context-free bullet dump — unless the user explicitly asks for another format.

---

## Integration with Other Instructions

- **Global `~/.claude/CLAUDE.md`** — defines the mandatory modern-CLI mapping (`grep→rg`, `find→fd`, etc.) used in Stages 1–3 shell fallbacks.
- **`software-engineering/claude-code/claude-code-cli-boost-tools.md`** — canonical reference for the shell tool layer; consult §"Shell Tool Selection — MANDATORY" and §"10. mq — jq for Markdown" before any `Bash` call.
- **`~/.ripgreprc`** — custom type `--type-add=research:*.md` enables `rg --type research` for markdown-only searches.
- **`fts5-reindex.py`** at vault root — generates `vault.fts5.db` with trigram tokenizer for Stage 1 BM25-ranked content match. Run after major edits (3s for ~200 files). DB absent → Stage 1 falls back to Grep/rg automatically.
- **Frontmatter contract** — files synthesized by `/deep-research` or other agents MUST carry `generated_by: claude-*` and `human_reviewed: false` until a human promotes them. Stage 4 enforces this gate.
- **Web augmentation (Stage 5)** — Brave Search MCP only (never built-in `WebSearch`); sequential calls only; freshness flags `pd`/`pw`/`pm`/`py` per global policy.
- **Archive maintenance** — run `lychee "**/*.md"` periodically to detect link rot in source citations.

---

Now execute the 5-Stage pipeline for: **"$ARGUMENTS"**
