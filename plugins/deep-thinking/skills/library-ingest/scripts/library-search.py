#!/usr/bin/env python3
"""library-search — the single entry point for searching the library.

  library-search.py <library folder> [--work ID]… [--not-work ID]… [--all] [--limit 8] [--context 60] TERM [TERM …]
  library-search.py <library folder> --works            list the works
  library-search.py <library folder> --toc ID           list one work's divisions

TERM may be a spelling bundle: "중유|中有|bardo" counts any of its spellings as that one term.
Several TERMs: by default a passage matches when it has ANY of them, and passages holding more of the
terms rank first; --all keeps only passages that hold EVERY term.
Matching ignores whitespace and letter case, and works for terms of any length. Repeat --work to search several works; --not-work searches every work but the ones named.
A one-syllable spelling matches inside longer words; prefer the two-syllable forms a text would use (허숭|숭은|숭이).

Output, one hit per line:
  <file>:<start>-<end> | <division path> | <term>×<count> … | @<lines> | …<text around the first match>…
@<lines> are the file lines inside the passage where a term occurs (first thirty) — cite those, not the passage range.
A count reads ×N(+M): N matches as typed, M more that run across a space in the text ("이혼" inside "단단이 혼이").
The +M matches are usually not the word; passages with only such matches rank last. Headings are searched too.
When a spelling in a bundle occurs nowhere in the works in scope, the first line names it, so a mistyped spelling
does not hide.
The first line gives the total and, per work, passages and occurrences (as typed, then "+M across a space"); only --limit hits
are printed (raise it to see more). Spellings in one bundle that differ only in spacing or case count once.
In the text, " ⏎ " marks a paragraph break. Exit code is 0 whether or not anything matched.
"""
import pathlib, re, signal, sqlite3, sys
signal.signal(signal.SIGPIPE, signal.SIG_DFL)               # end quietly when the output is cut by `| head`


def squeeze(s):
    return re.sub(r"\s+", "", s).lower()


def exact(body, forms):
    """Occurrences of any spelling in `forms` with its own spacing kept, ignoring case. Each place in the text
    counts once: where spellings overlap (아편 inside 아편쟁이) the longer one takes it."""
    pats = sorted({r"\s+".join(re.escape(w) for w in f.split()) for f in forms if f.split()}, key=len, reverse=True)
    return len(re.findall("|".join(pats), body, flags=re.I)) if pats else 0


def loose_count(sq, forms):
    """The same count on squeezed text (whitespace removed), so it includes matches that run across a space."""
    pats = sorted({re.escape(squeeze(f)) for f in forms if squeeze(f)}, key=len, reverse=True)
    return len(re.findall("|".join(pats), sq)) if pats else 0


def find(body, form):
    """Position of `form` in body, ignoring whitespace and case."""
    m = re.search(r"\s*".join(re.escape(c) for c in squeeze(form)), body, flags=re.I)
    return m.start() if m else -1


def main():
    a = [x.encode("utf-8", "replace").decode("utf-8") for x in sys.argv[1:]]     # a truncated multibyte argument
    if not a or "-h" in a or "--help" in a:
        print(__doc__); sys.exit(0 if a else 2)
    D = pathlib.Path(a.pop(0))
    if not (D / "library.fts5.db").exists():
        sys.exit(f"no index at {D}/library.fts5.db — run library-index.py {D}")
    con = sqlite3.connect(D / "library.fts5.db")
    opt = {"--limit": 8, "--context": 60, "--toc": None}
    flags, terms, works, skip = set(), [], [], []
    while a:
        x = a.pop(0)
        if x == "--work": works.append(a.pop(0))
        elif x == "--not-work": skip.append(a.pop(0))
        elif x in opt: opt[x] = a.pop(0)
        elif x.startswith("--"): flags.add(x)
        else:                                               # spellings differing only in spacing or case are one spelling
            seen, forms = set(), []
            for v in x.split("|"):
                if squeeze(v) and squeeze(v) not in seen:
                    seen.add(squeeze(v)); forms.append(v)
            terms.append(forms)
    if "--works" in flags:
        for r in con.execute("SELECT work_id, title, creator, translator, editor, date, language, chars, divisions, structure FROM works ORDER BY work_id"):
            who = r[2] + (f" (tr. {r[3]})" if r[3] else "") + (f" (ed. {r[4]})" if r[4] else "")
            print(f"{r[0]} | {r[1]} | {who} | {r[5]} | {r[6]} | {r[7]:,} chars | {r[8]} divisions | {r[9]}")
        return
    files = dict(con.execute("SELECT work_id, file FROM works"))
    for w in [opt["--toc"]] + works + skip:
        if w and w not in files:
            sys.exit(f"no such work id: {w} — list ids with --works")
    if opt["--toc"]:
        for r in con.execute("SELECT div_id, path, line_start, line_end, chars, notes FROM divisions WHERE work_id=? ORDER BY line_start", (opt["--toc"],)):
            print(f"{r[0]} | {r[1]} | {r[2]}-{r[3]} | {r[4]:,} chars" + (f" | ! {r[5]}" if r[5] else "")); shown = True
        if "shown" not in dir():
            print(f"# {opt['--toc']} has no divisions — the whole text sits under the title; search it or read it by line range")
        return
    if not terms:
        print(__doc__); sys.exit(2)
    if skip:                                                # every work but these (within --work, when both are given)
        works = [w for w in (works or sorted(files)) if w not in skip]
        if not works:
            sys.exit("--not-work leaves no work to search")
    limit, ctx = int(opt["--limit"]), int(opt["--context"])
    conds, args = [], []
    for forms in terms:
        sub = []
        for f in forms:
            q = squeeze(f)
            if len(q) >= 3:
                sub.append("rowid IN (SELECT rowid FROM passages WHERE passages MATCH ?)"); args.append('squeezed:"' + q.replace('"', '""') + '"')
            else:                                           # the trigram index holds nothing shorter than three characters
                sub.append("instr(squeezed, ?) > 0"); args.append(q)
        conds.append("(" + " OR ".join(sub) + ")")
    where = (" AND " if "--all" in flags else " OR ").join(conds)
    if works:
        where = f"work_id IN ({','.join('?' * len(works))}) AND ({where})"; args = works + args
    rows = con.execute(f"SELECT work_id, path, line_start, line_end, body, squeezed, lns FROM passages WHERE {where}", args).fetchall()
    scored = []
    for wid, path, s, e, body, sq, lns in rows:
        ex = [exact(body, forms) for forms in terms]                      # matches that do not run across a space
        counts = [max(loose_count(sq, forms), x) for forms, x in zip(terms, ex)]
        scored.append((-sum(1 for c in ex if c), -sum(1 for c in counts if c), -sum(ex) * 1000 / max(len(sq), 300), wid, s, e, path, counts, body, lns, ex))
    scored.sort(key=lambda r: r[:5])
    scored = [(r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]) for r in scored]
    if not scored:
        print("# 0 hits — widen each spelling bundle (other scripts, spellings, inflections) and search again")
        return
    scope_sql = f" AND work_id IN ({','.join('?' * len(works))})" if works else ""
    n_forms = sum(len(forms) for forms in terms)
    dead = [f for forms in terms for f in forms if n_forms > 1 and not con.execute(
        "SELECT 1 FROM passages WHERE instr(squeezed, ?) > 0" + scope_sql + " LIMIT 1", [squeeze(f)] + works).fetchone()]
    only_loose = [f for forms in terms for f in forms if n_forms > 1 and f not in dead and not any(
        exact(b, [f]) for (b,) in con.execute("SELECT body FROM passages WHERE instr(squeezed, ?) > 0" + scope_sql,
                                              [squeeze(f)] + works))]   # in scope, but never as typed: only across a space
    occ = {}
    loose = {}
    for r in scored:
        occ[r[2]] = occ.get(r[2], 0) + sum(r[9]); loose[r[2]] = loose.get(r[2], 0) + sum(r[6]) - sum(r[9])
    per = {}
    for r in scored: per[r[2]] = per.get(r[2], 0) + 1
    print(f"# {len(scored)} passages match, showing {min(limit, len(scored))} · per work: " + ", ".join(f"{k} {v} ({occ[k]} occurrences" + (f", +{loose[k]} across a space" if loose[k] else "") + ")" for k, v in sorted(per.items(), key=lambda kv: (-occ[kv[0]], -kv[1], kv[0])))
          + (" · spellings with no hit: " + ", ".join(dead) if dead else "")
          + (" · spellings matched only across a space: " + ", ".join(only_loose) if only_loose else ""))
    for _, _, wid, s, e, path, counts, body, lns, ex in scored[:limit]:
        firsts = [p for forms in terms for f in forms if (p := find(body, f)) >= 0]
        p = min(firsts) if firsts else 0
        snip = body[max(0, p - ctx):p + ctx].replace("\n", " ⏎ ")
        at = [n for n, l in zip(lns.split(), body.split("\n")) if any(find(l, f) >= 0 for forms in terms for f in forms)]
        print(f"{D.name}/{files[wid]}:{s}-{e} | {path} | " + " ".join(f"{'|'.join(forms)}×{x}" + (f"(+{c - x})" if c > x else "") for forms, c, x in zip(terms, counts, ex))
              + f" | @{','.join(at[:30])}{'…' if len(at) > 30 else ''} | …{snip}…")


if __name__ == "__main__":
    main()
