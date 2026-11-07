---
name: five-lens
description: Explain an object, brand, person, concept, or event through five lenses (TL;DR · one-liner · encyclopedia · sharp insights · narrative and metaphor). Use when the user asks for an explanation through five lenses, from TL;DR to narrative, or lists these five cells.
---

# Five Lens

Shine five lenses on one subject. All five cells draw from a single **ledger** — a list of facts, each paired with its source. The encyclopedia cell *is* the ledger; the other four cells only **rearrange** what the ledger holds. That is what makes two runs on the same subject speak from the same facts. Everything you need is in this file — no external doc required.

## 1. Gather material and build the ledger

- If you are working inside a knowledge vault, search it before anything else — settled cards first (in a deep-thinking vault, `./verdict-lookup.sh <keyword>`), then notes. Use search keywords of three or more characters with apostrophes and quotes stripped, switching to a different identifier when stripping breaks the word (an alias, an abbreviation, a version string): a quote inside the query can surface as a syntax error that reads like "0 rows", which looks exactly like "nothing on file". Facts already verified earlier in this conversation are material too.
- If the material is thin — fewer than five numbers, dates, and proper nouns combined — research before writing. If you cannot research, say the material is thin and write only the cells the ledger can support.
- Each ledger line is one pair: "fact — source". When sources disagree, record the disagreement as it stands (e.g. "first released in 2009 per one source / 2010 per another").

**Done when:** every number, year, and proper noun you intend to use in any other cell is in the ledger with its source.

## 2. Writing order and display order

Write in this order: **ledger → insights → TL;DR → one-liner → narrative.** Facts are fixed first; compression and story sit on top of them. Display in the table's order below, with headings in the user's language.

| Lens | Form | What it carries |
|---|---|---|
| TL;DR | At most 2 sentences | What the subject is, plus its one key fact |
| One-liner | One bold sentence (a single full stop) | The subject's contradiction or essence in one sentence |
| Encyclopedia | Bold labels + bullets | The ledger: numbers, years, proper nouns, and where sources diverge |
| Sharp insights | 3–4 numbered items | A conclusion not visible on the surface, reached by joining two ledger facts. Each insight shows which facts it came from |
| Narrative and metaphor | Prose | The ledger's facts rearranged in time order or cause-and-effect, plus one metaphor that binds the whole subject |

- The **narrative** uses only scenes the ledger holds. When scenes need joining, join them with feeling or meaning, never with invented dates or places. Write the metaphor so it is plainly a metaphor ("it is a protocol that behaves like…").
- The **one-liner** and **TL;DR** compress the ledger's own words. Keep out any era or figure the ledger lacks, even when it would make the sentence smoother.

**Done when:** all five cells are present, or a cell the ledger cannot support is marked "material too thin".

## 3. Trace

After writing, extract every **fact-carrying expression** from the TL;DR, one-liner, insights, and narrative cells:

- numbers · years · eras ("the early 2000s", "the dot-com era") · proper nouns · places
- words that assert order or degree: "first", "only", "most", "never", "all", "overnight"

For each extracted expression, point to the ledger line that backs it. If a line backs it, keep it. If none does, add it to the ledger when it has a source; when it has none, delete it or reduce it to what the ledger actually says ("became the standard overnight" → "became a standard").

**Done when:** every extracted expression points to a ledger line with none left over, and the sentences in your final answer are the very sentences you traced. Answer only after this trace.
