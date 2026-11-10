---
name: library-ingest
description: Ingest a long-form source (book, paper, report) into the library as canonical text with a structure ledger and a search index. Use when the user hands over a text to add to the library, or asks to rebuild the library index.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: <source text file or folder>
---

# Library Ingest

Ingest turns a source **as received** into **canonical text**: one file per work, in the author's divisions rather than the packaging's, that `library-query` can quote by line. A library root holds three things, and each step writes to exactly one of them:

```
raw/<source>/   as received — written in step 2; afterwards only SOURCES.tsv rows are corrected
library/        canonical text + ledger per work, and library.fts5.db
scripts/        the library-* scripts
```

**Packaging** is whatever the distributor added to carry the text: a header and footer, a transcriber's notes, illustration captions, headings an editor put in, a note of where the text first appeared (`(1939.3 문장)` — when it is the only place the year of first publication is stated, carry the first year into `meta.date` before dropping it), a note body whose marker in the text is lost (`↑ …`), a second copy of the same text. A mark that stands for the text itself stays and is reported as a source defect, not dropped: a transcriber's note that words are illegible or lost (`(원문에서 글자판독 불가능)`, `……(이하 원문 탈락)……`), and an end mark such as `(끝)` or `(未完)`. A page separator the distributor put between files (`=== Title/제3장 ===`) is packaging too, but when it is the only place a division's number survives, keep the number as the heading with a `headings` rule and `inline`, and when a title line follows it, add `join_number_headings` so the two become one heading (`제1장 하기방학`). A separator that names a bundle of divisions (`=== Title/1장~20장 ===`) carries nothing the headings lack: `drop` it. Packaging repeats — once one piece is found, search the whole raw file for its pattern, since the three places read show only the first. The **ledger** (`library/<id>.toc.tsv`) lists the author's divisions only.

Every `library-*.py` script prints its usage and output format with `--help`.

## Steps

1. **Set up the root.** Create `raw/`, `library/`, `scripts/` if absent. Copy this skill's `scripts/*` into `scripts/` when `scripts/library-normalize.py` is missing or differs from the skill's copy. In a git repository, add `library/library.fts5.db*` and `scripts/__pycache__/` to `.gitignore`.
   Done when `python3 scripts/library-check.py library` prints `checked N work(s)`.

2. **Stage the source as received** under `raw/<source>/`, one folder per origin (`raw/gutenberg/`, `raw/publisher-x/`), without editing a byte.
   - A txt file: copy it in and add its row to `raw/<source>/SOURCES.tsv`, tab-separated, under the header `file  title  creator  origin  rights  retrieved` — `origin` is the URL or path it came from, `rights` the source's rights label (`Public domain`, a licence name — the full statement stays in the file), `retrieved` the date it was obtained.
   - A PDF or scan: this skill takes text. Ask the user for a text export and stop for that source.

   Done when every source has an origin, a rights statement, and a retrieval date on record. A source with no rights statement stays in `raw/` with its `rights` cell empty — the normalizer refuses it: report it and ingest the rest.

3. **Normalize.** `python3 scripts/library-normalize.py plaintext raw/<source>/<file>.txt library [--id <short-id>] [--translator <name>] [--date <year first published>]` — give `--id` when the title would make an unwieldy file name. An option holds for that run only: once a work has a rules file, put the date and the other metadata in its `meta` so a rerun keeps them.
   Done when the work prints its summary line: `<id>: N chars · N divisions · depth N · N flagged`. `0 divisions` on a work that has chapters means its headings went unrecognized — step 4 fixes that with a `headings` rule.

4. **Read the result against the source.** For each new work:
   - run `python3 scripts/library-check.py library <id>`;
   - read `library/<id>.ingest.json` (how the text was read — hard-wrapped or not — and what each rule dropped, by its opening words and how many times; a key in the rules file that the normalizer does not know is named there and on the terminal) and `library/<id>.toc.tsv`;
   - open `library/<id>.txt` at three places — the lines between the title and the first division, one division boundary in the middle, the last screen — and compare each with the same place in the raw file;
   - count the divisions against the source's own table of contents, or against its heading lines when it has none. The summary's division count includes volumes, parts, and prefaces.

   Sort every `!` warning, every note, and everything the reading turned up into one of two bins:
   - **Source defect** — the source's own text is wrong: a skipped number, a missing heading, a passage the text repeats, a transcription slip. Leave the text as the source has it and list the defect in the report.
   - **Conversion fault** — the normalizer misread the source: packaging taken for a division or left in the text, a division missed, a run-in heading left in its paragraph, verse flattened into prose, wrong or missing metadata. Fix it with `library/<id>.rules.json` ([rules](#rules-file)) and rerun step 3.

   Done when everything found is binned and each conversion fault is either gone or — when no rule key or flag reaches it — written down as an **open fault** for the report.

5. **Check.** `python3 scripts/library-check.py library` exits 0.

6. **Index and probe.** Run `python3 scripts/library-index.py library`. For each new work copy a distinctive phrase from the start, the middle, and the end of its text and run `python3 scripts/library-search.py library --work <id> "<phrase>"`.
   Done when each probe's first hit is the passage it was copied from, under the right division path.

7. **Report** per work: the summary line, rules written, source defects left in place, open faults. Name every source that stopped at step 2.

## Canonical text

Canonical text is valid CommonMark under a YAML metadata block, so a later Markdown export is a split, not a rewrite. The full format — metadata keys, block and heading rules, division types and ids, ledger columns — is in [FORMAT.md](FORMAT.md). Read it before writing a rules file or judging a ledger.

Three rules decide most cases:

- **Heading text is the author's**, with numerals normalized to Arabic: `CHAPTER II.` → `Chapter 2`, `第一章` → `제1장`.
- **Depth, not unit names, sets the level.** The outermost division is `##` whatever it is called; three levels at most. Text before the first division — a title page, an unheaded preface — stays under the title.
- **Corrections are logged.** The normalizer repairs one transcription slip on its own — a one- or two-syllable heading stranded among numbered headings is rejoined to the paragraph it was cut from — and records each repair in `<id>.ingest.json`.

## Rules file

`library/<id>.rules.json` overrides the normalizer for one work. Step 3 regenerates the canonical text from `raw/` on every run, so a change made anywhere but the rules file is lost.

| Key | Effect |
|---|---|
| `meta: {"date": …, "title": …, "creator": …, "translator": …, "editor": …, "rights": …}` | Set metadata the source states but the normalizer did not pick up (a first-publication year, the title as printed, the translator). The id and file names stay as they are |
| `drop: ["regex", …]` | Drop every paragraph the pattern matches anywhere in its text — a transcriber's note, a caption, a page marker, a printer's mark. A line read as a heading is never dropped by it: use the two keys below |
| `drop_sections: ["regex", …]` | Drop a heading the pattern matches together with everything under it (this key and the next match the heading's own text — `참고`, not `## 참고` — and take every heading that reads so, a rule-made one included), down to the next heading of the same or a higher level (a contributor's parallel translation, an appendix the wiki added) |
| `drop_headings: ["regex", …]` | Remove a heading the packaging added and keep what is under it: the headings beneath move up one level, and text sitting directly under the removed heading joins the division before it — leave the heading in place when that would misfile an unheaded opening |
| `headings: [{"pattern", "level", "inline"}]` | Extra heading patterns, matched against the first line of a paragraph; without `inline` the whole line becomes the heading, so use `inline` with `(?P<h>…)` to shed characters before or after the title. `## Title` lines and unit words (`Chapter 3`, `제3장`, `Preface`) are recognized without a rule; a `## Title` line ranks as 2, `###` as 3. `level` ranks size — 1 volume, 2 part, 3 chapter, 4 section — and the ranks a work actually uses become `##`, `###`, `####` in order. `inline: true` is for a heading run into its paragraph: the whole match is cut from the paragraph and `(?P<h>…)` becomes the heading (a lookahead keeps what follows) |
| `wrapped: true` or `false` | Override how line breaks inside paragraphs are read: `true` joins them as hard-wrapped text, `false` keeps every line as its own paragraph. `ingest.json` says which way the file was read, and a `!` note there (also printed under the summary line) says many blocks hold several lines though no single wrap width was found — a source wrapped at mixed widths: read a few blocks and set `true` if lines break mid-sentence. Joined lines get a space between them, so a source that wraps inside words keeps a stray space there (`빛 을`); that is the source's defect, and searches see through it. `drop` is tested after the join |
| `disable_default_ranks: [4]` | Turn off a built-in heading rank: 1 volume words, 2 part words, 3 chapter words (`Chapter 3`, `제3장`), 4 a bare numeral on its own line. Turn 4 off when the source numbers verses or sections that way, and 3 off when navigation lines repeat the chapter labels (then `drop` removes them as paragraphs); name the real chapters with `headings` |
| `join_number_headings: true` | Join a number heading to the title heading right after it — `제1장` then `인간기념물` becomes `제1장 인간기념물` — for a source that carries a division's number and its title on separate lines. The pair needs no text between them; a front-matter title (`서문`) is never joined. Give the number heading the rank of the title it joins (2 for a `## Title` line), not the rank its unit word suggests |
