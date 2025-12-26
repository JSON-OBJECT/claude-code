---
description: Create bulletproof instructions/custom-commands/skills following the Superpowers philosophy - strong language, mandatory checklists, anti-rationalization tables, and iron laws
---

# Forge Prompt - Instruction Smithy

You are creating a **bulletproof instruction/custom-command/skill** following the Superpowers philosophy for:

**$ARGUMENTS**

---

## The Iron Law

NO INSTRUCTION WITHOUT ALL 9 COMPONENTS.
"A skill without Iron Law is a suggestion. A skill without Red Flags is a trap."

**Violating the letter of this structure is violating the spirit of effective instructions.**

---

## The Philosophy

Superpowers skills are NOT suggestions. They are **battle-tested protocols** designed to:

1. **Prevent rationalization** - The #1 failure mode is "this case is different"
2. **Force discipline** - Structure eliminates decision fatigue and shortcuts
3. **Make failure visible** - Clear criteria reveal when you're off track
4. **Be actionable** - Every rule has a concrete action, not abstract advice

**Core belief:** If you think you don't need the structure, you need it most.

---

## The 9 Required Components

Create TodoWrite todos for EACH component as you work through them.

### 1. YAML Frontmatter (Metadata)

---
name: kebab-case-name
description: Use when [TRIGGER CONDITION] - [WHAT IT DOES] that [WHY IT MATTERS]
---

**Trigger condition patterns:**
- "Use when encountering X, before doing Y"
- "Use when starting X that requires Y"
- "Use when finishing X, before claiming Y"

**Example:**

description: Use when encountering any bug, before proposing fixes - four-phase framework that ensures understanding before attempting solutions


### 2. Iron Law (Non-Negotiable Core Rule)

The ONE rule that, if broken, guarantees failure.

**Format:**

## The Iron Law

\`\`\`
[ALL CAPS, IMPERATIVE STATEMENT]
\`\`\`

[Supporting statement about why this matters]

**Violating the letter of this rule is violating the spirit of [skill name].**

**Examples:**
- `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`
- `NO REPORT WITHOUT 15+ SEARCHES AND PHASE ZERO FIRST`
- `NO CODE WITHOUT FAILING TEST FIRST`
- `NO COMMIT WITHOUT VERIFICATION COMMAND OUTPUT`

### 3. When to Use / When NOT to Use

**Format:**

## When to Use

Use for [CATEGORY]:
- Specific scenario 1
- Specific scenario 2
- Specific scenario 3

**Use this ESPECIALLY when:**
- Counter-intuitive trigger 1 (when you want to skip it most)
- Counter-intuitive trigger 2
- Counter-intuitive trigger 3

**Don't skip when:**
- Excuse that seems valid but isn't
- Another excuse
- Time pressure excuse

**Key insight:** The "ESPECIALLY when" section should list situations where people are MOST tempted to skip it.

### 4. Process/Phase Structure

Break the skill into clear, sequential phases with gates (checkpoints that must be passed before proceeding).

**Format:**

## The [Number] Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: [Name]

**[GATE CONDITION]:**

1. **Step Name**
   - Substep detail
   - Substep detail
   - Success criteria

2. **Step Name**
   - Substep detail

**Gate patterns:**
- "BEFORE attempting ANY [action]:"
- "You cannot proceed to Phase N until:"
- "If [condition], STOP and return to Phase 1"

### 5. Red Flags Section

Mental patterns that signal you're about to fail.

**Format:**

## Red Flags - STOP and [Action]

If you catch yourself thinking:
- "[Rationalization thought 1]"
- "[Rationalization thought 2]"
- "[Shortcut thought 1]"
- "[Overconfidence thought 1]"
- "[Time pressure thought 1]"

**ALL of these mean: STOP. [Specific action to take].**

**Common red flag patterns:**
- "Quick fix for now, investigate later"
- "This case is different/simple"
- "I already know what the problem is"
- "Just try this and see"
- "I don't have time for the full process"

### 6. Common Rationalizations Table

Preempt every excuse with direct rebuttal.

**Format:**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "[Excuse 1]" | [Direct rebuttal explaining why it's wrong] |
| "[Excuse 2]" | [Direct rebuttal explaining why it's wrong] |
| "[Excuse 3]" | [Direct rebuttal explaining why it's wrong] |

**Rebuttal tone:** Direct, no hedging, explains the consequence.

**Example rebuttals:**
- "Simple issues have root causes too. Process is fast for simple cases."
- "Emergency pressure is exactly when systematic approach saves time."
- "Partial understanding guarantees bugs. Read it completely."

### 7. Quick Reference Table

One-glance summary of the entire skill.

**Format:**

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. [Name]** | [2-3 activities] | [Measurable outcome] |
| **2. [Name]** | [2-3 activities] | [Measurable outcome] |

### 8. Key Principles / Summary

Core principles for quick recall.

**Format:**

## Key Principles

- **[Principle name]** - [One line explanation]
- **[Principle name]** - [One line explanation]
- **[Principle name]** - [One line explanation]

**Or alternative closing format:**

## Summary

**Starting [task type]:**
1. [First action]
2. [Second action]
3. [Third action]

**[Situation]?** [Action].

**[Key insight] = [mandatory action].**

### 9. Integration / Related Skills (Optional but Recommended)

**Format:**

## Integration with Other Skills

**This skill requires using:**
- **[skill-name]** - REQUIRED when [condition]
- **[skill-name]** - REQUIRED for [purpose]

**Complementary skills:**
- **[skill-name]** - [When to use together]

---

## Language & Tone Guide

### Strong Language Patterns

Use these deliberately and consistently:

| Weak (Avoid) | Strong (Use) |
|--------------|--------------|
| "You should" | "You MUST" |
| "Consider" | "REQUIRED" |
| "It's recommended" | "This is not negotiable" |
| "Try to" | "ALWAYS" / "NEVER" |
| "It's helpful to" | "CRITICAL" |
| "You might want to" | "You cannot proceed until" |
| "It's important" | "If you skip this, you will fail" |

### Emphasis Patterns

- **ALL CAPS** for critical terms: MUST, NEVER, ALWAYS, REQUIRED, CRITICAL, STOP
- **Code blocks** for Iron Laws and key rules
- **Bold** for section headers and key terms
- **Tables** for comparisons and quick reference
- **Bullet points** for lists, **numbered lists** for sequences

### Philosophical Phrases to Include

- "Violating the letter of this rule is violating the spirit of [X]"
- "If you think [X], you are rationalizing"
- "The moment you feel [X] is the most dangerous moment"
- "ALL of these mean: STOP."
- "[Excuse] is ALWAYS wrong"
- "This is not negotiable. This is not optional."

---

## Anti-Pattern Warnings

**DO NOT create instructions that:**

- ❌ Use soft language ("consider", "try to", "you might want to")
- ❌ Lack an Iron Law (the ONE rule that cannot be broken)
- ❌ Skip the Red Flags section (failing to anticipate rationalization)
- ❌ Have vague success criteria ("do a good job")
- ❌ Allow wiggle room ("unless you have a good reason")
- ❌ Assume good faith ("you probably know when to skip this")
- ❌ Are too abstract (no concrete actions or examples)
- ❌ Are too long without clear phases (wall of text)

**DO create instructions that:**

- ✅ Have ONE non-negotiable Iron Law
- ✅ Anticipate every excuse with direct rebuttals
- ✅ Include measurable success criteria
- ✅ Gate each phase with clear conditions
- ✅ Use strong, unambiguous language
- ✅ Provide concrete examples and patterns
- ✅ Are scannable (tables, bullets, clear headers)

---

## Final Verification Checklist

Before considering the instruction complete, verify:

### Structure Checklist
- [ ] YAML frontmatter with name and description (with trigger condition)
- [ ] Iron Law in code block with supporting statement
- [ ] When to Use section with "ESPECIALLY when" counter-intuitive triggers
- [ ] Clear phases with gate conditions
- [ ] Red Flags section with "If you catch yourself thinking" pattern
- [ ] Common Rationalizations table with Excuse | Reality format
- [ ] Quick Reference table for one-glance summary
- [ ] Key Principles or Summary section

### Language Checklist
- [ ] Uses MUST, NEVER, ALWAYS, REQUIRED appropriately
- [ ] No soft language (should, consider, try to, might)
- [ ] Includes at least 3 "Violating the letter" type phrases
- [ ] Red flags end with "ALL of these mean: STOP"
- [ ] Each rationalization has a direct, no-hedge rebuttal

### Content Checklist
- [ ] Iron Law is ONE clear rule (not multiple)
- [ ] Red Flags include time-pressure and overconfidence thoughts
- [ ] Rationalizations table has at least 5 entries
- [ ] Success criteria are measurable, not vague
- [ ] Examples are concrete and actionable

---

## Slash Command Syntax Reference

When generating slash commands (`.claude/commands/*.md`), follow this exact format:

### File Structure

```markdown
---
description: Brief description (<60 chars recommended)
allowed-tools: Bash(git:*), Read, Write, Edit
argument-hint: [arg1] [arg2]
disable-model-invocation: false
---

Prompt body goes here.
```

### Frontmatter Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `description` | Recommended | Shows in `/help` and autocomplete (<60 chars) |
| `allowed-tools` | If using tools | Whitelist: `Bash(npm:*)`, `Read`, `Write`, `Edit` |
| `argument-hint` | If accepting args | Shows in autocomplete: `[file] [mode]` |
| `disable-model-invocation` | Optional | Set `true` to prevent Claude auto-invocation |

### Arguments

| Syntax | Captures |
|--------|----------|
| `$ARGUMENTS` | All arguments as single string |
| `$1`, `$2`, `$3` | Positional arguments |

---

## Output Location

Save the generated instruction to:
- **For commands:** `.claude/commands/[command-name].md`
- **For skills:** `.claude/plugins/[plugin-name]/skills/[skill-name]/SKILL.md`
- **For standalone:** `docs/instructions/[name].md` or user-specified path

---

## Execution

Now create a bulletproof instruction for **$ARGUMENTS** following ALL components above.

Use TodoWrite to track each of the 9 components as you complete them.

Remember: **If you skip any component, the instruction will fail in production.**
