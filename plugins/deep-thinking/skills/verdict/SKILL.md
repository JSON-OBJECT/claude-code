---
name: verdict
description: Distil a saved Q&A thread into verdict cards — compact, binding conclusions a future session reads instead of re-researching the topic.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
argument-hint: "[path to an _answers/ file, or blank to use this conversation]"
---

# Verdict

A **verdict** is a settled conclusion a future session obeys instead of re-researching. It states the ruling, the branch rules, the **rejects**, and the **appeal** conditions that would overturn it. How the deliberation went stays in the source.

**Why this runs at all:** a session reaches a genuinely good answer and then ends before anyone files it. The reasoning evaporates and the next session pays for the same investigation again. This is the intake valve — it inhales that answer into the vault's brain while it is still there, compressed to the part a future session has to obey.

Source: **"$ARGUMENTS"** — an `_answers/` file crystallised earlier by `save-answer`, or this conversation when blank. Both are the same job: an answer that has not yet been filed.

## The inversion

Default summarising keeps the narrative and drops the numbers. A verdict does the opposite.

**Carry** every number, proper noun, version string, parameter value, price, rejected option with its reason, and recorded dissent.
**Leave behind** the research narrative, the comparison tables that produced the ruling, and the story of who found what.

**Read `ANATOMY.md` now** — it holds the slot template, the frontmatter contract, and the retrieval mechanics that decide how a card gets written. Both branches below assume it.

## Pick the branch

Run a search before choosing — from the vault root (the directory holding `fts5-reindex.py`):

```bash
grep -rl "tags:.*verdict" --include="*.md" . | head -20
sqlite3 vault.fts5.db "SELECT DISTINCT rel_path FROM notes_fts WHERE notes_fts MATCH '<topic>' ORDER BY bm25(notes_fts) LIMIT 10"
```

- Nothing covers the topic → **Mint**
- Cards exist and this source adds or overturns facts → **Amend**

---

# Mint

### 1. Prove the source is whole

A `_answers/` file may still be mid-write, and a source read at 40% yields cards that are wrong on arrival.

```bash
head -20 <source>              # the header usually declares the total ("9 rounds", "full thread")
grep -nE "^#{1,2} " <source>   # enumerate what is actually present
stat -c '%s %y' <source>       # size and mtime — a file touched minutes ago may still be growing
```

**Done when** the count the header declares equals the count you can enumerate. When they disagree, or the mtime is minutes old, re-check the size before starting rather than working from what is there.

### 2. Read forward and log every reversal

Read the whole source in order. Later rounds correct earlier ones — a licence term restated from primary sources, a model that turned out to be omitted, a price that moved.

**Done when** for every section you can name which earlier claim it corrects or supersedes, or state that it corrects none. The log drives step 4; a card built from an early round alone is born wrong.

### 3. Cut into decisions

Four axes, applied together:

- **Decision unit** — "which image model" is a topic and grows forever; "which image model do we use" is a decision and ends when the answer settles. Name each card with the question it closes.
- **Retrieval moment** — budgeting, sitting at the tool, and asking legal are three moments. One card per moment.
- **Decay rate** — model rankings and prices decay in ~2 months; craft principles and statute in ~6–12. Mixing rates forces the slow half through the fast half's review cycle.
- **Size ceiling** — ~15 KB / ~5k tokens per card. A card over it splits along the three axes above.

**Done when** every card answers one question, asked at one moment, under one `stale_after`, within the ceiling.

### 4. Write the cards

Follow the slot template in `ANATOMY.md`.

**Done when** every slot carries content, and every number, proper noun, parameter value, rejected option, dissent, and reversal you logged in step 2 appears in exactly one card. A fact that survives in no card is a fact the next session pays to rediscover.

### 5. Wire the hub — and amend what the new cards just contradicted

`verdicts.md` at the vault root indexes every card: path, the ruling in one line, `stale_after`. Create it if absent (`type: index`).

Its body carries every ruling, so one hit on the hub hands over the whole map — the backstop for the ranking failure described in `ANATOMY.md`.

**Watch the hub's size, because every question pays for it.** `/ground` reads the hub before searching anything, so its byte count is a fixed cost charged to questions that have nothing to do with any card. The failure is gradual and easy to miss: rulings get richer, each row grows from one line to a paragraph, and one domain quietly takes a third of the file. Measured on one vault, the hub reached **155 KB — roughly 44 K tokens, 4.4 % of a 1 M context window, spent before the question was even read.** Truncating the read does not save you; rows that long are not cut by `head`.

**Split at ~15 KB, the same ceiling a single card has**, into three tiers:

| Tier | Holds | Read when |
|---|---|---|
| `verdicts.md` — router | One row per domain: what it decides, card count, earliest expiry, link | **Every question** |
| `verdicts/<domain>/INDEX.md` | The per-card ruling rows for that domain | Lookup is ambiguous or returns nothing |
| `verdicts/CHARTER.md` | The genre contract | Minting or restructuring a card |

Move session-by-session landing narrative out of the hub entirely. It is the fastest-growing and least-queried content there, and git already records what changed — keep only the reasoning a diff cannot reconstruct.

Then make the router's next step a **query, not a read**. Nothing about locating one card justifies loading a whole domain index:

```bash
sqlite3 vault.fts5.db -separator $'\t' "
  SELECT DISTINCT rel_path, description, stale_after FROM notes_fts
  WHERE rel_path IN (SELECT rel_path FROM notes_fts
                     WHERE notes_fts MATCH '<keyword>' AND instr(rel_path,'verdicts/')=1)
    AND description != '' AND stale_after != ''
  ORDER BY stale_after;"
```

Worth wrapping in a `verdict-lookup.sh` at the vault root: it is the one command every session runs first. Two things it should handle — warn on query terms under three characters (see `ANATOMY.md`), and fall back to the main checkout's index when run from a git worktree, where the gitignored DB is absent.

Then close the loop minting opens. **A new card almost always overturns something an existing card asserts**, because the research that produced it went looking where the old cards were thin. Recording that only in the new card leaves the old one intact and wrong — and the old one is what retrieval hands the next session, because it owns the question the user will actually ask. A note in the hub does not fix this: the hub is read before searching, the stale card is read after.

For each card minted, ask what existing card owns each question it touches, and run **Amend** on that card now — rewrite its ruling line, cross-link both directions, log the reversal. Do the same for the domain's entry-point card: its **Map** slot must list every sibling, or the designated entry point conceals part of the vault.

**Done when** every card has a hub row, every hub row resolves to a file, the entry-point Map lists every card in the domain, and every claim the new cards overturn has been rewritten in the card that owns it — not merely noted in the new one.

### 6. Reindex and probe

```bash
python3 fts5-reindex.py
sqlite3 vault.fts5.db "SELECT rel_path, heading FROM notes_fts WHERE notes_fts MATCH '<question a future session would ask>' AND status != 'deprecated' ORDER BY bm25(notes_fts) LIMIT 3"
```

**Done when** one realistic question per card returns that card in the top 3, and the reindex contract report shows no off-contract `type` and no oversized file. A card that does not surface is a card that does not exist.

When a probe misses, sharpen the `description` and the body wording of the section that should have matched.

### 7. Hand back the open items, and settle promotion in the same session

A card left at `status: draft` / `human_reviewed: false` is filtered out of the grounding pipeline it exists to short-circuit — the retrieval query drops unreviewed files, so the next session re-researches the topic and may land somewhere else. The hub row is then the card's only path to a reader.

So do not leave promotion to a later session that will not come. Report the open items, then **ask outright whether to promote now**, naming what a human would be signing off on.

**Done when** the report names every claim the cards marked unverified, awaiting legal or vendor confirmation, or under live community dispute — and each card is either promoted (`status: stable`, `human_reviewed: true`) with that decision recorded, or left as a draft with the reason and the note that only the hub reaches it.

---

# Amend

New facts arrive in later sessions. The card absorbs them at constant size.

### 1. Find the owning card

Search first. Each fact belongs to the card whose question it answers.

**Done when** every incoming fact is assigned to an existing card, or flagged as a new decision that needs Mint.

### 2. Land each fact in a slot

Every fact lands in a slot the card already has. This is what holds size constant:

- A fact that changes the ruling → **rewrite the ruling line.** Replace, not append.
- A new candidate → **one row in the rejects table**, or one row in the branch table if adopted. The body does not grow.
- A new way the ruling could fail → **one bullet under appeal.**
- Deeper detail on something already ruled → push it to the linked source, and keep the card's line as it is.

**Done when** every fact occupies a slot, and a new section exists only where a genuinely new slot-worthy decision arrived.

### 3. Record reversals

When a fact overturns something the card asserts, keep one line in the correction ledger: what the card used to claim, what is true, and where the wrong version came from.

The ledger exists because bad secondary sources persist. Without it the next session re-imports the same error from the same vendor blog.

**Done when** every overturned claim has a ledger line and the body carries only the corrected version.

### 4. Re-measure, re-stamp, re-probe

```bash
stat -c%s <card>; python3 fts5-reindex.py
```

- Over the ceiling → split along the three content axes from Mint step 3, repoint every cross-reference, and update the hub.
- Bump `timestamp`; recompute `stale_after` from the fastest-decaying claim now in the card.
- Probe as in Mint step 6.

**Done when** the card is under the ceiling, its dates reflect today's edit, and it still surfaces on a realistic question.
