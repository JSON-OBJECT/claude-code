# Anatomy of a verdict card

The disclosed reference for [`verdict`](SKILL.md). Read it before minting or amending.

## Slot template

Slots run in priority order: a reader who stops early still has the ruling.

```markdown
---
type: canon
description: "<the ruling itself, ~40–140 chars — the answer, not a label>"
timestamp: 2026-08-04
stale_after: 2026-10-04
status: draft
generated_by: <model>
human_reviewed: false
distilled_from: _answers/2026-08-04-<slug>.md
tags: [verdict, <domain>, <the proper nouns a future question will contain>]
---

# Ruling — <the question this card closes>

> **Within the shelf life (2026-10-04), act on this without researching it again.**
> <The ruling in two or three lines. The sentence a colleague would repeat verbatim.>

## <Situation> — choosing <subject> for <case>

| Situation | Use | One-line reason |
|---|---|---|
| … | … | … |

## Rejects — <subject> options ruled out and why

| Candidate | Why rejected | What would reopen it |
|---|---|---|
| … | … | … |

## Appeal — what would overturn this ruling about <subject>

- <A change in the world that invalidates the ruling>
- <A measurement that, if it came back different, forces a recount>

## Evidence — primary sources

- <Primary source, with what was verified first-hand>
- Lineage (not evidence): `_answers/<file>.md` — excluded from the index
```

**Rejects** is the highest-value slot per token. Without it the next session re-investigates every option the card fails to mention, and the reason is what stops the re-litigation. Every card carries it, including cards that rule on something other than a tool choice — a card ruling on sources rejects the poisoned ones and says how to spot them. Keep the heading `## Rejects — …` so the slot stays identifiable.

**Appeal** is what makes brevity safe. A short card's risk is being quietly wrong; naming its failure conditions means an expired card needs three lines re-checked, not a fresh investigation.

Both slots are mandatory. `verdict-lookup.sh --lint` checks for them, along with the ceiling, dated headings, edit markers, non-card files and router hygiene — run it before promoting. The heading may be localised or numbered (`## 3. 탈락 (Rejects) — …`); the lint matches the slot's function, so keep the wording your vault already uses rather than renaming cards to satisfy a grep.

Optional slots, added only when the material exists:

- **Correction ledger** — one line per overturned claim: what the card used to say, what is true, where the wrong version came from. **This is the only place an edit may be recorded**, and it records the overturned claim, not the act of editing.
- **Open items** — claims awaiting legal, vendor, or first-hand confirmation. These stay listed even after `human_reviewed: true`, because that flag promotes the file, not the individual claim.

There is deliberately **no map slot**. A table of sibling cards inside a card is a third copy of routing state that already exists in the frontmatter and in `verdict-lookup.sh`, and it goes stale the moment a sibling is renamed or split. Point at a sibling where the prose genuinely needs it — an inline link, one direction, at the sentence that hands the question over.

**The card is state; git is the log** — so a card carries no mark that it changed. [`SKILL.md`](SKILL.md) Step 3 holds this rule and the byte gate that enforces it.

## Frontmatter contract

| Field | Rule |
|---|---|
| `type` | **`canon`.** `/ground` filters interpretive questions with `type IN ('canon','doctrine-canon')`, and the reindex contract report flags any value outside the OKF vocabulary. A card typed `verdict` is silently skipped by that filter. |
| `description` | Carries the ruling. It is an indexed column and rides only on the file's first section row, so it is what a search hit shows before the file is opened. |
| `tags` | Starts with `verdict`, then the proper nouns a future question will actually contain. Frontmatter sits inside the preamble section body, so tags are searchable text. |
| `stale_after` | Set from the **fastest-decaying** claim in the card. The reindex prints the expired list on every run, which is what turns review into a dated queue instead of a growing backlog. |
| `status` | `draft` until a human reviews. `deprecated` when retired, paired with `superseded_by`. **A draft card is invisible to retrieval** — the grounding query filters `human_reviewed != 'false'`, so an unpromoted card is reachable only through the hub row. Settle promotion in the minting session (Mint step 7) rather than accumulating a backlog of cards that cannot be found. |
| `distilled_from` | Names the `_answers/` file as lineage. Deliberately not `evidence:` — `_answers/` is excluded from indexing and grounding so that LLM output never re-enters as LLM source. Evidence points at what the answer cited. |
| `supersedes` / `superseded_by` | Paired, and used when a card splits or is replaced. The superseded file stays. |

## Retrieval mechanics

Verified against `fts5-reindex.py`. These decide how a card is worded.

**Only `description` and `body` are indexed.** `path`, `rel_path`, `heading`, `type`, `timestamp`, `stale_after` and `status` are all `UNINDEXED` — filterable, never matched.

> 🔴 **`LIKE` does not work on these columns. It returns zero rows, and it does not error.**
>
> `UNINDEXED` means "not full-text searchable", not "unusable in `WHERE`" — `=` and `instr()` work normally. But `LIKE` against an FTS5 column silently yields nothing:
>
> ```sql
> SELECT count(*) FROM notes_fts WHERE rel_path = 'verdicts.md';              -- 6   ✅
> SELECT count(*) FROM notes_fts WHERE instr(rel_path, 'verdicts/') = 1;      -- 731 ✅
> SELECT count(*) FROM notes_fts WHERE rel_path LIKE 'verdicts/%';            -- 0   ❌ silent
> ```
>
> This is the worst class of bug the layer can have: a filter that returns nothing reads as *"no card owns this question"*, so the pipeline proceeds to re-research a settled topic with no warning. **Use `instr(col, 'prefix') = 1` for prefix matching and `=` for exact matching. Never `LIKE`.**

Five consequences:

1. **The file name contributes nothing to ranking.** A `-verdict` suffix buys no retrieval. What the name still does: `rel_path` comes back with every hit, and the agent judges relevance from it before opening. So name the file after the decision it closes.
2. **Headings are invisible to search.** `## Rejects` alone matches nothing. Each H2 body restates the subject noun, because the retrieval unit is a section (H1–H3), not a file — a section arrives alone, stripped of the file's context. Headings still decide the card's *shape*, which is why they name a decision, a situation, or a subject and **never a date or an event**: a section titled with a date buys nothing in retrieval and turns the card into the log it is not. Facts arriving in waves are folded into the slot that owns them, not filed under the wave.
3. **Tags are searchable but imprecise.** There is no `tags` column — frontmatter is simply part of the preamble body, so a tag matches as ordinary text. That is fine for proper nouns, and wrong for genre. `MATCH 'verdict'` also hits any file whose prose contains the word: measured on one vault, **94 files for 59 cards** (a `### The Verdict` heading in an unrelated report is enough). **Load tags with proper nouns, and mark genre by location, not by tag** — a `verdicts/` prefix filtered with `instr()` is exact and costs nothing.
4. **The tokenizer is trigram**, which solves substring matching and Korean morphology but not synonyms. It will never connect one term to a card that only uses another word for it. Put the alternative phrasings in the body or tags yourself.
5. **Tokens shorter than three characters are not indexed at all.** In CJK that is a whole class of ordinary words — a two-glyph Korean tag is a tag no query can ever reach, and it fails silently rather than erroring. Verified: a `MATCH` on such a term returns zero rows across an entire vault. Write tags and key body terms at three characters or more, and when a two-character word is the natural one, put a longer compound beside it.

**A dense reference card can outrank the card holding the ruling**, because BM25 rewards term density and a table of many short rows concentrates a proper noun harder than the paragraph that decides about it. Sharpening the `description` does not always fix it. The router and the lookup query exist to cover this case — not a per-card index file, which loses to BM25 in the opposite direction.

> The same normalisation that lets a dense table win also makes a **large** file lose. A 99 KB index parsed into three enormous sections ranked **dead last** on every query it matched, and missed entirely on common terms. Size is not a ranking asset. Cards stay small so they stay findable, not only so they stay readable.

## Voice

- **State the ruling.** Uncertainty becomes a rule — "if X then A, otherwise B" — or a confidence marker on the line. It does not become a disclaimer, which returns the reader to the research the card exists to close.
- **Mark confidence where sources disagreed**: verified against the primary source / secondary only / actively disputed. A number that varied by 2× between sources says so, and says to re-check before committing money to it.
- **Keep the dissent.** One compressed line for the strongest recorded objection. A card with the objections stripped reads more settled than the evidence supports.
- **Date every decaying claim.** Claims are as-of `timestamp`; "current" and "latest" without a date rot silently.
