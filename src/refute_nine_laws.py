"""Rows of the laws with no small model (code 5) whose rule t -> v has no overlap: the T_A of step 16.

Same structure and search as src/refute_by_rewriting.py, run on code 5 pairs instead of open code 6 pairs.
For each target B: if the two sides of B differ in T_A, write a certificate in the format of
results/refutations_term_rewriting.json (checked by src/check_term_rewriting.py). If they are equal, the
rewriting steps that made them equal are instances of A; write them as a derivation in the format of
results/derivations_open.json (checked by src/check_derivations.py): B's left side is rewritten to its
normal form, then the steps of B's right side are replayed backwards.

Usage: python src/refute_nine_laws.py laws_json status_npz refutations_out derivations_out
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import VARS, show  # noqa: E402
from prove import tuplify  # noqa: E402
from refute_by_rewriting import has_overlap, match, orient, subterms, text, value  # noqa: E402


def term_text(t):
    return f"v{t[1]}" if t[0] == "v" else f"{t[0]}({','.join(term_text(c) for c in t[1:])})"


def normalize(t, lhs, v, d, pos, steps):
    """Innermost normal form of a law term under t -> v; each rewrite is appended as a step on fact 0."""
    if t[0] == "v":
        return t
    new = (t[0],) + tuple(normalize(c, lhs, v, d, pos + [i], steps) for i, c in enumerate(t[1:]))
    s = match(lhs, new, {})
    if s is None:
        return new
    steps.append({"fact": 0, "dir": d, "pos": pos, "subst": {f"v{i}": term_text(u) for i, u in sorted(s.items())}})
    return s[v]


def main():
    laws_file, status_file, ref_out, der_out = sys.argv[1:]
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    refs, sources, pairs, count, skipped = {}, {}, {}, Counter(), []
    for a in sorted({int(a) for a in np.argwhere(codes == 5)[:, 0]}):
        o = orient(laws[a])
        if o is None or has_overlap(o[0]):
            skipped.append(a + 1)
            continue
        lhs, v = o
        d = 1 if lhs == laws[a][0] else -1
        facts = [{"left": term_text(laws[a][0]), "right": term_text(laws[a][1]), "chain": None}]
        for b in np.argwhere(codes[a] == 5)[:, 0]:
            b = int(b)
            lb, rb = laws[b]
            left, right = value(lb, lhs, v), value(rb, lhs, v)
            if left != right:
                nb = len({s[1] for side in laws[b] for s in subterms(side) if s[0] == "v"})
                refs[f"{a},{b}"] = {
                    "A": texts[a], "B": texts[b], "rule": f"{show(lhs)} -> {VARS[v]}",
                    "witness": {VARS[i]: f"g{i}" for i in range(nb)},
                    "B_left": text(left), "B_right": text(right)}
                count["refuted"] += 1
                continue
            sl, sr = [], []
            nl, nr = normalize(lb, lhs, v, d, [], sl), normalize(rb, lhs, v, d, [], sr)
            assert nl == nr, (a, b)
            chain = sl + [{**st, "dir": -st["dir"]} for st in reversed(sr)]
            facts.append({"left": term_text(lb), "right": term_text(rb), "chain": chain})
            pairs[f"{a},{b}"] = {"A": texts[a], "B": texts[b], "verdict": "holds", "fact": len(facts) - 1}
            count["implied (derivation)"] += 1
        sources[str(a)] = {"A": texts[a], "facts": facts}
    json.dump(refs, open(ref_out, "w"), indent=1)
    json.dump({"sources": sources, "pairs": pairs}, open(der_out, "w"), indent=1)
    print(f"rows of code 5 laws: {len(sources)} with an overlap-free rule; skipped (no such rule): laws {skipped}")
    for k, n in count.items():
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
