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

#### `/deep-thinking:blog {topic or draft}` — IT Tech Blog Writer
> **Fact-based blog posts that cite every claim.**

A 16-year veteran blogger framework that produces source-cited IT tech articles with mandatory bullet point formatting and inline hyperlinks.

| Feature | What It Does |
|---------|--------------|
| **Phase Zero Validation** | Time context, terminology check, version sanity, alternative angles — before any drafting |
| **4-Tier Source Hierarchy** | Official docs → primary research → reputable secondary → user-generated (Reddit/HN) — each cited inline with its tier label |
| **Mandatory Bullet Formatting** | No wall-of-text — structured bullet hierarchies optimized for scan reading |
| **Inline Hyperlinks + Quote Format** | `[[Reddit]](url)` for facts, blockquote with `— u/user, r/sub [[Link]]` for direct quotes |
| **Community Sentiment Required** | Reddit + HN coverage is REQUIRED, not optional — unfiltered user experience over press releases |

**Anti-pattern:** Unsourced opinion essays. This produces journalism-grade tech writing where every claim is traceable.

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

**Verdict layer (optional).** If the vault root holds a `verdicts.md` hub, Stage 1 consults it *before* searching and stops there when a live verdict card already rules on the question — no re-research, no Stage 5. The hub is meant to stay a thin router: it is read on every question, so once it grows past ~15 KB the layer switches to a lookup query against `verdicts/<domain>/` and reads only the card that matched. Past a card's `stale_after`, only its appeal conditions get re-checked, never the whole topic. No `verdicts.md` means the step is skipped and the pipeline runs unchanged. See `/deep-thinking:verdict` below.

---

#### `/deep-thinking:verdict [path or blank]` — Conclusion Distiller

> **A verdict is a settled conclusion a future session obeys instead of re-researching.**

**The problem it solves:** a session produces a genuinely good answer, and then ends before anyone files it. The reasoning evaporates, and the next session pays for the same investigation again. This inhales that answer into the wiki's brain before it evaporates — compressed into **verdict cards**: compact, binding rulings a later session acts on directly.

Two sources, one skill — pass a path to an `_answers/` file saved earlier by `/deep-thinking:save-answer`, or leave it blank to distil the conversation you are in right now.

Default summarising keeps the narrative and drops the numbers. This does the opposite: it carries every number, proper noun, version string, parameter value, price, rejected option with its reason, and recorded dissent — and leaves behind the research narrative that produced them.

| Feature | What It Does |
|---------|--------------|
| **Two Sources** | An `_answers/` crystal from `save-answer`, or the live conversation when no path is given |
| **Rejects Slot** | The highest-value slot per token — candidate, why it lost, what would reopen it. Without it the next session re-investigates every option the card never mentions |
| **Appeal Slot** | Names the conditions that overturn the ruling, so an expired card needs three lines re-checked instead of a fresh investigation |
| **Shelf Life, Not a Backlog** | `stale_after` is set from the card's fastest-decaying claim, turning review into a dated queue instead of an ever-growing `human_reviewed: false` list |
| **Amend at Constant Size** | New facts land in slots the card already has — ruling rewritten, not appended — and every new card amends the existing cards it just contradicted |
| **Retrieval-Aware by Construction** | Written against the FTS5 index: `path` is unindexed, headings are invisible, tags are searchable, and sub-3-character CJK tokens never match at all |

**Philosophy:** Research is expensive and decays; a decision made from it should be paid for once. Deep research is the heavy axis and stays that way — the verdict layer is the fast one, the thing you reach for when the answer is already good and the only risk left is that it disappears. The card states the ruling and the conditions that would overturn it; how the deliberation went stays in the source it was distilled from.

---

#### `/deep-thinking:writing-z-image-turbo-prompts {seed}` — ZIT Photorealism Forger
> **90hex's discovery, operationalized — exit the beauty-stock prior with one camera body, one film stock, and an anti-AI 4-stack.**

Transforms any natural-language seed (any language, any length) into an `sd-dynamic-prompts` mustache template (300–450 words of template surface, expanding to a 200–400 word resolved prompt per roll) for Z-Image-Turbo, plus the exact Forge Neo / ComfyUI settings.

| Feature | What It Does |
|---------|--------------|
| **Iron Law: 90hex Triple** | Every output locks in (1) one real camera body + (2) one real film stock or lighting keyword + (3) anti-AI 4-stack — no exceptions |
| **11-Slot Doctrine** | Identity slots fixed plaintext; environment slots `{a\|b\|c}` mustache wildcards — variation without identity drift |
| **Anti-AI Armor** | Negative prompts, "average" alone, "cinematic lighting", tag-soup, and meta-tags are forbidden by construction |
| **Mustache Template Output** | Never a single frozen prompt — always a dynamic template that yields fresh resolved prompts per roll |
| **Runner Settings Included** | Forge Neo / ComfyUI sampler, CFG, steps, and resolution baked into the output |

**Philosophy:** ZIT's training prior is beauty stock photography. The only exit is naming a real camera body, a real film stock, and stacking anti-AI anchors. Violating the letter of the rule violates the spirit of ZIT photorealism.

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
| `/deep-thinking:blog` | Time, Brave Search, Reddit | Fetch, Context7 |
| `/deep-thinking:ground` | None | Brave Search, Reddit, Fetch (Stage 5 gap-filling only) |
| `/deep-thinking:verdict` | None | - |
| `/deep-thinking:writing-z-image-turbo-prompts` | None | - |

### Setup for `/deep-thinking:ground`

The 5-stage pipeline leans on modern shell CLIs for Stages 1–4 and reuses the globally-installed MCP servers for optional Stage 5 web augmentation.

**CLI tools — one-shot Homebrew install:**

```bash
brew install fd ripgrep bat sd fzf scc tokei yq glow lychee && \
brew install harehare/tap/mq
```

| Tool | Role in the 5-stage pipeline |
|------|------------------------------|
| `fd` | Stage 1 — filename/path match (replaces `find`) |
| `rg` (ripgrep) | Stage 1 content scan; Stage 3 `-C 5` context extraction with line numbers |
| `mq` | **Stage 2 — Markdown AST heading extraction (`mq '.h2' file.md`).** Zero false positives on `##` inside code blocks (40% error rate vs `rg '^##'` empirically) |
| `yq` | Stage 1 — YAML frontmatter field filtering (`yq --front-matter=extract '.tags[]'`) |
| `glow` | Stage 4 — terminal Markdown render for visual verification of tables, links, heading structure |
| `lychee` | Archive maintenance — async link validator (`lychee "**/*.md"`) to catch citation rot |
| `bat`, `sd`, `fzf`, `scc`, `tokei` | General modern-CLI layer invoked by Stage 0 tool awareness (readable cat, sed replacement, fuzzy finder, code counters) |

**MCP servers — Stage 5 (optional, for web gap-filling only):**

No ground-specific MCP server. The optional three (Brave Search, Reddit, Fetch) are already covered in the [MCP Servers Installation](#mcp-servers-installation) section above — install only if your local archive leaves gaps that need web augmentation.

## References

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices/)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
