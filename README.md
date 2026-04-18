# Claude Code Quick Setup

Anthropic's AI-powered terminal coding assistant with MCP Server integration.

## Prerequisites

```bash
# Install Node
nvm install node && nvm alias default node

# Install uv (for Python-based MCP servers)
brew install uv
```

## Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code

# Environment variables for non-English input lag fix
echo 'export TERM=xterm-256color' >> ~/.bashrc
echo 'export LC_ALL=C.UTF-8' >> ~/.bashrc
```

## Authentication

### Anthropic Console (Pro plan required)

```bash
claude
> /login
```

### Amazon Bedrock

```bash
export AWS_ACCESS_KEY_ID={your-key}
export AWS_SECRET_ACCESS_KEY={your-secret}
export AWS_REGION_NAME=us-west-1
export CLAUDE_CODE_USE_BEDROCK=1
```

### Custom LLM Gateway

```bash
export ANTHROPIC_BASE_URL={your-gateway-url}
export ANTHROPIC_AUTH_TOKEN={your-auth-token}
```

## Basic Usage

```bash
claude           # New session
claude -c        # Continue last session
claude -r        # Resume specific session
```

```bash
> /clear                    # Reset context
> /model opus               # Switch to Opus 4.5
> /model sonnet             # Switch to Sonnet 4.5
> /model sonnet[1m]         # Sonnet 4.5 with 1M context
> @{file-path} {prompt}     # Include files
> {prompt} ultrathink       # Enable extended thinking
> /compact "{instructions}" # Manual context compaction
```

**Mode Switching:**
- `TAB` - Toggle extended thinking
- `SHIFT+TAB` (2x) - Enter Plan Mode (read-only analysis)
- `SHIFT+TAB` (1x) - Exit to Edit Mode

## MCP Servers Installation

### Time

```bash
claude mcp add time -s user -- uvx mcp-server-time
```

### Context7 (Library Documentation)

```bash
claude mcp add context7 -s user -- npx -y @upstash/context7-mcp
```

### Brave Search

Get API key from [brave.com/search/api](https://brave.com/search/api) (Free: 5,000 queries/month)

```bash
claude mcp add-json -s user brave-search '{"command":"npx","args":["-y","brave-search-mcp"],"env":{"BRAVE_API_KEY":"{your-key}"}}'
```

### Fetch (Advanced Web Crawling)

```bash
claude mcp add fetch -s user -- uvx mcp-server-fetch
```

### Reddit

```bash
claude mcp add reddit -s user -- uvx --from git+https://github.com/adhikasp/mcp-reddit.git mcp-reddit
```

### Playwright (Browser Automation)

```bash
npm install -g @executeautomation/playwright-mcp-server
claude mcp add playwright -s user -- npx -y @executeautomation/playwright-mcp-server
```

### Serena (LSP + Long-term Memory RAG)

```bash
# Run from project root
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)

# Initial onboarding
claude
> start Serena onboarding
```

### Slack

```bash
claude mcp add-json -s user slack '{"command":"npx","args":["-y","slack-mcp-server@latest"],"env":{"SLACK_MCP_XOXP_TOKEN":"{your-token}"}}'
```

### Notion

```bash
claude mcp add-json -s user notion '{"command":"npx","args":["-y","@notionhq/notion-mcp-server"],"env":{"NOTION_TOKEN":"{your-token}"}}'
```

## Memory: CLAUDE.md

Claude Code uses `CLAUDE.md` files as persistent memory:

| Path | Scope |
|------|-------|
| `~/.claude/CLAUDE.md` | Global (all projects) |
| `./CLAUDE.md` | Project-specific |

The `CLAUDE.md` in this repository root serves as the **global memory** template, defining behavioral rules, MCP server usage patterns, and response preferences.

## Deep Thinking Plugin

This repository is a **Claude Code Plugin Marketplace** containing the `deep-thinking` plugin.

### Installation

```bash
# Add marketplace (one-time setup)
/plugin marketplace add JSON-OBJECT/claude-code

# Install plugin
/plugin install deep-thinking@jsonobject-marketplace

# Restart Claude Code to load the plugin
```

### Update

When a new plugin version is published (e.g. `1.1.0 → 1.2.0`), apply it to the current Claude Code session without a restart:

```bash
# 1. Pull latest marketplace metadata and cache the new plugin source
/plugin marketplace update jsonobject-marketplace

# 2. Hot-reload the active session so new commands/skills/agents become available
/reload-plugins
```

With `autoUpdate: true` on the marketplace (default), Claude Code also refreshes it automatically on launch — the two commands above just apply the update immediately instead of waiting for the next start.

### Commands

#### `/deep-thinking:pulse {topic}` — Trend Radar
> **Before you research, know WHAT to research.**

Scans 5-8 subreddits × 75+ posts to identify what's genuinely hot RIGHT NOW.

| Feature | What It Does |
|---------|--------------|
| **Heat Score Formula** | Objective ranking: (Upvotes × 0.4) + (Comments × 0.3) + (Cross-sub × 0.2) + (Recency × 0.1) |
| **News Cross-Validation** | Compares Reddit trends against mainstream news — prevents echo chamber reports |
| **Emerging Signals Watch** | Tracks low-heat topics with rising momentum — tomorrow's headlines today |
| **Actionable Output** | Every issue includes a ready-to-run `/deep-research` query |

**Use before:** `/deep-research` — ensures you research the RIGHT topic, not just any topic.

---

#### `/deep-thinking:deep-research {topic}` — Forensic Tech Audit
> **One-shot research that answers questions before you ask them.**

Conducts 15-20+ searches with mandatory Phase Zero "Unknown Unknowns" discovery.

| Feature | What It Does |
|---------|--------------|
| **Phase Zero Protocol** | Questions the question itself — catches terminology confusion, outdated assumptions, missed prerequisites |
| **One-Shot Completeness** | Anticipates 5 follow-up questions ("What is it?" → "How much?" → "Gotchas?" → "Show code" → "Verdict?") and answers ALL in one report |
| **Ki-Sho-Ten-Ketsu Structure** | Four-act narrative (Setup → Development → Turn → Conclusion) — reads like investigative journalism, not bullet lists |
| **Community + Official Balance** | Reddit/HN sentiment weighted proportionally against official sources — 70% positive / 30% concern = both reported |

**Output:** Publication-ready deep dive that feels like Ars Technica meets Gemini Deep Research.

---

#### `/deep-thinking:forge-prompt {instruction}` — Instruction Smithy
> **Build prompts that resist rationalization.**

Creates bulletproof instructions following the Superpowers philosophy with 9 mandatory components.

| Component | Purpose |
|-----------|---------|
| **Iron Law** | ONE non-negotiable rule that guarantees failure if broken |
| **Red Flags Section** | Mental patterns that signal you're about to fail — "If you catch yourself thinking..." |
| **Rationalization Table** | Preempts every excuse with direct rebuttal — Excuse \| Reality format |
| **Phase Gates** | Clear checkpoints that MUST be passed before proceeding |
| **Strong Language Protocol** | MUST/NEVER/ALWAYS — no soft language ("should", "consider", "try to") |

**Philosophy:** If you think you don't need the structure, you need it most.

---

#### `/deep-thinking:meeting-notes {transcript}` — Narrative Documentation
> **Meeting notes that tell a story, not list fragments.**

Transforms raw transcripts into narrative-driven documentation with 6-phase verification.

| Feature | What It Does |
|---------|--------------|
| **Counterparty Intelligence** | External meetings: 3+ searches per counterparty for context (size, tech stack, recent news) |
| **STT Error Correction** | Catches phonetic mishearings ("jenkinsun" → "Jenkins") with 2+ source verification |
| **Immediate Inline Definitions** | Technical terms explained right where they appear (> 📘 format), not buried in glossary |
| **Storytelling Tone + Metaphors** | Mandatory 1-2 metaphors per document — "From gatekeeper to guardrail" style |
| **Zero Detail Loss** | Every business-relevant point preserved — 400-5000+ words scaled to source density |

**Anti-pattern:** Bullet lists. This produces flowing narrative with cause-and-effect reasoning.

---

#### `/deep-thinking:translate-kr {article}` — Korean Transcreation
> **Rewriting in Korean, not converting English structures.**

Transcreates English IT articles into native Korean with terminology verification and 10 anti-artifact rules.

| Feature | What It Does |
|---------|--------------|
| **Tier 1/2 Verification** | Established terms: 1 official source / New terms: 2+ sources including community (velog, tistory) |
| **10 Anti-Translation-Artifact Rules** | Pronoun elimination, Passive→Active, Sino-Korean ban, Emotional modifier ban, etc. |
| **Community Standard Priority** | If Korean dev community uses English 70%+ of the time, keep English (Token, Prompt, Fine-tuning) |
| **Code Block Protection** | NEVER modifies content inside code blocks or inline code |

**Key insight:** "Fine-tuning" → "파인튜닝" (community usage), NOT "미세 조정" (textbook translation).

---

#### `/deep-thinking:blog-cover {title and concept}` — Creative Director for Gemini
> **Anti-AI-looking blog covers that make readers curious.**

Generates image prompts for Gemini Nano Banana Pro with 6-phase visual storytelling.

| Feature | What It Does |
|---------|--------------|
| **Visual Metaphor First** | Every cover starts with an unexpected analogy — "Kubernetes = postal worker sorting containers" |
| **Chain-of-Thought Composition** | Explicit 9-grid spatial positioning — asymmetry always, center composition = AI tell |
| **Anti-AI Armor** | Mandatory "Avoid" section with 8+ items (symmetry, HDR, plastic textures, generic tech imagery) |
| **Imperfection Keywords** | 2-3 required: "visible brushstrokes", "analog film grain", "slightly uneven lines" |
| **Title Typography Mandatory** | Every prompt includes title overlay specifications — covers without title = incomplete |

**Artist references:** Christoph Niemann, Saul Steinberg, The New Yorker editorial style.

---

#### `/deep-thinking:ground {question}` — Markdown Archive Grounding
> **No answer without local grounding — every claim cites `file:line`.**

Executes a 5-stage pipeline (Discovery → Map → Pinpoint → Verify → Augment) over your local `.md` archive to produce cite-grade answers without burning context on cold file reads.

| Feature | What It Does |
|---------|--------------|
| **5-Stage Pipeline** | Narrow → Map → Pinpoint → Verify → Augment — never reverse the order |
| **Context Budget Optimizer** | `mq '.h2'` heading scan turns 2,000-line files into 10-line maps — avoids Lost-in-the-Middle |
| **Multi-Language Discovery** | EN / KR / generic-name variants in Stage 1 — empirically expands 4→8 candidate files |
| **Multi-File Cross-Synthesis** | Interpretive questions pull layers from 4+ files (philosophy + archetype + facts + record) |
| **`file:line` Citations** | Every claim traceable — no line number, no claim |
| **Absence Proof, Not Assumption** | Web augmentation (Stage 5) only after local absence is demonstrated |

**Philosophy:** The curated `.md` corpus is ground truth. Web is a supplement for gaps only.

---

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

## References

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices/)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
