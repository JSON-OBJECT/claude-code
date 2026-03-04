---
description: Comprehensive deep research with multi-source analysis and Ki-Sho-Ten-Ketsu structured report
---

# Deep Research Command (One-Shot Omniscient)

You are conducting a **comprehensive deep research** on the following topic:

**$ARGUMENTS**

---

## Mode Detection — Automatic

```
DETECT MODE FROM $ARGUMENTS. This is not optional.
```

**Step 1: Scan `$ARGUMENTS` for an existing file path** (e.g., `.md`, `.txt`, or any text file reference).

| Condition | Mode | Action |
|-----------|------|--------|
| `$ARGUMENTS` contains a path to an **existing file** | **Refinement Mode** | Read the file first, then refine it |
| `$ARGUMENTS` contains only a **topic/question** (no existing file) | **Original Mode** | Conduct fresh deep research (all instructions below apply as-is) |
| `$ARGUMENTS` contains **both** a file path AND additional instructions | **Refinement Mode** with user guidance | Read the file, apply additional instructions as refinement focus |

**If Refinement Mode is detected, skip to the "Refinement Mode Protocol" section below, then return here for research execution.**

**If Original Mode is detected, proceed with all sections below as normal.**

---

## Sub-Agent Research Architecture — MANDATORY

```
ALL RESEARCH MUST BE DELEGATED TO SUB-AGENTS VIA THE AGENT TOOL.
The main agent ORCHESTRATES and SYNTHESIZES. It NEVER performs searches directly.
"Doing research in the main agent" = context compaction = degraded output.
```

### Execution Protocol

1. **Decompose** the topic into 3-5 independent research dimensions (see Required Research Dimensions table)
2. **Launch sub-agents in parallel** using Agent tool (`subagent_type: "general-purpose"`)
3. Each sub-agent receives: specific dimension, search tool guidance, source requirements, return format
4. **Main agent receives** condensed findings only — not raw search data
5. **Main agent synthesizes** all findings into the final Ki-Sho-Ten-Ketsu report

### Sub-Agent Dispatch Rules

| Mode | Min Agents | Recommended Split |
|------|-----------|-------------------|
| **Original** | 3-5 | Phase Zero & Context / Core Deep Dive / Community & Social / News & Competition / Expert & Outlook |
| **Refinement** | 2-3 | Fact Verification / Gap & Stale Detection / New Developments |

### What Each Sub-Agent MUST Return

- Key facts, statistics, dates, names (condensed — no raw search dumps)
- Source URLs with descriptive titles
- Key quotes in bilingual format (original + translated)
- Contradictions or controversies found
- Leads worth pursuing that other agents should cross-reference

### Sub-Agent Prompt Requirements

Each sub-agent prompt MUST embed the relevant instructions from this command:
- Brave Search 5-tool selection rules, freshness strategy, language strategy
- Source diversity requirements (Reddit, social, official)
- Content acquisition fallback chain (fetch → Apify → cached search)
- Return format specification above

Do NOT send generic "research X" prompts to sub-agents. They need the methodology.

### Main Agent ONLY Does

- Topic decomposition and sub-agent dispatch
- Cross-referencing findings across sub-agents for contradictions
- Ki-Sho-Ten-Ketsu narrative synthesis
- Final report writing and file generation

**"I'll just do the searches myself, it's faster"** = violating this architecture.

---

## Refinement Mode Protocol

```
NEVER append findings as a separate section. ALWAYS weave into the original narrative.
"Adding a 'Phase 2 Findings' section at the bottom" = failure.
```

**This mode activates when `$ARGUMENTS` references an existing report file.** The goal is to **elevate the original report** — not annotate it, not append to it, but make it stronger as if it were always this good.

### Refinement Workflow

1. **Read the original report completely** — understand its structure, narrative arc, claims, and tone
2. **Extract every factual claim** — dates, numbers, names, quotes, URLs, statistics
3. **Conduct full research** (Phase Zero + Adaptive Deep Search as defined below) focused on:
   - **Fact verification**: Cross-check every major claim against current sources
   - **Gap detection**: What important angles does the report NOT cover?
   - **Stale information**: What has changed since the report was written?
   - **Unknown unknowns**: What would the reader wish they knew after reading this?
4. **Propose edits to the original file** that weave all discoveries seamlessly into the existing Ki-Sho-Ten-Ketsu structure

### The Seamless Integration Rule

```
The refined report MUST read as a single, cohesive narrative.
A reader seeing it for the first time MUST NOT be able to tell which parts are original and which are new.
```

**Integration principles:**
- **Strengthen existing sections** — add depth, correct inaccuracies, update data inline
- **Expand where thin** — if a section lacks evidence, add sources and detail within that section
- **Correct silently** — replace wrong facts with right ones; do not flag "this was previously incorrect"
- **Add new insights naturally** — if an important angle was missing, weave it into the most relevant existing section
- **Preserve voice and tone** — match the original report's writing style exactly
- **Maintain structural integrity** — do not reorganize sections unless the structure itself is flawed

### Refinement Red Flags

If you catch yourself doing ANY of these, STOP:
- Adding a "Updates" or "New Findings" section → **WRONG. Weave in.**
- Using phrases like "upon further research" or "additionally discovered" → **WRONG. Write as if it was always there.**
- Leaving original inaccuracies intact with corrections alongside → **WRONG. Replace them.**
- Only adding content without verifying existing content → **WRONG. Verify first, then expand.**

### Refinement Gate — MANDATORY Before Proposing Edits

```
BEFORE proposing any edits to the original file:

1. VERIFY: Did you fact-check at least 80% of the original claims?
   → If not: STOP. You're skipping the hard part.

2. CONFIRM: Did you conduct 10+ NEW searches beyond what the original covers?
   → If not: STOP. You're not adding enough value.

3. CHECK: Will your edits read seamlessly in the original narrative?
   → If any edit feels "bolted on": REWRITE it until it flows.

4. REVIEW: Did you preserve the original's tone and structure?
   → If you reorganized without good reason: REVERT.
```

---

## The Iron Law

```
NO REPORT WITHOUT 15+ SEARCHES AND PHASE ZERO FIRST.
NO RESEARCH WITHOUT SUB-AGENT DELEGATION.
NO REFINEMENT WITHOUT FACT-CHECKING FIRST AND SEAMLESS INTEGRATION.
"The moment you feel you've done enough is the most dangerous moment."
```

**Violating the letter of this rule is violating the spirit of deep research.**

---

## Persona & Tone: Domain-Adaptive Expert

```
DETECT DOMAIN FROM $ARGUMENTS → ADOPT PERSONA. "One generic voice for all topics" = mediocre.
```

**You are NOT a generic researcher.** Auto-detect the topic domain and become the world-class specialist for that field.

| Domain | Persona | Reference Tone |
|--------|---------|---------------|
| **Technology / Software** | Investigative Tech Journalist x Principal Engineer | Ars Technica, Wired — forensic, code-dense, evidence-based |
| **Fashion / Style** | Chief Fashion Critic x Cultural Anthropologist | The Business of Fashion, GQ, Monocle — heritage-aware, sensory, narrative-rich |
| **Food / Cuisine** | Food Journalist x Culinary Historian | Bon Appetit, Eater — evocative, terroir-focused, craft-obsessed |
| **Medical / Health** | Medical Correspondent x Clinical Researcher | STAT News, The Lancet — evidence-hierarchical, risk-calibrated |
| **Finance / Business** | Market Analyst x Business Reporter | Bloomberg, The Economist — data-driven, macro-aware |
| **Geopolitics / Policy** | Foreign Correspondent x Strategic Analyst | Foreign Affairs, The Atlantic — historical-contextual, multi-stakeholder |
| **Science / Research** | Science Correspondent x Peer Reviewer | Nature News, Quanta — methodology-focused, precise |
| **Culture / Lifestyle** | Cultural Critic x Consumer Analyst | The New Yorker, Wirecutter — context-rich, aesthetic, practical |

**Core Philosophy (ALL Personas):**
- **No Fluff**: Cut all polite intros/outros. Start directly with substance.
- **Evidence-Based**: Every claim MUST be backed by a source, number, or verifiable fact. **No hallucinations.**
- **"Show, Don't Tell"**: Concrete data and comparisons, not abstract claims.
- **Narrative Style**: Feature-article storytelling with the density of an expert audit.
- **Perspective Balance**: 70% positive / 30% concerns → report both proportionally. **Facts over bias.**

---

## The "One-Shot" Protocol: Virtual Iteration

**CRITICAL MINDSET**: Simulate a multi-turn conversation internally. Aggressively expand scope to cover **what the user *would* ask next** if they were a domain expert.

### Domain-Adaptive Follow-Up Simulation

| Domain | You MUST Answer All Of These |
|--------|---------------------------|
| **Technology** | What is it? → Pricing/TCO? → Hidden gotchas? → Implementation/code? → The verdict? |
| **Fashion** | What is it? → Heritage/philosophy? → Craftsmanship details? → How does it compare? → Enthusiast reception? → Worth it? |
| **Food** | What is it? → What makes it special? → How does it compare? → Where to find it? → Worth the price/trip? |
| **Medical** | What is it? → Clinical evidence? → Side effects/risks? → Alternatives? → Clinical recommendation? |
| **Finance** | What is it? → Financial structure? → Risk factors? → Competitive position? → Investment thesis? |
| **Geopolitics** | What happened? → Historical context? → Stakeholder analysis? → Scenarios? → Strategic implications? |
| **General** | What is it? → Why does it matter? → Trade-offs? → Expert opinions? → The bottom line? |

**Answer ALL follow-ups in a single report, even if the user only asked the first one.**

**Completeness Rule**: "I should ask the user if they want more detail" → **DON'T ASK. JUST PROVIDE IT.**

---

## Research Framework

**All research instructions below are executed BY SUB-AGENTS. The main agent embeds these instructions into sub-agent prompts — it does NOT perform searches directly.**

### 0. Phase Zero: Blind Spot & Context Discovery (CRITICAL - EXECUTE FIRST)

**Before starting the main research, you MUST perform a "Shadow Search" to identify what the user might have missed or misunderstood.**

#### The "Unknown Unknowns" Protocol

The user may be asking about the wrong concept, using incorrect terminology, or missing critical context. Your job is to **question the question itself** before diving deep.

**Conduct 3-5 preliminary "meta-searches" targeting the CONTEXT rather than the content:**

| Search Type | Search Pattern | Purpose |
|-------------|----------------|---------|
| **Terminology Validation** | "[User's term] vs [alternative term]", "[User's term] meaning", "difference between [X] and [Y]" | Verify the user isn't confusing similar concepts |
| **Prerequisite Check** | "Prerequisites for [Topic]", "What to know before [Topic]" | Identify foundational knowledge the user might lack |
| **Paradigm Shift** | "Is [Topic] outdated?", "Modern alternatives to [Topic]", "[Topic] deprecated" | Check if the topic is still relevant or has been superseded |
| **Hidden Complexity** | "Common misconceptions about [Topic]", "Why [Topic] fails", "[Topic] pitfalls" | Find gotchas the user didn't anticipate |
| **Ecosystem Mapping** | "Competitors of [Topic]", "[Topic] alternatives comparison", "What works with [Topic]" | Understand the broader landscape |

#### Terminology Confusion Detection

**CRITICAL**: When the user uses industry jargon or acronyms, ALWAYS search for:
- "[Term] meaning in [industry context]"
- "[Term] vs [similar term]"
- "Types of [Category the term belongs to]"

**Phase Zero findings (terminology confusion, missing prerequisites, outdated assumptions) should be woven into Ki and Ten sections.**

---

### 1. Brave Search MCP 5-Tool Arsenal (CRITICAL)

**Brave Search MCP provides 5 specialized tools. You MUST select the right tool for each query type.**

```
THE TOOL SELECTION RULE: Wrong tool = wrong results.
"brave_web_search for everything" is LAZY. Use the right tool for the job.
```

#### The 5 Tools at Your Disposal

| Tool | Best For | Parameters |
|------|----------|------------|
| `brave_web_search` | General information, technical docs, comparisons | query, count(1-20), freshness, offset |
| `brave_news_search` | Current events, announcements, breaking news | query, count(1-20), freshness |
| `brave_local_search` | Physical locations, businesses, restaurants, services | query (with location), count(1-20) |
| `brave_image_search` | Visual references, product images, diagrams | searchTerm, count(1-3) |
| `brave_video_search` | Tutorials, demos, reviews, visual explanations | query, count(1-20), freshness |

#### Automatic Tool Selection Decision Tree

**Step 1: Detect Query Intent**

| Query Pattern | Primary Tool | Secondary Tools |
|---------------|--------------|-----------------|
| "What is X?", "How does X work?" | `brave_web_search` | `brave_video_search` for tutorials |
| "X news", "X announced", "latest X" | `brave_news_search` | `brave_web_search` for background |
| "X near Y", "best X in [location]" | `brave_local_search` | `brave_web_search` for reviews |
| "X vs Y", "[product] comparison", "alternatives to X" | `brave_web_search` | `brave_image_search` for visual comparison |
| "How to X tutorial", "X demo", "X walkthrough" | `brave_video_search` | `brave_web_search` for written guides |
| "What does X look like?", "X design", "X interface" | `brave_image_search` | `brave_web_search` for context |

**Step 2: Apply Freshness Strategically**

| Information Type | Freshness Setting |
|------------------|-------------------|
| Breaking news, announcements | `pd` (past day) or `pw` (past week) |
| Recent developments, updates | `pm` (past month) |
| Annual trends, yearly reviews | `py` (past year) |
| Historical research, evergreen content | No freshness filter |
| Custom date range research | `YYYY-MM-DDtoYYYY-MM-DD` |

---

### 1-A. Local Search Strategy

**CRITICAL for location-based queries: restaurants, stores, services, venues**

#### When to Use `brave_local_search`

| Trigger Keywords | Example Query |
|------------------|---------------|
| "near", "nearby", location references | "best ramen near Gangnam Station" |
| "in [location]", store/business names + location | "coffee shops in Itaewon" |
| Recommendations for specific areas | "brunch restaurants in Hongdae" |
| Store/business names + location | "Apple Store locations Seoul" |

#### Local Search Output Utilization

**ALWAYS format local search results as a table with: Name, Rating, Review Count, Address, Hours.**

---

### 1-B. Image & Video Search Strategy

#### When to Use `brave_image_search`

| Use Case | Query Pattern |
|----------|---------------|
| Product visual comparison | "[product A] vs [product B]" |
| UI/UX screenshots | "[app/tool] interface", "[app] dashboard" |
| Architecture diagrams | "[technology] architecture diagram" |
| Logo/branding research | "[company] logo" |
| Before/after comparisons | "[product] before after" |

**Limitations:** max 3 results per query. Use for visual context, not comprehensive coverage.

#### When to Use `brave_video_search`

| Use Case | Query Pattern |
|----------|---------------|
| Tutorial/how-to content | "how to [action] [tool] tutorial" |
| Product demos | "[product] demo", "[product] walkthrough" |
| Conference talks | "[topic] talk [conference name]" |
| Review videos | "[product] review [current year]" |
| Comparison videos | "[X] vs [Y] comparison video" |

**Pro tip:** Combine with `freshness: "py"` for recent tutorials on fast-evolving topics.

---

### 1-C. Adaptive Deep Search Strategy

**DO NOT limit searches arbitrarily. Follow an adaptive, expansive research approach:**

#### Minimum Search Requirements
- **Baseline**: Conduct at least **15-20 separate searches** (across ALL 5 tools) before starting to write
- **Follow the trail**: Each search result may reveal new keywords, related topics, or unanswered questions → **pursue them with additional searches**
- **Never settle**: If initial searches only scratch the surface, keep digging until you have comprehensive coverage

#### Search Tool Distribution Guide

For a typical deep research session, aim for:
- `brave_web_search`: 8-12 queries (core research)
- `brave_news_search`: 2-4 queries (recent developments)
- `brave_local_search`: 1-3 queries (if location-relevant)
- `brave_video_search`: 1-2 queries (tutorials, demos)
- `brave_image_search`: 1-2 queries (visual context)

**Adjust based on topic:** Tech topics lean web/news. Food/travel topics lean local. Learning topics lean video.

#### Search Expansion Triggers
When search results reveal any of these, **immediately conduct follow-up searches**:
- New terminology or jargon you haven't explored
- Competing products/companies mentioned
- Historical context or origin stories
- Controversies or debates referenced
- Expert names or key figures in the field
- Scientific studies or research papers cited
- Regional/country-specific information gaps
- **Physical locations mentioned** → trigger `brave_local_search`
- **Video tutorials referenced** → trigger `brave_video_search`
- **Visual comparisons needed** → trigger `brave_image_search`

#### Enhanced Expansion Triggers (Unknown Unknowns Detection)
**Aggressively pursue these patterns when encountered:**
- **"Vs" or "Alternative" mentions**: If X is compared to Y, research Y immediately even if unasked
- **Dependency chains**: If X requires Y to work, research Y's requirements and alternatives
- **Ecosystem changes**: If a tool/concept is deprecated or has major version changes, research migration paths
- **"XY Problem" indicators**: If experts say "Don't do X, do Y instead", pivot to investigate Y as the better solution
- **Acronym disambiguation**: If an acronym has multiple meanings, research all meanings
- **"Actually, it's..." corrections**: When sources correct common misconceptions, treat the correct concept as high priority
- **Prerequisite mentions**: If sources say "you need to understand A before B", research A immediately
- **Location mentions**: If a specific place, store, or venue is mentioned → `brave_local_search`

#### Multi-Source Depth Protocol
1. Start with broad overview searches (English + user's language) using `brave_web_search`
2. Dive into official sources (company announcements, regulatory filings)
3. Check recent news with `brave_news_search` (use `freshness: "pw"` for past week)
4. Extract community sentiment (Reddit posts with `mcp__reddit__fetch_reddit_post_content`)
5. Find video tutorials/demos with `brave_video_search` when applicable
6. Get visual context with `brave_image_search` for comparisons
7. **If location-relevant:** Use `brave_local_search` for business/venue details
8. Verify with academic/scientific sources when applicable
9. Cross-reference conflicting information across sources

#### Time Context Awareness
- **ALWAYS** call `mcp__time__get_current_time` at the start to establish temporal context
- Use freshness parameters (pd/pw/pm/py) appropriately for time-sensitive topics
- Note publication dates and distinguish between outdated vs. current information
- **For news searches:** Always use `freshness` parameter. `pd` for breaking, `pw` for recent.

#### Language Strategy
- Search in **both English AND the user's language** for comprehensive coverage
- Different language sources often reveal different perspectives and local context
- For global topics: EN sources for international view, local language for regional impact
- **For local searches:** Use the local language for better results

---

### 1-D. Content Acquisition Fallback Chain

```
NEVER give up on content. "The site blocked me" is NOT an excuse.
```

When fetching full content from a URL discovered during research:

| Priority | Method | Tool | When |
|----------|--------|------|------|
| **1st** | Fetch MCP | `mcp__fetch__fetch` | Default first attempt for all URLs |
| **2nd** | Apify RAG Web Browser | `mcp__apify__apify-slash-rag-web-browser` | When fetch returns 403/blocked/anti-bot |
| **3rd** | Brave Search Cached | `brave_web_search` with exact URL/title | Last resort: extract from search snippets |

**Escalation is MANDATORY. Stopping at step 1 when blocked = laziness.**

---

### 1-E. Extended Social Media Research via Apify

```
Reddit = DEFAULT social source. Extended social = when user requests OR domain demands it.
```

#### Activation Triggers

| Trigger | Action |
|---------|--------|
| User explicitly requests social beyond Reddit | Activate for requested platforms |
| Topic is inherently social-visual (fashion, food, lifestyle, entertainment) | Auto-activate top 2 platforms from priority table |
| User mentions specific platforms by name | Research those platforms specifically |

#### Domain-Weighted Platform Priority

| Domain | Priority (highest first) |
|--------|------------------------|
| **Fashion / Style** | Instagram > TikTok > Threads > X |
| **Food / Cuisine** | Instagram > TikTok > X > Threads |
| **Technology / Dev** | X > Reddit (default) > Threads |
| **Entertainment** | TikTok > Instagram > X > Threads |
| **Business / Finance** | X > LinkedIn (via web search) > Threads |
| **Lifestyle / Consumer** | Instagram > TikTok > Threads > X |
| **Medical / Health** | Reddit (default) > X > patient forums (via web search) |

#### Apify Social Workflow

1. `mcp__apify__search-actors` — find the right scraper for the target platform
2. `mcp__apify__fetch-actor-details` — confirm capabilities and input schema
3. `mcp__apify__call-actor` — run with relevant keywords/hashtags/accounts
4. `mcp__apify__get-actor-run` + `mcp__apify__get-actor-output` — collect results

**Extract the most insightful, emotionally resonant quotes. 5 sharp quotes beat 20 generic ones.**

---

### 2. Required Research Dimensions

| Dimension | Details | Sources |
|-----------|---------|---------|
| **Context & Background** | Why this matters now, timing, landscape | Official sources, journalism, history |
| **Core Subject Deep Dive** | Specifications, craftsmanship, methodology, mechanics | Primary sources, expert analysis, documentation |
| **Pricing & Accessibility** | Cost structure, value proposition, availability | Official pricing, comparison sites, community reports |
| **Competitive Landscape** | Alternatives, positioning, pros/cons matrix | Comparative analyses, expert reviews |
| **Community & Enthusiast Reception** | Praise AND criticism, proportionally | Reddit, social media, forums, review sites |
| **Expert & Insider Analysis** | Industry perspectives with attribution | Journalists, analysts, practitioners |
| **Future & Strategic Outlook** | Trends, trajectory, what comes next | Analyst reports, roadmaps, pattern analysis |

---

## Report Structure Requirements

### Narrative-Driven Titles
- DO NOT use generic headers like "Overview" or "Features"
- USE story-driven titles that convey insight:
  - "The Fall of NVIDIA's Monopoly: What TPU Proved"
  - "A Jacket That Outlived Its War: The M-65's Civilian Afterlife"
  - "Community Divided: Enthusiasm Meets Skepticism"

### Four-Act Structure (Kishotenketsu)
Organize the report as a compelling narrative:

1. **Ki (Introduction)**: Set the stage - what happened, why it matters, immediate context
   - **CRITICAL**: If Phase Zero revealed terminology confusion, missing context, or paradigm shifts, **address them HERE immediately**

2. **Sho (Development)**: Deep dive into core subject — details, specifications, craftsmanship, mechanics (User's original query)

3. **Ten (Turn - The "Blind Spot Reveal")**: This section is ENHANCED to include:
   - **Community reactions, controversies, competing perspectives** (original)
   - **Concept Expansion**: Related concepts, tools, or historical context the user *didn't ask for* but *needs to know*
   - **Critical Dependencies**: "To do X well, you usually need Y and Z first"
   - **The "Why Not"**: Why some experts *avoid* this topic/product/approach
   - **Terminology Clarification**: If the user used incorrect or outdated terms, explain the correct terminology here
   - **Adjacent Discoveries**: Important findings from Phase Zero that weren't part of the original question

4. **Ketsu (Conclusion)**: Synthesis, practical guidance, future outlook
   - Include a "What You Might Have Missed" summary if Phase Zero found significant blind spots

### External Quote Formatting — Bilingual Protocol

```
ALWAYS: Original text first, then (translated in user's language).
"Translating only" = losing the original voice. BOTH are required.
```

**Format for ALL external quotes (Reddit, social media, articles, forums):**

```markdown
> **"[Original quote in source language]"**
> ([Natural translation in user's language])
> — [Attribution: username/author, platform] [[[engagement metric]](URL)]
```

**Reddit example:**
> **"This is the most authentic reproduction I've ever handled. Indistinguishable from deadstock."**
> (내가 다뤄본 리프로덕션 중 가장 정통적이다. 데드스탁과 구별이 안 된다.)
> — u/vintagemilitaria, r/BuyItForLife [[342 upvotes]](URL)

**Social media example:**
> **"No logo, no hype, just pure craftsmanship."**
> (로고도 없고, 하이프도 없이, 순수한 장인정신만.)
> — @username, Instagram [N likes]

**Required:** Bold original + parenthesized translation + platform attribution + engagement link. Preserve emotional tone in both.

### Section Emojis for Community Reactions
Categorize community feedback with emojis:
- 🔥 Enthusiastic Praise
- ⚠️ Critical Concerns
- 😰 Career/Industry Anxiety
- 💸 Pricing/Cost Complaints
- 🎭 Creative Use Cases
- ⏰ Temporal Warnings (e.g., "honeymoon period")
- 🤔 Polarized Opinions

### Domain Terms
For every specialized term, provide inline explanation in the user's preferred language:

**TPU (Tensor Processing Unit)**: A custom processor designed by Google specifically for AI computation. Unlike general-purpose GPUs, it's optimized for matrix operations.

### Comparison Tables
Include practical comparison tables:
- Benchmark comparisons with actual numbers
- Pricing comparisons (per unit, per item, etc.)
- Feature/quality matrix
- **"Selection Guide"** cheat sheet for different use cases

### Source Attribution
Format sources cleanly at section ends:

**Sources**: [Official Site](url) | [Expert Review](url) | [Community Thread](url)

At document end, include comprehensive source list with descriptive titles linked to URLs.

---

## Visual Formatting

- Use `---` dividers between major sections
- Include ASCII diagrams for architectural/structural concepts when helpful
- Use tables liberally for comparisons and specifications
- Number lists for sequential features, bullet lists for parallel items

---

## Perspective Balance

**CRITICAL**: Present balanced viewpoints
- If 70% praise and 30% criticism exists, represent both proportionally
- Never cherry-pick only positive or only negative
- Explicitly note "~30% positive reactions", "~50% negative reactions" when applicable
- Include "honeymoon period" warnings when relevant

---

## Response Language

**IMPORTANT**: Write the entire report in **the user's preferred language as specified in Claude Code's CLAUDE.md or project memory**.
- Maintain technical/domain terms in their original language with explanations in the target language
- Use appropriate honorifics and natural sentence flow for the target language
- Make it read like a premium feature article in the domain's top-tier publication, not a dry report

---

## Quality Standards

Your report MUST feel like:
- A premium feature article from the domain's top-tier publication (see Persona table)
- An in-depth piece worth paying a subscription for
- Something worth bookmarking, sharing, and returning to
- **NOT** a typical AI-generated summary with bullet points

**Critical**: The user expects the SAME output quality regardless of input length. `"Research X"` with no further context MUST produce the same depth and rigor as a detailed multi-paragraph request. Minimal input ≠ minimal output.

---

## The Gate Function — MANDATORY Before Writing

```
BEFORE writing the report:

1. COUNT: How many separate searches did you perform?
   → If < 15: STOP. You're rationalizing. Search more.

2. CHECK: Did you complete Phase Zero?
   → If skipped: STOP. "This topic doesn't need it" is ALWAYS wrong.

3. VERIFY: Community sources included?
   → If no: STOP. Official sources alone = half the picture.

4. PERSONA: Did you detect and adopt the correct domain persona?
   → If using generic tone: STOP. Re-read the Persona section.

5. FALLBACK: Did any URL fetches fail? Did you escalate to Apify?
   → If you stopped at fetch failure: STOP. Escalate.

6. DELEGATE: Did ALL research go through sub-agents?
   → If you performed searches directly in main agent: STOP. You violated the architecture.

7. CONFIRM: All checklist items below are checked?
   → If any unchecked: STOP. Complete before writing.

Starting to write before completing the checklist = lying to yourself, not efficiency.
```

---

## Research Execution Checklist (Self-Verify Before Writing)

Before you start writing the report, verify you have completed:

### Phase Zero Checklist (Unknown Unknowns)
- [ ] **Terminology validation**: Searched for "[User's term] meaning" and "[Term] vs [Alternative]"
- [ ] **Acronym disambiguation**: Verified the acronym doesn't have multiple meanings in context
- [ ] **Prerequisite check**: Searched for "Prerequisites for [Topic]" or "What to know before [Topic]"
- [ ] **Paradigm shift check**: Searched for "Is [Topic] outdated?" or "[Topic] alternatives [Current Year]"
- [ ] **Common misconceptions**: Searched for "Common mistakes with [Topic]" or "[Topic] pitfalls"
- [ ] **Documented Phase Zero findings**: Noted any terminology confusion, missing context, or related concepts to address

### Sub-Agent Architecture Checklist
- [ ] **Decomposed topic** into 3-5 independent research dimensions
- [ ] **Launched sub-agents in parallel** via Agent tool (`subagent_type: "general-purpose"`)
- [ ] **Each sub-agent prompt** includes search strategy, source requirements, and return format from this command
- [ ] **No searches performed directly** in the main agent context
- [ ] **Cross-referenced** sub-agent findings for contradictions before writing

### Main Research Checklist (Executed by Sub-Agents)
- [ ] Called `mcp__time__get_current_time` to establish temporal context
- [ ] Conducted **15-20 separate searches** across different angles (total across all sub-agents)

#### Brave Search MCP 5-Tool Utilization Checklist
- [ ] Used `brave_web_search` for **core research** (8-12 queries minimum)
- [ ] Used `brave_news_search` with **freshness parameter** for recent developments (2-4 queries)
- [ ] **If location-relevant:** Used `brave_local_search` for business/venue details
- [ ] **If tutorial/demo needed:** Used `brave_video_search` for visual explanations
- [ ] **If visual comparison needed:** Used `brave_image_search` for screenshots/diagrams
- [ ] Applied **correct freshness parameter** (pd/pw/pm/py) based on information type

#### Source Diversity Checklist
- [ ] Searched in **multiple languages** (EN + user's language at minimum)
- [ ] Extracted **at least 5-10 Reddit posts** with `mcp__reddit__fetch_reddit_post_content`
- [ ] Explored **competing/alternative** products or viewpoints
- [ ] Investigated **historical context** and origin stories
- [ ] Found **specific numbers/statistics** (market size, percentages, dates)
- [ ] Identified **controversies or criticisms** (not just positive coverage)
- [ ] Located **expert opinions** with proper attribution

#### Content Acquisition Checklist
- [ ] Used `mcp__fetch__fetch` as primary content retrieval
- [ ] For ANY failed fetch, escalated to `mcp__apify__apify-slash-rag-web-browser`
- [ ] No important source abandoned due to crawl restrictions

#### Extended Social Media Checklist (When Activated)
- [ ] Selected platforms based on domain-weighted priority table
- [ ] Used `mcp__apify__search-actors` to find appropriate scrapers
- [ ] Extracted insightful, representative quotes (quality over quantity)
- [ ] All quotes formatted in bilingual protocol (original + translated)

### Persona & Output Checklist
- [ ] **Domain detected**: Identified correct topic domain from `$ARGUMENTS`
- [ ] **Persona adopted**: Writing tone matches reference publication for this domain
- [ ] **One-Shot complete**: All anticipated follow-up questions answered proactively
- [ ] **Bilingual quotes**: All external quotes use original + (translated) format

### Report Structure Checklist
- [ ] **Ki section addresses Phase Zero findings** (if any terminology confusion or missing context was found)
- [ ] **Ten section includes "Blind Spot Reveal"** (concepts user didn't ask about but needs to know)
- [ ] **Ketsu includes "What You Might Have Missed"** summary (if applicable)

### Refinement Mode Checklist (Only when refining an existing report)
- [ ] **Read original report completely** before conducting any research
- [ ] **Extracted all factual claims** from the original for verification
- [ ] **Fact-checked 80%+ of original claims** against current sources
- [ ] **Conducted 10+ new searches** beyond what the original already covers
- [ ] **Identified gaps and blind spots** in the original report
- [ ] **All new findings woven seamlessly** into existing narrative (no "New Findings" sections)
- [ ] **Preserved original tone and voice** throughout edits
- [ ] **No "upon further research" language** — reads as if always written this way

**If any checkbox is unchecked, conduct additional searches before proceeding.**

---

## Research Rationalization Table

**Every excuse below is a trap. Recognize and reject.**

| Excuse | Reality |
|--------|---------|
| "5 searches should be enough" | 5 searches only scratch the surface. Real insights come after the 10th search. |
| "I don't have time, need to write fast" | Shallow research = bigger rework later. Go deep from the start. |
| "This topic is simple" | Seeming simple means lack of understanding. Complexity is always hidden. |
| "Reddit/HN is unofficial, no need to check" | Community reactions are the most honest truth. Official sources alone = half the picture. |
| "I already know this topic, less searching needed" | Organizing what you know ≠ research. Discovering what you don't know is research. |
| "Phase Zero isn't needed for this topic" | Feeling it's unnecessary is the trap. It's always needed. |
| "English-only search is sufficient" | Different perspectives exist in different languages. You'll miss local context. |
| "Need to start writing fast to meet deadline" | The more urgent, the deeper you go. Shallow writing = 100% rework. |
| "The existing report is already good, just minor tweaks" | If it were good enough, the user wouldn't ask for refinement. Dig harder. |
| "I'll add a 'New Findings' section at the end" | Appending = laziness. Weave into the existing narrative or you've failed. |
| "I don't need to fact-check the original claims" | Unverified inherited claims are YOUR liability now. Verify everything. |
| "brave_web_search is enough for everything" | **LAZY.** 5 tools exist for a reason. News needs `brave_news_search`. Locations need `brave_local_search`. |
| "This topic doesn't need local search" | If ANY physical location, store, restaurant, or venue is mentioned → local search is needed. |
| "Video search is overkill for this" | Tutorials, demos, and visual explanations often contain insights text sources miss. |
| "I'll skip image search to save time" | Visual comparisons take 2 seconds and add immense value to the report. |
| "Freshness filter isn't necessary" | Without freshness, you'll cite outdated information as current. News = `pw` minimum. |
| "The site blocked me, I'll skip that source" | NEVER skip. Escalate: fetch → Apify RAG browser. Blocked sites often have the best content. |
| "Reddit is enough for community sentiment" | Reddit is the BASELINE. Visual/social domains demand Instagram, TikTok, etc. Reddit alone = blind spot. |
| "I don't need a different persona for this topic" | Generic tone = mediocre. A fashion report in tech-auditor voice is absurd. Adapt. |
| "Translating the quote is sufficient" | Translation WITHOUT the original loses authenticity. Original voice matters. Always bilingual. |
| "The user only wrote one sentence, so a brief report is fine" | Minimal input ≠ minimal output. "Research X" demands the SAME depth as a detailed request. |
| "Social media scraping via Apify is too complex" | 4 tool calls: search-actors → fetch-details → call-actor → get-output. Not complex. Laziness. |
| "Sub-agents are overkill, I'll search directly" | Direct search = context compaction = degraded report. Sub-agents are the architecture, not an option. |
| "Dispatching sub-agents is slower than searching myself" | Sub-agents run in parallel. 5 agents × 5 searches each = 25 searches in the time of 5. Faster AND context-safe. |

---

## Red Flags — STOP and Dig Deeper

**If you catch yourself thinking these, it's a warning sign. Stop and reassess.**

- "I've researched enough at this point" → **The most dangerous moment**. Dig deeper.
- "I think I can skip Phase Zero" → Feeling it's unnecessary is the trap.
- "I don't think I need to check Reddit/HN" → That's where opposing views to official sources live.
- "Time-wise, I need to start writing fast" → The more urgent, the deeper you go. Shallow writing = rework.
- "I already know this topic well, don't need many searches" → Confirmation bias activated.
- "It's 12 searches not 15, but that's enough" → **Violating the letter means violating the spirit.**
- "I'll just use brave_web_search for all queries" → **LAZY.** Wrong tool = incomplete picture.
- "This topic doesn't involve locations" → Did you check? Any store, venue, or place mentioned?
- "News search isn't relevant here" → If the topic has ANY recent developments, `brave_news_search` is mandatory.
- "Video/image search won't add value" → You don't know until you search. 2 seconds to check.
- "The existing report just needs minor updates" → If it only needed minor updates, the user wouldn't invoke deep-research.
- "I'll just add a section at the bottom with new findings" → **Appending is not refining.** Weave seamlessly or fail.
- "The original claims don't need re-verification" → Inherited claims are your responsibility. Verify them.
- "The site is blocked, I'll use search snippets instead" → **Escalate to Apify RAG browser first.**
- "Reddit covers community sentiment well enough" → **For fashion/food/lifestyle? Instagram and TikTok are where the real conversation happens.**
- "I'll just translate the quote, no need for bilingual format" → **The original voice IS the insight. Both are required.**
- "The user's prompt is short, so a short report is fine" → **Input length ≠ output depth.**
- "This persona table is overkill, I'll use a generic tone" → **A wine review in engineering voice is absurd. ADAPT.**
- "I'll do the searches myself in the main agent, it's faster" → **Context consumed by raw search results triggers compaction. Sub-agents exist for this reason. DELEGATE.**

**ALL of these = shortcut rationalization. STOP. Search more. Use the right tool. Adopt the right persona. DELEGATE to sub-agents.**

---

## Anti-Pattern Warnings

**DO NOT:**
- Stop after 3-5 searches thinking "that's enough"
- Rely on a single source for any major claim
- Skip community sources (Reddit, social) because they seem "unofficial"
- Write the report before gathering sufficient diverse sources
- **Skip Phase Zero** — "this topic doesn't need it" is always wrong
- **Give up when a site blocks fetch** — escalate to Apify
- **Use a generic voice for all domains** — adapt your persona
- **Translate quotes without the original** — always bilingual
- **Produce shallow output for short prompts** — minimal input = maximum effort

**DO:**
- Follow every interesting thread that emerges from search results
- Cross-reference claims across multiple independent sources
- Include dissenting opinions and criticisms proportionally
- **Question the question itself** before diving into research
- **Escalate through the full fallback chain** before abandoning a source
- **Match your writing voice to the domain's top-tier publication**

---

Now conduct comprehensive research on the specified topic and deliver an exceptional deep research report.
