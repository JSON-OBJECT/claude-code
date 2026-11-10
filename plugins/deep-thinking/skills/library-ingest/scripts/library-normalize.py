#!/usr/bin/env python3
"""library-normalize — turn a source as received into canonical text plus a structure ledger.

  library-normalize.py <adapter> <source> <library folder> [adapter options]

An adapter reads one kind of source; each is a file `adapter_<name>.py` beside this script (usage below).
Writes <id>.txt (canonical text), <id>.toc.tsv (ledger), <id>.ingest.json (what was dropped or repaired).
Reads <id>.rules.json from the library folder when present.

Summary line per work:
  <id>: N chars · N divisions · depth N · N flagged
`divisions` counts every ledger row — volumes, parts and prefaces as well as chapters. `flagged` counts the rows
with a note (a number skipped or repeated, numbering that starts past 1).
"""
import hashlib
import importlib
import json
import pathlib
import re
import sys
import unicodedata
import datetime

sys.dont_write_bytecode = True                              # leave no __pycache__ beside the scripts
sys.path.insert(0, str(pathlib.Path(__file__).parent))


def nfc(s):
    return unicodedata.normalize("NFC", s).replace("\xa0", " ")

VERSION = "0.9"
HAN = {"〇": 0, "○": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
UNIT = {"章": "장", "回": "회", "節": "절", "篇": "편", "編": "편", "部": "부", "卷": "권", "券": "권"}
UNITS_KO = "장회절편부권"
TYPE_BY_UNIT = {"권": "volume", "부": "part", "편": "part", "장": "chapter", "회": "chapter", "절": "subchapter",
                "Volume": "volume", "Book": "part", "Part": "part", "Chapter": "chapter", "Section": "subchapter"}
FRONT = {"서문": "preface", "머리말": "preface", "서": "preface", "序": "preface", "서언": "preface", "前言": "preface",
         "자서": "preface", "작가의 말": "preface", "서편": "prologue", "프롤로그": "prologue", "에필로그": "epilogue",
         "후기": "afterword", "발문": "afterword", "부록": "appendix",
         "preface": "preface", "foreword": "foreword", "introduction": "introduction", "prologue": "prologue",
         "epilogue": "epilogue", "afterword": "afterword", "appendix": "appendix", "conclusion": "conclusion", "dedication": "dedication"}


def han2int(s):
    """Chinese numerals (一二三…百) → int; None when the string is not a number."""
    if not s or not s.strip("○") or any(c not in HAN and c not in "十百" for c in s):   # a lone ○ is a mark, not zero
        return None
    if all(c in HAN for c in s):                      # 二三 = 23 (positional notation)
        return int("".join(str(HAN[c]) for c in s))
    total, cur = 0, 0
    for c in s:
        if c in HAN:
            cur = HAN[c]
        elif c == "十":
            total += (cur or 1) * 10; cur = 0
        elif c == "百":
            total += (cur or 1) * 100; cur = 0
    return total + cur


def roman(s):
    v = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}; s = s.lower(); t = 0
    for a_, b_ in zip(s, s[1:] + " "):
        t += -v[a_] if b_ != " " and v[a_] < v[b_] else v[a_]
    return t if 0 < t < 400 else None


def norm_heading(s):
    """Normalize a heading → (display text, number or None, unit or None)."""
    s = re.sub(r"\s+", " ", nfc(s)).strip()
    m = re.fullmatch(r"(\d+)\s*[.)]?", s)
    if m:
        return m.group(1), int(m.group(1)), None
    m = re.fullmatch(r"([〇○一二三四五六七八九十百]+)(?:\s*\[[가-힣 ]+\])?\s*[.)]?", s)
    if m and han2int(m.group(1)) is not None:
        n = han2int(m.group(1)); return str(n), n, None
    m = re.match(r"第\s*([〇○一二三四五六七八九十百\d]+)\s*([章回節篇編部卷券])(?:\s*\[[가-힣 ]+\])?\s*(.*)$", s)
    if m:
        n = int(m.group(1)) if m.group(1).isdigit() else han2int(m.group(1)); u = UNIT[m.group(2)]
        return f"제{n}{u} {m.group(3)}".strip(), n, u
    m = re.match(rf"제?\s*(\d+)\s*([{UNITS_KO}])(?:\s+(.*))?$", s)
    if m:
        n, u = int(m.group(1)), m.group(2)
        return f"제{n}{u} {m.group(3) or ''}".strip(), n, u
    m = re.match(r"(?i)(chapter|book|part|volume|section)\s+([ivxlcdm]+|\d+)\b[.:—\-]?\s*(.*)$", s)
    if m:
        n = int(m.group(2)) if m.group(2).isdigit() else roman(m.group(2)); u = m.group(1).capitalize()
        if n:
            return f"{u} {n} {m.group(3)}".strip(), n, u
    m = re.fullmatch(r"([IVXLCDM]+)\.?", s)
    if m and roman(m.group(1)):
        return str(roman(m.group(1))), roman(m.group(1)), None
    m = re.fullmatch(r"([상중하])\s*권|卷?([上中下])卷?", s)
    if m:
        k = m.group(1) or {"上": "상", "中": "중", "下": "하"}[m.group(2)]
        return f"{k}권", "상중하".index(k) + 1, "권"
    return s, None, None


class Div:
    def __init__(self, heading="", n=None, unit=None, orig="", src="authorial", page=""):
        self.heading, self.n, self.unit, self.orig, self.src, self.page = heading, n, unit, orig, src, page
        self.blocks, self.children, self.notes, self.type, self.id = [], [], [], "", ""


RULE_KEYS = {"meta", "drop", "drop_sections", "drop_headings", "headings", "disable_default_ranks", "wrapped",
             "join_number_headings", "exclude", "include"}


def tally(d, text):
    k = text[:60] + ("…" if len(text) > 60 else "")
    d[k] = d.get(k, 0) + 1


def build(src, rules):
    title, mblocks, revs = src["title"], src["mblocks"], src.get("revs", {})
    notes = list(src.get("notes", []))
    count = {"paragraph": 0, "section": 0, "heading": 0}
    gone = {"paragraph": {}, "section": {}, "heading": {}}   # what each rule removed → how many times
    drops = [re.compile(x) for x in rules.get("drop", [])]
    unhead = [re.compile(x) for x in rules.get("drop_headings", [])]
    unsect = [re.compile(x) for x in rules.get("drop_sections", [])]
    mk = [(int(r["level"]), re.compile(r["pattern"])) for r in rules.get("headings", [])] if src.get("promote_headings") else []
    def ruled(blocks):
        out, lift, cut = [], None, None
        for b in blocks:
            text = b[1] if b[0] in ("p", "bold") else (" ".join(b[1]) if b[0] == "lines" else (b[2] if b[0] == "h" else ""))
            if b[0] in ("p", "bold"):
                hit = next((lv for lv, pat in mk if pat.search(text)), None)
                if hit:
                    b = ("h", hit, text)                      # a rule promotes the paragraph to a heading
            if b[0] == "h":
                if cut is not None and b[1] > cut: continue   # a sub-heading of the section being dropped
                cut = None
                if lift is not None and b[1] <= lift: lift = None
                if any(d.search(b[2]) for d in unsect):
                    cut = b[1]; count["section"] += 1; tally(gone["section"], b[2]); continue   # drop the heading and everything under it
                if any(d.search(b[2]) for d in unhead):
                    lift = b[1]; count["heading"] += 1; tally(gone["heading"], b[2]); continue  # remove only the heading; headings under it move up a level
                if lift is not None and b[1] > lift:
                    b = ("h", b[1] - 1, b[2])
            elif cut is not None:
                continue
            elif b[0] in ("p", "bold", "lines") and any(d.search(text) for d in drops):
                count["paragraph"] += 1; tally(gone["paragraph"], text); continue
            out.append(b)
        if rules.get("join_number_headings"):                # 「제1장」 + the title heading right after it → one heading
            joined = []
            for b in out:
                a = joined[-1] if joined else None
                if (b[0] == "h" and a and a[0] == "h" and norm_heading(a[2])[1] is not None
                        and norm_heading(b[2])[1] is None and b[2].strip().lower() not in FRONT):
                    joined[-1] = ("h", a[1], a[2].strip() + " " + b[2].strip()); count["joined"] = count.get("joined", 0) + 1
                else:
                    joined.append(b)
            out = joined
        return out
    mblocks = ruled(mblocks)
    root = Div(heading=title)
    src["rule_count"] = count; src["rule_gone"] = gone
    if src.get("assemble"):                                  # a multi-page source: the adapter weaves its pages into divisions
        src["assemble"](CORE, src, root, mblocks, ruled, rules, notes)
    else:
        attach(root, repair_stray_headings(mblocks, "(main page)", notes), title, top=True)
    return root, src["meta"], revs, notes


def repair_stray_headings(blocks, page, notes):
    """A one- or two-syllable Hangul heading among numbered headings is a transcription slip: the tail of the
    paragraph before it, cut off and marked up as a heading. Rejoin it."""
    by_level = {}
    for b in blocks:
        if b[0] == "h":
            by_level.setdefault(b[1], []).append(b)
    out = []
    for b in blocks:
        if b[0] == "h":
            sib = by_level[b[1]]
            numeric = sum(1 for x in sib if norm_heading(x[2])[1] is not None)
            if (len(sib) >= 4 and numeric >= 0.7 * len(sib) and norm_heading(b[2])[1] is None
                    and re.fullmatch(r"[가-힣]{1,2}", b[2].strip()) and out and out[-1][0] == "p"):
                out[-1] = ("p", out[-1][1] + b[2].strip())
                notes.append(f"transcription slip repaired: stray heading 「{b[2].strip()}」 on page {page} rejoined to the paragraph before it")
                continue
        out.append(b)
    return out


def attach(div, blocks, page, top=False):
    """Hang the headings found in a page under `div` as its children."""
    levels = sorted({b[1] for b in blocks if b[0] == "h"})
    stack = [(0, div)]
    for b in blocks:
        if b[0] == "h":
            depth = levels.index(b[1]) + 1
            h, n, u = norm_heading(b[2])
            d = Div(h, n, u, b[2], "authorial", page)
            while stack[-1][0] >= depth:
                stack.pop()
            stack[-1][1].children.append(d); stack.append((depth, d))
        else:
            stack[-1][1].blocks.append(b)


def renumber_volumes(root):
    """Number 상·중·하 volumes in the order present (with only 상 and 하, 하 is volume 2)."""
    def walk(d):
        vols = [c for c in d.children if c.unit == "권" and re.fullmatch(r"[상중하]권", c.heading)]
        for i, c in enumerate(vols, 1):
            c.n = i
        for c in d.children:
            walk(c)
    walk(root)


def classify(root):
    def walk(d, depth, parent):
        if d is not root:
            base = re.sub(r"\s*[\(（\[].*$", "", d.heading).strip().rstrip(".:").lower()
            if d.unit:
                d.type = TYPE_BY_UNIT[d.unit]
            elif base in FRONT:
                d.type = FRONT[base]
            elif re.search(r"요약|개요|槪要|梗槪", d.heading):
                d.type = "abstract"
            elif parent is not root and parent.type in ("chapter", "subchapter"):
                d.type = "subchapter"
            elif d.children and all(c.children for c in d.children):
                d.type = "part"
            else:
                d.type = "chapter"
        for c in d.children:
            walk(c, depth + 1, d)
    walk(root, 0, None)


LETTER = {"volume": "v", "part": "p", "chapter": "c", "subchapter": "s"}


def assign_ids(root):
    def walk(d, prefix):
        seen = {}
        for i, c in enumerate(d.children, 1):
            L = LETTER.get(c.type)
            if L:
                k = seen.setdefault(L, 0) + 1; seen[L] = k
                num = c.n if c.n is not None else k
                local = f"{L}{num:02d}"
            else:
                k = seen.setdefault(c.type, 0) + 1; seen[c.type] = k
                local = c.type + (str(k) if k > 1 else "")
            c.local = local
        locs = [c.local for c in d.children]
        for i, c in enumerate(d.children, 1):
            if locs.count(c.local) > 1:                 # siblings sharing a number get their position appended
                c.notes.append(f"duplicate number ({c.local})"); c.local = f"{c.local}x{i}"
            c.id = (prefix + "." if prefix else "") + c.local
            walk(c, c.id)
    walk(root, "")
    # drop the volume prefix when chapter numbers are unique across the work
    flat = []
    def collect(d):
        for c in d.children:
            flat.append(c); collect(c)
    collect(root)
    stripped = [re.sub(r"^v\d+\.", "", c.id) if c.type != "volume" else c.id for c in flat]
    if len(set(stripped)) == len(stripped):
        for c, s in zip(flat, stripped):
            c.id = s


def check_sequence(root, notes):
    last_seen = {}
    def walk(d):
        if d.type in ("chapter", "part", "preface") or d is root:
            last_seen.pop("subchapter", None)                # section numbers restart in every chapter
        nums = [(c.n, c) for c in d.children if c.n is not None and c.type in LETTER]
        if nums and nums[0][1].type != "volume":
            first, c0 = nums[0]
            carry = last_seen.get(c0.type)                    # numbering that carries on across volumes (1–13, then 14–) is normal
            if first != 1 and first != (carry or 0) + 1:
                c0.notes.append(f"numbering starts at {first}" + (f" after {carry}" if carry else "") + " — an earlier division may be missing")
            last_seen[c0.type] = nums[-1][0]
        for (a, _), (b, c) in zip(nums, nums[1:]):
            if b != a + 1 and c.type != "volume":
                c.notes.append(f"number skips {a}→{b}")
        for c in d.children:
            walk(c)
    walk(root)


def escape_md(t):
    """Keep a body line from parsing as a Markdown block: escape only what starts it."""
    m = re.match(r"(\d{1,9})([.)])(\s|$)", t)
    if m:                                                    # "1930. 4." → "1930\. 4." (a backslash before a digit would print literally)
        return m.group(1) + "\\" + t[len(m.group(1)):]
    if re.match(r"(#{1,6}\s|>|[-+*](\s|$)|={3,}\s*$|-{3,}\s*$|`{3,}|~{3,})", t):
        return "\\" + t
    return t


def render(root, meta, title, work_id, tlen):
    lines, toc, fnmap, defs = [], [], {}, {}
    def gather(d):                                           # footnote definitions sit at the end of a page: collect them first
        for b in d.blocks:
            if b[0] == "fn": defs[b[1]] = b[2]
        for c in d.children: gather(c)
    gather(root)
    def emit(s=""):
        lines.append(s)
    def mark(t, used):
        def sub(m):
            k = fnmap.setdefault(m.group(1), len(fnmap) + 1)
            if m.group(1) not in used: used.append(m.group(1))
            return f"[^{k}]"
        return re.sub(r"\[\^(\d+)\]", sub, t)
    def body(blocks, used):
        for b in blocks:
            if b[0] == "p" or b[0] == "bold":
                t = mark(b[1], used)
                emit(f"**{t}**" if b[0] == "bold" else escape_md(t)); emit()
            elif b[0] == "lines":
                ls = [mark(l, used) for l in b[1]]
                for i, l in enumerate(ls):
                    emit("> " + l + ("  " if i < len(ls) - 1 else ""))
                emit()
            elif b[0] == "break":
                if lines and lines[-2:] != ["* * *", ""]:
                    emit("* * *"); emit()
    def flush_notes(used):
        for k in used:
            if k in defs:
                emit(f"[^{fnmap[k]}]: {defs[k]}"); emit()
        used.clear()
    def walk(d, depth, parent_id, used):
        if depth == 1: used = []                             # footnotes go to the end of the top-level division their marks occur in
        if depth:
            start = len(lines) + 1
            emit("#" * min(depth + 1, 6) + " " + d.heading); emit()
            row = [d.id, depth, d.type, "" if d.n is None else d.n, d.heading, d.orig, d.src, start, 0, 0, parent_id, d.page[tlen + 1:] or "(main page)", "; ".join(d.notes)]
            toc.append(row)
        body(d.blocks, used)
        if depth == 0: flush_notes(used)                     # footnotes of the text before the first division
        for c in d.children:
            walk(c, depth + 1, d.id, used)
        if depth:
            if depth == 1: flush_notes(used)
            row[8] = len(lines)
    J = lambda v: json.dumps(v, ensure_ascii=False)
    head = ["---", f"title: {J(title)}", f"creator: {J(meta.get('creator', ''))}"]
    for k in ("translator", "editor"):                       # Dublin Core contributor, one key per role
        if meta.get(k):
            head.append(f"{k}: {J(meta[k])}")
    if meta.get("date"):
        head.append(f"date: {J(meta['date'])}")
    depth_types = []
    def types(d, k):
        for c in d.children:
            if c.type in LETTER:
                while len(depth_types) <= k: depth_types.append(set())
                depth_types[k].add(c.type)
            types(c, k + 1)
    types(root, 0)
    head += [f"language: {meta.get('language', 'ko')}", f"type: {meta.get('type', 'book')}", f"identifier: {J(work_id)}",
             f"source: {meta.get('source', '')}"]
    if meta.get("source_revision"):
        head.append(f"source_revision: {meta['source_revision']}")
    head += [f"rights: {J(meta.get('rights') or 'not stated')}", f"retrieved: {meta.get('retrieved') or datetime.date.today().isoformat()}",
             f"structure: {J(' > '.join('/'.join(sorted(x)) for x in depth_types) or 'no divisions')}",
             f"normalizer: library-normalize {VERSION}", "---", ""]
    lines.extend(head)
    emit(f"# {title}"); emit()
    walk(root, 0, "", [])
    while lines and lines[-1] == "":
        lines.pop()
    for row in toc:
        row[8] = min(row[8], len(lines))
    text = "\n".join(lines) + "\n"
    # fill in character counts
    for row in toc:
        row[9] = sum(len(l) for l in lines[row[7]:row[8]] if l and not l.startswith("#"))
    return text, toc


def work_id_of(title):
    t = re.sub(r"\s*\(.*?\)\s*$", "", title)
    return re.sub(r"\s+", "-", t.strip())


def write(src, OUT):
    title = src["title"]
    wid = src.get("id") or work_id_of(title)
    rf = OUT / f"{wid}.rules.json"
    rules = json.loads(rf.read_text()) if rf.exists() else {}
    root, meta, revs, notes = build(src, rules)
    meta.update(rules.get("meta", {}))                       # metadata corrections from the rules file
    if meta.get("date") not in (None, ""):
        meta["date"] = str(meta["date"])                     # 1928 and "1928" are written the same way
    title = meta.pop("title", title)
    renumber_volumes(root); classify(root); assign_ids(root); check_sequence(root, notes)
    rc = {k: v for k, v in src.get("rule_count", {}).items() if v and k != "joined"}
    if rc:
        notes.append("rules file dropped " + ", ".join(f"{v} {k}(s)" for k, v in rc.items()))
    for kind, key in (("section", "drop_sections"), ("heading", "drop_headings"), ("paragraph", "drop")):
        seen = sorted(src.get("rule_gone", {}).get(kind, {}).items(), key=lambda kv: -kv[1])
        notes += [f"dropped by `{key}`: 「{k}」" + (f" ×{v}" if v > 1 else "") for k, v in seen[:40]]
        if len(seen) > 40:
            notes.append(f"… and {len(seen) - 40} more distinct {kind}(s)")
    if src.get("rule_count", {}).get("joined"):
        notes.append(f"`join_number_headings` joined {src['rule_count']['joined']} number heading(s) to the title heading after them")
    unknown = sorted(set(rules) - RULE_KEYS)
    if unknown:
        notes.append("rules file keys not understood and ignored: " + ", ".join(repr(k) for k in unknown))
        print(f"   ! {wid}.rules.json: unknown key(s) ignored — " + ", ".join(repr(k) for k in unknown), file=sys.stderr)
    text, toc = render(root, meta, title, wid, len(src["title"]))
    (OUT / f"{wid}.txt").write_text(text, encoding="utf-8")
    hdr = ["id", "level", "type", "n", "heading", "original", "heading_source", "line_start", "line_end", "chars", "parent", "source_page", "notes"]
    (OUT / f"{wid}.toc.tsv").write_text("\t".join(hdr) + "\n" + "".join("\t".join(str(x) for x in r) + "\n" for r in toc), encoding="utf-8")
    (OUT / f"{wid}.ingest.json").write_text(json.dumps({k: v for k, v in (("title", title), ("pages", src.get("tally")), ("notes", notes), ("revisions", revs)) if v or k in ("title", "notes")}, ensure_ascii=False, indent=1), encoding="utf-8")
    t = src.get("tally", {})
    body_chars = sum(len(l) for l in text.split("\n---\n", 1)[-1].split("\n"))
    print(f"{wid}: {body_chars:,} chars · {len(toc)} divisions · depth {max((r[1] for r in toc), default=0)} · {sum(1 for r in toc if r[12])} flagged"
          + (f" · pages {sum(t.values())} = " + " + ".join(f"{k} {v}" for k, v in t.items()) if sum(t.values()) else ""))
    for n in notes:
        print("   -", n)


def adapters():
    return sorted(p.stem[len("adapter_"):] for p in pathlib.Path(__file__).parent.glob("adapter_*.py"))


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help") or a[0] not in adapters():
        print(__doc__)
        for name in adapters():
            print(importlib.import_module(f"adapter_{name}").USAGE)
        sys.exit(0 if a and a[0] in ("-h", "--help") else 2)
    mod = importlib.import_module(f"adapter_{a[0]}")
    out = pathlib.Path(a[2]) if len(a) > 2 else None
    if out is None:
        print(mod.USAGE); sys.exit(2)
    out.mkdir(parents=True, exist_ok=True)
    for src in mod.sources(CORE, a[1], out, a[3:]):
        write(src, out)


CORE = sys.modules[__name__]

if __name__ == "__main__":
    main()
