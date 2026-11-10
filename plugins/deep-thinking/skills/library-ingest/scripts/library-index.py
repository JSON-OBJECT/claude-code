#!/usr/bin/env python3
"""library-index — index the library's canonical texts by passage → <library>/library.fts5.db

  library-index.py <library folder> [--target 1500]

One row = consecutive paragraphs inside one leaf division (about `target` characters); a passage never
crosses a heading, and each heading is a one-line passage of its own. Matching runs on `squeezed` — the passage lower-cased with all whitespace removed — so a
word the source split with a stray space ("가까 운") or wrote with different spacing still matches.
"""
import json, pathlib, re, sqlite3, sys


def squeeze(s):
    s = re.sub(r"\\([#>+*.)\-])", r"\1", s)                   # Markdown escapes are not text
    return re.sub(r"\s+", "", s).lower()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(0 if len(sys.argv) > 1 else 2)
    D = pathlib.Path(sys.argv[1]); target = int(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else 1500
    db = D / "library.fts5.db"
    for f in (db, db.with_name(db.name + "-wal"), db.with_name(db.name + "-shm")):
        f.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.executescript("""
      CREATE TABLE works(work_id TEXT PRIMARY KEY, title, creator, translator, editor, date, type, language, file, chars INT, divisions INT, structure);
      CREATE TABLE divisions(work_id, div_id, level INT, type, heading, path, line_start INT, line_end INT, chars INT, notes);
      CREATE VIRTUAL TABLE passages USING fts5(work_id UNINDEXED, div_id UNINDEXED, path UNINDEXED, line_start UNINDEXED,
                                               line_end UNINDEXED, body UNINDEXED, lns UNINDEXED, squeezed, tokenize='trigram');""")
    n_pass = 0
    for txt in sorted(D.glob("*.txt")):
        L = txt.read_text(encoding="utf-8").split("\n")
        end = L.index("---", 1)
        meta = {}
        for l in L[1:end]:
            k, v = l.split(":", 1); v = v.strip()
            meta[k] = json.loads(v) if v.startswith('"') else v
        wid = meta["identifier"]
        rows = [r.split("\t") for r in txt.with_name(txt.stem + ".toc.tsv").read_text().split("\n")[1:] if r]
        by_line = {int(r[7]): r for r in rows}; by_id = {r[0]: r for r in rows}
        def path(r):
            p = [r[4]]
            while r[10]:
                r = by_id[r[10]]; p.append(r[4])
            return " > ".join([meta["title"]] + p[::-1])
        for r in rows:
            con.execute("INSERT INTO divisions VALUES(?,?,?,?,?,?,?,?,?,?)", (wid, r[0], int(r[1]), r[2], r[4], path(r), int(r[7]), int(r[8]), int(r[9]), r[12]))
        cur_id, cur_path = "", meta["title"]
        buf, nums, start, last, size, prev = [], [], 0, 0, 0, None
        def flush():
            nonlocal buf, nums, size, n_pass, prev
            if buf:
                body = "\n".join(buf); ln_s = " ".join(map(str, nums))
                if prev and prev[0] == cur_id and size < target // 4:        # a short tail joins the passage before it
                    con.execute("UPDATE passages SET line_end=?, body=body||char(10)||?, lns=lns||' '||?, squeezed=squeezed||? WHERE rowid=?", (last, body, ln_s, squeeze(body), prev[1]))
                else:
                    c = con.execute("INSERT INTO passages VALUES(?,?,?,?,?,?,?,?)", (wid, cur_id, cur_path, start, last, body, ln_s, squeeze(body))); n_pass += 1
                    prev = (cur_id, c.lastrowid)
            buf, nums, size = [], [], 0
        for i in range(end + 1, len(L)):
            ln, l = i + 1, L[i]
            if ln in by_line or l.startswith("# "):
                flush(); prev = None
                if ln in by_line:
                    cur_id, cur_path = by_line[ln][0], path(by_line[ln])
                    head = by_line[ln][4]                    # a heading is searchable too, as a one-line passage
                    con.execute("INSERT INTO passages VALUES(?,?,?,?,?,?,?,?)", (wid, cur_id, cur_path, ln, ln, head, str(ln), squeeze(head)))
                continue
            if not l or l == "* * *": continue
            if not buf: start = ln
            buf.append(l); nums.append(ln); last = ln; size += len(l)
            if size >= target and not l.startswith("> "): flush()
        flush()
        chars = sum(len(l) for l in L[end + 1:])
        con.execute("INSERT INTO works VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (wid, meta["title"], meta.get("creator", ""), meta.get("translator", ""), meta.get("editor", ""), meta.get("date", ""), meta.get("type", ""), meta.get("language", ""), txt.name, chars, len(rows), meta.get("structure", "")))
    con.commit()
    w = con.execute("SELECT count(*), coalesce(sum(chars),0) FROM works").fetchone()
    con.execute("VACUUM"); con.close()
    print(f"[OK] {w[0]} works · {w[1]:,} chars · {n_pass:,} passages → {db} ({db.stat().st_size/1048576:.1f} MB)")


if __name__ == "__main__":
    main()
