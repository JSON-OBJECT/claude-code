#!/usr/bin/env python3
# =============================================================================
# fts5-reindex.py — Full reindex of vault .md files into SQLite FTS5
# =============================================================================
#
# Purpose
# -------
# Index every .md file in the vault (the directory this script lives in)
# into a SQLite FTS5 virtual table with the trigram tokenizer, producing
# `vault.fts5.db` for
# the Stage 1.5 acceleration layer of the `/ground` command. Each run
# drops the DB and rebuilds from scratch (no incremental updates).
#
# Section-level indexing (v2)
# ---------------------------
# Each row is a **section**, not a whole file. Files are split at H1–H3
# heading boundaries (code fences respected), so a BM25 hit returns
# `rel_path + heading + start_line` directly — collapsing /ground
# Stage 1 (discovery), Stage 2 (heading map), and part of Stage 3
# (pinpoint) into a single query. Whole-file rows distorted BM25: a
# 150K-char file competed as one giant document, and a match told you
# the file but not where. Section rows fix both.
#
# Why the trigram tokenizer
# -------------------------
# FTS5's default `unicode61` tokenizer splits only on whitespace and
# punctuation, so substring matches inside CJK words fail
# (e.g. "지식관리" → "지식" yields nothing). `trigram` (SQLite 3.34+,
# 2021) slices text into 3-character windows, enabling CJK substring
# matching and typo tolerance. Index size grows ~3x, but at 200–few-thousand
# files that overhead is negligible.
#
# Supersession frontmatter
# ------------------------
# Files may declare knowledge lineage in frontmatter:
#
#   supersedes: old-doc.md          # this file replaces old-doc.md
#   superseded_by: new-doc.md       # this file is stale; read new-doc.md
#
# `superseded_by` is indexed as a filterable column. /ground Stage 1
# excludes superseded rows by default (`AND superseded_by = ''`), and
# Stage 4 refuses to cite a superseded file as primary evidence.
#
# OKF frontmatter (v3)
# --------------------
# Vaults following the OKF-compatible frontmatter contract (Google
# Cloud Open Knowledge Format v0.1: type / description / timestamp)
# get three more columns:
# - `type` and `timestamp` are filterable UNINDEXED columns, enabling
#   question-type-aware Stage 1 filtering (e.g. AND type = 'deep-research').
# - `description` is a *searchable* column so BM25 can match the curated
#   one-line summary. It is populated only on the file's FIRST section
#   row — repeating it on every section row would let one description
#   match N times and skew ranking.
# Files without these keys index normally (empty strings) — the columns
# are additive, never a gate.
#
# =============================================================================
# Installation — Homebrew, unified across macOS / Linux / WSL2
# =============================================================================
#
# Prerequisite: Homebrew must be installed.
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#   # On Linux/WSL, follow the post-install hint to add brew to PATH:
#   #   eval "$($(brew --prefix)/bin/brew shellenv)"
#
# [1] Core: Python (bundles a recent SQLite) + PyYAML
#     ----------------------------------------------------------------
#     brew install python
#     # brew's python links against brew's sqlite (3.50+), so FTS5 +
#     # trigram are enabled out of the box. No need to touch the system
#     # sqlite or system python.
#
#     # PyYAML — brew's python enforces PEP 668, which blocks plain
#     # `pip install`. Use pipx or a project venv instead:
#     brew install pipx && pipx install pyyaml
#     # Or a venv at the project root:
#     #   python3 -m venv .venv && .venv/bin/pip install pyyaml
#     #   then run: .venv/bin/python fts5-reindex.py
#     #
#     # PyYAML is optional — the script falls back to a regex parser if
#     # it isn't installed. Install it only when frontmatter contains
#     # nested structures.
#
#     # Smoke test (FTS5 + trigram):
#     python3 -c "import sqlite3; \
#       c=sqlite3.connect(':memory:'); \
#       c.execute(\"CREATE VIRTUAL TABLE t USING fts5(x, tokenize='trigram')\"); \
#       print('FTS5 + trigram OK', sqlite3.sqlite_version)"
#
#     # Note: Korean morphological analyzers (mecab-ko, khaiii, ...) are
#     # not required. trigram is a zero-config approach that solves
#     # substring matching without morphological analysis.
#
# [2] (Optional) sqlite3 CLI — only if you want to run the example
#     queries directly from the shell
#     ----------------------------------------------------------------
#     brew install sqlite
#     # On macOS the system sqlite3 takes precedence on PATH, so to use
#     # brew's sqlite follow the keg-only hint and prepend it to PATH:
#     #   echo 'export PATH="$(brew --prefix sqlite)/bin:$PATH"' >> ~/.zshrc
#     # This script uses the Python sqlite3 module, so this step is
#     # optional.
#
# [3] (Optional) Modern CLIs used by the /ground command
#     ----------------------------------------------------------------
#     brew install ripgrep fd eza dust bat sd fzf jq yq glow lychee
#     # Not required by this script itself, but consumed by the /ground
#     # 5-stage pipeline. mq (Markdown jq) is separate — install via
#     # Cargo or a GitHub release.
#
# =============================================================================
# Usage
# =============================================================================
#
#   cd /path/to/your/vault
#   python3 fts5-reindex.py
#
#   # Example output:
#   #   Indexed 210 notes (1450 sections) in 4.2s → vault.fts5.db (31.7 MB)
#
# Example query (BM25 ranking, section-level):
#
#   sqlite3 vault.fts5.db -separator $'\t' "
#     SELECT rel_path, heading, start_line, bm25(notes_fts) AS score
#     FROM notes_fts
#     WHERE notes_fts MATCH '\"키워드\"'
#       AND human_reviewed != 'false'
#       AND superseded_by = ''
#     ORDER BY score LIMIT 10;"
#
# Example: filter by OKF type (interpretive question → canon docs first):
#
#   sqlite3 vault.fts5.db -separator $'\t' "
#     SELECT rel_path, heading, start_line, bm25(notes_fts) AS score
#     FROM notes_fts
#     WHERE notes_fts MATCH '\"키워드\"'
#       AND type IN ('canon', 'doctrine-canon')
#       AND superseded_by = ''
#     ORDER BY score LIMIT 10;"
#
# =============================================================================

import re
import sqlite3
import sys
import time
from pathlib import Path

# ----- Configuration -----
VAULT = Path(__file__).resolve().parent
DB_PATH = VAULT / "vault.fts5.db"

# Directories excluded from indexing (prompt-injection defense + noise removal)
EXCLUDE_DIRS = {
    "_inbox",       # Web Clipper, unreviewed — never cite
    "_archive",     # Explicit graveyard — not an active search target
    "_answers",     # Crystallized Q&A pairs — LLM output, NEVER a grounding source
    ".git",
    ".claude",
    ".obsidian",
    "node_modules",
    "worktrees",
}

# ----- Frontmatter parser -----
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FM_KEYS = (
    "generated_by", "human_reviewed", "supersedes", "superseded_by",
    "type", "description", "timestamp",
)

try:
    import yaml  # type: ignore
    def parse_frontmatter(text: str) -> dict:
        m = FM_RE.match(text)
        if not m:
            return {}
        try:
            data = yaml.safe_load(m.group(1)) or {}
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError:
            return {}
except ImportError:
    # PyYAML missing: fall back to extracting only the FM_KEYS via regex.
    KEY_RE = re.compile(
        r"^(" + "|".join(FM_KEYS) + r")\s*:\s*(.+?)\s*$", re.MULTILINE
    )
    def parse_frontmatter(text: str) -> dict:
        m = FM_RE.match(text)
        if not m:
            return {}
        result = {}
        for key, val in KEY_RE.findall(m.group(1)):
            result[key] = val.strip().strip('"').strip("'")
        return result


def fm_str(meta: dict, key: str) -> str:
    """Normalize a frontmatter value to a lowercase-safe string.

    PyYAML parses `human_reviewed: false` into Python False, whose
    str() is 'False' (capital F) — which silently defeated the
    `!= 'false'` SQL filter in /ground Stage 1. Booleans are therefore
    lowercased; lists (e.g. supersedes: [a.md, b.md]) join with ', '.
    """
    val = meta.get(key, "")
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val) if val is not None else ""


# ----- Markdown section splitter -----
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")


def split_sections(text: str):
    """Split markdown into (heading, start_line, end_line, body) tuples.

    Boundaries are H1–H3 headings outside code fences and outside the
    YAML frontmatter block. Content before the first heading becomes a
    '(preamble)' section. Line numbers are 1-indexed to match rg/Read.
    """
    lines = text.split("\n")

    # Frontmatter span (skipped for heading detection, kept in preamble body)
    fm_end = 0  # last line index (0-based, exclusive) of frontmatter
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                fm_end = i + 1
                break

    boundaries = []  # (line_index_0based, heading_text)
    in_fence = False
    fence_marker = ""
    for i, line in enumerate(lines):
        if i < fm_end:
            continue
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence = False
            continue
        if in_fence:
            continue
        h = HEADING_RE.match(line)
        if h:
            boundaries.append((i, h.group(0).strip()))

    if not boundaries:
        return [("(preamble)", 1, len(lines), text)]

    sections = []
    first = boundaries[0][0]
    if any(l.strip() for l in lines[:first]):
        sections.append(("(preamble)", 1, first, "\n".join(lines[:first])))

    for n, (start, heading) in enumerate(boundaries):
        end = boundaries[n + 1][0] if n + 1 < len(boundaries) else len(lines)
        sections.append((heading, start + 1, end, "\n".join(lines[start:end])))

    return sections


def verify_runtime():
    """Verify that SQLite FTS5 + the trigram tokenizer are available."""
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE VIRTUAL TABLE _t USING fts5(x, tokenize='trigram')")
    except sqlite3.OperationalError as e:
        sys.exit(
            f"[FATAL] FTS5 trigram tokenizer unavailable: {e}\n"
            f"        SQLite {sqlite3.sqlite_version} — 3.34 or newer required.\n"
            f"        See section [1] at the top of this file to upgrade SQLite."
        )
    finally:
        con.close()


def is_excluded(path: Path) -> bool:
    rel_parts = path.relative_to(VAULT).parts
    return any(part in EXCLUDE_DIRS for part in rel_parts)


def main():
    verify_runtime()

    print(f"[*] Vault: {VAULT}", file=sys.stderr)
    print(f"[*] DB:    {DB_PATH}", file=sys.stderr)

    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[*] Existing DB removed — reindexing from scratch", file=sys.stderr)

    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous = NORMAL;

        CREATE VIRTUAL TABLE notes_fts USING fts5(
            path UNINDEXED,
            rel_path UNINDEXED,
            heading UNINDEXED,
            start_line UNINDEXED,
            end_line UNINDEXED,
            mtime UNINDEXED,
            size UNINDEXED,
            generated_by UNINDEXED,
            human_reviewed UNINDEXED,
            supersedes UNINDEXED,
            superseded_by UNINDEXED,
            type UNINDEXED,
            timestamp UNINDEXED,
            description,
            body,
            tokenize = 'trigram'
        );
    """)

    t0 = time.perf_counter()
    rows = []
    n_files = 0
    skipped = 0

    for f in VAULT.rglob("*.md"):
        if is_excluded(f):
            skipped += 1
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[!] Failed to read {f}: {e}", file=sys.stderr)
            continue

        n_files += 1
        meta = parse_frontmatter(text)
        mtime = int(f.stat().st_mtime)
        common = (
            str(f),
            str(f.relative_to(VAULT)),
        )
        tail = (
            mtime,
            len(text),
            fm_str(meta, "generated_by"),
            fm_str(meta, "human_reviewed"),
            fm_str(meta, "supersedes"),
            fm_str(meta, "superseded_by"),
            fm_str(meta, "type"),
            fm_str(meta, "timestamp"),
        )
        description = fm_str(meta, "description")
        for n_sec, (heading, start_line, end_line, body) in enumerate(
            split_sections(text)
        ):
            # description rides only on the first section row (see header)
            desc_col = description if n_sec == 0 else ""
            rows.append(
                common + (heading, start_line, end_line) + tail + (desc_col, body)
            )

    with con:
        con.executemany(
            "INSERT INTO notes_fts"
            "(path, rel_path, heading, start_line, end_line,"
            " mtime, size, generated_by, human_reviewed,"
            " supersedes, superseded_by, type, timestamp, description, body)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )

    con.execute("INSERT INTO notes_fts(notes_fts) VALUES('optimize')")
    con.close()

    elapsed = time.perf_counter() - t0
    db_mb = DB_PATH.stat().st_size / 1e6

    print(
        f"[OK] Indexed {n_files} notes ({len(rows)} sections, "
        f"skipped {skipped} excluded) "
        f"in {elapsed:.2f}s → {DB_PATH.name} ({db_mb:.1f} MB)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
