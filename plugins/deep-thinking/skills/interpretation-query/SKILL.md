---
name: interpretation-query
description: Bring back what the reader said before about a work or an idea, from the numbered readings under interpretation/ and the digest pages. Use when the reader asks what they said or thought earlier, where they left off, which readings are still tentative or were corrected, or asks for a summary of their thinking.
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <a work, an idea, or "where were we">
---

# Interpretation Query

`interpretation/` holds the reader's readings — numbered, in their own words, stamped. `digest/` holds the assistant's pages that gather those readings by idea. This skill answers "what did I say": it finds readings and tells them in the reader's words. What a text says is `library-query`'s to answer.

Run every command from the folder that holds `interpretation/`; `python3 scripts/interpretation.py --help` prints every option.

## Steps

1. **Find** by what the reader asked:

   | They ask | Run |
   |---|---|
   | what they said about a thing ("did I say …", "that thing about …") | `recall . "<their words>" --limit 6` |
   | exactly where a word or name was said, or when it first came up | `find . "<spelling\|spelling>"` — output is oldest first within a rank; `first said` is the reading's first turn, so open it to see which turn holds the word |
   | their readings of a work | `list . --work <id>` |
   | what is still tentative | `find . --tentative` |
   | what they corrected or took back | `find . --rejected` |
   | everything under one of their names | `find . --reach "<name>"` |
   | where they left off, or "let's go on" | `desk . show`, then `list .` (latest first) and `show .` the latest reading: its Asked line is the question the assistant left open — pick the thread up there, as the assistant's question, not the reader's thought. Follows lines chain a reading to the ones before it in the same train of thought |
   | where their thinking on an idea stands | read `digest/<idea>.md`; if there is none, `material . --reach "<idea>"` |
   | how they talk about their ideas, at the start of a session | `lexicon .` — their names, most used first, each with their latest words using it, what they took back, and its renames. Speak to them in these names |

   `find` ignores spaces, so a short spelling can match across two words — read the hit before counting it.
   Done when you hold the number of every reading you will speak of.

2. **Read** them: `python3 scripts/interpretation.py show . <no> <no> …` prints each without its quotes; open the file when you need the quoted lines.

3. **Answer** in the reader's language, as you would remind a colleague — a few sentences, most relevant first. For each reading you mention: its number, when (today, three days ago — the date only when it matters), and the reader's own sentence in 「」, copied from the reading.
   - A tentative reading is told as not settled; a rejected line as what they took back and why; a paragraph of the assistant's as the assistant's.
   - A digest page is the assistant's summary: say so, and give the reading numbers it rests on.
   - End with how many readings matched when you showed only some.

   Done when every quoted word is copied from a reading and every reading named has its number.
