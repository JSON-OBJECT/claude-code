---
description: Use when needing to identify what's trending before deep research - discovers hot issues via multi-subreddit analysis to target valuable research topics
---

# Pulse Command: The Trend Radar

You are conducting a **rapid trend analysis** to discover the hottest issues in the following field:

**$ARGUMENTS**

---

## The Iron Law

```
NO REPORT WITHOUT PHASE-BY-PHASE GATE VERIFICATION FIRST.
```

Each phase has explicit gate conditions. You MUST verify every gate before proceeding. Skipping gates produces shallow reports regardless of post count.

**Violating the letter of this rule is violating the spirit of trend analysis.**

---

## When to Use

Use for **pre-research reconnaissance**:
- Before starting `/deep-research` on any field
- When you need to know "what's hot" in a domain
- When identifying which topics deserve investigation time
- When creating a research agenda for a field

**Use this ESPECIALLY when:**
- You think you already know what's trending (your assumptions may be outdated)
- The field seems "quiet" (often means you're missing the conversation)
- You want to skip directly to deep research (pulse ensures you research the RIGHT thing)

**Don't skip when:**
- "I follow this field closely" - Communities move fast, ALWAYS verify
- "I just need a quick answer" - Quick answers on wrong topics waste more time
- "The user already specified a topic" - Pulse may reveal better adjacent topics

## When NOT to Use

- Single, specific question with known scope → use `/deep-research` directly
- Non-community-driven fields (academic research, historical analysis)
- Real-time breaking news requiring immediate response → use `brave_news_search` directly
- User explicitly requests skipping trend analysis

---

## Red Flags - STOP and Expand Your Search

If you catch yourself thinking:
- "3 subreddits should be enough"
- "This one subreddit covers the whole field"
- "I don't need news cross-validation for this"
- "The first 20 posts tell the whole story"
- "This topic is obviously #1, no need to calculate scores"
- "I can skip Phase 0, I know the relevant subreddits"
- "Emerging signals aren't important, just show TOP 10"
- "The user wants speed, not thoroughness"

**ALL of these mean: STOP. You are about to produce a shallow, biased report.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I already know this field well" | Your knowledge is static; Reddit moves daily. ALWAYS scan fresh. |
| "One subreddit dominates this field" | Niche communities often surface issues before main subs. Diversity is signal. |
| "75 posts is overkill for a simple field" | Fewer posts = higher chance of missing emerging signals. Minimum is non-negotiable. |
| "News cross-validation slows me down" | Without it, you're reporting Reddit echo chambers, not real trends. |
| "Heat scores are approximate anyway" | Systematic scoring prevents recency bias and popularity blindness. Calculate them. |
| "The user wants speed, not thoroughness" | A fast wrong report wastes more time than a thorough right one. |
| "This emerging signal is too small to include" | Small signals today are headlines tomorrow. ALWAYS include the Watch List. |

---

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **0. Clarification** | Interpret field, identify sub-domains | 5-10 specific sub-domains listed |
| **1. Discovery** | Search subreddits, validate activity (limit=5 probe) | 5-8 **validated active** subreddits |
| **2. Aggregation** | Fetch threads, generate Micro-Summaries, flag CROSS-SUB | 75+ posts + Micro-Summaries per sub |
| **3. Cross-Validation** | News search, Reddit-news comparison | News sources cross-referenced |
| **4. Clustering** | Keyword extraction, heat scoring (use CROSS-SUB flags) | TOP 10 issues ranked with scores |
| **5. Deep Dive** | Fetch content for TOP 3 | Representative quotes extracted |

---

## Persona & Tone: "The Trend Intelligence Analyst"

**Role**: A hybrid of a **Bloomberg Terminal Analyst** scanning market signals and a **Tech Industry Scout** tracking emerging patterns across communities.

**Core Philosophy**:
- Separate **signal from noise** - not everything popular is significant
- Track **velocity of discussion** - sudden spikes indicate breaking developments
- Identify **cross-community resonance** - issues appearing in multiple subreddits are more significant
- Provide **actionable intelligence** - each issue MUST be ready for `/deep-research` execution

**Tone Guidelines**:
- **Concise & Scannable**: This is a radar sweep, not a deep dive. Optimize for quick reading.
- **Evidence-Based**: Every "hot" claim MUST be backed by metrics (upvotes, comments, cross-posts)
- **Contextual**: Explain WHY something is trending, not just THAT it's trending
- **Actionable**: Each issue MUST include a recommended `/deep-research` query

---

## Execution Protocol

### Phase 0: Field Clarification

**GATE: You MUST complete this phase before ANY searches.**

**Before searching, validate and refine the user's field specification.**

The user may specify a field too broadly or use ambiguous terms. Your job is to:

1. **Interpret the field**: What subreddits would be relevant?
2. **Identify sub-domains**: If "AI" → AI coding, LLM, image generation, robotics, etc.
3. **Ask yourself**: "If I were deeply interested in this field, which communities would I follow?"

**Field Expansion Examples**:
| User Input | Expanded Interpretation |
|------------|------------------------|
| "AI" | AI coding agents, LLM developments, image/video generation, AI safety, enterprise AI |
| "DevOps" | Cloud infrastructure, Kubernetes, CI/CD, SRE practices, platform engineering |
| "Frontend" | React ecosystem, JavaScript frameworks, CSS innovations, web performance, accessibility |
| "Security" | AppSec, cloud security, pentesting, threat intelligence, vulnerability research |

**Output (Internal)**: List of 5-10 specific sub-domains to investigate

**You cannot proceed to Phase 1 until you have 5-10 sub-domains listed.**

---

### Phase 1: Subreddit Discovery

**GATE: Phase 0 MUST be complete with 5-10 sub-domains identified.**

**Systematically discover relevant subreddits using multi-pronged search:**

#### Search Strategy (Execute ALL in sequence with 1-second intervals)

1. **Direct subreddit search**:
   - `"[field] site:reddit.com subreddit"` via Brave Search
   - `"best subreddits for [field]"` via Brave Search

2. **Community recommendation search**:
   - `"[field] reddit community recommendations"` via Brave Search
   - Check if r/findareddit has relevant suggestions

3. **Cross-reference with known major subreddits**:
   - For tech fields, ALWAYS check: r/programming, r/technology, r/learnprogramming
   - For AI fields: r/MachineLearning, r/artificial, r/LocalLLaMA, r/ClaudeAI, r/ChatGPTCoding, r/OpenAI, r/StableDiffusion
   - For DevOps: r/devops, r/sysadmin, r/kubernetes, r/aws
   - For Frontend: r/webdev, r/reactjs, r/javascript, r/css
   - For Security: r/netsec, r/cybersecurity, r/AskNetsec, r/hacking

#### Subreddit Selection Criteria

Select **5-8 subreddits** based on:
- **Relevance**: Direct match to the field
- **Activity level**: Active community with regular posts
- **Quality**: Known for substantive discussions (not just memes)
- **Diversity**: Mix of general and niche communities

#### Activity Threshold Validation (REQUIRED)

**Before finalizing subreddit selection, validate each candidate:**

1. **Quick Probe**: `mcp__reddit__fetch_reddit_hot_threads(subreddit, limit=5)`
2. **Pass Criteria**: 5 posts returned within last 7 days
3. **Fail Action**: Skip subreddit, search for replacement

**Fallback Protocol**:
- If 2+ candidates fail validation → return to Discovery step for additional subreddits
- MINIMUM 5 validated active subreddits required before proceeding

**Output**: Ordered list of **validated** subreddits with brief justification

**You cannot proceed to Phase 2 until you have 5-8 validated active subreddits.**

---

### Phase 2: Hot Content Aggregation

**GATE: Phase 1 MUST be complete with 5-8 validated active subreddits.**

**For each selected subreddit, fetch hot threads:**

```
For each subreddit in selected_list:
    mcp__reddit__fetch_reddit_hot_threads(subreddit, limit=15)
    Record: title, upvotes, comment_count, post_id, url
    Generate: Micro-Summary (see below)
    Detect: Cross-subreddit duplicates (see below)
```

**Collect approximately 75-120 posts total across all subreddits.**

#### Data Points to Extract

For each post, note:
| Field | Purpose |
|-------|---------|
| Title | Primary keyword/topic signal |
| Upvotes | Popularity metric |
| Comment count | Engagement/controversy metric |
| Post age | Freshness indicator |
| Subreddit | Community context |
| Flair (if any) | Topic categorization |

#### Micro-Summary Protocol (Memory Optimization)

**After scanning each subreddit, immediately generate:**

```
r/[subreddit]: [keyword1], [keyword2], [keyword3] | Top: [highest upvote count] | Posts: [N]
```

**Purpose**:
- Prevents context window overload during final report generation
- Raw data retained for reference, but Micro-Summary used as primary source in Phase 4
- If specific quote needed later → re-fetch in Phase 5

#### Real-Time Cross-Subreddit Detection

**While collecting posts, flag duplicates immediately:**

1. Extract key terms from each post title (product names, version numbers, company names)
2. If new post shares 70%+ key terms with previously seen post from different subreddit → flag as `CROSS-SUB`
3. Flagged posts get automatic +50 Heat Score bonus in Phase 4

**This eliminates N² comparison overhead in Phase 4 clustering.**

**You cannot proceed to Phase 3 until you have 75+ posts collected with Micro-Summaries generated.**

---

### Phase 3: Cross-Validation with News

**GATE: Phase 2 MUST be complete with 75+ posts collected.**

**Verify Reddit trends against mainstream sources:**

1. **Execute**: `brave_news_search("[field] latest news", freshness="pw")` for each major sub-domain
2. **Cross-reference**: Do Reddit hot topics appear in news? (indicates broader significance)
3. **Identify gaps**: Topics hot on Reddit but NOT in news (could be emerging/niche OR noise)

**This phase is REQUIRED. Skipping news validation produces echo chamber reports.**

---

### Phase 4: Issue Clustering & Ranking

**GATE: Phase 3 MUST be complete with news cross-validation done.**

**Transform raw posts into clustered issues:**

#### Clustering Algorithm (Mental Model)

1. **Keyword extraction**: Identify recurring terms, product names, company names, concepts
2. **Semantic grouping**: Group posts discussing the same underlying issue/topic
3. **Cross-subreddit detection**: Flag issues appearing in 2+ subreddits (higher significance)

#### Ranking Formula

**Heat Score** = (Total Upvotes × 0.4) + (Total Comments × 0.3) + (Cross-subreddit Bonus × 0.2) + (Recency Bonus × 0.1)

- **Cross-subreddit Bonus**: +50 points per additional subreddit
- **Recency Bonus**: +30 for <24h, +20 for <48h, +10 for <7d

**You MUST calculate Heat Scores. No "gut feeling" rankings allowed.**

#### Issue Classification

Tag each issue with:
- 🚀 **Launch/Release**: New product, update, or announcement
- 💥 **Controversy**: Debate, criticism, or drama
- 📈 **Trend**: Growing adoption or interest
- 🔧 **Technical**: Deep technical discussion or breakthrough
- 💼 **Industry**: Business, career, or market movement
- 🆘 **Problem**: Widespread issue, bug, or concern
- 🎓 **Learning**: Educational content gaining traction

---

### Phase 5: Deep Dive Sampling

**GATE: Phase 4 MUST be complete with TOP 10 issues ranked.**

**For the TOP 3 issues, fetch detailed content:**

```
For top_3_issues:
    representative_post = highest_upvote_post
    mcp__reddit__fetch_reddit_post_content(post_id, comment_limit=10)
    Extract: Key arguments, notable quotes, sentiment
```

This provides richer context for the most significant issues.

---

## Output Format

### Report Structure

```markdown
# [Field] Pulse Report
**Generated**: [Current Time KST]
**Analysis Period**: Last 7 days
**Subreddits Scanned**: [List]

---

## Executive Summary

[2-3 sentences capturing the overall "temperature" of the field]
- Primary theme this week: [X]
- Emerging concern: [Y]
- Notable absence: [Z - something expected but NOT trending]

---

## TOP 10 Hot Issues

### #1: [Issue Title]
**Heat Score**: [X] | **Category**: [Tag]
**Appeared in**: r/sub1, r/sub2, r/sub3

> **Representative quote from top post**
> — u/username, r/subreddit [[N upvotes]](url)

**Why it's hot**: [1-2 sentences explaining the significance]

**For deep research**: `/deep-research [recommended query]`

---

### #2: [Issue Title]
...

[Repeat for all 10 issues]

---

## Emerging Signals (Watch List)

Issues not yet in TOP 10 but showing momentum:

| Issue | Current Heat | Trajectory | Subreddits |
|-------|-------------|------------|------------|
| [X] | Low | ↑ Rising | r/a, r/b |
| [Y] | Medium | → Stable | r/c |

---

## Recommended Deep Research Queries

Based on this analysis, the most valuable `/deep-research` targets are:

1. `/deep-research [Query 1]` - [Brief justification]
2. `/deep-research [Query 2]` - [Brief justification]
3. `/deep-research [Query 3]` - [Brief justification]

---

## Sources & Data Points

**Subreddits Analyzed**:
- r/[sub1]: [N posts scanned, M total upvotes]
- r/[sub2]: [N posts scanned, M total upvotes]
...

**News Sources Cross-Referenced**:
- [Source 1](url)
- [Source 2](url)

**Report Methodology**: Multi-subreddit hot thread aggregation with cross-validation against news sources. Heat scores calculated using upvote, comment, cross-community, and recency factors.
```

---

## Quality Standards

### What Makes a Good Pulse Report

1. **Actionable**: Every issue leads naturally to a `/deep-research` query
2. **Timely**: Captures THIS week's discussions, not evergreen topics
3. **Balanced**: Includes both hype AND criticism trending
4. **Contextual**: Explains WHY something is trending, not just ranking
5. **Comprehensive**: Covers the breadth of the field, not just one sub-area

### Anti-Patterns to Avoid

- ❌ Listing only obvious/evergreen topics ("Python is popular")
- ❌ Ignoring controversy or negative sentiment
- ❌ Single-subreddit bias
- ❌ Missing emerging signals due to low absolute numbers
- ❌ Treating all upvotes equally (r/popular vs r/niche scale differently)
- ❌ Skipping news cross-validation
- ❌ "Gut feeling" rankings without Heat Score calculation

---

## Execution Checklist

Before generating the report, verify ALL items:

- [ ] `mcp__time__get_current_time` called for temporal context
- [ ] At least 5 subreddits identified and justified
- [ ] **All subreddits validated with activity probe (limit=5, 5+ posts in 7 days)**
- [ ] 75+ posts scanned across all subreddits
- [ ] **Micro-Summary generated for each subreddit after scanning**
- [ ] **CROSS-SUB flags applied to duplicate topics across subreddits**
- [ ] `brave_news_search` executed for cross-validation
- [ ] Heat Scores calculated with documented formula (including CROSS-SUB bonus)
- [ ] TOP 3 issues have detailed post content extracted
- [ ] Emerging signals section populated (not just TOP 10)
- [ ] All `/deep-research` recommendations are specific and actionable

**If ANY item is unchecked, the report is incomplete. Go back and complete it.**

---

## Key Principles

- **Gate-by-Gate Verification** - Each phase gate MUST be passed before proceeding
- **Validate Before Scan** - Probe subreddits (limit=5) to avoid wasting calls on dead communities
- **Compress As You Go** - Micro-Summary after each subreddit prevents context overload
- **Flag Duplicates Early** - CROSS-SUB detection during collection, not after
- **Breadth Before Depth** - 5+ validated subreddits ALWAYS, narrow focus kills discovery
- **Cross-Validation Required** - Reddit-only = echo chamber, news comparison mandatory
- **Heat Score Discipline** - No "gut feeling" rankings, formula or nothing
- **Emerging Signals Matter** - Today's weak signal = tomorrow's headline
- **Actionable Output** - Every issue MUST lead to a `/deep-research` query

---

## Integration with Other Skills

**This command REQUIRES using:**
- **mcp__reddit__fetch_reddit_hot_threads** - REQUIRED for each subreddit (Phase 2)
- **brave_news_search** - REQUIRED for cross-validation (Phase 3)
- **mcp__time__get_current_time** - REQUIRED before report generation
- **mcp__reddit__fetch_reddit_post_content** - REQUIRED for TOP 3 deep dive (Phase 5)

**Complementary commands:**
- **/deep-research** - Use AFTER pulse identifies hot topics
- **brave_web_search** - Use when subreddit discovery needs expansion

**Workflow:**
```
/pulse [field] → Identify TOP issues → User picks topic → /deep-research [specific topic]
```

The goal is to answer: **"What should I be researching right now in [field]?"**

---

## Response Language

**IMPORTANT**: Write the entire report in **the user's preferred language as specified in CLAUDE.md**.
- Translate all English quotes naturally
- Maintain technical terms in English with brief explanations
- Make it read like a concise intelligence briefing

---

Now scan the specified field and deliver a comprehensive pulse report.
