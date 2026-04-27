#!/usr/bin/env python3
# =============================================================================
# fts5-reindex.py — Full reindex of vault .md files into SQLite FTS5
# =============================================================================
#
# Purpose
# -------
# Index every .md file under the directory containing this script
# (treated as the LLM Wiki / vault root) into a SQLite FTS5 virtual
# table with the trigram tokenizer, producing `vault.fts5.db` for the
# Stage 1.5 acceleration layer of the `/ground` command. Drop this
# script at the root of any markdown archive and run it in place — no
# path configuration required. Each run drops the DB and rebuilds from
# scratch (no incremental updates).
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
#   cd /path/to/your/markdown-vault   # the directory containing this script
#   python3 fts5-reindex.py
#
#   # Example output:
#   #   Indexed 210 notes in 4.2s → vault.fts5.db (28.4 MB)
#
# Example query (BM25 ranking):
#
#   sqlite3 vault.fts5.db -header -column "
#     SELECT rel_path, snippet(notes_fts, 5, '«', '»', '…', 10) AS preview
#     FROM notes_fts
#     WHERE notes_fts MATCH 'framework'
#       AND (human_reviewed != 'false' OR human_reviewed IS NULL)
#     ORDER BY bm25(notes_fts) LIMIT 10;"
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
    ".git",
    ".claude",
    ".obsidian",
    "node_modules",
    "worktrees",
}

# ----- Frontmatter parser -----
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

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
    # PyYAML missing: fall back to extracting only generated_by and
    # human_reviewed via regex.
    KEY_RE = re.compile(r"^(generated_by|human_reviewed)\s*:\s*(.+?)\s*$", re.MULTILINE)
    def parse_frontmatter(text: str) -> dict:
        m = FM_RE.match(text)
        if not m:
            return {}
        result = {}
        for key, val in KEY_RE.findall(m.group(1)):
            result[key] = val.strip().strip('"').strip("'")
        return result


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
            mtime UNINDEXED,
            size UNINDEXED,
            generated_by UNINDEXED,
            human_reviewed UNINDEXED,
            body,
            tokenize = 'trigram'
        );
    """)

    t0 = time.perf_counter()
    rows = []
    skipped = 0

    for f in VAULT.rglob("*.md"):
        if is_excluded(f):
            skipped += 1
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[!] Failed to read {f}: {e}", file=sys.stderr)
            continue

        meta = parse_frontmatter(body)
        rows.append((
            str(f),
            str(f.relative_to(VAULT)),
            int(f.stat().st_mtime),
            len(body),
            str(meta.get("generated_by", "")),
            str(meta.get("human_reviewed", "")),
            body,
        ))

    with con:
        con.executemany(
            "INSERT INTO notes_fts"
            "(path, rel_path, mtime, size, generated_by, human_reviewed, body)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )

    con.execute("INSERT INTO notes_fts(notes_fts) VALUES('optimize')")
    con.close()

    elapsed = time.perf_counter() - t0
    db_mb = DB_PATH.stat().st_size / 1e6

    print(
        f"[OK] Indexed {len(rows)} notes "
        f"(skipped {skipped} excluded) "
        f"in {elapsed:.2f}s → {DB_PATH.name} ({db_mb:.1f} MB)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
