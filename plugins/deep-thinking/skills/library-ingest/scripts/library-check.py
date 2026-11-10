#!/usr/bin/env python3
"""library-check — check canonical texts and their ledgers. Exit 1 when any work has an error.

  library-check.py <library folder> [work id …]

Per work:  ✓|✗ <id>  errors N · warnings N
  ✗ lines are format errors — the normalizer or a hand edit broke the format; fix and rerun.
  ! lines are warnings to sort by hand: a ledger note (skipped or duplicated number), an unusually long
    leaf division (a heading may be missing), long paragraphs that occur twice (text carried twice).
  · lines are facts for orientation.
"""
import collections, hashlib, pathlib, re, sys, unicodedata
REQ = ["title", "creator", "language", "type", "identifier", "source", "rights", "retrieved"]


def check(txt):
    err, warn, info = [], [], []
    raw = txt.read_bytes()
    if b"\r" in raw: err.append("CR line endings")
    s = raw.decode("utf-8")
    if not unicodedata.is_normalized("NFC", s): err.append("not NFC")
    L = s.split("\n")
    if L[0] != "---":
        err.append("no metadata block"); return err, warn, info
    end = L.index("---", 1)
    keys = {l.split(":", 1)[0]: l.split(":", 1)[1].strip() for l in L[1:end]}
    for k in REQ:
        if k not in keys: err.append(f"metadata key missing: {k}")
    if keys.get("rights") in ('"not stated"', '""'): warn.append("rights not stated — the source carries no rights statement")
    body = L[end + 1:]; off = end + 2
    heads = [(i + off, len(m.group(1)), m.group(2)) for i, l in enumerate(body) if (m := re.match(r"(#{1,6}) (.+)$", l))]
    if sum(1 for h in heads if h[1] == 1) != 1: err.append("there must be exactly one `#` title")
    if any(h[1] > 4 for h in heads): err.append("a heading is deeper than three levels (####)")
    prev = 1
    for ln, lv, t in heads:
        if lv > prev + 1: err.append(f"{ln}: heading level jumps {prev}→{lv} ({t})")
        prev = lv
    for i, l in enumerate(body):
        ln = i + off
        if l != l.rstrip() and not l.startswith("> "): err.append(f"{ln}: trailing whitespace")
        if i and l == "" and body[i - 1] == "": err.append(f"{ln}: two blank lines in a row"); break
        if l.startswith("#") and not re.match(r"#{1,6} \S", l): err.append(f"{ln}: a line starts with # but is not a heading")
        if re.match(r"(>|[-+*]( |$)|\d{1,9}[.)]( |$)|={3,}\s*$|-{3,}\s*$|`{3,}|~{3,})", l) and not l.startswith("> ") and l != "* * *":
            err.append(f"{ln}: body line would parse as a Markdown block: {l[:30]}")
        if l and not l.startswith(("#", ">", "[^")) and i + 1 < len(body) and body[i + 1] != "":
            err.append(f"{ln}: no blank line after the paragraph")
    refs = set(re.findall(r"\[\^(\d+)\](?!:)", s)); defs = set(re.findall(r"^\[\^(\d+)\]:", s, flags=re.M))
    if refs - defs: err.append(f"footnote marks without a definition: {sorted(refs - defs)[:5]}")
    if defs - refs: warn.append(f"footnote definitions never referenced: {sorted(defs - refs)[:5]}")
    toc = txt.with_name(txt.stem + ".toc.tsv")
    if not toc.exists():
        err.append("no ledger (.toc.tsv)")
    else:
        rows = [r.split("\t") for r in toc.read_text().split("\n")[1:] if r]
        hl = {ln: (lv, t) for ln, lv, t in heads if lv > 1}
        if len(rows) != len(hl): err.append(f"ledger has {len(rows)} rows, text has {len(hl)} headings")
        if not rows and len(s) > 20000: warn.append("no divisions at all — the headings were not recognized; write a `headings` rule")
        if len({r[0] for r in rows}) != len(rows): err.append("duplicate division id in the ledger")
        for r in rows:
            ln = int(r[7])
            if ln not in hl or hl[ln][1] != r[4]:
                err.append(f"ledger {r[0]}: no heading 「{r[4]}」 at line {ln}"); break
            if r[12]: warn.append(f"{r[0]} 「{r[4]}」 (line {ln}): {r[12]}")
        leaves = [(int(r[9]), r) for r in rows if not any(x[10] == r[0] for x in rows)]
        if len(leaves) >= 3:
            med = sorted(c for c, _ in leaves)[len(leaves) // 2]
            for c, r in leaves:
                if med and c > 6 * med and c > 8000:
                    warn.append(f"{r[0]} 「{r[4]}」 (line {r[7]}): {c:,} chars, {c // med}× the median leaf — a heading may be missing in the source")
        big = sorted(leaves, key=lambda x: -x[0])[:3]
        info.append(f"{len(rows)} divisions; longest leaves: " + ", ".join(f"{r[0]} {c:,}" for c, r in big))
        first = min((int(r[7]) for r in rows), default=None)
        pre = sum(len(l) for l in L[end + 1:(first - 1 if first else len(L))] if l and not l.startswith("# "))
        if pre > 3000: warn.append(f"{pre:,} chars of text before the first division — a title page and front matter, or a first division whose heading was lost")
        elif pre > 400: info.append(f"{pre:,} chars of text before the first division (title page, front matter)")
        sib = collections.defaultdict(list)
        for r in rows: sib[(r[10], r[4])].append(r[0])
        for (par, h), ids in sib.items():
            if len(ids) > 1 and not h.isdigit(): warn.append(f"sibling divisions share the heading 「{h}」: {', '.join(ids)}")
    seen = collections.defaultdict(list)
    for i, l in enumerate(body):
        if len(l) >= 80: seen[hashlib.sha1(l.encode()).hexdigest()].append(i + off)
    dup = [v for v in seen.values() if len(v) > 1]; tot = sum(len(v) for v in seen.values())
    if dup and tot and sum(len(v) - 1 for v in dup) / tot > 0.02:
        err.append(f"{sum(len(v) - 1 for v in dup)} of {tot} long paragraphs are repeats — the same text was ingested twice")
    elif dup:
        warn.append(f"{len(dup)} long paragraph(s) occur twice, at lines " + "; ".join("/".join(map(str, v)) for v in dup[:6]))
    return err, warn, info


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(0 if len(sys.argv) > 1 else 2)
    D = pathlib.Path(sys.argv[1]); only = sys.argv[2:]; bad = 0; n = 0
    for t in sorted(D.glob("*.txt")):
        if only and t.stem not in only: continue
        err, warn, info = check(t); bad += bool(err); n += 1
        print(f"{'✗' if err else '✓'} {t.stem}  errors {len(err)} · warnings {len(warn)}")
        for e in err[:10]: print("   ✗", e)
        for w in warn[:12]: print("   !", w)
        if len(warn) > 12: print(f"   ! … and {len(warn) - 12} more warnings of the same kinds")
        for i in info: print("   ·", i)
    print(f"checked {n} work(s), {bad} with errors")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
