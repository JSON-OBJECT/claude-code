---
description: Use when turning a folder of markdown files (or an empty folder) into an LLM Wiki vault for the deep-thinking pipeline — verifies the FTS5 trigram runtime per OS, installs fts5-reindex.py, scaffolds convention folders, git-inits with .gitignore, appends the vault protocol to CLAUDE.md non-destructively, builds vault.fts5.db, and proves it with a BM25 smoke query
allowed-tools: Glob, Grep, Read, Bash, Write, Edit
argument-hint: [target-directory] (defaults to current working directory)
---

# Initialize an LLM Wiki Vault

You are transforming **one directory** into a fully operational LLM Wiki vault: a markdown archive that the deep-thinking pipeline (`/deep-thinking:ground`, `/deep-thinking:save-answer`, `/deep-thinking:journal`, `/deep-thinking:schedule`, `/deep-thinking:deep-research`) can ground against with section-level BM25 search.

Think `git init`, but for knowledge: run it once inside a folder, and that folder becomes a vault — in place, without touching anything outside it.

---

## The Iron Law

```
EVERYTHING HAPPENS INSIDE THE VAULT ROOT. NOTHING OUTSIDE IT.
EXISTING FILES ARE PRESERVED — CLAUDE.md IS APPENDED TO, NEVER REWRITTEN.
fts5-reindex.py IS DEPLOYED VERBATIM — NEVER EDITED, "IMPROVED", OR PATCHED.
SETUP IS NOT DONE UNTIL A BM25 SMOKE QUERY RETURNS A REAL HIT.
```

**Violating the letter of this rule is violating the spirit of this command.**

The vault root is `$ARGUMENTS` if a path was given, otherwise the current working directory. Every file you create or modify MUST live under that root. You MUST NOT touch the user's global `~/.claude/CLAUDE.md`, any other repository, or any file outside the vault root.

---

## EXECUTE: The 6 Stages (Sequential, No Skipping)

### Stage 0 — Resolve Target & Safety Gate

**GATE: Know exactly which directory you are converting before creating anything.**

1. Resolve the vault root (argument path or cwd) to an absolute path.
2. Survey it: `eza -la` (or `ls -la`) plus `fd -e md . <root> | head -20` (fallback `find <root> -name '*.md'`). Count the `.md` files.
3. **Refuse unsafe targets.** If the root is the user's home directory itself, a system path (`/`, `/usr`, `/etc`, `/tmp` root), or clearly another kind of project (e.g. contains `package.json`/`Cargo.toml` with a `src/` tree and no markdown corpus), STOP and ask the user to confirm or pick a subdirectory. A vault is a folder of markdown notes — not someone's entire home.
4. **Idempotency check.** If `fts5-reindex.py` AND `vault.fts5.db` already exist at the root, this is a re-run: switch to upgrade mode (refresh the script from the plugin, re-append nothing that already exists, reindex, re-verify). Never duplicate scaffolding or CLAUDE.md sections.

### Stage 1 — Preflight (Environment, Per OS)

**GATE: Prove the runtime works BEFORE deploying anything. Check first, install only what is missing.**

1. Detect the platform: `uname -s` (+ `uname -r` — a `microsoft` substring means WSL).
2. **Python present?** `python3 --version`. Missing → remedy per OS:
   - macOS / Linux / WSL with Homebrew: `brew install python`
   - Debian/Ubuntu without Homebrew: `sudo apt install python3`
3. **FTS5 + trigram smoke test (the one hard requirement):**
   ```bash
   python3 -c "import sqlite3; c=sqlite3.connect(':memory:'); \
     c.execute(\"CREATE VIRTUAL TABLE t USING fts5(x, tokenize='trigram')\"); \
     print('FTS5 trigram OK', sqlite3.sqlite_version)"
   ```
   Failure means Python links against SQLite older than 3.34. Remedy: install a Python whose SQLite is current — `brew install python` bundles SQLite 3.50+ on macOS, Linux, and WSL alike. Re-run the smoke test after installing. Do NOT proceed on a failing smoke test.
4. **PyYAML (optional).** `python3 -c "import yaml"` — if missing, do NOT install anything; the script ships a regex fallback that covers flat frontmatter. Only mention it in the final report as "install via `pipx install pyyaml` if frontmatter ever gains nested structures".
5. **Pipeline CLIs (install the missing ones).** The `/ground` 5-stage pipeline consumes this toolset (see the plugin README, "CLI Tools for `/deep-thinking:ground`"):

   | Tool | Pipeline role |
   |------|---------------|
   | `fd` | Stage 1 filename match |
   | `rg` (ripgrep) | Stage 1 content scan; Stage 3 context extraction |
   | `mq` | Stage 2 Markdown AST heading extraction (zero false positives inside code blocks) |
   | `yq` | Stage 1 YAML frontmatter filtering |
   | `glow` | Stage 4 render verification |
   | `lychee` | Archive-wide link validation |
   | `sqlite3` | Stage 1 BM25 ranking via `vault.fts5.db` |
   | `bat`, `sd`, `fzf`, `scc`, `tokei` | General modern-CLI layer (Stage 0 tool awareness) |

   Check each with `command -v`; then install ONLY the missing ones. With Homebrew (macOS / Linux / WSL alike):
   ```bash
   brew install <missing tools among: fd ripgrep bat sd fzf scc tokei yq glow lychee sqlite>
   brew install harehare/tap/mq   # mq lives in a tap, not core
   ```
   Missing tools do not hard-block setup — `/ground` has internal-tool fallbacks — but a vault initialized without `mq` and `sqlite3` runs the pipeline degraded, so install unless the user declines or no package manager exists (then list the leftovers in the report with the command above as the remedy).
   **macOS PATH caveat:** Homebrew's `sqlite` is keg-only; ensure `$(brew --prefix)/opt/sqlite/bin` precedes the system path so `sqlite3` resolves to the FTS5-capable binary.

### Stage 2 — Deploy fts5-reindex.py

**GATE: The script arrives verbatim, from the closest trusted source.**

Source priority (try in order, stop at first success):

1. **Installed plugin copy** — `${CLAUDE_PLUGIN_ROOT}/fts5-reindex.py`. Version-matched to this command and works offline. Copy it to `<vault-root>/fts5-reindex.py`.
2. **GitHub raw fallback** (plugin copy unavailable):
   ```bash
   curl -fsSL -o fts5-reindex.py \
     https://raw.githubusercontent.com/JSON-OBJECT/claude-code/main/plugins/deep-thinking/fts5-reindex.py
   ```

After deploying: `python3 -m py_compile fts5-reindex.py` MUST pass (guards against truncated downloads). You MUST NOT edit the script — not its code, not its comments, not "just the docstring". If a copy already exists at the root, overwrite it with the plugin version (report that you refreshed it).

### Stage 3 — Scaffold Convention Folders + Git

**GATE: The vault contract is structural. Folders and git are not optional decorations.**

1. **Convention folders** (each with a `.gitkeep` so git tracks them):
   - `_inbox/` — unreviewed external captures (web clipper, pasted notes). Excluded from indexing and grounding: it is a prompt-injection surface.
   - `_archive/` — explicitly buried documents. Excluded from indexing.
   - `_answers/` — crystallized past answers written by `/deep-thinking:save-answer`. Excluded from indexing so LLM-synthesized answers never feed back into LLM sources.
   These names match `EXCLUDE_DIRS` inside `fts5-reindex.py` — do not invent different names.
2. **Git.** If the root is not inside a git repository: `git init`. Then ensure `.gitignore` contains these entries (append only the missing ones; create the file if absent):
   ```gitignore
   vault.fts5.db
   vault.fts5.db-shm
   vault.fts5.db-wal
   __pycache__/
   .venv/
   ```
   `vault.fts5.db` is a rebuildable build artifact; git history is the vault's change log (`/journal` and `/lint` depend on it). "It's not a git repo, so no .gitignore needed" is a baseline failure — make it a git repo.

### Stage 4 — CLAUDE.md Vault Protocol (Append-Only, Never Rewrite)

**GATE: Read before writing. Existing CLAUDE.md content is the user's — preserve every line of it.**

1. If `CLAUDE.md` exists at the root, `Read` it first. If it already contains the heading `## LLM Wiki Vault Protocol`, skip this stage entirely (idempotency).
2. If it exists without that heading: **append** the block below after the existing content (one blank line between). Do NOT reorder, reformat, deduplicate, "clean up", or delete anything already there.
3. If it does not exist: create `CLAUDE.md` containing exactly the block below.

Append this block verbatim:

```markdown
## LLM Wiki Vault Protocol

This directory is an LLM Wiki vault. For EVERY question about this vault's topics, you MUST execute the `/deep-thinking:ground` command's Markdown Source Grounding Protocol (5-Stage pipeline) to generate answers grounded in the local `.md` archive. No exceptions.

### Command Routing

| Task | Command |
|------|---------|
| Answering any question about the vault's topics | `/deep-thinking:ground` |
| Saving/archiving an answer the user wants to keep | `/deep-thinking:save-answer` |
| Recording raw thoughts, insights, or daily logs | `/deep-thinking:journal` — if the target log file does not exist yet, create it FIRST, before writing the entry |
| Creating or updating schedule/calendar records | `/deep-thinking:schedule` |
| Deep multi-source investigation of a new topic | `/deep-thinking:deep-research` |

### Index Contract

- `vault.fts5.db` (SQLite FTS5, trigram tokenizer, one row per H1–H3 section) powers BM25-ranked search. If it is missing or stale, run `python3 fts5-reindex.py` BEFORE answering — it takes seconds.
- Re-run `python3 fts5-reindex.py` after adding or editing `.md` files so changes become searchable.
- `_inbox/`, `_archive/`, and `_answers/` are excluded from indexing and grounding by design. Never cite them as sources.

### Frontmatter Contract

- EVERY new `.md` file (outside `_inbox/`, `_archive/`, `_answers/`) MUST open with a YAML frontmatter block carrying the OKF trio (Google Cloud Open Knowledge Format v0.1): `type` (short kind string — reuse existing values such as deep-research, canon, playbook, journal-log, schedule-index, guide, report, index, note), `description` (one-line summary, ~40–140 chars, quoted), and `timestamp` (ISO 8601 of last meaningful change — update it when meaningfully editing).
- Files synthesized by an LLM MUST additionally carry `generated_by: <model>` and `human_reviewed: false` until a human reviews them. Unreviewed synthesis is never primary evidence.
- Knowledge lineage uses paired fields: the new canon gets `supersedes: <older>.md`, the stale file gets `superseded_by: <newer>.md`. Superseded files are excluded from grounding but never deleted.
- NEVER create `log.md` or any manual changelog file — git history is the vault's change log.
```

### Stage 5 — Build Index & Prove It Works

**GATE: "The DB file exists" is not verification. A BM25 query returning a real section hit is.**

1. Build: `cd <vault-root> && python3 fts5-reindex.py` — capture the `Indexed N notes (M sections)` line.
2. **Smoke query.** Pick a word that actually appears in an indexed file (≥3 characters — the trigram tokenizer needs 3+; pick from a heading or body you saw in Stage 0). Run the exact query shape `/ground` uses:
   ```bash
   sqlite3 vault.fts5.db -separator $'\t' "
     SELECT rel_path, heading, start_line || '-' || end_line, bm25(notes_fts)
     FROM notes_fts WHERE notes_fts MATCH '\"<word>\"'
     ORDER BY bm25(notes_fts) LIMIT 5;"
   ```
   It MUST return ≥1 row with `rel_path + heading + line range`. If the corpus contains CJK text, run a second smoke query with a ≥3-character CJK substring to prove trigram matching.
3. **Empty-vault path.** If Stage 0 counted zero `.md` files, the index will legitimately report `0 notes`. That is not a failure: verify the DB was created and `PRAGMA integrity_check` returns `ok`, then tell the user to re-run `python3 fts5-reindex.py` after adding their first notes.
4. A smoke query returning 0 rows on a non-empty corpus means the setup is broken (wrong word, unindexed file, or stale DB). Diagnose and fix before reporting success.

### Stage 6 — Report

Summarize in this order:

1. **Environment** — OS, Python + SQLite versions, smoke-test result, pipeline CLIs checked / newly installed / still missing (with remedies).
2. **Files created/modified** — script source used (plugin copy vs GitHub), folders scaffolded, git/.gitignore actions, CLAUDE.md action taken (created / appended / already-present-skipped).
3. **Index** — `N notes / M sections`, DB size, smoke-query hit(s) shown verbatim.
4. **Provenance flags** — if any indexed file carries `human_reviewed: false`, tell the user those files are excluded from primary-evidence grounding until promoted to `human_reviewed: true`.
5. **Next steps** — make the first git commit if the repo has none (git history is the vault's change log), add notes, re-run `python3 fts5-reindex.py` after edits, try `/deep-thinking:ground <question>`.

---

## Red Flags — STOP and Re-Read the Iron Law

- "CLAUDE.md is messy — I'll rewrite it cleanly while adding the protocol."
- "I'll fix a typo / generalize a comment in fts5-reindex.py while I'm at it."
- "It's not a git repo, so no .gitignore is needed."
- "The scaffolding folders are optional; the user can create them later."
- "The DB file was created, so the setup works." — Run the smoke query.
- "Python is installed, so FTS5 must work." — System SQLite may predate trigram (3.34). Run the smoke test.
- "Downloading from GitHub is simpler than locating the plugin copy."
- "This home directory has some markdown files — close enough to a vault."
- "The user's global ~/.claude/CLAUDE.md would be a better place for the protocol."

**ALL of these mean: STOP. Return to the relevant stage and follow it.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Appending to CLAUDE.md is enough; nobody re-runs this." | Re-runs happen. Without the `## LLM Wiki Vault Protocol` heading check, every re-run duplicates the block and the file rots. |
| "Rewriting CLAUDE.md produces a cleaner file." | Existing lines are the user's standing instructions to every future agent session. Deleting or reflowing one line silently changes agent behavior. Append-only. |
| "The script's hardcoded comments should be localized for this vault." | The script auto-detects its parent directory at runtime. Editing it forks it from the plugin version and breaks future upgrade diffs. Deploy verbatim. |
| "No git repo → skip .gitignore." | `git init` is part of this command. `/journal` and `/lint` treat git history as the change log; a vault without git has no lineage. |
| "_answers/ can wait until the user first runs /save-answer." | `/save-answer`'s quarantine is structural: the folder plus its index exclusion. Pre-creating it is exactly this command's job. |
| "Trigram failed but unicode61 works — good enough." | Without trigram there is no CJK substring matching, the plugin's headline feature. Fix the runtime (Stage 1 remedy); do not ship a degraded index silently. |
| "0 rows on the smoke query, but the build printed success." | The build printing success only proves the script ran. Zero hits on a non-empty corpus means /ground Stage 1 will silently fall back to grep forever. Diagnose now. |
| "brew install everything up front to be safe." | Installing over a working runtime wastes minutes and can shadow the user's Python. Check first; install only what the smoke test proves missing. |
| "The 2-char CJK query returned nothing — setup is broken." | Trigram needs ≥3 characters by design. Test with a 3+ character term; /ground's grep fallback covers shorter ones. |
| "The pipeline CLIs are optional — skip the install step." | Optional means non-blocking, not skippable. Without `mq` heading extraction gains false positives; without `sqlite3` there is no BM25 CLI. Check all, install the missing, and only report leftovers when installation is impossible. |

---

## Quick Reference

| Stage | Activity | Key Tool | Success Criterion |
|-------|----------|----------|-------------------|
| **0. Resolve** | Absolute root, survey, safety + idempotency gates | `eza`/`fd` | Target confirmed safe; re-run detected |
| **1. Preflight** | Python + FTS5 trigram smoke test; install missing pipeline CLIs | `python3 -c "...fts5(x, tokenize='trigram')..."`, `command -v`, `brew install` | Smoke test prints OK; pipeline CLIs present (or remedies reported) |
| **2. Deploy** | Copy script: plugin root → GitHub raw fallback | `cp` / `curl -fsSL` | `py_compile` passes; script verbatim |
| **3. Scaffold** | `_inbox/ _archive/ _answers/` + `git init` + `.gitignore` | `mkdir` / `git` | Folders exist; DB artifacts ignored |
| **4. CLAUDE.md** | Append vault protocol block, never rewrite | `Read` → `Edit`/`Write` | Existing content byte-identical; block present once |
| **5. Verify** | Reindex + BM25 smoke query (CJK if applicable) | `python3 fts5-reindex.py`, `sqlite3` | ≥1 real section hit (or clean empty-vault path) |
| **6. Report** | Environment, files, index stats, provenance, next steps | — | User can run `/deep-thinking:ground` immediately |

---

## Integration with Other Commands

- **`/deep-thinking:ground`** — the consumer of everything this command builds: `vault.fts5.db` for Stage 1 BM25, the frontmatter contract for Stage 4 gates, the folder exclusions for Stage 1 filtering.
- **`/deep-thinking:save-answer`** — writes into the `_answers/` quarantine this command scaffolds.
- **`/deep-thinking:journal`** / **`/deep-thinking:schedule`** — write `.md` records into the vault and rely on `git init` (history) plus `fts5-reindex.py` (searchability) from this command.
- **`fts5-reindex.py`** — the single build tool this command deploys; its header documents installation remedies in depth if Stage 1 fails on an exotic platform.

---

Now initialize the vault at: **"$ARGUMENTS"** (or the current working directory if empty).
