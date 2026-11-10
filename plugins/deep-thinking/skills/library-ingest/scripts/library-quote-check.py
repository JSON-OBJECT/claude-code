#!/usr/bin/env python3
"""library-quote-check — verify an answer against the library. Exit 1 on any failure.

  library-quote-check.py <library root (the folder that holds library/)> < answer.md

What the answer must contain, and what is checked:

  QUOTE BLOCK — consecutive lines starting with "> ", the last of which is the anchor line:
      > 무론 영채는 제가 기생이 되고 싶어 된 것은 아니었다.
      > — 무정 > 13 · library/무정.txt:403
    Every line above the anchor line must occur word for word inside the anchored lines, and the anchor must
    be tight: it starts and ends on a line the quote touches. Put one "> " line per source line quoted.
    Whitespace is ignored; nothing else is. " … " inside a quote line marks an omission: each piece is
    checked, in order. The anchor is library/<file>.txt:<line> or :<start>-<end>.

  ABSENCE BLOCK — one line stating that spellings were searched and not found:
      > ∅ 직녀성: 바이칼 | 빠이칼 | Baikal
    The part before ":" is a work id, * for the whole library, or `* except <id>, <id>` for every work
    but those. Each spelling is searched again here; the block fails if any of them occurs as typed.
    A spelling matched only across a space (이혼 inside 「단단이 혼이」) passes with a `~` line naming the works.
  Not checked: the division path on an anchor line, the Coverage line, and any sentence outside a quote block.

  INTERPRETATION — a paragraph opening with [Interpretation] or [해석] must cite at least two different anchors,
    each a line that some quote block in the answer anchors.

An answer with no quote block and no absence block fails: it rests on nothing in the library.
"""
import pathlib, re, sqlite3, sys, unicodedata

A = re.compile(r"(library/[^\s:|)\]]+\.txt):(\d+)(?:-(\d+))?")


def N(s):
    s = re.sub(r"\\([#>+*.)\-])", r"\1", unicodedata.normalize("NFC", s))     # Markdown escapes are not text
    return re.sub(r"\s+", "", s)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(0 if len(sys.argv) > 1 else 2)
    root = pathlib.Path(sys.argv[1]); text = sys.stdin.read(); bad = []; warn = []; cache = {}; n_q = n_abs = 0
    quoted = set()                                          # (file, line) of every line a quote block anchors
    def span(f, a, z, where):
        fp = root / f
        if fp not in cache:
            cache[fp] = fp.read_text(encoding="utf-8").split("\n") if fp.is_file() else None
        L = cache[fp]
        if L is None:
            bad.append(f"{where}: no such file {f}"); return None
        if not (1 <= a <= z <= len(L)):
            bad.append(f"{where}: no such lines {f}:{a}-{z}"); return None
        if not L[a - 1].strip() or not L[z - 1].strip():
            bad.append(f"{where}: anchor {f}:{a}{'' if a == z else '-' + str(z)} starts or ends on a blank line — anchor the lines the quote sits on"); return None
        return [N(l) for l in L[a - 1:z]]
    lines = text.split("\n"); i = 0
    while i < len(lines):
        if not lines[i].startswith(">"):
            i += 1; continue
        j = i
        while j < len(lines) and lines[j].startswith(">"):
            j += 1
        block = [re.sub(r"^>\s?", "", l) for l in lines[i:j]]; first = i + 1; where = f"line {j}"; i = j
        if block[0].startswith("∅"):
          for k, bl in enumerate(block):                    # one absence statement per line
            where = f"line {first + k}"
            n_abs += 1
            m = re.match(r"∅\s*([^:]+):\s*(.+)$", bl)
            if not m:
                bad.append(f"{where}: absence block must read `> ∅ <work id, * or * except id, id>: spelling | spelling`"); continue
            scope, forms = m.group(1).strip(), [f.strip() for f in m.group(2).split("|") if f.strip()]
            db = root / "library" / "library.fts5.db"
            if not db.exists():
                bad.append(f"{where}: no index to verify the absence against"); continue
            con = sqlite3.connect(db)
            ex = re.fullmatch(r"\*\s+except\s+(.+)", scope)        # `* except <id>, <id>` — every work but these
            ids = [x.strip() for x in ex.group(1).split(",") if x.strip()] if ex else ([] if scope == "*" else [scope])
            unknown = [x for x in ids if not con.execute("SELECT 1 FROM works WHERE work_id=?", (x,)).fetchone()]
            if unknown:
                bad.append(f"{where}: no such work id `{unknown[0]}`"); continue
            marks = ",".join("?" * len(ids))
            cond = "" if scope == "*" else (f" AND work_id NOT IN ({marks})" if ex else " AND work_id = ?")
            for f in forms:
                q = N(f).lower()
                typed = r"\s+".join(re.escape(w) for w in f.split())
                real, chance, seen = {}, {}, []              # work → passages: as typed / only across a space
                loose = re.compile(r"\s*".join(re.escape(c) for c in q), flags=re.I)
                for wid, body, lns in con.execute("SELECT work_id, body, lns FROM passages WHERE instr(squeezed, ?) > 0" + cond, [q] + ids):
                    d = real if typed and re.search(typed, body, flags=re.I) else chance
                    d[wid] = d.get(wid, 0) + 1
                    if d is chance and len(seen) < 6:        # show the words as the text has them, with their line
                        for n, line in zip(lns.split(), body.split("\n")):
                            m = loose.search(line)
                            if m:
                                seen.append(f"{wid}:{n} 「{line[max(0, m.start() - 6):m.end() + 6].strip()}」"); break
                if real:
                    bad.append(f"{where}: `{f}` does occur in " + ", ".join(f"{w} ({n} passage{'s' if n > 1 else ''})" for w, n in sorted(real.items())) + " — not absent")
                elif chance:
                    warn.append(f"{where}: `{f}` is matched only across a space in " + ", ".join(f"{w} ({n} passage{'s' if n > 1 else ''})" for w, n in sorted(chance.items()))
                                + " — accepted as absent, as the text has it: " + ", ".join(seen) + (" …" if sum(chance.values()) > len(seen) else "")
                                + ". If that is the word itself — split by a stray space, or a phrase the text writes with a space — it is not absent")
          continue
        anchors = A.findall(block[-1])
        if not block[-1].lstrip().startswith(("—", "–", "-")) or not anchors:
            bad.append(f"{where}: quote block has no anchor line (`> — <path> · library/<file>.txt:<line>`)"); continue
        if len(block) < 2:
            bad.append(f"{where}: anchor line without a quote above it"); continue
        spans = [s for f, a, z in anchors if (s := span(f, int(a), int(z or a), where)) is not None]
        if len(spans) < len(anchors):
            continue                                        # the anchor itself was rejected above
        n_q += 1
        def inside(span_lines):
            hay, pos = "".join(span_lines), 0
            for piece in re.split(r"\s…\s|\(중략\)|\[…\]", "\n".join(block[:-1])):
                for qline in piece.split("\n"):
                    q = N(qline)
                    if not q: continue
                    k = hay.find(q, pos)
                    if k < 0:
                        miss.append(qline.strip()); return False
                    pos = k + len(q)
            return True
        miss = []
        hit = next((sp for sp in spans if inside(sp)), None)
        for f, a, z in anchors:
            quoted.update((f, n) for n in range(int(a), int(z or a) + 1))
        if hit is None:
            bad.append(f"{where}: not in the anchored lines — 「{(miss[0] if miss else block[0])[:60]}」")
        elif len(hit) > 1 and (inside(hit[1:]) or inside(hit[:-1])):
            bad.append(f"{where}: anchor range is wider than the quote — narrow it to the lines the quote sits on")
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if p.startswith(("[해석]", "[Interpretation]")):
            anchors = set(A.findall(p))
            if len(anchors) < 2:
                bad.append(f"interpretation cites {len(anchors)} distinct anchor(s), needs two: {p[:40]}…")
            for f, a, z in sorted(anchors):
                if span(f, int(a), int(z or a), "interpretation") is not None and (f, int(a)) not in quoted:
                    bad.append(f"interpretation cites {f}:{a}, a line no quote block above anchors — quote it first")
    if not n_q and not n_abs and not bad:
        bad.append("no quote block and no absence block — the answer rests on nothing in the library")
    n_int = sum(1 for p in text.split("\n") if p.lstrip().startswith(("[Interpretation]", "[해석]")))
    print("\n".join(bad) if bad else f"quote-check ok — {n_q} quote block(s), {n_abs} absence block(s), {n_int} interpretation paragraph(s)")
    for w in warn:
        print("~ " + w)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
