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

| Command | Description |
|---------|-------------|
| `/deep-thinking:pulse {topic}` | Trend radar scanning 5+ subreddits and 75+ posts to identify hot issues before deep research |
| `/deep-thinking:deep-research {topic}` | Comprehensive multi-source research with 15+ searches, Reddit/news cross-validation, and Ki-Sho-Ten-Ketsu structured report |
| `/deep-thinking:forge-prompt {instruction}` | Create bulletproof instructions/skills with Iron Laws, anti-rationalization tables, and mandatory checklists |
| `/deep-thinking:meeting-notes {transcript}` | Transform meeting transcripts into narrative-driven documentation with counterparty research and verified terminology |
| `/deep-thinking:translate-kr {article}` | Transcreate English IT articles into native Korean with terminology verification and anti-translation-artifact rules |
| `/deep-thinking:blog-cover {title and concept}` | Generate anti-AI-looking blog cover image prompts for Gemini Nano Banana Pro with visual metaphors and title typography |
| `/deep-thinking:ground {question}` | 5-stage pipeline (Discovery → Map → Pinpoint → Verify → Augment) that grounds answers in the local `.md` archive with mandatory `file:line` citations; web augmentation only for proven gaps |

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

# Ground an answer in your local markdown archive
/deep-thinking:ground What does my archive say about microservices failure modes?
```

## Requirements

- Claude Code 1.0.33+

### MCP Server Dependencies

| Command | Required | Optional |
|---------|----------|----------|
| `/deep-thinking:pulse` | Time, Brave Search, Reddit | - |
| `/deep-thinking:deep-research` | Time, Brave Search, Reddit | - |
| `/deep-thinking:forge-prompt` | None | - |
| `/deep-thinking:meeting-notes` | Time, Brave Search | Context7, Fetch |
| `/deep-thinking:translate-kr` | Brave Search | - |
| `/deep-thinking:blog-cover` | None | - |
| `/deep-thinking:ground` | None | Brave Search, Reddit, Fetch (Stage 5 gap-filling only) |

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

The `/deep-thinking:ground` pipeline runs without an index (Stage 1 falls back to `rg`/`Grep`), but the FTS5 index unlocks **BM25-ranked candidate selection** — the single biggest context-budget saver across the 5 stages, especially for CJK substring matching via the trigram tokenizer. Drop `fts5-reindex.py` into the markdown directory you want to ground against (it auto-detects its own parent as the vault root) and run it once:

```bash
# 1. Copy the script into the LLM Wiki / markdown archive root
cp ~/.claude/plugins/marketplaces/jsonobject-marketplace/fts5-reindex.py /path/to/your/llm-wiki/

# 2. Build vault.fts5.db at that root (~3s for ~200 files)
cd /path/to/your/llm-wiki
python3 fts5-reindex.py
```

Re-run after major edits to refresh the index. If `vault.fts5.db` is absent or stale, Stage 1 transparently falls back to `rg`/`Grep` — the index is purely an acceleration layer.

The optional Stage 5 MCP servers (Brave Search, Reddit, Fetch) are already covered in **Quick MCP Setup** above — no ground-specific MCP is required.

## License

MIT
