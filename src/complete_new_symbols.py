"""Completion with new symbols for the open pairs whose plain completion stopped (step 18).

Step 17 (src/complete_open.py) gave up when an equation s = t could not be oriented, typically because one
side has a letter the other lacks, as in f(x)*z = f(x*x). Such an equation says that s, as a value, does not
depend on its letters outside V = (letters of s) & (letters of t). Here a new symbol h is introduced for that
value, with the definition  h(V) = s[w := x0 for every letter w of s not in V]  (x0 the first letter of V),
and the two rules  s -> h(V)  and  t -> h(V)  are added. Both follow from s = t and the definition. The new
symbols come last in the precedence, in order of creation; all weights are 1. A definition of a new symbol
by a term in the old ones is conservative: an equation without new symbols that follows from A and the
definitions follows from A alone. An equation with V empty is not handled (no letters to define h with).

Everything else is as in step 17: when completion ends, R terminates (KBO) and all critical pairs join, so
normal forms are unique and the structure T_R of normal forms over generators g0, g1, ... (with the new
symbols as extra operations, which the structure may simply forget) satisfies A. A target B whose sides,
with B's letters sent to distinct generators, have different normal forms fails in T_R (A does not imply B);
equal normal forms mean B follows from A and the definitions, hence from A.

Output: the format of results/completions_open.json, with "precedence" listing every symbol (for example
"f > * > h0 > h1") and definition facts stored as {"left", "right", "chain": null, "definition": true}.
src/check_completion.py checks both files.

Usage: python src/complete_new_symbols.py laws_json status_npz etp_json retry_json out_json cert_json...
(a cert_json in the format of results/completions_open.json counts its pairs as decided)
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from complete_open import (Completion, kbo_greater, match, positions, show, size, subst,  # noqa: E402
                           variables)
from prove import tuplify  # noqa: E402
from refute_by_rewriting import has_overlap, orient  # noqa: E402
from search_open_larger import open_pairs  # noqa: E402

MAX_RULES = 40
MAX_SIZE = 14
MAX_EQUATIONS = 4000
DEFINITION = "definition"


class NewSymbolCompletion(Completion):
    def __init__(self, law, prec):
        super().__init__(law, dict(prec))
        self.symbols = 0

    def ident(self, fid, s=None):
        return self.full_subst(fid, s or {})

    def add_rule(self, l, r, fid, d, todo):
        keep = []
        for rule in self.rules:  # interreduce, as in step 17
            rl, rr, rf, rd = rule
            if any(match(l, u, {}) is not None for _, u in positions(rl)):
                todo.append((rl, rr, [(rf, rd, (), self.ident(rf))]))
                continue
            keep.append(rule)
        self.rules = keep + [(l, r, fid, d)]
        for k, (rl, rr, rf, rd) in enumerate(self.rules):
            nr, steps = self.normalize(rr)
            if nr != rr:
                self.facts.append((rl, nr, [(rf, rd, (), self.ident(rf))] + steps))
                self.rules[k] = (rl, nr, len(self.facts) - 1, 1)
        n = len(self.rules) - 1
        for k in range(len(self.rules)):
            todo += self.critical_pairs(k, n)
            if k != n:
                todo += self.critical_pairs(n, k)

    def new_symbol(self, s, t, eq):
        """Facts and rules s -> h(V), t -> h(V) for the fact eq: s = t. Returns None or a reason to stop."""
        vs, vt = variables(s), variables(t)
        common = sorted(vs & vt)
        if vs == vt or not common:
            return f"cannot orient {show(s)} = {show(t)}"
        name = f"h{self.symbols}"
        self.symbols += 1
        self.prec[name] = -self.symbols
        h = (name,) + tuple(("v", x) for x in common)
        x0 = ("v", common[0])
        to_x0 = {w: x0 for w in vs - set(common)}
        self.facts.append((h, subst(s, to_x0), DEFINITION))
        dfn = len(self.facts) - 1
        # s -> t -> s[w := x0] -> h ; t -> s[w := x0] -> h
        chains = [(s, [(eq, 1, (), self.ident(eq)), (eq, -1, (), self.ident(eq, to_x0)),
                       (dfn, -1, (), self.ident(dfn))]),
                  (t, [(eq, -1, (), self.ident(eq, to_x0)), (dfn, -1, (), self.ident(dfn))])]
        out = []
        for side, chain in chains:
            if not kbo_greater(side, h, self.prec):
                return f"cannot orient {show(side)} -> {show(h)}"
            self.facts.append((side, h, chain))
            out.append((side, h, len(self.facts) - 1, 1))
        return out

    def run(self):
        todo = [(self.facts[0][0], self.facts[0][1], [])]
        seen = 0
        while todo:
            seen += 1
            if seen > MAX_EQUATIONS:
                return "equation limit"
            todo.sort(key=lambda e: size(e[0]) + size(e[1]))
            s, t, chain = todo.pop(0)
            s2, st = self.normalize(s)
            t2, tt = self.normalize(t)
            if s2 == t2:
                continue
            if not chain and s == self.facts[0][0] and t == self.facts[0][1]:  # A itself
                chain = [(0, 1, (), self.ident(0))]
            chain = [(f, -d, p, sb) for f, d, p, sb in reversed(st)] + chain + tt
            if max(size(s2), size(t2)) > MAX_SIZE:
                return "term size limit"
            if kbo_greater(s2, t2, self.prec):
                l, r, d = s2, t2, 1
            elif kbo_greater(t2, s2, self.prec):
                l, r, d = t2, s2, -1
            else:
                l = None
            self.facts.append((s2, t2, chain))
            fid = len(self.facts) - 1
            if l is not None:
                self.add_rule(l, r, fid, d, todo)
            else:
                new = self.new_symbol(s2, t2, fid)
                if isinstance(new, str):
                    return new
                for rule in new:
                    self.add_rule(*rule, todo)
            if len(self.rules) > MAX_RULES:
                return "rule limit"
        return "complete"


def precedence_text(prec):
    return " > ".join("*" if x == "m" else x for x in sorted(prec, key=lambda x: -prec[x]))


def fact_json(l, r, ch):
    if ch == DEFINITION:
        return {"left": show(l), "right": show(r), "chain": None, "definition": True}
    return {"left": show(l), "right": show(r),
            "chain": None if ch is None else [
                {"fact": f, "dir": d, "pos": list(p), "subst": {f"v{x}": show(u) for x, u in sb.items()}}
                for f, d, p, sb in ch]}


def main():
    laws_file, status_file, etp_file, retry_file, out, *cert_files = sys.argv[1:]
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    certs = [json.load(open(c)) for c in cert_files]
    decided = {k for cert in certs if "sources" in cert for k in cert["pairs"]}  # step 17 files
    certs = [cert for cert in certs if "sources" not in cert]
    pairs = open_pairs(entries, codes, json.load(open(etp_file)), json.load(open(retry_file)), certs)
    pairs = [(a, b) for a, b in pairs if f"{a},{b}" not in decided]
    rows = {}
    for a, b in pairs:
        o = orient(laws[a])
        if o is not None and has_overlap(o[0]):
            rows.setdefault(a, []).append(b)
    sources, results, count = {}, {}, Counter()
    for a in sorted(rows):
        done = None
        for prec in ({"f": 2, "m": 1}, {"f": 1, "m": 2}):
            c = NewSymbolCompletion(laws[a], prec)
            outcome = c.run()
            print(f"law {a + 1} {texts[a]} ({precedence_text(c.prec)}): {outcome}, {len(c.rules)} rules, "
                  f"{len(c.facts)} equations, {c.symbols} new symbols", flush=True)
            if outcome == "complete":
                done = c
                break
        if done is None:
            count["pairs whose source did not complete"] += len(rows[a])
            continue
        c = done
        sources[str(a)] = {"A": texts[a], "precedence": precedence_text(c.prec),
                           "facts": [fact_json(*fa) for fa in c.facts],
                           "rules": [{"fact": f, "dir": d, "rule": f"{show(l)} -> {show(r)}"}
                                     for l, r, f, d in c.rules]}
        for b in rows[a]:
            left, _ = c.normalize(laws[b][0])
            right, _ = c.normalize(laws[b][1])
            verdict = "holds" if left == right else "fails"
            count[f"B {verdict} in T_R"] += 1
            results[f"{a},{b}"] = {"A": texts[a], "B": texts[b], "verdict": verdict,
                                   "B_left": show(left), "B_right": show(right)}
    json.dump({"sources": sources, "pairs": results}, open(out, "w"), indent=1)
    print(f"open pairs: {len(pairs)}; from sources with an overlap: {sum(map(len, rows.values()))}")
    print(f"sources completed: {len(sources)} of {len(rows)}")
    for k, n in count.items():
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
