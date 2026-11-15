---
name: interpretation-init
description: Turn a repo into a reading room (사유의 방) — one owner's library they think with by talking, with a second brain that lands and recalls what they say. Use when asked to set up or initialise a reading room or 사유의 방, usually right after init-vault and before the first book.
allowed-tools: Bash, Read, Edit, Write, AskUserQuestion
argument-hint: "[owner name] [room name]"
---

# Interpretation Init

A **reading room** is a repo with one owner: they talk with the books in its library, often by voice on a phone, and every turn lands as their own numbered reading, chained to the last, so the next session picks up where they stopped. The engine is `interpretation-save/scripts/interpretation.py` in this plugin; the books come in through `library-ingest`.

Run everything from the repo root. It works on an empty repo and on one `init-vault` has already set up; nothing there is deleted.

## Steps

1. **Ask two things: whose room it is, and what to call it.** A reading room thinks for exactly one person, and it has a name the owner chose. Ask, in the user's language, unless the argument already said:
   - **the owner** — the name sessions should know their counterpart by;
   - **the room's name** — what the owner wants to call this room. Offer 사유의 방 ("the room of contemplation") as the suggestion, and take any name they give instead, exactly as given.
   Ask once, together, and use the answers as given.
   Done when you hold both names.

2. **Ask where it will run.** If the repo will be opened in cloud sessions (a phone, the web), the records must be committed and pushed after every turn, and the session may run without this plugin. Ask whether it will; default to yes when the user does not know.

3. **Initialise.** From the repo root:
   ```
   python3 <this plugin>/skills/interpretation-save/scripts/interpretation.py setup . --owner "<owner>" --room "<room name>" [--autosave --vendor]
   ```
   `<this plugin>` is two folders above this skill's own folder. Add `--autosave --vendor` for cloud use. It writes:
   - `scripts/` — the engine and the library scripts;
   - `.claude/settings.json` — the hooks (session start, every utterance, every answer) and a deny on web search, merged into what is there;
   - `CLAUDE.md` — a block on top naming the room and its owner, the session guide, and a profile of how a name-coining reader talks, marked `<!-- reading-room:begin -->` … `<!-- reading-room:end -->`; anything already in `CLAUDE.md` (an init-vault protocol) stays below with a note that reading-room sessions do not follow it;
   - `interpretation/` — `locale.json` (English defaults; the first session rewrites it in the owner's language) and an empty `names.tsv`;
   - with `--autosave`, a Stop hook that commits and pushes the records once the repo has a first commit; with `--vendor`, the four skills under `.claude/skills/`;
   - `.gitignore` entries for the indexes.
   Done when it prints `init:`.

4. **Hand over.** Tell the user, in their language and in three lines, calling the room by its name: 「<room name>」 is ready for <owner>; add books with "put this book in the library" (`library-ingest`) — only the books the owner wants; and they may edit `CLAUDE.md` freely outside the marked block (a rerun of setup rewrites only the block). The hooks start with the next session. In a cloud repo, make the first commit and push before the first conversation.
