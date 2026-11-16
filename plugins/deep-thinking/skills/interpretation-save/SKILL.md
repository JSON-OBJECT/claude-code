---
name: interpretation-save
description: Land and firm up what a reader says about passages in the library as numbered readings under interpretation/. A Stop hook lands every turn that quoted the library by itself (status `auto`); use this skill when the reader settles, marks tentative, retitles, corrects, or takes back part of a reading, or names what it reaches, or when asked to set up a repo for it (a reading room, a second brain over a library).
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <what the reader wants kept>
---

# Interpretation Save

The reader reads; the hooks keep. `interpretation.py hook` (UserPromptSubmit) logs every utterance verbatim and puts the earlier readings it touches in front of you; `interpretation.py land` (Stop) turns each turn whose answer quoted `library/<file>.txt:<line>` into a numbered reading, status `auto`, titled by the reader's words — with the quoted lines when there are any, and a Follows line to the earlier readings the reader's words named. A thought with no passage is a reading too; short chat, commands and memory questions stay in the log; a slash command at the start of an utterance is the reader's instruction to the tool, so `hook` logs only the words after it. No model, under half a second. So nothing waits for the reader to say "save".

Three things land without a skill call:
- **The title.** When the reader talks long, the session runs `python3 -I scripts/interpretation.py title . "<a stretch of the reader's words>"` while answering — the point of what they said, copied verbatim. `land` titles the reading with it only when it occurs character for character in this turn's words; otherwise it picks by rule: a claim of the reader's, else their question, else a request without its request word (`request_tail`, `request_helpers`) — never a bare reaction (`reaction_phrases`).
- **A yes.** When the reader's turn opens with one of their own words for yes (`adopt_phrases`, a whole word among its first `adopt_max_words` words, no not-yet word right after it), `land` adds the first sentences of the previous answer to the reading before as a `Took up (assistant's)` line — a meta line like `Asked`, so it needs no anchors and never passes for the reader's own words. An `[Interpretation]` paragraph still goes in only through `keep --paragraph`, on two quoted lines. A yes with more after it ("yes, but …") also lands as its own reading.
- **A second try.** `brief` sends an answer back once when it runs past `max_chars` (unless this turn's words hold one of `long_ok`, "all of it"), quotes more than `max_quotes` passages, opens with a comparison as fact (`compare_words` in the first sentence with none of `own_marks` or `attribution_marks`), or quotes words that are not in the lines its anchor names. `land` then waits and lands the fixed answer, so a wrong anchor never lands the wrong passage. This skill only changes a reading that has landed: almost always `--to <no>`.

**The hooks come with the plugin.** They run in every project but act only in a reading room: a repo whose library has been indexed by `library-ingest` (`library/library.fts5.db`), or that has an `interpretation/` folder. So in a new repo, ingest the first book and the next session already logs, recalls, and lands; `interpretation/` is created on its first session start. A repo that wires these hooks itself is left alone, so nothing lands twice.

**Vendoring, for a repo that runs without the plugin** (a cloud session that may not carry it): from the repo root run this skill's own copy once —
```
python3 <this skill's folder>/scripts/interpretation.py setup . --autosave
```
It copies itself and the `library-ingest` scripts into `scripts/`, merges the hooks below into `.claude/settings.json`, creates `interpretation/` with a `locale.json` template (English defaults; translate the labels and signal words into the reader's language) and an empty `names.tsv`, adds `.gitignore` entries, and with `--autosave` a Stop hook that commits and pushes the records (a cloud container goes away). Safe to run again. Hooks take effect in the next session.
   Done when it prints `init:` and `python3 scripts/interpretation.py check .` runs.

The hooks, for reference (each Stop hook in its own entry, so each gets the input). `P` stands for `"$CLAUDE_PROJECT_DIR"`:
```
"SessionStart":     python3 -I P/scripts/interpretation.py open P     # desk, the reader's names, where the last session stopped
"UserPromptSubmit": python3 -I P/scripts/interpretation.py hook P     # log the words verbatim, put earlier readings in front of you
"Stop":             python3 -I P/scripts/interpretation.py land P     # the turn becomes a reading
                    python3 -I P/scripts/interpretation.py brief P    # send back once: too long, too many quotes, or a quote its anchor does not hold
```
In a cloud session the container goes away, so add a Stop hook that commits `interpretation/` and `desk.md` and pushes them. Keep the library scripts (`library-search.py`, `library-quote-check.py`) in the repo's `scripts/` next to `interpretation.py`.

**It learns the reader as they talk.** `interpretation/names.tsv` holds the reader's own names for ideas — each with every spelling speech-to-text has given it and the names it was renamed from or to (`name<TAB>variant<TAB>stt|renamed|modeled|name`). Recall searches an utterance under all of them, and landing tags a reading with the name whichever spelling was heard. The list grows three ways: `land` adds a name the moment the reader coins one (the coining phrases are `naming_regex` in `interpretation/locale.json`); you add a misheard spelling or a rename with `python3 scripts/interpretation.py alias . "<name>" "<spelling or old name>" stt|renamed` whenever you corrected one from context or the reader renamed an idea; and every reading tagged with a name adds to what `lexicon` reports. `locale.json` also carries the reader's language: labels, particles, fillers, and the words that mark a thought as firm (`settled_signals`) or not yet (`tentative_signals`), which `land` uses for the status. Take the reader's words for yes, for not-yet and for requests from how they actually talk (transcripts of them, not a textbook): a word like "okay" that mostly hands out a task is not a yes.

A **reading** is one numbered entry: the reader's own words with the moment they said them, and the passages those words are about. You choose which words and which lines; `scripts/interpretation.py keep` copies both — the words from the log of what the reader said, the lines from the library — so nothing in a reading is retyped or reworded.

Run every command from the folder that holds `interpretation/`. If `scripts/interpretation.py` is missing or differs from this skill's copy, copy it from this skill's `scripts/`; `--help` prints every option.

## Steps

1. **Name what is kept.** For each reading the request covers:
   - **the turns** — the stamps (`HH:MM:SS`) of the reader's utterances that carry it. Every utterance is in `interpretation/log/<date>.md` with its stamp; spoken turns often fall in the same minute, so give the seconds. A bare request ("save it") covers what the reader has said since the last keep, except what they took back or said to leave out; what they held back ("not yet") stays held.
   - **the lines** — the anchors (`library/<file>.txt:<line>`) of the passages it is about: the quote blocks already shown, and lines the reader pointed to. Lines the reader says go against the reading are named with `--against`.
   - **the title** — the reader's own phrase: the title they gave, as given; else their sentence that states the reading, shortened only by cutting.
   - **the status** — `tentative` when they say it is not firm yet; `settled` when they firm it up ("lock it in"). A landed reading is `auto` until then.
   - **what it reaches** — their own names for what the reading is about (a concept or project of theirs, their word for a thing in the text), as they said them.
   - **what they took back** — their withdrawn words and their reason, both as they said them.
   - **what to leave out** — any stretch of those turns they said not to write down (`--omit`).

2. **New, or added to.** `python3 scripts/interpretation.py recall . "<the title>"` shows the readings it touches. The reader is firming up, correcting, or adding to one of them — they say so, or name its number → `--to <no>`. Otherwise it is new.

3. **Keep.**
   ```
   python3 scripts/interpretation.py keep . --title "<title>" --from <HH:MM> [--from <HH:MM>] \
     --anchor library/<file>.txt:<line> [--anchor …] [--against library/<file>.txt:<line>] \
     [--status tentative|settled] [--reach "<name>"] [--omit "<stretch>"] \
     [--reject "<words>" --why "<reason>"] [--to <no>] [--drop-anchor <anchor>] [--file <topic>]
   ```
   - A new reading whose lines are all in one work goes to that work's file; lines in several works need `--file <topic>`, a noun from the reader's own words — or the file the reader names.
   - `--to <no>` adds the turns, lines, status, rejections to that reading; `--title` there replaces its heading; `--drop-anchor` removes a line the reader said to take off; `--follows <no>` links it to an earlier reading the reader tied it to; `--asked "<question>"` records a question of the assistant's that the reader left open; `--took "<sentence>"` records a point of the assistant's the reader said yes to.
   - A paragraph of yours goes in only when the reader says to keep it: `--paragraph <file> --paragraph-kind adopted` when they took it as theirs in so many words ("you're right", "change it to that"), `kept` when they said to keep it as yours. A bare "lock that in" right after your own suggestion settles the reader's reading, not yours — when it is ambiguous, the reader's words win.

   Done when the command prints `reading <no> — <file> — new|added to` and exits 0. It has already checked the file and rebuilt the index.

4. **Answer in one line per reading**, in the reader's language: its number, its title, tentative if it is — "Reading 12: 「…」 — tentative." Name a held-back or left-out part in a few words. Then go on with whatever else the reader asked.
