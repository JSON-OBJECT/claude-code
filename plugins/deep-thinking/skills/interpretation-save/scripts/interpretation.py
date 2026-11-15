#!/usr/bin/env python3
"""interpretation — the reader's own readings: capture, keep, find, check.

HOME is the folder that holds interpretation/, digest/ and desk.md. The library root (the folder that holds
library/) is HOME itself when it has a library/ folder, else the path in HOME/interpretation/library-root,
else --library <root>.

  interpretation.py said   <home> [--at "YYYY-MM-DD HH:MM"] < utterance      log one utterance of the reader
  interpretation.py hook   <home> < hook-input.json                          said + recall, for a UserPromptSubmit hook
  interpretation.py recall <home> "<utterance>" [--limit N]                  earlier readings an utterance touches
  interpretation.py keep   <home> --title T --from STAMP [--from STAMP …] --anchor library/<f>.txt:<n>[-<m>] …
                           [--file <topic>] [--to <no>] [--status tentative|settled] [--reach NAME …]
                           [--omit TEXT …] [--reject TEXT --why TEXT …] [--drop-anchor A …] [--against ANCHOR …]
                           [--paragraph FILE --paragraph-kind adopted|kept] [--follows <no> …] [--asked TEXT]
  interpretation.py find   <home> [--limit N] [--tentative] [--rejected] [--reach NAME] ["<a|b>" …]
  interpretation.py list   <home> [--work <id>] [--tentative]
  interpretation.py show   <home> <no> [<no> …]                              entries without their quotes
  interpretation.py check  <home> [interpretation/<file>.md …]               exit 1 on any failure
  interpretation.py index  <home>                                            rebuild interpretation/interpretation.fts5.db
  interpretation.py desk   <home> show | task "<words>" | done <n> | rule "<words>"
  interpretation.py land   <home> < stop-hook-input.json                     Stop hook: land this turn as a reading (status auto)
  interpretation.py alias  <home> <name> <variant> [stt|renamed|modeled]   a spelling of one of the reader's names
  interpretation.py lexicon <home> [--limit N]                              the reader's names, as they last used them
  interpretation.py setup  <home> --owner NAME [--room NAME] [--autosave] [--vendor]   a reading room for one owner, under its own name
  interpretation.py auto   SessionStart|UserPromptSubmit|Stop < hook-input   the plugin's hooks: act only in a reading room
  interpretation.py open   <home>                                            SessionStart: desk, names, where the last session stopped
  interpretation.py brief  <home> < stop-hook-input.json                     Stop: send a too-long answer back once (max_quotes)
  interpretation.py pages  <home>                                            digest pages due: names, works, their readings
  interpretation.py material <home> --reach NAME | --work ID | --all         what a digest page is written from
  interpretation.py digest-check <home>                                       exit 1 on any failure

DIGEST — digest/<name>.md: the assistant's page gathering what the reader has said about one idea or work.
  Every "- " bullet ends with the readings it rests on, "(12)" or "(3, 12)". Words inside 「」 in a bullet
  are the reader's and must occur, character for character, in a reading the bullet cites.
  A name's readings: every reading whose Reaches holds the name, plus every reading in interpretation/<name>.md
  when that file is a topic file (not a work). pages, material and digest-check all count this one way.
  A page is due for a name with three readings or more; a work's page only when asked for by name.
  digest-check also fails: a tentative reading under Settled, a tentative reading under Where it stands
  without its tentative mark in the bullet, a ### sub-heading that is not the reader's words or a name, and
  a page that leaves out a reading of its name.
LOG — interpretation/log/<date>.md, one line per utterance: "- (HH:MM) 「…」", written by said/hook, never edited.
ENTRY — "## <no> · <heading>" in interpretation/<work or topic>/<YYYY-MM>.md (a new file each month, so no file
  grows without bound). <no> runs across all files and never changes; say "reading 12".
  - **Reader (stamp)**: 「…」        the reader's words in one turn, copied from the log by keep
  - **Status (stamp)**: tentative    or settled. Absent means settled.
  - **Reaches**: a, b                 the reader's own names for what the reading is about
  - **Rejected (stamp)**: 「…」 — 「…」  what the reader took back, and why
  - **Against**: anchor, anchor       the quoted lines the reader said go against the reading
  quote blocks                        copied from the library by keep, one per anchor
  [Interpretation] (… stamp …) …      a paragraph of the assistant's, adopted or only kept
LOCALE — interpretation/locale.json (optional) renames every label, status word and page heading into the
  reader's language, and gives the particles and suffixes recall strips from words. English always parses too.
  Keys: see DEFAULT_LOCALE below.

keep   — writes or adds to one entry and never asks the model to copy text: reader lines come from the log
         by their stamps (HH:MM of today, or "YYYY-MM-DD HH:MM"), quotes come from the library by their
         anchors. Without --to it makes a new entry: every anchor in one work → interpretation/<work id>.md,
         else --file <topic> is required. With --to <no> it adds reader lines, anchors, a status, a new
         title, rejections to that entry. --omit cuts a stretch of the reader's words, leaving " … ".
         Then it checks the file and rebuilds the index. Prints the entry number.
recall — the entries and unkept log lines an utterance touches, best first, a line or two each. Words of three
         letters or more go through the FTS5 trigram index (BM25, heading and reaches weighted); shorter
         words are matched as substrings.
find   — entries holding any spelling of every bundle (whitespace and case ignored, any length); with no
         bundle, every entry the flags select. no | file | first said | status | heading
check  — every entry: a number, a stamped reader line, each quote (when it has any) against its anchored lines,
         a stamped parenthesis opening every [Interpretation] paragraph, a known status word.
"""
import pathlib, re, subprocess, sys, unicodedata

ANCHOR = re.compile(r"library/([^\s:|)\]]+)\.txt:(\d+)(?:-(\d+))?")
D = r"\((\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}(?::\d{2})?)?)\)"
DEFAULT_LOCALE = {
    "reader": "Reader", "status": "Status", "reaches": "Reaches", "rejected": "Rejected", "against": "Against",
    "interpretation": "Interpretation", "tentative": "tentative", "settled": "settled", "auto": "auto",
    "settled_heads": ["settled"], "stands_heads": ["where it stands"], "tentative_mark": "(tentative)",
    "adopted": "the assistant's reading — adopted by the reader on {date}",
    "kept": "the assistant's reading — the reader said to keep it, not adopted, on {date}",
    "desc_topic": "Readings the reader linked across works under \"{name}\"",
    "desc_work": "The reader's readings of passages in {title}",
    "desc_desk": "Tasks the reader gave that are not done yet, and what they said about how to work",
    "multi_work_file": "across-works",
    "particles": "", "suffixes": [], "sentence_end": "",
    "title_drop_leading": ["uh", "um", "so", "well", "okay"],
    "follows": "Follows", "thoughts_file": "thoughts", "min_chars": 20, "title_chars": 40,
    "settled_signals": [], "tentative_signals": [], "tail_drop": [],
    "memory_phrases": ["what did i say", "where were we", "did i say"],
    "max_quotes": 0, "brief_reason": "This answer quotes {n} passages; the reader reads on a phone. Rewrite it with at most {max} quote blocks, first sentence the answer.",
    "open_desk": "Desk — the reader's standing rules (follow them from the first answer) and open tasks",
    "open_lexicon": "The reader's names — speak to them in these names and words",
    "open_last": "Where the last session stopped — offer in one sentence to go on from here; the Asked line is the assistant's question, not the reader's thought",
    "naming_regex": ["(?:call (?:it|this|that) |named? (?:it|this) )([\\w-]+(?: [\\w-]+){0,3})"],
    "naming_drop": ["the", "a", "an", "my", "our", "this", "that"],
    "stopwords": ["the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "is", "are", "was", "it", "this", "that",
                  "he", "she", "they", "we", "you", "i", "me", "my", "his", "her", "as", "if", "not", "be", "so", "for", "with"],
    "asked": "Asked", "chat_phrases": ["got to go", "see you", "talk later", "goodnight", "i'm tired"], "chat_max_chars": 60,
}
L = dict(DEFAULT_LOCALE)


def setup(home):
    """Load interpretation/locale.json over the English defaults and build the line patterns."""
    import json
    global L, READER, READER_ANY, REJECT, REJECT_ANY, REACH, ADOPT, ADOPT_OK, STATUS, STATUS_ANY, AGAINST, FOLLOWS, ASKED, TENT, SETT, AUTO
    f = home / "interpretation" / "locale.json"
    L = dict(DEFAULT_LOCALE, **(json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}))
    alt = lambda k: "(?:" + "|".join(re.escape(x) for x in dict.fromkeys([DEFAULT_LOCALE[k], L[k]])) + ")"
    READER = re.compile(r"^- \*\*" + alt("reader") + " " + D + r"\*\*:\s*(\S.*)$")
    READER_ANY = re.compile(r"^- \*\*" + alt("reader") + r"(?:\s|\*)")
    REJECT = re.compile(r"^- \*\*" + alt("rejected") + " " + D + r"\*\*:\s*(\S.*)$")
    REJECT_ANY = re.compile(r"^- \*\*" + alt("rejected") + r"(?:\s|\*)")
    REACH = re.compile(r"^- \*\*" + alt("reaches") + r"\*\*:\s*(\S.*)$")
    AGAINST = re.compile(r"^- \*\*" + alt("against") + r"\*\*:\s*(.*)$")
    FOLLOWS = re.compile(r"^- \*\*" + alt("follows") + r"\*\*:\s*(.*)$")
    ASKED = re.compile(r"^- \*\*" + alt("asked") + " " + D + r"\*\*:\s*(\S.*)$")
    ADOPT = re.compile(r"^\[" + alt("interpretation") + r"\]")
    ADOPT_OK = re.compile(r"^\[" + alt("interpretation") + r"\] \([^)]*\d{4}-\d{2}-\d{2}[^)]*\)")
    STATUS = re.compile(r"^- \*\*" + alt("status") + " " + D + r"\*\*:\s*(\S+)\s*$")
    STATUS_ANY = re.compile(r"^- \*\*" + alt("status") + r"(?:\s|\*)")
    TENT, SETT, AUTO = (("tentative", L["tentative"]), ("settled", L["settled"]), ("auto", L["auto"]))


NO = re.compile(r"^(\d+) · (.*)$")


def lib_root(home, rest=()):
    if "--library" in rest: return pathlib.Path(rest[list(rest).index("--library") + 1])
    f = home / "interpretation" / "library-root"
    if (home / "library").is_dir(): return home
    if f.exists(): return pathlib.Path(f.read_text().strip())
    return home


def squeeze(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", s)).lower()


def load(root, only=None):
    """[(rel, text, topic, description, [entry dict])] for interpretation/*.md."""
    folder = root / "interpretation"
    out = []
    for f in (sorted(x for x in folder.rglob("*.md") if "log" not in x.relative_to(folder).parts[:-1]) if folder.is_dir() else []):
        rel = f.relative_to(root).as_posix()
        if only and rel not in only:
            continue
        text = f.read_text(encoding="utf-8")
        topic = (re.search(r"(?m)^# (\S.*)$", text) or [None, ""])[1]
        desc = (re.search(r'(?m)^description:\s*"?(.*?)"?\s*$', text) or [None, ""])[1]
        ents, cur = [], None
        for i, line in enumerate(text.splitlines(), 1):
            if line.startswith("## "):
                h = line[3:].strip(); m = NO.match(h)
                cur = {"file": rel, "line": i, "head": m[2] if m else h, "no": int(m[1]) if m else None, "body": [], "reader": [],
                       "reach": [], "reject": [], "adopt": [], "undated": [], "status": [], "follows": [], "asked": []}
                ents.append(cur)
            elif cur is not None:
                cur["body"].append(line)
                m = READER.match(line)
                if m: cur["reader"].append((m[1], m[2]))
                elif READER_ANY.match(line): cur["undated"].append(line)
                m = REJECT.match(line)
                if m: cur["reject"].append((m[1], m[2]))
                elif REJECT_ANY.match(line): cur["undated"].append(line)
                m = REACH.match(line)
                if m: cur["reach"] += [x.strip() for x in m[1].split(",") if x.strip()]
                m = FOLLOWS.match(line)
                if m: cur["follows"] += [int(x) for x in re.findall(r"\d+", m[1])]
                m = ASKED.match(line)
                if m: cur["asked"].append((m[1], m[2]))
                if ADOPT.match(line): cur["adopt"].append(line)
                m = STATUS.match(line)
                if m: cur["status"].append((m[1], m[2]))
                elif STATUS_ANY.match(line): cur["undated"].append(line)
        for e in ents:
            body = "\n".join(e["body"])
            e["anchors"] = [m.group(0) for m in ANCHOR.finditer(body) if m.group(0)]
            e["works"] = sorted({m.group(1) for m in ANCHOR.finditer(body)})
            stamps = [d for d, _ in e["reader"]] + [d for d, _ in e["reject"]] + [d for d, _ in e["status"]]
            e["date"] = max(stamps or [""])
            e["first"] = min([d for d, _ in e["reader"]] or [""])
            e["tent"] = bool(e["status"]) and max(e["status"])[1] in TENT
            e["auto"] = bool(e["status"]) and max(e["status"])[1] in AUTO
        out.append((rel, text, topic, desc, ents))
    return out


def by_latest(ents):
    return sorted(ents, key=lambda e: (e["date"], e["file"], e["line"]), reverse=True)


def line_of(e):
    return f"{e['no'] or '—'} | {e['file']} | {e['date'] or '—'} | {', '.join(e['works'])} | {'~ ' if e['tent'] else ''}{e['head']}"


def opt(rest, name, default=None):
    return rest[rest.index(name) + 1] if name in rest and rest.index(name) + 1 < len(rest) else default


def check(root, rest):
    only = {a for a in rest if a.endswith(".md")}
    here = pathlib.Path(__file__).resolve().parent
    checker = next((c for c in (here / "library-quote-check.py", lib_root(root, rest) / "scripts" / "library-quote-check.py",
                                here.parent.parent / "library-ingest" / "scripts" / "library-quote-check.py") if c.exists()), None)
    if checker is None: print("! library-quote-check.py not found (next to this script, in <library>/scripts/, or the library-ingest skill) — quotes not verified")
    bad, n_e, files = [], 0, load(root, only or None)
    for miss in sorted(only - {f[0] for f in files}):
        bad.append(f"{miss}: no such file under interpretation/")
    for rel, text, topic, desc, ents in files:
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            bad.append(f"{rel}: no metadata block")
        if len(re.findall(r"(?m)^# \S", text)) != 1:
            bad.append(f"{rel}: needs exactly one '# <topic>' line")
        if not desc:
            bad.append(f"{rel}: no description in the metadata block")
        if not ents:
            bad.append(f"{rel}: no entry")
        if len(text.encode()) > 40000:
            print(f"! {rel}: {len(text.encode()):,} bytes — recall reads it by --recent; split by part or volume when it keeps growing")
        seen = set()
        for e in ents:
            where = f"{rel}:{e['line']} 「{e['head'][:30]}」"
            n_e += 1
            if e["no"] is None: bad.append(f"{where}: heading has no number — '## <no> · <heading>'")
            if e["head"] in seen: bad.append(f"{where}: heading repeated in this file")
            seen.add(e["head"])
            if not e["reader"]: bad.append(f"{where}: no stamped reader line")
            for u in e["undated"]: bad.append(f"{where}: line without a (YYYY-MM-DD HH:MM) stamp — {u[:40]}")
            for a in e["adopt"]:
                if not ADOPT_OK.match(a): bad.append(f"{where}: [Interpretation] paragraph does not open with a stamped parenthesis saying adopted or kept")
            for d, w in e["status"]:
                if w not in TENT + SETT + AUTO: bad.append(f"{where}: status '{w}' is not one of {', '.join(TENT + SETT + AUTO)}")
            if not e["anchors"] or checker is None: continue  # a thought of the reader's with no passage is a reading too
            r = subprocess.run([sys.executable, "-I", str(checker), str(lib_root(root, rest))], input="\n".join(e["body"]),
                               capture_output=True, text=True)
            if r.returncode != 0:
                bad += [f"{where}: {l}" for l in (r.stdout + r.stderr).strip().splitlines()]
    for b in bad: print(b)
    if not bad: print(f"interpretation check ok — {len(files)} file(s), {n_e} entr{'y' if n_e == 1 else 'ies'}")
    sys.exit(1 if bad else 0)


def parse_now(v):
    import datetime
    return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S" if v.count(":") == 2 else "%Y-%m-%d %H:%M")


def desk(root, rest):
    """desk.md — open tasks and working rules, in the reader's words."""
    import datetime, os
    f = root / "desk.md"; now = datetime.datetime.now()
    if os.environ.get("INTERPRETATION_NOW"):          # a fixed clock, for tests: "YYYY-MM-DD HH:MM"
        now = parse_now(os.environ["INTERPRETATION_NOW"])
    head = ('---\ntype: note\ndescription: "' + L["desc_desk"] + '"\n'
            'timestamp: {ts}\nhuman_reviewed: true\ntags: [desk]\n---\n\n# Desk\n\n## Tasks\n\n## Rules\n')
    text = f.read_text(encoding="utf-8") if f.exists() else head.format(ts=now.astimezone().isoformat(timespec="seconds"))
    lines = text.split("\n")
    opens = [i for i, l in enumerate(lines) if l.startswith("- [ ] ")]
    cmd = rest[0] if rest else "show"
    stamp = now.strftime("%Y-%m-%d %H:%M")
    if cmd == "show":
        print(f"# {len(opens)} open task(s)")
        for n, i in enumerate(opens, 1): print(f"{n} | {lines[i][6:]}")
        rules = [l[2:] for l in lines[lines.index("## Rules"):] if l.startswith("- ")] if "## Rules" in lines else []
        print(f"# {len(rules)} rule(s)")
        for r in rules: print(f"- {r}")
        sys.exit(0)
    if cmd in ("task", "rule") and len(rest) > 1:
        at = lines.index("## Rules") if cmd == "task" else len(lines)
        while at > 0 and lines[at - 1] == "": at -= 1
        new = (f"- [ ] ({stamp}) 「{rest[1]}」" if cmd == "task" else f"- ({stamp}) 「{rest[1]}」")
        lines[at:at] = [new] if lines[at - 1].startswith("- ") else ["", new]
        if cmd == "task": lines[at + (0 if lines[at] == new else 1) + 1:at + (0 if lines[at] == new else 1) + 1] = [""] if lines[at + (1 if lines[at] != new else 0) + 1:][:1] != [""] else []
    elif cmd == "done" and len(rest) > 1 and rest[1].isdigit() and 0 < int(rest[1]) <= len(opens):
        i = opens[int(rest[1]) - 1]; lines[i] = "- [x] " + lines[i][6:] + f" — done ({stamp})"
    else:
        print('desk: show | task "<words>" | done <n> | rule "<words>"'); sys.exit(2)
    text = "\n".join(lines)
    text = re.sub(r"(?m)^timestamp: .*$", "timestamp: " + now.astimezone().isoformat(timespec="seconds"), text, count=1)
    f.write_text(re.sub(r"\n{3,}", "\n\n", text).rstrip("\n") + "\n", encoding="utf-8")
    print(f"desk: {cmd} recorded ({stamp})"); sys.exit(0)


LOGLINE = re.compile(r"^- \((\d{2}:\d{2}(?::\d{2})?)\) 「(.*)」$")


def now_stamp(rest=()):
    import datetime, os
    v = opt(list(rest), "--at") or os.environ.get("INTERPRETATION_NOW")
    return v or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      # seconds: spoken turns come less than a minute apart


def log_said(home, text, rest=()):
    stamp = now_stamp(rest); day, hm = stamp.split(" ")
    text = re.sub(r"\s*\n\s*", " ", unicodedata.normalize("NFC", text)).replace("**", "").strip()
    if not text: return stamp
    d = home / "interpretation" / "log"; d.mkdir(parents=True, exist_ok=True)
    with open(d / f"{day}.md", "a", encoding="utf-8") as f: f.write(f"- ({hm}) 「{text}」\n")
    return stamp


def log_lines(home):
    """[(stamp, text)] from interpretation/log/*.md, oldest first."""
    out = []
    d = home / "interpretation" / "log"
    for f in (sorted(d.glob("*.md")) if d.is_dir() else []):
        for l in f.read_text(encoding="utf-8").splitlines():
            m = LOGLINE.match(l)
            if m: out.append((f"{f.stem} {m[1]}", m[2]))
    return out


def all_entries(home):
    return [e for f in load(home) for e in f[4]]


def build_index(home):
    import sqlite3
    db = home / "interpretation" / "interpretation.fts5.db"
    if db.exists(): db.unlink()
    c = sqlite3.connect(db)
    c.execute("create virtual table rows using fts5(kind unindexed, ref unindexed, stamp unindexed, heading, reaches, said, rest, tokenize='trigram')")
    ents = all_entries(home); kept = set()
    for e in ents:
        for d, t in e["reader"]: kept.add((d, squeeze(t)[:40]))
        c.execute("insert into rows values('entry',?,?,?,?,?,?)", (str(e["no"]), e["first"], e["head"], ", ".join(e["reach"]),
                  " ".join(t for _, t in e["reader"]), " ".join(t for _, t in e["reject"]) + " " + " ".join(e["adopt"]) + " "
                  + " ".join(l[4:] for l in e["body"] if l.startswith("> — ")) + " " + " ".join(t for _, t in e["asked"])))
    for stamp, text in log_lines(home):
        if (stamp, squeeze("「" + text)[:40]) in kept or (stamp, squeeze(text)[:40]) in kept: continue
        if any(d == stamp for e in ents for d, _ in e["reader"]): continue
        c.execute("insert into rows values('said',?,?,?,?,?,?)", (stamp, stamp, "", "", text, ""))
    c.commit(); c.close()
    return len(ents)


def names_of(home):
    """interpretation/names.tsv — one line per spelling: name <TAB> variant <TAB> kind (stt | renamed | modeled).
    A name the reader coined, every way speech-to-text has written it, and the names it was renamed from or to."""
    f = home / "interpretation" / "names.tsv"; out = []
    for l in (f.read_text(encoding="utf-8").splitlines() if f.exists() else []):
        x = [c.strip() for c in l.split("\t")]
        if len(x) >= 2 and x[0] and x[1] and not l.startswith("#"): out.append((x[0], x[1], x[2] if len(x) > 2 else "stt"))
    return out


def names_in(home, text, known=()):
    """The reader's names an utterance carries, spaces ignored, longest spelling first; a variant counts as its name.
    Returns (names, lineage): lineage adds the names each one was renamed from or to."""
    rows = names_of(home); flat = squeeze(text); found = []
    spell = [(n, n) for n in set(known) | {r[0] for r in rows}] + [(r[1], r[0]) for r in rows]
    for sp, nm in sorted(spell, key=lambda x: -len(squeeze(x[0]))):
        k = squeeze(sp)
        if k and k in flat:
            flat = flat.replace(k, " ")
            if nm not in found: found.append(nm)
    line = set(found)
    for _ in range(3):                                  # an idea renamed twice is found under every name: follow renames both ways
        line |= {r[1] for r in rows if r[2] == "renamed" and r[0] in line} | {r[0] for r in rows if r[2] == "renamed" and r[1] in line}
    return found, sorted(line - set(found))


def alias(home, rest):
    if len(rest) < 2: print("alias: <name> <variant> [stt|renamed|modeled|name]"); sys.exit(2)
    kind = rest[2] if len(rest) > 2 else "stt"
    if kind not in ("stt", "renamed", "modeled", "name"): sys.exit("alias: kind is name, stt, renamed or modeled")
    f = home / "interpretation" / "names.tsv"
    if any(r[0] == rest[0] and squeeze(r[1]) == squeeze(rest[1]) for r in names_of(home)): print("alias: already there"); sys.exit(0)
    with open(f, "a", encoding="utf-8") as h: h.write(f"{rest[0]}\t{rest[1]}\t{kind}\n")
    build_index(home); print(f"alias: {rest[1]} → {rest[0]} ({kind})"); sys.exit(0)


def terms_of(text):
    out = []
    part, suf, stop = L["particles"], tuple(L["suffixes"]), {x.lower() for x in L.get("stopwords", [])}
    for w in re.findall(r"\w+", unicodedata.normalize("NFC", text)):
        for v in {w, w.rstrip(part) if part else w} | ({w[:-len(x)] for x in suf if len(w) > len(x) + 1 and w.endswith(x)}):
            if len(v) >= 2 and v not in out and v.lower() not in stop: out.append(v)
    return out


def recall(home, text, limit=4):
    import sqlite3, math
    db = home / "interpretation" / "interpretation.fts5.db"
    if not db.exists(): build_index(home)
    c = sqlite3.connect(db); n = c.execute("select count(*) from rows").fetchone()[0] or 1
    score, why, strong = {}, {}, set()
    known = {r for (x,) in c.execute("select reaches from rows where kind='entry'") for r in x.split(", ") if r}
    found, lineage = names_in(home, text, known)
    expanded = set(found + lineage)
    text = text + " " + " ".join(found + lineage)        # a misheard spelling said, the name searched; a renamed idea under every name
    for t in terms_of(text):
        if len(t) >= 3:
            q = '"' + t.replace('"', '""') + '"'
            hits = c.execute("select rowid, -bm25(rows, 0, 0, 0, 6.0, 5.0, 2.0, 1.0) from rows where rows match ?", (q,)).fetchall()
        else:
            cols = "heading||' '||reaches||' '||said" + ("||' '||rest" if t in expanded else "")
            hits = [(r, 1.0) for (r,) in c.execute(f"select rowid from rows where instr({cols}, ?) > 0", (t,))]
        named = {r for (r,) in c.execute("select rowid from rows where kind='entry' and instr(', '||reaches||',', ?) > 0", (", " + t + ",",))}
        if t in expanded:                                # a name from the names list, under any spelling: as strong as a Reaches hit
            named |= {r for r, _ in hits if c.execute("select kind from rows where rowid=?", (r,)).fetchone()[0] == "entry"}
        for r in named:                                  # the reader's own name for an idea, said again: the strongest signal
            score[r] = score.get(r, 0) + 8; why.setdefault(r, []).append(t); strong.add(r)
        hits = [(r, b) for r, b in hits if r not in named]
        if not hits or len(hits) > max(3, n * 0.5): continue                # a word in half the rows says nothing
        idf = math.log(1 + n / len(hits))
        for r, b in hits:
            score[r] = score.get(r, 0) + idf * (1 + min(b, 3)); why.setdefault(r, []).append(t)
            if c.execute("select instr(heading||' '||reaches, ?) from rows where rowid=?", (t, r)).fetchone()[0]: strong.add(r)
    out = []
    def stems(ws):                       # a word and the same word with a particle are one word
        out = []
        for w in sorted(ws, key=len):
            if not any(w.startswith(o) for o in out): out.append(w)
        return out
    keep_rows = {r: sc for r, sc in score.items() if r in strong or len(stems(why[r])) >= 2}
    seen = set()
    rows = {r: c.execute("select kind, ref, stamp, heading, reaches, said from rows where rowid=?", (r,)).fetchone() for r in keep_rows}
    for r, sc in sorted(keep_rows.items(), key=lambda x: -(x[1] * (2 if rows[x[0]][0] == "entry" else 1))):   # a kept reading outranks a raw line
        kind, ref, stamp, head, reach, saidtxt = rows[r]
        if squeeze(saidtxt) == squeeze(text) or squeeze(saidtxt) in seen: continue      # the same words again say nothing new
        seen.add(squeeze(saidtxt))
        if len(out) >= limit: break
        k = min([saidtxt.find(w) for w in why[r] if saidtxt.find(w) >= 0] or [0])
        snip = ("…" if k > 50 else "") + saidtxt[max(0, k - 50):k + 110] + ("…" if len(saidtxt) > k + 110 else "")
        out.append((kind, ref, stamp, head, snip, why[r], r in strong))
    c.close()
    return out


def print_recall(home, text, limit=4):
    hits = recall(home, text, limit)
    if not hits: return []
    ents = {str(e["no"]): e for e in all_entries(home)}
    print("Earlier words of the reader that this utterance touches (their own, with when they said them):")
    for kind, ref, stamp, head, snip, why, _ in hits:
        if kind == "entry":
            e = ents.get(ref); st = " · tentative" if e and e["tent"] else ""
            print(f"- reading {ref} ({stamp}{st}) 「{head}」 — {snip}  [hit: {', '.join(why)}]")
        else:
            print(f"- said {stamp}, not kept — {snip}  [hit: {', '.join(why)}]")
    return hits


def copy_quote(lib, anchor):
    """A quote block for an anchor, copied from the canonical text; the division path comes from the ledger."""
    m = ANCHOR.fullmatch(anchor)
    if not m: sys.exit(f"keep: bad anchor {anchor}")
    f = lib / "library" / f"{m[1]}.txt"
    if not f.exists(): sys.exit(f"keep: no such work file {f}")
    L = f.read_text(encoding="utf-8").split("\n"); a = int(m[2]); b = int(m[3] or m[2])
    got = [L[i - 1] for i in range(a, b + 1) if 0 < i <= len(L) and L[i - 1].strip()]
    if not got or not L[a - 1].strip() or not L[b - 1].strip(): sys.exit(f"keep: {anchor} starts or ends on a blank line")
    path = m[1]
    toc = lib / "library" / f"{m[1]}.toc.tsv"
    if toc.exists():
        rows = [r.split("\t") for r in toc.read_text(encoding="utf-8").splitlines()]
        if rows:
            h = {k: i for i, k in enumerate(rows[0])}
            byid = {r[h["id"]]: r for r in rows[1:] if len(r) > h["line_end"]}
            best = None
            for r in byid.values():
                try:
                    if int(r[h["line_start"]]) <= a <= int(r[h["line_end"]]) and (best is None or int(r[h["level"]]) > int(best[h["level"]])): best = r
                except ValueError: pass
            names = []
            while best:
                names.append(best[h["heading"]]); best = byid.get(best[h["parent"]]) if best[h["parent"]] else None
            title = next((l[2:].strip() for l in L if l.startswith("# ")), m[1])
            path = " > ".join([title] + names[::-1])
    return "\n".join(["> " + l for l in got] + [f"> — {path} · {anchor}"])


def multi(rest, name):
    return [rest[i + 1] for i, x in enumerate(rest) if x == name and i + 1 < len(rest)]


def keep(home, rest):
    import datetime
    lib = lib_root(home, rest); stamp_now = now_stamp(rest); today = stamp_now.split(" ")[0]
    title, to, topic = opt(rest, "--title"), opt(rest, "--to"), opt(rest, "--file")
    froms, anchors, omits = multi(rest, "--from"), multi(rest, "--anchor") + multi(rest, "--against"), multi(rest, "--omit")
    reaches, drops, follows, asked = multi(rest, "--reach"), multi(rest, "--drop-anchor"), multi(rest, "--follows"), opt(rest, "--asked")
    against = multi(rest, "--against"); AG = AGAINST
    rej, why = multi(rest, "--reject"), multi(rest, "--why")
    status = opt(rest, "--status"); para, pkind = opt(rest, "--paragraph"), opt(rest, "--paragraph-kind")
    lab = {"r": L["reader"], "s": L["status"], "re": L["reaches"], "x": L["rejected"], "ag": L["against"]}
    if status and status not in ("tentative", "settled", "auto"): sys.exit("keep: --status tentative|settled|auto")
    logs = dict(log_lines(home)); rl = []
    for f in froms:
        st = f if " " in f else f"{today} {f}"
        if st not in logs:
            near = [k for k in logs if k.startswith(st + ":")]
            if len(near) == 1: st = near[0]
            elif near: sys.exit(f"keep: {len(near)} utterances at {st} — give the seconds: " + ", ".join(k.split(' ')[1] for k in near))
            else: sys.exit(f"keep: no utterance logged at {st} — `said` it first, or check the stamp")
        t = logs[st]
        for o in omits:
            if o in t: t = re.sub(r"\s*…\s*…\s*", " … ", t.replace(o, " … ")).strip()
        rl.append(f"- **{lab['r']} ({st})**: 「{t}」")
    quotes = [copy_quote(lib, a) for a in anchors]
    works = sorted({ANCHOR.fullmatch(a)[1] for a in anchors})
    ents = all_entries(home)
    sline = f"- **{lab['s']} ({stamp_now})**: {L[status]}" if status else None
    rlines = [f"- **{lab['x']} ({stamp_now})**: 「{r}」 — 「{why[i] if i < len(why) else ''}」" for i, r in enumerate(rej)]
    ptext = None
    if para:
        body = ADOPT.sub("", pathlib.Path(para).read_text(encoding="utf-8").strip().replace("\n", " ")).strip()
        body = re.sub(r"^\([^)]*\)\s*", "", body)
        mark = L["adopted" if pkind == "adopted" else "kept"].format(date=today)
        ptext = f"[{L['interpretation']}] ({mark}) {body}"
    if to:
        e = next((x for x in ents if str(x["no"]) == to), None)
        if not e: sys.exit(f"keep: no reading {to}")
        f = home / e["file"]; FL = f.read_text(encoding="utf-8").split("\n")
        a = e["line"] - 1; b = next((i for i in range(a + 1, len(FL)) if FL[i].startswith("## ")), len(FL))
        blk = FL[a:b]
        if title: blk[0] = f"## {to} · {title}"
        meta_end = max([i for i, l in enumerate(blk) if l.startswith("- **")] or [1])
        last_reader = max([i for i, l in enumerate(blk) if READER_ANY.match(l)] or [1])
        blk[last_reader + 1:last_reader + 1] = rl
        if sline:
            blk = [l for l in blk if not STATUS_ANY.match(l)]
            lr = max(i for i, l in enumerate(blk) if READER_ANY.match(l)); blk[lr + 1:lr + 1] = [sline]
        me = max(i for i, l in enumerate(blk) if l.startswith("- **"))
        blk[me + 1:me + 1] = rlines
        if reaches:
            have = e["reach"] + [r for r in reaches if r not in e["reach"]]
            blk = [l for l in blk if not REACH.match(l)]
            me = max(i for i, l in enumerate(blk) if l.startswith("- **")); 
            ins = next((i for i, l in enumerate(blk) if STATUS_ANY.match(l)), max(i for i, l in enumerate(blk) if READER_ANY.match(l)))
            blk[ins + 1:ins + 1] = [f"- **{lab['re']}**: {', '.join(have)}"]
        if against:
            old = [x.strip() for l in blk for m in [AG.match(l)] if m for x in m[1].split(",") if x.strip()]
            blk = [l for l in blk if not AG.match(l)]
            me = max(i for i, l in enumerate(blk) if l.startswith("- **"))
            blk[me + 1:me + 1] = [f"- **{lab['ag']}**: " + ", ".join(dict.fromkeys(old + against))]
        if follows or asked:
            old = [x.strip() for l in blk for m in [FOLLOWS.match(l)] if m for x in m[1].split(",") if x.strip()]
            blk = [l for l in blk if not FOLLOWS.match(l)]
            me = max(i for i, l in enumerate(blk) if l.startswith("- **"))
            blk[me + 1:me + 1] = ([f"- **{L['follows']}**: " + ", ".join(dict.fromkeys(old + follows))] if old or follows else []) \
                + ([f"- **{L['asked']} ({stamp_now})**: 「{asked}」"] if asked else [])
        text = "\n".join(blk)
        for d in drops:
            text = re.sub(r"(?:^> .*\n)+?^> — [^\n]*" + re.escape(d) + r"\n?\n?", "", text, flags=re.M)
        have_a = set(ANCHOR.findall(text)) and {m.group(0) for m in ANCHOR.finditer(text)}
        add = [q for q, an in zip(quotes, anchors) if an not in have_a]
        text = text.rstrip("\n")
        if add:
            k = min([x for x in (text.find(f"\n[{L['interpretation']}]"), text.find("\n[Interpretation]")) if x >= 0] or [-1])
            text = (text[:k].rstrip("\n") + "\n\n" + "\n\n".join(add) + text[k:]) if k >= 0 else text + "\n\n" + "\n\n".join(add)
        if ptext: text += "\n\n" + ptext
        FL[a:b] = (text + "\n").split("\n") if b < len(FL) else text.split("\n") + [""]
        out = "\n".join(FL); no = int(to)
    else:
        if not title or not rl: sys.exit("keep: a new reading needs --title and --from")
        if len(works) != 1 and not topic: sys.exit("keep: anchors in several works, or none — give --file <topic>")
        name = topic or works[0]; f = home / "interpretation" / name / f"{today[:7]}.md"      # one file per name per month
        f.parent.mkdir(parents=True, exist_ok=True)
        no = max([x["no"] or 0 for x in ents] or [0]) + 1
        if f.exists(): out = f.read_text(encoding="utf-8").rstrip("\n") + "\n"
        else:
            wt = name
            if not topic:
                src = lib / "library" / f"{name}.txt"
                wt = next((l[2:].strip() for l in src.read_text(encoding="utf-8").split("\n") if l.startswith("# ")), name)
            desc = L["desc_topic"].format(name=name) if topic else L["desc_work"].format(title=wt)
            out = f'---\ntype: note\ndescription: "{desc}"\ntimestamp: X\nhuman_reviewed: true\ntags: [interpretation]\n---\n\n# {wt}\n'
        parts = [f"## {no} · {title}", ""] + rl + ([sline] if sline else []) + ([f"- **{lab['re']}**: {', '.join(reaches)}"] if reaches else []) + rlines + ([f"- **{lab['ag']}**: " + ", ".join(against)] if against else []) + ([f"- **{L['follows']}**: " + ", ".join(follows)] if follows else []) + ([f"- **{L['asked']} ({stamp_now})**: 「{asked}」"] if asked else [])
        out += "\n" + "\n".join(parts) + ("\n\n" + "\n\n".join(quotes) if quotes else "") + ("\n\n" + ptext if ptext else "") + "\n"
    out = re.sub(r"(?m)^timestamp: .*$", "timestamp: " + parse_now(stamp_now).astimezone().isoformat(timespec="seconds"), out, count=1)
    tm = re.search(r"(?m)^tags: \[(.*)\]$", out)
    if tm:
        tags = [t.strip() for t in tm[1].split(",") if t.strip()]
        for t in works + reaches:
            if t not in tags: tags.append(t)
        out = out[:tm.start()] + "tags: [" + ", ".join(tags) + "]" + out[tm.end():]
    f.write_text(re.sub(r"\n{3,}", "\n\n", out).rstrip("\n") + "\n", encoding="utf-8")
    build_index(home)
    r = subprocess.run([sys.executable, "-I", __file__, "check", str(home), f.relative_to(home).as_posix()] + (["--library", str(lib)] if "--library" in rest else []), capture_output=True, text=True)
    print(f"reading {no} — {f.relative_to(home).as_posix()} — {'added to' if to else 'new'}" + (f" — {status}" if status else ""))
    if r.returncode != 0: print(r.stdout.strip()); sys.exit(1)
    sys.exit(0)


def lexicon(home, rest):
    """The reader's names, most used first: how many readings carry each, when last, the reader's latest words with it,
    what they took back in those readings, and the names it was renamed from or to. Rebuilt from the readings every time,
    so it deepens as the reader talks; a session reads it at the start to speak the reader's language."""
    lim = int(opt(rest, "--limit", 12)); ents = all_entries(home); rows = names_of(home)
    spell = {}
    for r in rows: spell.setdefault(r[0], set()).update({r[0], r[1]})
    for e in ents:
        for r in e["reach"]: spell.setdefault(r, set()).add(r)
    out = []
    for nm, sp in spell.items():
        keys = [squeeze(x) for x in sp]
        es = [e for e in ents if nm in e["reach"] or any(k in squeeze(" ".join(t for _, t in e["reader"])) for k in keys)]
        if not es: continue
        last = max(es, key=lambda e: e["date"]); words = [t for _, t in last["reader"]][-1].strip("「」")
        k = next((words.find(x) for x in sp if words.find(x) >= 0), 0)
        snip = ("…" if k > 40 else "") + words[max(0, k - 40):k + 80] + ("…" if len(words) > k + 80 else "")
        took = [t for e in es for _, t in e["reject"]][-1:]
        ren = sorted({r[1] for r in rows if r[0] == nm and r[2] == "renamed"} | {r[0] for r in rows if r[1] == nm and r[2] == "renamed"})
        out.append((len(es), last["date"], nm, last["no"], snip, took, ren, "tentative" if last["tent"] else ""))
    out.sort(key=lambda x: (-x[0], x[1]), reverse=False)
    print(f"# the reader's names — {len(out)} in use, most used first")
    for n, d, nm, no, snip, took, ren, tent in out[:lim]:
        print(f"- {nm} — {n} reading(s), last {d} (reading {no}{', ' + tent if tent else ''}): 「{snip}」"
              + (f" · took back: 「{took[0][:60]}」" if took else "") + (f" · renamed: {', '.join(ren)}" if ren else ""))
    sys.exit(0)


AUTOSAVE = """#!/usr/bin/env bash
# Stop hook: keep what landed. A cloud session's container goes away; the records must reach the remote.
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
git rev-parse -q --verify HEAD >/dev/null || exit 0     # no first commit yet: still being set up
for x in interpretation desk.md digest; do [ -e "$x" ] && git add -A "$x"; done
git diff --cached --quiet && exit 0
git commit -qm "readings: $(date '+%F %H:%M')" || exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0
git pull -q --rebase origin "$(git branch --show-current)" 2>/dev/null; git push -q origin HEAD 2>/dev/null || true
exit 0
"""


def init(home, rest):
    """Make a repo ready in one run: this script and the library scripts in scripts/, the hooks merged into
    .claude/settings.json, interpretation/ with a locale template and an empty names list, .gitignore entries,
    and (--autosave) a Stop hook that commits and pushes the records. Safe to run again."""
    import json, shutil
    owner, room = (opt(rest, "--owner") or "").strip(), (opt(rest, "--room") or "").strip()
    cm = home / "CLAUDE.md"
    if cm.exists():                                     # a rerun keeps the owner and the room's name already written
        m = re.search(r"This repo is \u300c(.+?)\u300d, the reading room of (.+?)\. Every session", cm.read_text()) \
            or re.search(r"This repo is ()the reading room of (.+?)\. Every session", cm.read_text())
        if m: room, owner = room or m[1], owner or m[2]
    room = room or "reading room"
    if not owner:
        print("setup: a reading room has one owner — ask the user for the owner's name, then run again with --owner \"<name>\""); sys.exit(2)
    here = pathlib.Path(__file__).resolve().parent; sc = home / "scripts"; sc.mkdir(parents=True, exist_ok=True)
    done = []
    if (sc / "interpretation.py").resolve() != pathlib.Path(__file__).resolve():
        shutil.copy2(__file__, sc / "interpretation.py"); done.append("scripts/interpretation.py")
    ing = here.parent.parent / "library-ingest" / "scripts"
    if ing.is_dir():
        for f in sorted(ing.glob("*.py")):
            if not (sc / f.name).exists(): shutil.copy2(f, sc / f.name); done.append(f"scripts/{f.name}")
    elif not (sc / "library-quote-check.py").exists():
        print("! library-ingest skill not found — copy its scripts/ here before quoting the library")
    (home / "interpretation").mkdir(exist_ok=True)
    loc = home / "interpretation" / "locale.json"
    if not loc.exists():
        keys = ["reader", "status", "reaches", "rejected", "against", "follows", "asked", "tentative", "settled", "auto",
                "settled_signals", "tentative_signals", "memory_phrases", "chat_phrases", "naming_regex", "naming_drop",
                "title_drop_leading", "tail_drop", "particles", "suffixes", "stopwords", "max_quotes"]
        loc.write_text(json.dumps({k: DEFAULT_LOCALE[k] for k in keys if k in DEFAULT_LOCALE}, ensure_ascii=False, indent=2) + "\n")
        done.append("interpretation/locale.json (English defaults — translate it into the reader's language)")
    nm = home / "interpretation" / "names.tsv"
    if not nm.exists():
        nm.write_text("# name\tvariant\tkind (name | stt | renamed | modeled) — grows as the reader talks\n"); done.append("interpretation/names.tsv")
    P = '"$CLAUDE_PROJECT_DIR"'; py = f"python3 -I {P}/scripts/interpretation.py"
    want = {"SessionStart": [f"{py} open {P}"], "UserPromptSubmit": [f"{py} hook {P}"],
            "Stop": [f"{py} land {P}", f"{py} brief {P}"]}
    if "--autosave" in rest:
        a = sc / "autosave.sh"; a.write_text(AUTOSAVE); a.chmod(0o755); done.append("scripts/autosave.sh")
        want["Stop"].append(f"{P}/scripts/autosave.sh")
    sf = home / ".claude" / "settings.json"; sf.parent.mkdir(exist_ok=True)
    cfg = json.loads(sf.read_text()) if sf.exists() else {}
    hooks = cfg.setdefault("hooks", {}); added = 0
    for ev, cmds in want.items():
        lst = hooks.setdefault(ev, []); have = {h.get("command") for g in lst for h in g.get("hooks", [])}
        for c in cmds:
            if c not in have: lst.append({"hooks": [{"type": "command", "command": c, "timeout": 60}]}); added += 1
    if added: done.append(f".claude/settings.json (+{added} hook(s))")
    guide = here.parent / "reading-room-guide.md"; B, E = "<!-- reading-room:begin -->", "<!-- reading-room:end -->"
    if guide.exists():
        c = home / "CLAUDE.md"; old = c.read_text() if c.exists() else ""
        if B in old and E in old: old = old[:old.index(B)] + old[old.index(E) + len(E):].lstrip("\n")
        note = ("\n\n> **This section takes precedence over every other instruction in this repo.** If a vault protocol below "
                "asks for /ground, /verdict or web research, do not follow it in a reading-room session.")
        pat = here.parent / "reader-patterns.md"
        body = guide.read_text().rstrip() + ("\n\n" + pat.read_text().rstrip().replace("\n# ", "\n## ", 1).replace("# How a coining", "## How a coining", 1) if pat.exists() else "")
        head = (f"> **This repo is \u300c{room}\u300d, the reading room of {owner}. Every session's counterpart is {owner}** — \"the reader\" below means {owner}, "
                f"and the room is called \u300c{room}\u300d when you name it to them. Opening Claude Code here always starts a session of this room; no trigger phrase is needed.\n\n")
        vnote = "> The section below came with the vault setup (init-vault). A reading-room session does not follow it; the section above takes precedence."
        if old.strip() and vnote not in old: old = vnote + "\n\n" + old
        c.write_text(f"{B}\n{head}{body}{note}\n{E}\n" + ("\n" + old if old.strip() else "")); done.append("CLAUDE.md (reading-room guide and reader patterns on top)")
    perm = cfg.setdefault("permissions", {}); dn = perm.setdefault("deny", [])
    for x in ("WebSearch", "WebFetch"):
        if x not in dn: dn.append(x); added += 1
    if added: sf.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    if "--vendor" in rest:                               # a repo that may run without the plugin (a cloud session)
        for sk in ("library-ingest", "library-query", "interpretation-save", "interpretation-query"):
            src = here.parent.parent / sk
            if src.is_dir():
                dst = home / ".claude" / "skills" / sk
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__")); done.append(f".claude/skills/{sk}")
    gi = home / ".gitignore"; lines = gi.read_text().splitlines() if gi.exists() else []
    need = [x for x in ("interpretation/interpretation.fts5.db*", "library/library.fts5.db*", "scripts/__pycache__/") if x not in lines]
    if need: gi.write_text("\n".join(lines + need) + "\n"); done.append(".gitignore")
    print("init: " + ("; ".join(done) if done else "already set up"))
    if not (home / "library").is_dir(): print("next: put books in with the library-ingest skill")
    sys.exit(0)


def auto(event, raw):
    """The plugin's own hooks call this in every project; it acts only in a reading room — a repo whose library has
    been indexed (library-ingest) or that has interpretation/ — and steps aside when the repo wires these hooks itself."""
    import os, json
    home = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    if not ((home / "library" / "library.fts5.db").exists() or (home / "interpretation").is_dir()): sys.exit(0)
    sf = home / ".claude" / "settings.json"
    if sf.exists() and "interpretation.py" in sf.read_text(encoding="utf-8", errors="ignore"): sys.exit(0)
    (home / "interpretation").mkdir(exist_ok=True)
    me = [sys.executable, "-I", __file__]
    if event == "SessionStart": open_session(home)
    if event == "UserPromptSubmit":
        print(subprocess.run(me + ["hook", str(home)], input=raw, capture_output=True, text=True).stdout, end=""); sys.exit(0)
    if event == "Stop":
        subprocess.run(me + ["land", str(home)], input=raw, capture_output=True, text=True)
        print(subprocess.run(me + ["brief", str(home)], input=raw, capture_output=True, text=True).stdout, end=""); sys.exit(0)
    sys.exit(0)


def open_session(home):
    """SessionStart: what a session needs before the reader's first words — the desk, the reader's names, the last stop."""
    me = [sys.executable, "-I", __file__]
    lib = lib_root(home) / "library"; idx = next((p for p in (pathlib.Path(__file__).with_name("library-index.py"), lib.parent / "scripts" / "library-index.py") if p.exists()), None)
    if lib.is_dir() and not (lib / "library.fts5.db").exists() and any(lib.glob("*.txt")) and idx:
        subprocess.run([sys.executable, "-I", str(idx), str(lib)], capture_output=True, text=True)   # a fresh clone has no index (it is not committed)
    d = subprocess.run(me + ["desk", str(home), "show"], capture_output=True, text=True).stdout
    print(f"## {L['open_desk']}\n\n{d}")
    lx = subprocess.run(me + ["lexicon", str(home)], capture_output=True, text=True).stdout
    if "\n- " in lx: print(f"## {L['open_lexicon']}\n\n{lx}")
    ents = by_latest(all_entries(home))
    if ents:
        sh = subprocess.run(me + ["show", str(home), str(ents[0]["no"])], capture_output=True, text=True).stdout
        print(f"## {L['open_last']}\n\n{sh}")
    sys.exit(0)


def brief(raw):
    """Stop: send an answer back once when it quotes more passages than the reader can read on a phone (max_quotes)."""
    import json
    try: inp = json.loads(raw or "{}")
    except Exception: sys.exit(0)
    cap = int(L["max_quotes"])
    if not cap or inp.get("stop_hook_active"): sys.exit(0)
    n = sum(1 for l in (inp.get("last_assistant_message") or "").splitlines() if l.lstrip().startswith("> — ") or l.lstrip().startswith(">— "))
    if n > cap: print(json.dumps({"decision": "block", "reason": L["brief_reason"].format(n=n, max=cap)}, ensure_ascii=False))
    sys.exit(0)


def title_of(text):
    """A reading's title from the reader's words: a sentence said twice wins (a point lands by repetition), else the
    last statement, else the first sentence. Unpunctuated speech that runs long gives its tail — the point comes last."""
    n = int(L["title_chars"]); t = text.strip("「」 ")
    drop = [re.escape(w) for w in L["title_drop_leading"]]; tail = [re.escape(w) for w in L["tail_drop"]]
    def clean(x):
        x = x.strip()
        if drop: x = re.sub(r"^(?:(?:" + "|".join(drop) + r")[\s,.]+)+", "", x + " ").strip() or x
        if tail: x = re.sub(r"[\s,]*(?:" + "|".join(tail) + r")[?？.!\s]*$", "", x).strip() or x
        return x
    sents = [clean(x) for x in re.split(r"(?<=[.?!。？])\s+", t) if x.strip()]
    if len(sents) > 1:
        seen = {}
        for x in sents: seen[squeeze(x)] = seen.get(squeeze(x), 0) + 1
        rep2 = [x for x in sents if seen[squeeze(x)] > 1]
        stm = [x for x in sents if not x.rstrip().endswith(("?", "？"))]
        pick = rep2[0] if rep2 else stm[-1] if stm else sents[0]
    else:
        pick = sents[0] if sents else t
        if len(pick) > n * 2: return "… " + pick[-n:].split(" ", 1)[-1]          # a long unpunctuated run: its tail
    return pick if len(pick) <= n else pick[:n].rsplit(" ", 1)[0] + " …"


def land(home, raw):
    """Stop hook: the reader's words since the last landing → one reading, status auto, no model. The library lines
    the answer quoted become its quotes; the readings the reader's words named (recall's strong hits) become its
    Follows line. Skipped: words a keep or a desk command already took, and short words with no quote (chat,
    commands, questions to the memory) — those stay in the log, where recall still finds them."""
    import json
    try: inp = json.loads(raw or "{}")
    except Exception: inp = {}
    if inp.get("stop_hook_active"): return
    logd = home / "interpretation" / "log"; mark = logd / ".landed"
    last = mark.read_text().strip() if mark.exists() else ""
    said = [(st, t) for st, t in log_lines(home) if st > last]
    if not said: return
    mark.write_text(said[-1][0] + "\n")
    ents = all_entries(home)
    taken = {d for e in ents for d, _ in e["reader"]}
    desk_text = squeeze((home / "desk.md").read_text(encoding="utf-8")) if (home / "desk.md").exists() else ""
    said = [(st, t) for st, t in said if st not in taken and squeeze(t) not in desk_text]
    chat = [squeeze(x) for x in L["chat_phrases"]]
    said = [(st, t) for st, t in said if not (len(t) <= int(L["chat_max_chars"]) and any(c in squeeze(t) for c in chat))]   # goodbyes, small talk
    said = [(st, t) for st, t in said if not (t.lstrip().startswith("/") or re.search(r"https?://|(?:^|\s)~?/[\w.\-]+/[\w.\-/]+", t))]   # commands, paths, URLs: an instruction, not a thought
    mem = [squeeze(x) for x in L["memory_phrases"]]
    said = [(st, t) for st, t in said if not any(m in squeeze(t) for m in mem)]          # "what did I say": a question to the memory, not a thought
    lib = lib_root(home); ans = inp.get("last_assistant_message") or ""
    anchors = list(dict.fromkeys(m.group(0) for m in ANCHOR.finditer(ans) if (lib / "library" / f"{m[1]}.txt").exists()))[:6]
    if not said or (not anchors and len(squeeze(" ".join(t for _, t in said))) < int(L["min_chars"])): return
    rec = json.loads((logd / ".recalled").read_text()) if (logd / ".recalled").exists() else {}
    sid = inp.get("session_id", ""); sf = logd / ".sessions"
    sess = json.loads(sf.read_text()) if sf.exists() else {}
    prev = [sess[sid]] if sid and sid in sess else []                     # the train of thought: the previous reading of this session
    follows = list(dict.fromkeys(prev + [n for st, _ in said for n in rec.get(st, [])]))
    q = [l.strip().lstrip("*- ").strip() for l in ans.strip().splitlines()
         if not l.lstrip().startswith(">") and l.strip().rstrip("*").endswith(("?", "？"))]   # never a line of a quote block
    asked = re.split(r"(?<=[.!?。？])\s+", re.sub(r"[*_`]", "", q[-1]))[-1] if q and q[-1] else ""          # the assistant's last open question, kept so the next session can pick it up
    words = " ".join(t for _, t in said)
    coined = []                                          # "I call this X": the reader names an idea — the names list grows by itself
    for rx in L["naming_regex"]:
        for m in re.finditer(rx, words, flags=re.I):
            w = m.group(1).split()
            while w and w[0].lower() in [x.lower() for x in L["naming_drop"]]: w = w[1:]
            nm = " ".join(w).strip(" ,.?!")
            if 1 < len(nm) <= 30 and nm not in coined: coined.append(nm)
    if coined:
        f = home / "interpretation" / "names.tsv"; have = {r[0] for r in names_of(home)}
        with open(f, "a", encoding="utf-8") as h:
            for nm in coined:
                if nm not in have: h.write(f"{nm}\t{nm}\tname\n")
    reach, _ = names_in(home, words, {r for e in ents for r in e["reach"]} | set(coined))   # longest first; a misheard spelling counts as its name
    title = title_of(max(said, key=lambda x: len(x[1]))[1])
    flat = squeeze(words)
    status = ("tentative" if any(squeeze(x) in flat for x in L["tentative_signals"])
              else "settled" if any(squeeze(x) in flat for x in L["settled_signals"]) else "auto")   # his own words for firm and not-yet
    works = {ANCHOR.fullmatch(a)[1] for a in anchors}
    args = ["keep", str(home), "--title", title, "--status", status] + sum((["--from", st] for st, _ in said), [])
    args += sum((["--anchor", a] for a in anchors), []) + sum((["--reach", r] for r in reach), [])
    args += sum((["--follows", str(x)] for x in follows), []) + (["--asked", asked] if asked else [])
    if len(works) != 1: args += ["--file", reach[0] if reach else L["thoughts_file"]]
    r = subprocess.run([sys.executable, "-I", __file__] + args, capture_output=True, text=True)
    m = re.match(r"reading (\d+)", r.stdout)
    if m and sid: sess[sid] = int(m[1]); sf.write_text(json.dumps(sess))
    print((r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else "", file=sys.stderr)


def show(home, nos, ents=None):
    for e in (ents if ents is not None else all_entries(home)):
        if str(e["no"]) in nos:
            print(f"## {e['no']} · {'~ ' if e['tent'] else ''}{e['head']}   ({e['file']})")
            for l in e["body"]:
                if l.startswith("- **") or ADOPT.match(l): print(l)
            print(f"- anchors: {', '.join(dict.fromkeys(e['anchors']))}\n")


def topic_of(rel):
    """interpretation/<name>/<YYYY-MM>.md → name; an older flat interpretation/<name>.md → name."""
    p = pathlib.PurePosixPath(rel)
    return p.parent.name if p.parent.name != "interpretation" else p.stem


def page_sets(home):
    """{name: (kind, [entry])} — kind is 'name' (a Reaches name or a topic file) or 'work'. One count for
    pages, material and digest-check."""
    ents = all_entries(home); lib = lib_root(home)
    def is_work(stem): return (lib / "library" / f"{stem}.txt").exists()
    out = {}
    for e in ents:
        for r in e["reach"]: out.setdefault(r, ("name", []))[1].append(e)
        stem = topic_of(e["file"])
        if not is_work(stem): out.setdefault(stem, ("name", []))[1].append(e)
        for w in e["works"]: out.setdefault(w, ("work", []))[1].append(e) if out.get(w, ("work",))[0] == "work" else None
    for k, (kind, es) in out.items():
        seen = {}
        for e in es: seen.setdefault(e["no"], e)
        out[k] = (kind, sorted(seen.values(), key=lambda e: (e["first"], e["no"] or 0)))
    return out


def pages(home):
    sets = page_sets(home); have = {f.stem for f in (home / "digest").glob("*.md")} if (home / "digest").is_dir() else set()
    print("# kind | name | readings | due | page | numbers")
    for k, (kind, es) in sorted(sets.items(), key=lambda x: (x[1][0] != "name", -len(x[1][1]), x[0])):
        due = "due" if kind == "name" and len(es) >= 3 else "on request" if kind == "work" else "—"
        print(f"{kind} | {k} | {len(es)} | {due} | {'digest/' + k + '.md' if k in have else '—'} | {', '.join(str(e['no']) for e in es)}")
    sys.exit(0)


def material(home, rest):
    r, w = opt(rest, "--reach"), opt(rest, "--work")
    if r or w:
        kind, ents = page_sets(home).get(r or w, ("", []))
        if w and kind != "work": ents = []
    elif "--all" in rest: ents = sorted(all_entries(home), key=lambda e: (e["first"], e["no"] or 0))
    else: print("material: --reach NAME | --work ID | --all"); sys.exit(2)
    print(f"# {len(ents)} reading(s), oldest first: {', '.join(str(e['no']) for e in ents)}")
    show(home, {str(e["no"]) for e in ents}, ents)
    sys.exit(0)




def digest_check(home):
    d = home / "digest"; bad = []; n = 0
    SETTLED_H = tuple(dict.fromkeys(["settled"] + [x.lower() for x in L["settled_heads"]]))
    STANDS_H = tuple(dict.fromkeys(["where it stands"] + [x.lower() for x in L["stands_heads"]]))
    marks = [DEFAULT_LOCALE["tentative_mark"], L["tentative_mark"]]
    ents = {e["no"]: e for e in all_entries(home)}
    hay = {no: squeeze(e["head"] + " " + " ".join(t for _, t in e["reader"]) + " " + " ".join(t for _, t in e["reject"])) for no, e in ents.items()}
    sets = page_sets(home)
    names = {squeeze(k) for k in sets} | {squeeze(r) for e in ents.values() for r in e["reach"]}
    for f in (sorted(d.glob("*.md")) if d.is_dir() else []):
        text = f.read_text(encoding="utf-8"); where = f"digest/{f.name}"
        if not text.startswith("---\n"): bad.append(f"{where}: no metadata block")
        lines = text.splitlines(); h2 = ""; h3 = None; cited = set()
        def close_h3():
            if h3 is None: return
            i3, words, under = h3
            w = squeeze(re.sub(r"[「」『』]", "", words))
            if w and w not in names and not any(w in hay.get(x, "") for x in under):
                bad.append(f"{where}:{i3}: sub-heading 「{words[:30]}」 is neither the reader's words in the readings under it nor one of their names")
        for i, l in enumerate(lines, 1):
            if l.startswith("## "): close_h3(); h3 = None; h2 = l[3:].strip().lower(); continue
            if l.startswith("### "): close_h3(); h3 = (i, l[4:].strip(), set()); continue
            if l.startswith("# "): close_h3(); h3 = None; continue
            if not l.lstrip().startswith("- "): continue
            n += 1; m = re.search(r"\(((?:\d+)(?:,\s*\d+)*)\)\s*$", l)
            if not m: bad.append(f"{where}:{i}: bullet cites no reading — end it with (12) or (3, 12)"); continue
            nos = [int(x) for x in m[1].split(",")]; cited |= set(nos)
            if h3 is not None: h3[2].update(nos)
            for x in nos:
                if x not in ents: bad.append(f"{where}:{i}: no reading {x}")
            for q in re.findall(r"「([^「」]+)」", l):
                if not any(squeeze(q) in hay.get(x, "") for x in nos):
                    bad.append(f"{where}:{i}: 「{q[:30]}」 is not in reading {', '.join(map(str, nos))}")
            tent = [x for x in nos if x in ents and ents[x]["tent"]]
            if tent and h2.startswith(SETTLED_H):
                bad.append(f"{where}:{i}: reading {', '.join(map(str, tent))} is tentative — put it under Open, or under Where it stands with its tentative mark")
            if tent and h2.startswith(STANDS_H) and not any(mk in l for mk in marks):
                bad.append(f"{where}:{i}: reading {', '.join(map(str, tent))} is tentative — add {L['tentative_mark']} to the bullet")
        close_h3()
        kind, es = sets.get(f.stem, ("", []))
        missing = [e["no"] for e in es if e["no"] not in cited]
        if missing: bad.append(f"{where}: leaves out reading {', '.join(map(str, missing))} of 「{f.stem}」 — `material --{'work' if kind == 'work' else 'reach'} {f.stem}`")
    for b in bad: print(b)
    if not bad: print(f"digest check ok — {n} bullet(s)")
    sys.exit(1 if bad else 0)


def main():
    a = sys.argv[1:]
    if a[:1] == ["auto"]:
        auto(a[1] if len(a) > 1 else "", sys.stdin.read())
    if len(a) < 2 or a[0] in ("-h", "--help") or a[0] not in ("check", "list", "recall", "find", "desk", "said", "hook", "keep", "index", "show", "material", "digest-check", "pages", "land", "alias", "lexicon", "open", "brief", "init", "setup", "auto"):
        print(__doc__); sys.exit(0 if a[:1] in (["-h"], ["--help"]) else 2)
    cmd, root, rest = a[0], pathlib.Path(a[1]), a[2:]
    setup(root)
    if "-h" in a or "--help" in a: print(__doc__); sys.exit(0)
    if cmd == "check":
        check(root, rest)
    if cmd == "desk":
        desk(root, rest)
    if cmd == "said":
        print(log_said(root, sys.stdin.read(), rest)); build_index(root); sys.exit(0)
    if cmd == "hook":
        import json
        try: text = json.load(sys.stdin).get("prompt", "")
        except Exception: text = ""
        hits = print_recall(root, text); st = log_said(root, text, rest)
        named = [int(ref) for kind, ref, *_, strong in (hits or []) if kind == "entry" and strong]
        if named:                                       # the readings this utterance named: land links the new one to them
            f = root / "interpretation" / "log" / ".recalled"
            d = json.loads(f.read_text()) if f.exists() else {}
            d[st] = named; f.write_text(json.dumps(d))
        build_index(root); sys.exit(0)
    if cmd == "keep":
        keep(root, rest)
    if cmd == "material":
        material(root, rest)
    if cmd == "digest-check":
        digest_check(root)
    if cmd == "pages":
        pages(root)
    if cmd == "alias":
        alias(root, rest)
    if cmd == "lexicon":
        lexicon(root, rest)
    if cmd == "open":
        open_session(root)
    if cmd in ("setup", "init"):
        init(root, rest)
    if cmd == "brief":
        brief(sys.stdin.read())
    if cmd == "land":
        land(root, sys.stdin.read()); sys.exit(0)
    if cmd == "index":
        print(f"indexed {build_index(root)} entr(ies)"); sys.exit(0)
    if cmd == "show":
        show(root, rest); sys.exit(0)
    if cmd == "recall" and "--work" not in rest:
        lim = int(opt(rest, "--limit", 4)); print_recall(root, " ".join(x for x in rest if not x.startswith("--") and x != str(lim)), lim); sys.exit(0)
    files = load(root)
    ents = [e for f in files for e in f[4]]
    meta = {f[0]: (f[2], f[3]) for f in files}
    work = opt(rest, "--work")
    if cmd == "list":
        for e in by_latest(ents):
            if (work is None or work in e["works"]) and ("--tentative" not in rest or e["tent"]): print(line_of(e))
    elif cmd == "recall":
        if not work: print("recall needs --work <id>"); sys.exit(2)
        hit = by_latest([e for e in ents if work in e["works"]])
        n = int(opt(rest, "--recent", len(hit) or 0))
        print(f"# {len(hit)} entr{'y' if len(hit) == 1 else 'ies'} anchored in {work}" + (f", {n} in full" if n < len(hit) else ""))
        for e in hit[:n]:
            print(f"\n## {'~ ' if e['tent'] else ''}{e['head']}\n{e['file']}:{e['line']}")
            for d, t in e["reader"]: print(f"- reader ({d}): {t}")
            if e["reach"]: print(f"- reaches: {', '.join(e['reach'])}")
            for d, t in e["reject"]: print(f"- rejected ({d}): {t}")
            print(f"- anchors: {', '.join(dict.fromkeys(e['anchors']))}")
            for d, w in e["status"][-1:]: print(f"- status ({d}): {w}")
            for x in e["adopt"]: print(f"- assistant paragraph: {x[x.index('('):x.index(')') + 1]}")
        if hit[n:]: print()
        for e in hit[n:]: print(line_of(e))
    else:
        skip = {rest.index(x) + 1 for x in ("--limit", "--reach", "--library") if x in rest}
        if "--tentative" in rest: ents = [e for e in ents if e["tent"]]
        if "--rejected" in rest: ents = [e for e in ents if e["reject"]]
        if opt(rest, "--reach"): ents = [e for e in ents if opt(rest, "--reach") in e["reach"]]
        bundles = [b for i, b in enumerate(rest) if not b.startswith("--") and i not in skip]
        if not bundles and not ({"--tentative", "--rejected", "--reach"} & set(rest)): print('find needs a bundle or a flag'); sys.exit(2)
        limit = int(opt(rest, "--limit", 30)); scored = []
        for e in ents:
            topic, desc = meta[e["file"]]
            said = squeeze(" ".join(t for _, t in e["reader"]))
            fields = [("heading", e["head"], 5), ("reaches", ", ".join(e["reach"]), 4),
                      ("reader line", " ".join(t for _, t in e["reader"]), 2), ("topic", topic, 1),
                      ("the rest", "\n".join(e["body"]), 1)]
            score, where, ok, snip, in_said = 0, [], True, "", True
            for b in bundles:
                sp = [squeeze(s) for s in b.split("|") if s.strip()]; got = False
                for name, val, w in fields:
                    if any(s in squeeze(val) for s in sp):
                        score += w; got = True
                        if name not in where: where.append(name)
                        break
                ok = ok and got
                in_said = in_said and any(s in said for s in sp)
                if not snip:
                    for _, t in e["reader"]:
                        for s in b.split("|"):
                            k = t.find(s.strip())
                            if s.strip() and k >= 0:
                                snip = ("…" if k > 60 else "") + t[max(0, k - 60):k + 100] + "…"; break
                        if snip: break
            if ok: scored.append((score + (3 if in_said else 0), e, where, snip))
        scored.sort(key=lambda x: x[1]["first"])
        scored.sort(key=lambda x: x[0], reverse=True)
        print(f"# {len(scored)} entr{'y' if len(scored) == 1 else 'ies'} match, showing {min(limit, len(scored))}")
        for i, (s, e, where, snip) in enumerate(scored[:limit], 1):
            print(f"{e['no']} | {e['file']} | first said {e['first'] or '—'} | {'tentative' if e['tent'] else 'settled'}{' | hit in ' + ', '.join(where) if where else ''} | {e['head']}")
            if "--rejected" in rest:
                for d, t in e["reject"]: print(f"    took back ({d}): {t}")
            if snip: print(f"    {snip}")
    sys.exit(0)


if __name__ == "__main__":
    main()
