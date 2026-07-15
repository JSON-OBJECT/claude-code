# Deep Thinking Plugin

A Claude Code plugin for deep research, prompt engineering, trend analysis, and meeting documentation.

## Installation

```bash
# Add marketplace (one-time setup)
/plugin marketplace add JSON-OBJECT/claude-code

# Install plugin
/plugin install deep-thinking@jsonobject-marketplace
```

## Update

Apply a new plugin version to the current Claude Code session without a restart:

```bash
# 1. Pull latest marketplace metadata and cache the new plugin source
/plugin marketplace update jsonobject-marketplace

# 2. Hot-reload the active session
/reload-plugins
```

With `autoUpdate: true` on the marketplace (default), refresh also happens automatically at Claude Code launch.

## Commands

### LLM Wiki Commands

These commands turn a folder of markdown notes into an **LLM Wiki vault** — a grounded knowledge base with a section-level FTS5 BM25 index (`vault.fts5.db`) — and operate on it. Run `init-vault` once; the rest work inside the vault, in roughly this lifecycle order.

Vault frontmatter follows an **OKF-compatible contract** ([Google Cloud Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)): every concept file carries `type` / `description` / `timestamp`, with the pipeline's provenance keys (`generated_by`, `human_reviewed`, `supersedes`, `superseded_by`) as OKF extension keys. `fts5-reindex.py` indexes the trio — `type`/`timestamp` as filterable columns, `description` as a searchable column — so `/ground` can filter by document kind and match curated summaries.

| Command | Description |
|---------|-------------|
| `/deep-thinking:init-vault [directory]` | Transform any folder of markdown files (or an empty folder) into an LLM Wiki vault in one shot — per-OS FTS5 trigram preflight, pipeline CLI install, `fts5-reindex.py` deployment, `_inbox/`/`_archive/`/`_answers/` scaffolding, `git init` + `.gitignore`, non-destructive CLAUDE.md vault protocol with command routing, and a BM25 smoke-query verification |
| `/deep-thinking:ground {question}` | 5-stage pipeline (Discovery → Map → Pinpoint → Verify → Augment) that grounds answers in the local `.md` archive with mandatory `file:line` citations; web augmentation only for proven gaps |
| `/deep-thinking:journal "{raw thoughts}"` | Turn a raw thought-dump into a clean, lineage-aware, ground-searchable entry in the monthly insight log — supports add, refine, promote, and review modes |
| `/deep-thinking:schedule {path-or-directory}` | Create, refine, or audit schedule/calendar markdown into month-anchored, bookmark-style ground-truth indexes optimized for grounding, RAG retrieval, and chunk-based parsing instead of narrative-stuffed tables |
| `/deep-thinking:deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report — the primary way new long-form source documents enter the vault |
| `/deep-thinking:lint [scope]` | Vault health check — report-only lint that audits contradictions, supersession lineage, broken links, frontmatter provenance, and index freshness without mutating a single vault file |
| `/deep-thinking:save-answer` | Archive the previous grounded answer verbatim into `_answers/` — a quarantine folder permanently excluded from `/ground` and FTS5 indexing, so LLM-synthesized answers never feed back into LLM sources |

### General Commands

Standalone research, writing, and creative utilities — no vault required.

| Command | Description |
|---------|-------------|
| `/deep-thinking:pulse {topic}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/deep-thinking:forge-prompt {instruction}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |
| `/deep-thinking:meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |
| `/deep-thinking:translate-kr {article}` | Transcreate English IT articles into native Korean with terminology verification and anti-translation-artifact rules |
| `/deep-thinking:blog-cover {title and concept}` | Generate anti-AI-looking blog cover image prompts for Gemini Nano Banana Pro with visual metaphors and title typography |
| `/deep-thinking:blog {topic or draft}` | 16-year veteran IT tech blogger framework — fact-based, source-cited content with mandatory bullet point formatting and inline hyperlinks |
| `/deep-thinking:writing-z-image-turbo-prompts {seed}` | Forge a Z-Image-Turbo (ZIT) photorealism prompt from any natural-language seed — outputs an sd-dynamic-prompts mustache template implementing the 90hex 11-slot doctrine (camera body + film stock + anti-AI 4-stack) |
| `/deep-thinking:hidden-reality {idea or topic}` | Anti-optimization idea forge — suggests, verifies, or defends "Hidden Reality" software ideas against an 11-mechanism doctrine (imperfection, friction, anti-utility, defamiliarization, scale violation, etc.) with academic backbone (Tega Brain, 한병철, Shklovsky, Dunne & Raby) and a 2-week prototype scope |

## Skills

Skills activate automatically when their trigger conditions match — no slash command needed.

| Skill | Description |
|-------|-------------|
| `game-juice` | Build or polish browser UI that FEELS like a Japanese gacha/casual mobile game — damage numbers, hit impact, screen shake, springy buttons, combos. Treats juice as FEEDBACK (not decoration), enforces earned-juice restraint to avoid the generic AI-mass-produced feel, and orchestrates `impeccable` (visuals) + `gsap` skills (animation) with canon-anchored parameters |
| `cozy-refuge` | Create content that feels like a warm refuge — lo-fi girl vibes, Ghibli-esque everyday peace, rainy-window rooms, ambience loops, cozy apocalypse (終末日常系) — in any medium (image prompts, web UI, video, soundscapes, copy). Three axioms (safety-abundance-softness fantasy / semi-permeable membrane / ma 間), six fully-specified modes, verified audio numbers (BPM · swing · LUFS), a 10-question QA gate, and anti-patterns blocking liminal-space drift, AI-slop clichés, and streak/obligation reinvention |

## Usage Examples

```bash
# Discover trending topics in a field
/deep-thinking:pulse AI agents

# Deep dive into a specific topic
/deep-thinking:deep-research Claude Code plugin marketplace best practices

# Create a new skill/instruction
/deep-thinking:forge-prompt code review checklist for security vulnerabilities

# Process meeting transcript
/deep-thinking:meeting-notes [paste transcript or provide file path]

# Translate English IT article to Korean
/deep-thinking:translate-kr [paste English article or provide file path]

# Generate blog cover image prompt
/deep-thinking:blog-cover "Why Microservices Fail" | "complexity debt accumulates faster than you think"

# Write an IT tech blog article with source-cited bullet points
/deep-thinking:blog Why Microservices Fail — complexity debt patterns from 16 years of post-mortems

# Ground an answer in your local markdown archive
/deep-thinking:ground What does my archive say about microservices failure modes?

# Forge a Z-Image-Turbo photorealism prompt
/deep-thinking:writing-z-image-turbo-prompts 30s woman in a rainy Seoul alley

# Forge or verify a Hidden Reality (anti-optimization) software idea
/deep-thinking:hidden-reality calendar app that deliberately wastes AI on aesthetic shock

# Refactor a schedule file into a ground-truth index
/deep-thinking:schedule schedules/schedule-2026-06.md --mode=refine

# Capture a raw thought-dump into the monthly insight log
/deep-thinking:journal "realized passive index investing only works if I never check prices"
```

## Requirements

- Claude Code 1.0.33+

### MCP Server Dependencies

| Command | Required | Optional |
|---------|----------|----------|
| `/deep-thinking:init-vault` | None | - |
| `/deep-thinking:ground` | None | Brave Search, Reddit, Fetch (Stage 5 gap-filling only) |
| `/deep-thinking:journal` | Time | - |
| `/deep-thinking:schedule` | None | - |
| `/deep-thinking:deep-research` | Time, Brave Search, Reddit | - |
| `/deep-thinking:lint` | None | - |
| `/deep-thinking:save-answer` | None | - |
| `/deep-thinking:pulse` | Time, Brave Search, Reddit | - |
| `/deep-thinking:forge-prompt` | None | - |
| `/deep-thinking:meeting-notes` | Time, Brave Search | Context7, Fetch |
| `/deep-thinking:translate-kr` | Brave Search | - |
| `/deep-thinking:blog-cover` | None | - |
| `/deep-thinking:blog` | Time, Brave Search, Reddit | Fetch, Context7 |
| `/deep-thinking:writing-z-image-turbo-prompts` | None | - |
| `/deep-thinking:hidden-reality` | None | Brave Search (SCOUT mode for live 2025–2026 artifacts) |

### Quick MCP Setup

```bash
# Time
claude mcp add time -s user -- uvx mcp-server-time

# Brave Search (get API key: https://brave.com/search/api)
claude mcp add-json -s user brave-search '{"command":"npx","args":["-y","brave-search-mcp"],"env":{"BRAVE_API_KEY":"YOUR_API_KEY"}}'

# Reddit
claude mcp add reddit -s user -- uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit

# Context7 (Library Documentation)
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp

# Fetch (Web Crawling)
claude mcp add fetch -s user -- uvx mcp-server-fetch
```

### CLI Tools for `/deep-thinking:ground`

The 5-stage pipeline relies on modern shell CLIs, plus SQLite (FTS5-enabled) and Python 3 for the BM25 index that ranks Stage 1 candidates. One-shot Homebrew install:

```bash
brew install fd ripgrep bat sd fzf scc tokei yq glow lychee sqlite python && \
brew install harehare/tap/mq
```

| Tool | Role |
|------|------|
| `fd` | Stage 1 filename match |
| `rg` (ripgrep) | Stage 1 content scan; Stage 3 `-C 5` context extraction |
| `mq` | **Stage 2 Markdown AST heading extraction — critical.** Zero false positives on `##` inside code blocks |
| `yq` | Stage 1 YAML frontmatter filtering |
| `glow` | Stage 4 render verification |
| `lychee` | Archive-wide link validator |
| `sqlite` | **Stage 1 BM25 ranking via `vault.fts5.db`** — FTS5-enabled SQLite CLI; biggest context-budget saver when the index exists |
| `python` | Runs `fts5-reindex.py` at the vault root to (re)build `vault.fts5.db` with the trigram tokenizer (~3s for 200 files) |
| `bat`, `sd`, `fzf`, `scc`, `tokei` | General modern-CLI layer referenced by Stage 0 tool awareness |

> Homebrew's `sqlite` ships with FTS5 compiled in, unlike some system-shipped builds. After install, ensure `$(brew --prefix)/opt/sqlite/bin` is on your `PATH` so `sqlite3` resolves to the FTS5-capable binary rather than the OS default.

#### Optional but Recommended — Build the FTS5 Index

The `/deep-thinking:ground` pipeline runs without an index (Stage 1 falls back to `rg`/`Grep`), but the FTS5 index unlocks **BM25-ranked candidate selection** — the single biggest context-budget saver across the 5 stages, especially for CJK substring matching via the trigram tokenizer.

> **Shortcut:** run `/deep-thinking:init-vault` inside the folder — it performs the CLI preflight above, deploys the script, scaffolds the vault conventions, builds the index, and verifies it with a BM25 smoke query, all in one command. The manual steps below remain for setups outside Claude Code.

Drop `fts5-reindex.py` into the markdown directory you want to ground against (it auto-detects its own parent as the vault root) and run it once:

```bash
# 1. Copy the script into the LLM Wiki / markdown archive root
cp ~/.claude/plugins/marketplaces/jsonobject-marketplace/plugins/deep-thinking/fts5-reindex.py /path/to/your/llm-wiki/

# 2. Build vault.fts5.db at that root (~3s for ~200 files)
cd /path/to/your/llm-wiki
python3 fts5-reindex.py
```

Re-run after major edits to refresh the index. If `vault.fts5.db` is absent or stale, Stage 1 transparently falls back to `rg`/`Grep` — the index is purely an acceleration layer.

The optional Stage 5 MCP servers (Brave Search, Reddit, Fetch) are already covered in **Quick MCP Setup** above — no ground-specific MCP is required.

## License

MIT
