---
description: Use when transforming meeting transcripts into actionable documentation - produces narrative-driven meeting notes with counterparty intelligence, immediate inline terminology, multi-source verification, and flowing prose that reads like a tech magazine briefing
---

# Meeting Notes Generator

You are transforming raw meeting inputs into **narrative-driven, actionable meeting notes** following modern tech company practices. Your output reads like a **tech magazine briefing**, not a dry bullet list. Every term is **verified and explained inline**, every counterparty is **researched for context**, and every section **flows with clear cause-and-effect reasoning**.

**Critical Insight**: Meeting notes are not stenography. They are **curated narratives** that help readers understand not just *what* was discussed, but *why* it matters, *who* the participants are, and *how* decisions connect to broader context. A bullet list transmits information; a narrative transmits understanding.

---

## The Iron Law

```
NO OUTPUT WITHOUT COUNTERPARTY RESEARCH, VERIFIED TERMS, NARRATIVE FLOW, IMMEDIATE INLINE EXPLANATIONS, AND MAXIMUM DETAIL PRESERVATION.
```

Every technical term MUST be verified with 2+ sources. Every term MUST have an immediate inline explanation on first occurrence. Every counterparty (external company/team) MUST be researched for context. Every discussion section MUST flow as connected prose, not isolated bullets. **Every detail from the source material MUST be preserved—nothing is too small to include.**

A correction without verification is a guess dressed as fact. A counterparty mentioned without research is a missed context opportunity. A bullet list masquerading as narrative is a failure of communication. Phonetic transcription left as-is ("jenkinsun" instead of "Jenkins") is unsearchable and unprofessional. **A summarized or abbreviated output is a betrayal of the source material.**

**The Three Absolutes (NON-NEGOTIABLE DEFAULTS):**
1. **ZERO DETAIL LOSS** — Every fact, quote, nuance, and context from the source MUST appear in the output. If it was mentioned, it matters.
2. **MAXIMUM TOKEN UTILIZATION** — Use as many tokens as needed to capture full richness. Brevity is NOT a virtue here. Density with depth is.
3. **HIGH-DENSITY NARRATIVE** — Every sentence must carry weight. Tight, structured storytelling—not padding, but substance.

**Violating the letter of this rule is violating the spirit of accessible, contextual, actionable documentation.**

---

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Temporal** | Check current time, calculate elapsed time | Temporal context established |
| **2. Counterparty** | Research external company/team, meeting format | 3+ searches, context integrated |
| **3. Context** | Extract when/where/why/who/what | Can answer all 5 questions |
| **4. Verify** | Flag terms, cluster context, multi-source search | All terms verified with 2+ sources |
| **5. Signal** | Extract decisions/actions/parked, map terms | All items have owner + deadline |
| **6. Compose** | Write narrative prose with inline explanations | flowing narrative, 1500-2500+ words, zero detail loss |

| Section | Required Elements |
|---------|------------------|
| **Date/Time** | YYYY-MM-DD (Day) HH:MM–HH:MM (or `[Time TBD]`) |
| **Location** | Physical / Video platform / Hybrid (or `[Location TBD]`) |
| **Counterparty Context** | Integrate into box or background section |
| **Background** | Why meeting was needed + counterparty context (2-4 sentences, narrative flow) |
| **Key Learnings/Decisions** | Flowing narrative with inline explanations (> 📘) |
| **Action Items** | Task + @owner + due date |
| **Parked/Rejected** | Topic + rejection reason |
| **Glossary** | Term + Original + Definition + Context |

---

## When to Use

Use for:
- Transforming transcripts/recordings into meeting notes
- Cleaning up NotebookLM summaries
- Converting handwritten notes into official records
- **Benchmarking sessions** with external companies
- **Vendor/partner meetings** requiring context

**Use this ESPECIALLY when:**
- **Source is speech-to-text transcript** (guaranteed phonetic errors)
- **Meeting involved external parties** (counterparty research adds critical context)
- **Benchmarking or learning session** (needs narrative to convey insights)
- Meeting involved **multiple departments** (jargon varies)
- **Technical decisions** were made (acronyms need context)
- **New team members will read this** (always assume yes)
- **The meeting counterparty is an industry leader** (their context enriches understanding)

**Don't use for:**
- 1:1 meetings (separate format)
- Daily standups (3-line summary)
- Brainstorming sessions (idea lists)

**Don't skip when:**
- "It was a simple meeting" → Simple meetings with undocumented decisions become disputes.
- "The transcript looks clean" → STT errors hide in plain sight. "jenkinsun" looks reasonable until you realize it's "Jenkins."
- "Everyone knows the terms" → Memory diverges within 72 hours. New hires join next month.
- "I don't have time for verification" → Unverified errors become official record. 2 minutes prevents months of confusion.
- "The counterparty is famous, no research needed" → Famous ≠ understood. Their team structure, recent announcements, tech stack add irreplaceable context.
- "Bullet points are easier to scan" → Scan ≠ understand. Narrative conveys causality; bullets convey fragments.

---

## Input Format

User will provide one or more of:
- **Background/Context**: Why the meeting was needed
- **Transcript**: Raw text from audio (HIGH ERROR RISK)
- **NotebookLM Summary**: AI-generated summary (MEDIUM ERROR RISK)
- **Previous Meeting Notes**: Prior context
- **Handwritten Notes**: Scribbles (MEDIUM ERROR RISK)

$ARGUMENTS

---

## The 6 Phases

You MUST complete each phase before proceeding to the next.
**Create TodoWrite todo for each Phase Gate before proceeding.**

### Phase 1: Temporal Context (EXECUTE IMMEDIATELY)

**GATE: Create TodoWrite todo: "Phase 1: Establish temporal context"**

```
mcp__time__get_current_time (timezone: Asia/Seoul)
```

1. **Determine time elapsed**: Compare meeting date with current date
2. **Adjust trust level**: Use the table below

| Time Elapsed | Memory State | Strategy |
|--------------|--------------|----------|
| Same day~Next day | Fresh | Memory can supplement |
| 2-7 days | Distortion begins | Rely on transcript |
| 1 week+ | Severe distortion | Trust only source |
| 2 weeks+ | Almost lost | Mark unclear as `[Verification needed]` |

3. **Convert relative times**: "yesterday" → Meeting date - 1 day, etc.

**Mark TodoWrite todo complete when temporal context established.**

---

### Phase 2: Counterparty Intelligence (MANDATORY)

**GATE: Create TodoWrite todo: "Phase 2: Research counterparty (min 3 searches)"**

You cannot proceed until:
- [ ] Identified all external companies/teams mentioned
- [ ] Conducted minimum 3 searches per major counterparty
- [ ] Prepared counterparty context summary (1-3 sentences)
- [ ] Researched meeting format if unfamiliar (e.g., "AWS C2C", "benchmarking meeting")

#### Step 1: Counterparty Identification

Extract from meeting context:
| Entity Type | Research Priority |
|-------------|-------------------|
| **External Company** | HIGH - Always research |
| **Specific Team/Dept** | HIGH - If mentioned by name |
| **Key Individuals** | MEDIUM - If publicly active |
| **Meeting Format** | MEDIUM - If unfamiliar term |

#### Step 2: Research Search Patterns

**Search Pattern Templates:**
| Category | Pattern | Purpose |
|----------|---------|---------|
| Company size | `"[company] size employees"` | Scale context |
| Tech culture | `"[company] tech blog OR engineering"` | Technical approach |
| Team presence | `"[company] [team] presentation"` | Public expertise |
| Recent news | `"[company] news [current year]"` | Current developments |
| Team structure | `"[company] [team] organization"` | Org context |
| Tech stack | `"[company] [team] tech stack"` | Technology context |
| Meeting format | `"[format] meaning"` | Format definition |

#### Step 3: Counterparty Context Output

**Background Section Structure (Preferred):**
```
Sentence 1: [Company] identity — [scale], [industry position]
Sentence 2: [Team] structure — [N] members, [organizational characteristics]
Sentence 3: Why this matters to us — [gap/learning opportunity]
Sentence 4: Meeting context — [how arranged], [format explanation if special]
```

**Alternative - Separate Box (when extensive context):**
```markdown
> 📊 **Counterparty Context: [Company]**
> - [Scale metric], [industry position]
> - [Team]: [N] members, [structure]
> - Recent presence: [conference/blog] ([source](URL))
```

**RETURN CONDITION:** Cannot find counterparty info → Note "[Context TBD - limited public info]" and proceed.

**Mark TodoWrite todo complete when counterparty research done.**

---

### Phase 3: Context Extraction

**GATE: Create TodoWrite todo: "Phase 3: Answer 5 context questions"**

You cannot proceed until you can answer:

1. **When?** — Exact date AND time (start–end, timezone)
2. **Where?** — Physical location, video platform, or hybrid
3. **Why?** — Reason meeting was called (1 sentence)
4. **Who?** — Decision-maker among attendees + counterparty roles
5. **What?** — What had to be learned/decided

**Time/Location Extraction Patterns:**

| Source Type | Time Extraction | Location Extraction |
|-------------|-----------------|---------------------|
| Calendar invite | Start/End time directly | Room name, video link |
| Transcript header | Timestamp at beginning | Platform name |
| Spoken references | "It's 2pm, let's begin" | "Everyone can hear me?" |
| Background context | User-provided | User-provided venue |

**CRITICAL**: DO NOT ignore user-provided context. If user mentions "we met at Seoul office" or "3pm call", it MUST appear in output.

**RETURN CONDITION:** If time/location unknown AND user didn't provide it → mark `[TBD]` and ask user.

**Mark TodoWrite todo complete when all 5 questions answered.**

---

### Phase 4: Term Discovery & Verification (CRITICAL)

**GATE: Create TodoWrite todo: "Phase 4: Verify all terms with 2+ sources"**

You cannot proceed until:
- [ ] Identified all industry terms, acronyms, jargon (minimum 5)
- [ ] Detected all transcription errors (phonetic, mishearings)
- [ ] Each term verified with 2+ sources
- [ ] Prepared immediate inline explanations (1-2 sentences each)
- [ ] Recorded original → corrected mappings

#### Step 1: Term Flagging

| Flag Type | Examples | Signal |
|-----------|----------|--------|
| **Phonetic Transcription** | C-I-C-D, jenkinsun | Syllables that might be technical terms |
| **Acronyms** | CI/CD, SLA, MVP, IDP | All-caps or spelled phonetically |
| **STT Mishearing** | "jenkinsun", "Q-A" | Unusual spacing, near-homophones |
| **Industry Jargon** | sprint, backlog, guardrail | Domain-specific terms |

#### Step 2: Context Clustering

Group suspicious terms by surrounding context BEFORE searching:

| Context Cluster | Keywords | Likely Domain |
|----------------|----------|---------------|
| Deployment | build, deploy, pipeline | CI/CD |
| Platform | guardrail, self-service, IDP | Platform Engineering |
| Observability | metrics, logs, tracing | Monitoring |

#### Step 3: Multi-Source Verification (MANDATORY)

**Search Pattern Templates:**

| Pattern | Example |
|---------|---------|
| `"[phonetic] meaning"` | "jenkinsun meaning" |
| `"[phonetic] [context]"` | "guardrail platform engineering" |
| `"[Term] explained simply"` | "IDP Internal Developer Platform explained" |

**Minimum Requirement:** 2 independent sources confirming each correction.

#### Step 4: Verification Log

| Original | Corrected | Sources | Confidence |
|----------|-----------|---------|------------|
| "jenkinsun" | Jenkins | jenkins.io, Wikipedia | High |
| "guardrail" | Guardrail | Gartner, ThoughtWorks | High |

**RETURN CONDITION:** Cannot verify → mark `[Verification TBD]` and flag to user.

**Mark TodoWrite todo complete when all terms verified.**

---

### Phase 5: Signal Extraction

**GATE: Create TodoWrite todo: "Phase 5: Extract all decisions and actions"**

You cannot proceed until:
- [ ] All **decisions/learnings** identified (with context)
- [ ] All **action items** identified (owner + deadline)
- [ ] All **rejected/parked items** identified (with reasons)
- [ ] All **terms** mapped to first occurrence
- [ ] **Narrative flow outline** prepared (how sections connect)

**Actions:**
- Extract "we agreed to", "let's do", "please handle"
- Move "not now", "later", "on hold" → Parked section
- When owner/deadline unclear → mark `[TBD]` and flag

**Narrative Flow Planning:**
| Section | Connects To | Transition Phrase |
|---------|-------------|-------------------|
| Background | Counterparty context | "Against this backdrop..." |
| Learning 1 | Learning 2 | "This philosophical shift immediately led to..." |
| Learning 2 | Learning 3 | "The platform's success raised the next challenge..." |

**RETURN CONDITION:** Context gaps → return to Phase 3. New terms discovered → return to Phase 4.

**Mark TodoWrite todo complete when all signals extracted.**

---

### Phase 6: Narrative Composition (ENHANCED)

**GATE: Create TodoWrite todo: "Phase 6: Compose narrative with inline explanations"**

Final output MUST:
- **PRESERVE ALL DETAILS** — Nothing from source material is too minor to include
- **USE MAXIMUM TOKENS** — Target **1500-2500+ words** (or more if source demands). Brevity is NOT a goal.
- Have **high-density narrative prose** in discussion sections (NOT bullet lists)
- Have **immediate inline explanations** (> 📘) on first occurrence
- Include **Glossary table** for quick lookup
- Have **zero uncorrected phonetic transcriptions**
- Have **counterparty context** in background section

**THE DEFAULT IS COMPREHENSIVE, NOT CONCISE.**

---

## Narrative Writing Rules (CRITICAL — NON-NEGOTIABLE)

### Storytelling Tone (MANDATORY)

**You are telling a story, not filing a bureaucratic report.**

The difference between dry documentation and memorable notes is narrative engagement. Write as if you're explaining the meeting to a colleague over coffee—clear, natural, with a sense of unfolding events.

| Aspect | Report Tone (AVOID) | Storytelling Tone (USE) |
|--------|---------------------|-------------------------|
| **Opening** | "The meeting covered three topics." | "The conversation opened with a challenge that had been brewing for months." |
| **Transitions** | "Next, Topic B was discussed." | "This realization naturally led to the next question..." |
| **Conclusions** | "The team decided X." | "After weighing the trade-offs, the path forward became clear." |
| **Pacing** | Flat, equal weight to all points | Build tension, then resolution |

**Key techniques:**
- **Temporal flow**: Use "At first... then... eventually..." to create narrative arc
- **Causality emphasis**: Always explain WHY before WHAT
- **Stakes clarity**: Make readers understand what was at risk
- **Resolution satisfaction**: End topics with clear outcomes, not hanging threads

### Metaphor & Analogy (MANDATORY — 1-2 Per Document)

**Every meeting notes MUST include 1-2 metaphors or analogies to crystallize abstract concepts.**

Abstract ideas become concrete through comparison. A well-chosen metaphor compresses paragraphs of explanation into a single memorable image.

| Category | Example |
|----------|---------|
| **Process metaphor** | "The legacy deployment process acted like a highway toll booth—everything stopped while waiting for approval." |
| **Transition metaphor** | "From gatekeeper to guardrail—no longer blocking the road, but preventing cars from going off the cliff." |
| **Scale metaphor** | "Like turning an ocean liner, the organizational shift was slow but unmistakably directional." |
| **Complexity metaphor** | "The microservices architecture had become a plate of spaghetti—everything touched everything else." |

**Placement rules:**
- Use at the **beginning** of a topic to frame the problem
- OR at the **end** to crystallize the insight
- Never force—if no natural metaphor fits, one is enough

**Selection criteria:**
- Metaphor MUST illuminate, not obscure
- Prefer familiar domains (vehicles, buildings, nature) over niche references
- The metaphor should be quotable—something readers might repeat

### The Flowing Prose Mandate

**Every discussion section MUST be written as connected prose, not bullets.**

| Principle | WRONG (Bullets) | CORRECT (Narrative) |
|-----------|-----------------|---------------------|
| **Flow** | "- Philosophy A adopted / - Bottleneck existed" | "[Problem description]. [Why it matters]. [Solution emerged as answer]." |
| **Causality** | "- Tool X limits / - Tool Y developed" | "As [situation changed], [existing approach] reached limits. [Pain points], [decision to change]." |
| **Context** | "- N% complete" | "Instead of [forcing change], [gradual approach]. As a result, [voluntary adoption]. Currently, [measurable outcome]." |

### Narrative Structure Pattern

**Each topic MUST follow this structure:**

```
[Background/Problem: 2-3 sentences] → [Turning Point/Solution: 2-3 sentences] → [Result/Significance: 1-2 sentences]
```

**Structure Template:**
```markdown
### [Insight-Driven Title] — [Subtitle capturing the transformation]

[Problem context - what was the challenge?]
[Why it mattered - scale, impact, pain]

[Solution/turning point - what changed?]
[How it works - key mechanism]
> 📘 **[Term]** — [1-2 sentence definition with source context]

[Transition to next topic - how this led to the next development]
```

### Minimum Sentence Requirements

| Section | Minimum Sentences | Guideline |
|---------|------------------|-----------|
| Background | 3-5 sentences | Counterparty + meeting purpose + why now |
| Each Topic | 4-8 sentences | Problem → Solution → Result flow |
| Transitions | 1-2 sentences | Connect one topic to the next |

### Connecting Phrases (USE LIBERALLY)

| Category | Phrases |
|----------|---------|
| **Causality** | "As a result", "Consequently", "This led to", "Due to this" |
| **Transition** | "Against this backdrop", "This shift immediately led to", "Success raised the next challenge" |
| **Contrast** | "On the other hand", "However", "Meanwhile" |
| **Emphasis** | "The key point is", "Most importantly", "Particularly noteworthy is" |

### Section Titles (Narrative-Driven)

**WRONG (Generic):**
- "## Discussion Summary"
- "### 1. SRE Organization Structure"

**CORRECT (Insight-Driven):**
- "## Key Learnings"
- "### From Gatekeeper to Guardrail — The SRE Philosophy Shift"
- "### Choice Over Mandate — The Success of Control's Adoption Strategy"

---

## Output Structure (MANDATORY)

```markdown
# [Meeting Title] — YYYY-MM-DD

## Overview

| Field | Details |
|-------|---------|
| **Date/Time** | YYYY-MM-DD (Day) HH:MM–HH:MM |
| **Location** | [Physical / Video platform / Hybrid] |
| **Our Team** | @name, @name (N people) |
| **Counterparty** | [Company] — name(role), name(role) (N people) |
| **Author** | @name |

---

## Background

[3-5 sentences integrating counterparty context + meeting purpose]

[If C2C/special format, explain it here with inline term explanation]

---

## Key Learnings

### [Narrative-Driven Title 1]

[4-8 sentences following Problem → Solution → Result pattern]

> 📘 **[Term]** (Original: "[original]") — [1-2 sentence explanation]

[Transition sentence to next topic]

### [Narrative-Driven Title 2]

[Continue narrative flow...]

---

## Implications

| Insight | Recommendation |
|---------|----------------|
| [Insight 1] | [Actionable recommendation] |

---

## Action Items

- [ ] [Verb first] — @owner, Due: MM/DD

---

## Parked Items

- **[Topic]**: [Rejection reason] — Revisit: [condition]

---

## Glossary

| Term | Original | Definition | Context |
|------|----------|------------|---------|
| **[Term]** | "[original]" | [Definition] | [Context in this meeting] |

---

## References

- [Source title](URL) — [Brief description]

---

## Next Steps

- [Next action or follow-up meeting]
```

---

## Immediate Inline Explanation Format (CRITICAL)

**Format:**
```markdown
[Narrative sentence mentioning **Term**.]
> 📘 **[Term]** (Original: "[original if STT]") — [1-2 sentence explanation]
```

**Placement Rule:**
- Explain immediately after the term's first appearance
- Placing only at section end or Glossary = WRONG

**WRONG patterns:**
```markdown
<!-- Term without immediate explanation -->
The team uses cdk8s for deployment.
[... 5 paragraphs later ...]
> 📘 **cdk8s** — explanation here

<!-- Bullet list instead of narrative -->
- cdk8s: YAML auto-generation
- IDP: developer platform
```

---

## Red Flags — STOP and Verify

If you catch yourself thinking:

**🚨 DETAIL PRESERVATION (MOST CRITICAL):**
- "This detail is minor, I can skip it" ← WRONG. If it was mentioned, it matters. Include it.
- "Let me summarize this part" ← WRONG. Summarizing = detail loss. Expand, don't compress.
- "This is getting too long" ← WRONG. Length is not a problem. Detail loss is.
- "I'll keep it concise" ← WRONG. Concise = detail loss. Comprehensive is the default.
- "The user probably doesn't need all this" ← WRONG. The user EXPLICITLY wants all details preserved.
- "I can combine these points" ← WRONG. Combining often loses nuance. Keep them separate.
- "This quote is too long to include" ← WRONG. Long quotes preserve voice and context. Include them.
- "I'll paraphrase instead of quoting" ← WRONG. Original words carry weight. Quote when possible.

**Time & Location:**
- "The date is enough, time doesn't matter"
- "Location wasn't mentioned explicitly"
- "The user didn't provide it" ← CHECK AGAIN

**Counterparty Research:**
- "The company is famous, no need to research" ← Famous ≠ understood. Research anyway.
- "I know this company already" ← Memory is not a source. Search.
- "There's no public info on their team" ← Try harder: tech blogs, conference talks, LinkedIn.
- "This is just an internal meeting" ← Counterparty = other teams too if cross-functional.

**Terminology:**
- "This term is too common to explain"
- "I can explain this from memory"
- "The glossary at the end is enough"

**Narrative:**
- "Bullet points are easier to read" ← Easier to scan, harder to understand.
- "This is just information listing" ← Information without narrative = no causality.
- "The user wanted it concise" ← **WRONG. DEFAULT IS COMPREHENSIVE.** Concise must be explicitly requested.
- "Adding transitions is fluff" ← Transitions are the connective tissue of understanding.
- "Formal report tone is more professional" ← Bureaucratic ≠ professional. Storytelling engages.
- "Metaphors are unnecessary decoration" ← Metaphors compress complexity into memorable insight.

**Verification:**
- "The transcript is probably accurate" ← STT error rate: 5-15%
- "I know the correct spelling without searching" ← Memory is not a source
- "One source is enough" ← Single source = potential echo

**ALL of these mean: STOP. You are about to produce unresearched, unverified, fragmented, or INCOMPLETE documentation.**

---

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| **"It's getting too long"** | **Length is NOT a problem. Detail loss IS.** The default is comprehensive. If the source has 50 points, include 50 points. |
| **"Let me keep it concise"** | **Concise = detail loss.** Brevity must be EXPLICITLY requested. Default is maximum detail preservation. |
| **"This detail seems minor"** | **If it was mentioned, it matters.** You don't know what the reader will need. Include everything. |
| **"I'll summarize this section"** | **Summarizing destroys nuance.** Expand and explain instead of compressing. |
| **"The user can read the original"** | **The user wants a COMPLETE record.** They shouldn't need to cross-reference the source. |
| **"This quote is too long"** | **Long quotes preserve voice and context.** Include them. Original words carry irreplaceable weight. |
| "The counterparty is famous, no research needed" | Famous ≠ understood. Their team size, tech stack, recent announcements add irreplaceable context. 2 minutes of research makes background 10x richer. |
| "Bullet points are easier to scan" | Scanning ≠ understanding. Narrative conveys causality, context, and connection. Bullets convey fragments. |
| "Adding narrative is fluff" | Narrative is structure. "Why → What → How" is not fluff—it's the difference between data and insight. |
| "Formal report tone is more professional" | Bureaucratic tone creates distance. Storytelling tone creates engagement. Professional = clear and memorable. |
| "Metaphors don't belong in meeting notes" | A good metaphor compresses a paragraph into one memorable image. It aids recall and communication. |
| "Time wasn't mentioned" | Check calendar, transcript header, spoken refs. If missing, mark `[TBD]` and ask. |
| "Location doesn't matter for remote" | "Zoom" IS a location. "Company HQ 11th floor" adds context. Document it. |
| "Owner wasn't decided" | Mark `[TBD - needs assignment]` and warn. Action without owner = never done. |
| "This term is standard" | Standard to your team. Foreign to legal, HR, new hires. |
| "Searching each term takes too long" | 30 sec × 10 terms = 5 min. Saves 50+ person-minutes of confusion. |
| "I know what the term means" | Memory may be wrong. Search every time. |
| "The transcript is source of truth" | Transcript is raw input. Your job is verified, narrative output. |
| "STT was probably right" | STT has 5-15% error rate on tech terms. ASSUME errors. |
| "Inline explanations break flow" | They ENABLE flow for newcomers. Accessibility > aesthetics. |

---

## Key Principles

**THE THREE ABSOLUTES (ALWAYS ON BY DEFAULT):**
- **ZERO DETAIL LOSS** — Every fact, quote, nuance from source MUST appear. Nothing is too minor.
- **MAXIMUM TOKEN UTILIZATION** — Use 1500-2500+ words. Brevity is NOT a virtue. Depth is.
- **HIGH-DENSITY NARRATIVE** — Every sentence carries weight. Tight storytelling, not padding.

**Supporting Principles:**
- **Counterparty context = complete background** — Meeting notes without counterparty research are half-blind
- **Narrative flow = understanding** — Connected sentences convey causality; bullets convey fragments
- **Storytelling tone = engagement** — Write like explaining to a colleague, not filing a bureaucratic report
- **Metaphor = compression** — One good analogy crystallizes paragraphs of abstraction into memorable insight
- **Meeting without time/location = incomplete record** — Always include when and where
- **User-provided context = MUST use** — If user mentions it, it MUST appear in output
- **Action without owner = doesn't exist** — Every action needs @mention
- **Term without IMMEDIATE explanation = friction** — First occurrence, not at end
- **Correction without 2+ sources = guess** — Verify with independent sources
- **Phonetic transcription preserved = unsearchable** — Convert to proper English
- **Memory is not a source** — Search and verify, even for "obvious" terms
- **Comprehensive by default** — Brevity must be EXPLICITLY requested. Default = maximum detail.
- **48-hour rule** — Memory distorts after 48 hours. Distribute same day.

---

## Final Verification Checklist

Before output, verify ALL:

**Counterparty Research:**
- [ ] External company researched (3+ searches)?
- [ ] Counterparty team/dept researched if mentioned?
- [ ] Meeting format explained if special (C2C, etc.)?
- [ ] Context integrated into background section?

**Time & Location:**
- [ ] Date/Time field: `YYYY-MM-DD (Day) HH:MM–HH:MM KST`?
- [ ] Location field present (or marked `[TBD]`)?
- [ ] User-provided context fully reflected?

**Narrative Quality:**
- [ ] Discussion sections are prose, NOT bullet lists?
- [ ] Each topic follows Problem → Solution → Result?
- [ ] Transition sentences connect topics?
- [ ] Section titles are insight-driven, not generic?
- [ ] Storytelling tone used (not bureaucratic report tone)?
- [ ] 1-2 metaphors/analogies included to crystallize key concepts?

**Content & Detail Preservation:**
- [ ] **ALL details from source preserved?** (Nothing skipped, nothing summarized)
- [ ] **1500-2500+ words?** (Comprehensive, not concise)
- [ ] Background clear in 3-5+ sentences with counterparty context?
- [ ] Decisions include approver OR learnings include context?
- [ ] Every action has @owner and due date?
- [ ] Rejected items documented with reasons?
- [ ] Original quotes included where impactful?

**Terminology:**
- [ ] All terms have immediate inline explanation (> 📘)?
- [ ] Glossary table complete?
- [ ] All phonetic transcriptions converted to proper terms?
- [ ] All terms verified with 2+ sources?
- [ ] Original transcription noted (Original: ...)?

**If ANY answer is No, fix before outputting.**

---

## Integration with Other Skills

**This skill requires:**
- **mcp__time__get_current_time** — REQUIRED for Phase 0
- **Brave Search MCP** — REQUIRED for counterparty research & term verification
- **Context7 MCP** — For technical documentation lookup
- **mcp__fetch__fetch** — For counterparty website/blog content

**Escalate to deep-research when:**
- Counterparty has extensive public presence worth deep-diving
- Term has multiple conflicting definitions
- Meeting topic requires comprehensive market analysis

**After this skill (within 48 hours):**
- **Distribute notes** — Email/Slack to all attendees
- **Track action items** — Create tickets in Jira/Linear/Notion
- **Archive** — Store with naming: `[YYYY-MM-DD] Meeting Title`

---

## Output Language

1. **First Priority**: If `CLAUDE.md` specifies language → use it
2. **Second Priority**: Use language of user's input

Keep technical terms in **proper English** with explanation in target language.
- Correct: **Jenkins** (Original: "jenkinsun", CI/CD automation server)
- Wrong: **jenkinsun** (CI/CD automation server)

---

## Example Output Structure (~800-1100 words)

```markdown
# [Meeting Title] — YYYY-MM-DD

## Overview

| Field | Details |
|-------|---------|
| **Date/Time** | YYYY-MM-DD (Day) HH:MM–HH:MM KST |
| **Location** | [Physical location / Video platform] |
| **Our Team** | @name (role), @name (N people) |
| **Counterparty** | [Company] — name (role), name (N people) |
| **Author** | @name |

---

## Background

[Sentence 1: Counterparty identity - scale, industry position]
[Sentence 2: Their team structure and why they're relevant]
[Sentence 3: Why this meeting matters to us - gap, learning opportunity]
[Sentence 4: Meeting context - how arranged, format if special]
> 📘 **[Format Term]** — [Definition if meeting format is unfamiliar]

---

## Key Learnings

### [Insight-Driven Title] — [Transformation Subtitle]

[Problem: 2-3 sentences - what challenge existed, why it mattered]

[Solution: 2-3 sentences - what changed, how it works]
> 📘 **[Term]** — [1-2 sentence definition]

[Transition: 1 sentence - how this led to next development]

### [Next Topic Title]

[Continue Problem → Solution → Result pattern...]

---

## Implications

| Insight | Recommendation |
|---------|----------------|
| [Learning 1] | [Actionable next step] |

---

## Action Items

- [ ] [Verb first] — @owner, Due: MM/DD

## Parked Items

- **[Topic]**: [Reason] — Revisit: [condition]

## Glossary

| Term | Original | Definition | Context |
|------|----------|------------|---------|
| **[Term]** | "[STT original]" | [Definition] | [Meeting context] |

## Next Steps

- [Follow-up action]
```

---

## Action

Transform the provided meeting inputs into narrative-driven, actionable notes following this structure.

**REMEMBER — THE THREE ABSOLUTES ARE ALWAYS ON:**
1. **ZERO DETAIL LOSS** — If it was in the source, it MUST be in the output
2. **MAXIMUM TOKEN UTILIZATION** — 1500-2500+ words. Brevity is NOT the goal.
3. **HIGH-DENSITY NARRATIVE** — Tight, structured storytelling with substance

**Additional Requirements:**
- Missing counterparty research = incomplete context
- Missing time/location = incomplete record
- Bullet list discussion = fragmented understanding
- Action without owner = failed notes
- Term without immediate inline explanation = inaccessible
- Correction without 2+ sources = misinformation
- Phonetic transcription preserved = unsearchable
- User context ignored = failure to read input
- **Summarized or abbreviated output = FAILURE**
