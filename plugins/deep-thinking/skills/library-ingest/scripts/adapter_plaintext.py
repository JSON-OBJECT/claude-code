#!/usr/bin/env python3
"""Plain-text adapter — one txt file is one work.

· Encoding: UTF-8 (BOM allowed), else CP949. Line endings become LF.
· A Project Gutenberg header and footer (*** START/END OF …) are cut off; Title, Author, Translator, Editor and
  Language are read from the header.
· Paragraphs are blank-line separated. When the lines inside paragraphs crowd one width the text is hard-wrapped
  and they are joined — with a space, except between Han or kana characters. Otherwise each line is its own paragraph.
· A heading is a one-line paragraph that reads as a division mark: 제N장, 第N章, CHAPTER N, a bare numeral or Roman
  numeral, a front-matter word (Preface, 서문 …), or a Markdown heading line (## Title). Levels follow unit size:
  volume > part/book > chapter > section; Markdown headings rank by their number of #.
· Short lines indented two spaces or more are verse.
· Rules (<id>.rules.json): headings · disable_default_ranks · drop · wrapped — see the skill's rules table.
"""
import json
import pathlib
import re
import unicodedata

ORNAMENT = re.compile(r"^[\s🙝🙟❦❧*＊※×✕◇◆○●□■△▲☆★~∼〜─━—–\-_]+$")        # a line of dots is text, not a break
MD_HEAD = re.compile(r"^(#{1,6})\s+(\S.*)$")
RANK = [
    (1, re.compile(r"(?i)^(volume|vol\.)\s+([ivxlcdm]+|\d+)\b|^제?\s*\d+\s*권|^[上中下]卷|^[상중하]\s*권$|^第[〇○一二三四五六七八九十百\d]+卷")),
    (2, re.compile(r"(?i)^(book|part)\s+([ivxlcdm]+|\d+|the\s+\w+)\b|^제?\s*\d+\s*[부편]|^第[〇○一二三四五六七八九十百\d]+[部篇編]")),
    (3, re.compile(r"(?i)^chapter\s+([ivxlcdm]+|\d+)\b|^제?\s*\d+\s*[장회]\b|^제?\s*\d+\s*[장회]\s|^第[〇○一二三四五六七八九十百\d]+[章回]")),
    (3, re.compile(r"(?i)^(preface|foreword|introduction|prologue|epilogue|afterword|appendix|conclusion)\.?$|^(서문|머리말|서언|후기|발문|부록)$")),
    (4, re.compile(r"(?i)^section\s+\d+|^제?\s*\d+\s*절|^(\d{1,3}|[ivxlc]{1,7}|[〇○一二三四五六七八九十百]{1,5})\s*[.)]?$")),
]
NOSPACE = re.compile(r"[\u3000-\u30ff\u3400-\u9fff\uff00-\uffef]")   # Han, kana, full-width: scripts written without spaces


def _join(lines):
    out = lines[0]
    for l in lines[1:]:
        out += ("" if NOSPACE.search(out[-1:]) and NOSPACE.search(l[:1]) else " ") + l     # Hangul wraps at spaces
    return out


def parse_text(data, rules=None):
    rules = rules or {}
    off = set(rules.get("disable_default_ranks", []))
    custom = [(int(r["level"]), re.compile(r["pattern"]), bool(r.get("inline"))) for r in rules.get("headings", [])]
    drops = [re.compile(x) for x in rules.get("drop", [])]
    try:
        s = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        s = data.decode("cp949", errors="replace")
    s = unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n")).replace("\xa0", " ")
    meta = {}
    a = re.search(r"^\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", s, flags=re.M)
    if a:
        head = s[:a.start()]
        for k, key in (("Title", "title"), ("Author", "creator"), ("Translator", "translator"), ("Editor", "editor"), ("Language", "language")):   # the release date is not the year of first publication
            m = re.search(rf"^{k}: (.+)$", head, flags=re.M)
            if m: meta[key] = m.group(1).strip()
        meta["language"] = {"English": "en", "Korean": "ko", "Japanese": "ja", "Chinese": "zh", "German": "de", "French": "fr"}.get(meta.get("language", ""), meta.get("language", ""))
        meta["rights"] = "Public domain in the USA (Project Gutenberg License)"
        z = re.search(r"^\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", s, flags=re.M)
        s = s[a.end():z.start() if z else len(s)]
    chunks, cur, gap, gaps = [], [], 0, []              # chunks, and the blank lines before each
    for l in s.split("\n"):
        if l.strip():
            if not cur: gaps.append(gap)
            cur.append(l.rstrip()); gap = 0
        else:
            if cur: chunks.append(cur); cur = []
            gap += 1
    if cur: chunks.append(cur)
    # Hard-wrapped text: the lines that are not the last of their paragraph crowd up against one width.
    inner = sorted(len(l) for c in chunks if len(c) > 1 for l in c[:-1])
    if "wrapped" in rules:
        wrapped = bool(rules["wrapped"])
    elif len(inner) >= 20:
        width = inner[int(len(inner) * 0.95)]
        wrapped = sum(1 for n in inner if n >= 0.7 * width) >= 0.8 * len(inner)
    else:
        wrapped = False
    multi = sum(1 for c in chunks if len(c) > 1)             # blocks of several lines in a text read as not wrapped
    unsure = "wrapped" not in rules and not wrapped and multi >= 20 and multi >= 0.2 * len(chunks)
    blocks, found, illus, n_drop, gone = [], set(), False, 0, []
    for c, g in zip(chunks, gaps):
        first = c[0].strip()
        whole = " ".join(l.strip() for l in c)
        hit = next(((rank, pat.search(first), inline) for rank, pat, inline in custom if pat.search(first)), None)
        if not hit and (illus or re.match(r"\[Illustration", first, flags=re.I)):   # an [Illustration: … ] block spanning several chunks
            illus = whole.count("[") + (1 if illus else 0) > whole.count("]")
            continue
        illus = False                                    # a heading named by a rule survives even inside an illustration block
        lv, md = None, MD_HEAD.match(first) if len(c) == 1 else None
        if not hit and md:                               # a Markdown heading line left in the text
            lv, first = min(len(md.group(1)), 4), md.group(2)
        elif not hit and len(c) <= 2 and len(first) <= 80 and first.strip("○ "):   # a lone ○ is an ornament, not zero
            for rank, pat in RANK:
                if rank not in off and pat.search(first):
                    lv = rank; break
        if not hit and not lv and any(d.search(whole) for d in drops):     # `drop` never removes a heading
            n_drop += 1; gone.append(whole[:60] + ("…" if len(whole) > 60 else "")); continue
        if not hit and not lv and len(c) == 1 and ORNAMENT.match(first) and len(first) <= 40:
            blocks.append(("break",)); continue
        if hit and hit[2]:                               # a run-in heading: split it off, the rest stays a paragraph
            m = hit[1]
            title = (m.groupdict().get("h") or m.group(0)).strip()
            blocks.append(("h", hit[0], title)); found.add(hit[0])
            rest = [first[m.end():].strip()] + [l.strip() for l in c[1:]]
            rest = [l for l in rest if l]
            if rest: blocks.append(("p", re.sub(r"[ \t]+", " ", _join(rest))))
            continue
        if hit:
            lv = hit[0]
        if lv:
            title = first if len(c) == 1 else first + " " + c[1].strip()     # the chapter title on the line after "CHAPTER I."
            blocks.append(("h", lv, re.sub(r"\s+", " ", title))); found.add(lv); continue
        if not wrapped and len(c) > 1:
            for l in c:
                blocks.append(("p", re.sub(r"[ \t]+", " ", l.strip())))
            continue
        indented = sum(l.startswith(("  ", "\t")) for l in c) >= 0.8 * len(c) and len(c) > 1
        if indented and wrapped and max(len(l) for l in c) < 60:              # short indented lines = verse
            blocks.append(("lines", [l.strip() for l in c])); continue
        blocks.append(("p", re.sub(r"[ \t]+", " ", _join([l.strip() for l in c]))))
    order = sorted(found)                                                      # keep only the ranks that occur, densely
    blocks = [("h", order.index(b[1]) + 2, b[2]) if b[0] == "h" else b for b in blocks]
    tops = sorted(((g, gone.count(g)) for g in dict.fromkeys(gone)), key=lambda t: -t[1])
    meta["_notes"] = ([f"rules file dropped {n_drop} paragraph(s)"] if n_drop else []) + \
                     [f"dropped by `drop`: 「{g}」" + (f" ×{n}" if n > 1 else "") for g, n in tops[:40]] + \
                     ([f"… and {len(tops) - 40} more distinct paragraph(s)"] if len(tops) > 40 else []) + \
                     (["read as hard-wrapped because the rules file says `wrapped: true`: wrapped lines joined"] if wrapped and "wrapped" in rules
                      else [f"read as hard-wrapped at about {inner[int(len(inner) * 0.95)]} columns: wrapped lines joined"] if wrapped and inner
                      else ["read as one paragraph per blank-line-separated block: lines kept as written"]) + \
                     ([f"! {multi} of {len(chunks)} blocks hold several lines, yet no single wrap width was found — "
                       "read a few of them: if the lines break mid-sentence, set `wrapped: true`"] if unsure else [])
    return blocks, meta


USAGE = """  library-normalize.py plaintext <file.txt> <library folder> [--id ID] [--title T] [--creator C] [--translator T]
                                 [--editor E] [--date YEAR] [--language ko] [--type book|paper|report]
                                 [--source URL] [--rights LABEL]
      title · creator · origin · rights · retrieved come from the SOURCES.tsv row beside the file; flags override
      it, and a rules file's `meta` overrides both."""


def load(core, path, given, out):
    """One txt file → a source bundle. Metadata: file header, then the SOURCES.tsv row, then flags."""
    path = pathlib.Path(path)
    data = path.read_bytes()
    blocks, m = parse_text(data)
    src = path.parent / "SOURCES.tsv"                       # file · title · creator · origin · rights · retrieved
    if src.exists():
        for r in (l.split("\t") for l in src.read_text(encoding="utf-8").splitlines()):
            if len(r) >= 6 and r[0] == path.name:
                m.update({k: v for k, v in zip(("title", "creator", "source", "rights", "retrieved"), r[1:6]) if v.strip()})
    m.update({k: v for k, v in given.items() if v})
    if not (m.get("rights") or "").strip():
        raise SystemExit(f"{path.name}: no rights statement on record — add its rights label to SOURCES.tsv or pass --rights. "
                         "A source without one stays in raw/ and is not ingested.")
    title = m.pop("title", "") or path.stem
    wid = m.pop("id", "") or core.work_id_of(title)
    rf = out / f"{wid}.rules.json"                          # a rules file, when present, means parsing again under its rules
    if rf.exists():
        blocks, m2 = parse_text(data, json.loads(rf.read_text())); m["_notes"] = m2["_notes"]
    m.setdefault("language", "ko"); m.setdefault("type", "book"); m.setdefault("source", str(path))
    return {"title": title, "id": wid, "mblocks": blocks, "notes": m.pop("_notes", []), "meta": m}


def sources(core, source, out, rest):
    given = {}
    rest = list(rest)
    while rest:
        k = rest.pop(0).lstrip("-"); given[k] = rest.pop(0)
    yield load(core, source, given, out)
