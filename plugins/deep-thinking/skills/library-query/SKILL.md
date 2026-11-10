---
name: library-query
description: Answer from the library's canonical texts with verbatim quotes anchored to file and line. Use when the user asks what a work in the library says, where something appears in it, or how works in the library compare.
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <question about works in the library>
---

# Library Query

The library is the only source. Every statement about a work rests on a **verbatim** quote with an **anchor** — `library/<file>.txt:<line>` — that the user can open and check, and what the texts do not say is reported as absent. `library-quote-check.py` verifies the quotes, anchors, and absences; whether each statement is one its quote supports is yours to hold.

Run every command from the library root (the folder holding `library/` and `scripts/`). All searching goes through `scripts/library-search.py`; it searches text and headings, ignores whitespace and letter case, and matches terms of any length. If `library/library.fts5.db` is missing, run the `library-ingest` skill's index step first.

## Steps

1. **Scope.** `python3 scripts/library-search.py library --works` lists each work as `id | title | author | year | language | size | divisions | structure`. Name the works the question is about and pass `--work <id>` from here on — repeated for several works; search the whole library only when the question does.

2. **Build a spelling bundle for each key term** — one term, every way the texts might write it, joined by `|`: Hangul, Hanja, the original script, older orthography, the bare stem of an inflected word. `"대원군|흥선|大院君"`, `"가르치|가르쳐|교육"`. People and places go in as bundles too. Spacing variants are already covered. A one-syllable spelling matches inside other words (`역` in `징역`, `역시`; the verb stem `죽` in `죽이면서`): give a one-syllable name or noun the forms the text would use (`허숭|숭은|숭이`, `정거장|평양역`) — a name of two syllables or more needs no inflected forms, and the one-syllable forms are for a search inside that work (`--work`): across the library `숭이` is `원숭이` —, and a verb its inflected forms (`죽었|죽은|죽음|죽게`).
   Done when each key term of the question has a bundle.

3. **Search.** `python3 scripts/library-search.py library [--work <id>] [--not-work <id>] [--all] [--limit N] "<bundle>" "<bundle>"…`
   - Several bundles match a passage holding any of them; `--all` requires every one somewhere in the same passage (a run of paragraphs, not a sentence). A phrase the text writes with spaces is typed with them (`삼도 통제사`): typed solid it shows as a match across a space. The first output line gives the total, each work's passages and occurrences (works listed by occurrences, most first; a place where two spellings of one bundle overlap — `아편` inside `아편쟁이` — counts once), any spelling that occurs nowhere in the works in scope (under `--work` or `--not-work` that says nothing of the works left out — search those before writing `*`), and any spelling matched only across a space; raise `--limit` (default 8) to see the rest.
   - Each hit is `file:start-end | division path | bundle×N(+M) | @lines | snippet`. `N` counts matches as typed; `+M` counts matches that run across a space in the text (`이혼` inside `단단이 혼이`) and are usually not the word — read before relying on one. `@lines` are the lines inside the passage where a term occurs (the first thirty) — the lines to read and to cite. `--context <chars>` sets the snippet width.
   - A question about a theme: search the theme's own vocabulary with `--all`; when a work's headings are titles, `library-search.py library --toc <id>` shows them with sizes for choosing divisions to read.
   - A broad question about a person or place: raise `--limit` and take hits from early, middle, and late divisions, so the answer follows the work's course.
   - A question about every work but one ("outside the novel named after him"): `--not-work <id>`, repeated, leaves those works out, so the rest are not buried under them.
   - A question of how often or where most: the per-work passages and occurrences on the first line are the figures; report them as search counts, leaving the `+M across a space` out. Count one word with a bundle of its spellings only, not its neighbours (`양귀비` is not a spelling of `아편`); when the question names one spelling and the bundle ranks the works differently (`이혼` alone against `이혼|리혼|離婚`), give both figures. The figures include headings and a Hanja gloss beside its word (`리혼(離婚)` is two), so say so when either is there; when works tie for a rank, name them all and say so. When matches sit inside a longer word (`풍금` in `손풍금`), say how many: search the longer word alone and subtract. Another name for the same person or thing (`보나파르트` for `나폴레옹`) is counted and reported separately, not folded into the figure. A `+M` match that the line shows to be the word itself — a name before `씨`, a word the source split with a stray space (`톨스 토이`) — is counted, and the answer says it was. An answer that is only counts still carries a quote block showing the word in use: the checker passes nothing that rests on no quote and no absence.
   - A question naming a division ("the last chapter"): `--toc <id>` gives its line range; read the division whole. In a work with chapters and sections, "the last chapter" is the last top-level division; say which level you read.
   - **0 hits:** widen each bundle once with spellings it lacks — other scripts and orthographies of the same name, not a shorter piece of it (`청석` for `청석골` only finds `방청석`) — and search again. Still 0 → the term is **absent**; carry the spellings tried into the answer's absence block.
   - **The asked-for word is absent but the widened search finds the thing under another name:** the word goes in an absence block with the spellings that returned nothing; the other name is quoted as found, and the judgement that the two are the same belongs in `[Interpretation]`, said to be your inference.
   Done when every part of the question has lines to read or a recorded absence.

4. **Read.** Open each `@line` you will rely on with the Read tool. One line is one paragraph, often thousands of characters, and paragraphs sit on every other line: `offset` = line − 2 with `limit` 5 shows the paragraph and its neighbours; widen from there. Read enough to know who is speaking and what the sentence answers. A snippet is a pointer; quote only from what you read in the file.
   Done when every line the answer will cite has been read in the file.

5. **Answer** in the user's language, built from these parts in whatever order reads best — the absence block and `[Interpretation]` only when the answer has one:

   ```
   <a sentence or two stating what the text says, in your words>

   > <the quote, copied character for character; … with a space on each side where you skip>
   > — <division path> · library/<file>.txt:<line>

   > ∅ <work id, * or * except id, id>: <spelling> | <spelling> | …

   [Interpretation] <a paragraph that connects works or infers beyond the quoted words, citing at least two anchors inline>

   Coverage: <which hits you read, and how many matched that you did not>
   ```

   - **Quote block**: every statement about what a work says is followed by one; a count taken from the search output stands on the search. The anchor is the line the quote sits on (`:403`). A quote running across source lines takes one `> ` line per source line that holds text — the blank lines between paragraphs are skipped — and a range that starts and ends on those lines (`:5550-5552`).
   - **Absence block**: one line per absent term and per work, listing every spelling of it that returned nothing. `*` is the whole library; `* except 이순신, 꿈하늘` is every work but those — use it when a term is absent from all but a few works, and list only works where the spelling does occur: the checker confirms the rest are empty, not that the listed ones are not. A spelling that occurs only inside another word (`흥선` in `유흥선`) or as a different word of the same spelling (`영채` the gleam of an eye, not the name) is not absent: list that work among the exceptions and quote the line to show what the word is. When a common word turns up in too many passages to read them all, search the forms only the name takes (`炯植|이형식|형식씨`) and say in the Coverage line how many passages went unread. A spelling whose only matches run across a space counts as absent: the checker accepts it and prints a `~` line showing the words as the text has them, with their lines — say in a sentence that it occurs there only as a chance run of syllables. If the `~` line shows the word itself, split by a stray space (`괴 테`) or written as a spaced phrase (`인력거 삯`), it is not absent: take it out of the block and quote the line.
   - **`[Interpretation]`** (`[해석]` in a Korean answer — the checker knows both): the only place for comparison and inference. Its anchors go inline in parentheses — `(library/흙.txt:674)` — at least two different ones, each a line or range a quote block above anchors.
   - **Coverage line** (`읽은 범위:` in a Korean answer): closes the answer, labelled in the user's language — for a division read whole, its line range — so the user knows what the answer does not cover.

6. **Verify.** Write the answer to a scratch file outside the library and run `python3 scripts/library-quote-check.py . < <file>` (`.` is the library root). It checks each quote against its anchored lines and rejects an anchor wider than the quote, re-searches every spelling in an absence block, and holds each `[Interpretation]` anchor to a line already quoted. Fix what it rejects — reread the line and recopy, correct the anchor, or cut the statement — and run it again. It does not check the division path on an anchor line, the Coverage line, or a line number mentioned outside a quote block: those are yours to get right, and a line you did not open is named as unread.
   Done when it exits 0. Send the answer only then.

## Reading a hit

- **Division path** (`애인 > 상권 > 戀愛講座[연애강좌] > 1`) goes on the anchor line as written. A bare number is a division the author numbered without a title. A work with no divisions has only its title as the path.
- **`! …` after a `--toc` row** marks a defect in the source at that division (a skipped number, a missing heading). Say so when the answer depends on where that division begins or ends.
- **A stray space inside a word** (`가까 운`, `숭 은`) is a transcription slip the source carries. Searches see through it; a quote keeps it, because the quote is the text as it stands.
