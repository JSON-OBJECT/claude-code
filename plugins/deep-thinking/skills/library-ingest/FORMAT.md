# Canonical text format

One work = `library/<id>.txt` (canonical text) + `library/<id>.toc.tsv` (ledger) + `library/<id>.ingest.json` (what the normalizer dropped and repaired). Optional `library/<id>.rules.json`.

The division model follows the EPUB 3 Structural Semantics Vocabulary (front matter, body, back matter; volume, part, chapter, subchapter) and the TEI convention that every division carries a type, a number, and a heading. The three stores map onto the OAIS packages: `raw/` is the submission package, `library/` the archival package, an answer with anchors the dissemination package.

## File

- UTF-8, LF, NFC. One paragraph per line, one blank line between blocks.
- Opens with a YAML metadata block, then `# <title>` exactly once.
- Work `id`: the `--id` given at ingest, else the title with a trailing parenthetical dropped and spaces as hyphens.

## Metadata block

Dublin Core names, as EPUB uses them.

| Key | Required | Value |
|---|---|---|
| `title`, `creator` | yes | As the source gives them |
| `translator`, `editor` | no | The Dublin Core contributor, by role. Written only when the work has one |
| `date` | no | Year of first publication — from the source when it states one, else the `--date` flag or the rules file's `meta.date`; a distributor's release date is not it |
| `language` | yes | ISO 639-1 |
| `type` | yes | `book`, `paper`, or `report` |
| `identifier` | yes | The work id |
| `source` | yes | Origin URL or path |
| `rights` | yes | The source's rights label (`Public domain`, a licence name). The full statement stays in `raw/`. A source without one is not ingested |
| `retrieved` | yes | ISO date |
| `structure` | generated | Division types by depth, e.g. `volume > chapter > subchapter` |
| `normalizer` | generated | Script name and version |

## Blocks

| Block | Written as |
|---|---|
| Division heading | `##`, `###`, `####` — by depth |
| Paragraph | One line |
| Scene break (ornament, rule, lone `×` or `*`) | `* * *`. A line of dots is text — a silence or an elision — and stays |
| Verse, song, letter lines (in plain text: short lines indented two spaces or more) | `> ` per line, two trailing spaces on every line but the last |
| Emphasised line that is not a division | `**…**` paragraph |
| Footnote | `[^n]` in the text; `[^n]: …` at the end of the top-level division its mark occurs in; numbered through the work |
| A body line that would parse as Markdown | `#`, `>`, `- `: backslash before the first character. A numbered-list look (`1930. 4. 26.`, a lone `3.`): backslash before the delimiter — `1930\. 4. 26.`. Search and quote-check read through these backslashes |

Dropped: a distributor's header and footer, illustration markers and their captions.

Text before the first division heading belongs to no division: it sits under the title and is indexed with the work title as its path.

## Headings

- Numerals are Arabic: `一`, `一[일]`, `1.`, `I.` → `1`; `一○` and `一〇` → `10`. A line holding only `○` is a scene break.
- A unit keeps its word and gains the number: `第一章[제일장] 少年時代[소년 시대]` → `제1장 少年時代[소년 시대]`; `CHAPTER II.` → `Chapter 2`.
- A title is kept as written, including glosses such as `戀愛講座[연애강좌]`.

## Division types and ids

| Type | Assigned when | Id letter |
|---|---|---|
| `volume` | unit 권 / Volume | `v` |
| `part` | unit 부·편 / Book·Part, or a division whose children all have children | `p` |
| `chapter` | unit 장·회 / Chapter, or the default | `c` |
| `subchapter` | unit 절 / Section, or a child of a chapter | `s` |
| `preface`, `foreword`, `introduction`, `prologue`, `epilogue`, `afterword`, `appendix`, `abstract` | the heading is that word (Korean or English); in plain text such a word alone on a line is taken as a heading | the type word |

An id is letter + two-digit number, joined by dots down the tree: `c14.s03`. The number is the author's when there is one, the position otherwise; 상·중·하 volumes are numbered in the order present. A volume prefix is dropped when chapter numbers are unique across the work. Two siblings with the same number get `x<position>` appended and a ledger note.

## Ledger columns

`id`, `level`, `type`, `n` (the author's number; empty for a division titled without one), `heading`, `original` (the source's string before normalization; for a rule-made inline heading, the captured text), `heading_source` (`authorial` — the source's own heading line; an adapter for a multi-page source may also write `label` or `derived`), `line_start`, `line_end`, `chars`, `parent`, `source_page`, `notes` (numbering defects the normalizer saw: `number skips 3→5`, `duplicate number (c01)`, `numbering starts at 2`).

## Index

`library/library.fts5.db` — SQLite, rebuilt from the canonical texts on every run, never edited.

- `works` — one row per work.
- `divisions` — the ledgers, with each division's full path.
- `passages` — FTS5 (trigram): consecutive paragraphs within one leaf division, about 1,500 characters, with `work_id`, `div_id`, `path`, `line_start`, `line_end`, the file line of each paragraph, and `squeezed` — the text lower-cased with whitespace removed, which is what searches match against.
