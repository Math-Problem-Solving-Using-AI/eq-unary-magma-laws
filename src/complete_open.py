"""Knuth-Bendix completion for the open pairs whose source rule overlaps itself (step 17).

Step 16 read each open source law A (shape t = v, v a variable in t) as one rule t -> v and settled the
pairs where that rule has no overlap. Here the source laws with an overlap are completed: the equations
produced by overlaps (critical pairs) are added as new rules, oriented by the Knuth-Bendix order (KBO,
weight 1 for f, * and every variable, one of the two precedences f > * or * > f), until every critical
pair is joinable. A run gives up when an equation cannot be oriented or a limit is reached.

When completion ends with a rule set R, R is terminating (KBO) and confluent (all critical pairs join,
Newman's lemma), so normal forms are unique. The structure T_R: elements are the R-normal forms of terms
over generators g0, g1, ...; f(e) and d*e are the normal forms of F(e) and P(d,e). A's two sides have the
same normal form, so T_R satisfies A. For a target B, both sides are normalized with B's letters sent to
distinct generators: different normal forms mean B fails in T_R (A does not imply B); equal normal forms
mean B follows from A, because every rule of R is derived from A.

Every derived equation is stored with its derivation: a chain of steps from its left to its right side,
each step "replace the instance under substitution s of side d of an earlier equation, at position p".
src/check_completion.py re-checks all of it without importing this file.

Output: {"sources": {a: {A, precedence, facts, rules}}, "pairs": {"a,b": {A, B, verdict, B_left,
B_right}}}. Terms are written f(t), m(s,t) and v0, v1, ... for variables (generators when evaluating B).

Usage: python src/complete_open.py laws_json status_npz etp_json retry_json out_json cert_json...
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prove import tuplify  # noqa: E402
from refute_by_rewriting import has_overlap, orient  # noqa: E402
from search_open_larger import open_pairs  # noqa: E402

MAX_RULES = 40
MAX_SIZE = 14
MAX_EQUATIONS = 4000


def size(t):
    return 1 if t[0] == "v" else 1 + sum(size(c) for c in t[1:])


def varcount(t, c=None):
    c = Counter() if c is None else c
    if t[0] == "v":
        c[t[1]] += 1
    else:
        for x in t[1:]:
            varcount(x, c)
    return c


def kbo_greater(s, t, prec):
    """s > t in KBO, all weights 1, prec maps 'f' and 'm' to their rank."""
    if s == t or s[0] == "v":
        return False
    cs, ct = varcount(s), varcount(t)
    if any(cs[x] < n for x, n in ct.items()):
        return False
    if t[0] == "v":
        return True
    ws, wt = size(s), size(t)
    if ws != wt:
        return ws > wt
    if s[0] != t[0]:
        return prec[s[0]] > prec[t[0]]
    for x, y in zip(s[1:], t[1:]):
        if x != y:
            return kbo_greater(x, y, prec)
    return False


def subst(t, s):
    if t[0] == "v":
        return s.get(t[1], t)
    return (t[0],) + tuple(subst(c, s) for c in t[1:])


def walk(t, s):
    while t[0] == "v" and t[1] in s:
        t = s[t[1]]
    return t


def resolve(t, s):
    t = walk(t, s)
    if t[0] == "v":
        return t
    return (t[0],) + tuple(resolve(c, s) for c in t[1:])


def occurs(v, t, s):
    t = walk(t, s)
    return t[1] == v if t[0] == "v" else any(occurs(v, c, s) for c in t[1:])


def unify(a, b, s):
    a, b = walk(a, s), walk(b, s)
    if a == b:
        return s
    if a[0] == "v":
        return None if occurs(a[1], b, s) else {**s, a[1]: b}
    if b[0] == "v":
        return unify(b, a, s)
    if a[0] != b[0]:
        return None
    for x, y in zip(a[1:], b[1:]):
        s = unify(x, y, s)
        if s is None:
            return None
    return s


def match(p, t, s):
    if p[0] == "v":
        if p[1] in s:
            return s if s[p[1]] == t else None
        return {**s, p[1]: t}
    if t[0] != p[0]:
        return None
    for x, y in zip(p[1:], t[1:]):
        s = match(x, y, s)
        if s is None:
            return None
    return s


def positions(t, p=()):
    yield p, t
    if t[0] != "v":
        for i, c in enumerate(t[1:]):
            yield from positions(c, p + (i,))


def at(t, p):
    for i in p:
        t = t[1 + i]
    return t


def replace(t, p, u):
    if not p:
        return u
    k = 1 + p[0]
    return t[:k] + (replace(t[k], p[1:], u),) + t[k + 1:]


def variables(t):
    return {x for x in varcount(t)}


class Completion:
    def __init__(self, law, prec):
        self.prec = prec
        self.facts = [(law[0], law[1], None)]  # (left, right, chain); fact 0 is A itself
        self.rules = []  # (left, right, fact id, direction)
        self.next_var = 1 + max(variables(law[0]) | variables(law[1]))

    def sides(self, fid, d):
        l, r, _ = self.facts[fid]
        return (l, r) if d == 1 else (r, l)

    def full_subst(self, fid, s):
        l, r, _ = self.facts[fid]
        return {x: s.get(x, ("v", x)) for x in sorted(variables(l) | variables(r))}

    def normalize(self, t):
        steps = []
        while True:
            for p, u in positions(t):
                for l, r, fid, d in self.rules:
                    s = match(l, u, {})
                    if s is not None:
                        steps.append((fid, d, p, self.full_subst(fid, s)))
                        t = replace(t, p, subst(r, s))
                        break
                else:
                    continue
                break
            else:
                return t, steps

    def fresh(self, fid):
        l, r, _ = self.facts[fid]
        ren = {}
        for x in sorted(variables(l) | variables(r)):
            ren[x] = ("v", self.next_var)
            self.next_var += 1
        return ren

    def critical_pairs(self, i, j):
        """Overlaps of rule i into a non-variable position of rule j (both renamed apart)."""
        out = []
        l1, r1, f1, d1 = self.rules[i]
        l2, r2, f2, d2 = self.rules[j]
        ren1, ren2 = self.fresh(f1), self.fresh(f2)
        a1, b1 = subst(l1, ren1), subst(r1, ren1)
        a2, b2 = subst(l2, ren2), subst(r2, ren2)
        for p, u in positions(a2):
            if u[0] == "v" or (i == j and p == ()):
                continue
            th = unify(a1, u, {})
            if th is None:
                continue
            peak = resolve(a2, th)
            left = replace(peak, p, resolve(b1, th))
            right = resolve(b2, th)
            s1 = {x: resolve(subst(("v", x), ren1), th) for x in self.full_subst(f1, {})}
            s2 = {x: resolve(subst(("v", x), ren2), th) for x in self.full_subst(f2, {})}
            chain = [(f1, -d1, p, s1), (f2, d2, (), s2)]
            out.append((left, right, chain))
        return out

    def run(self):
        todo = [(self.facts[0][0], self.facts[0][1], [])]  # chain [] for A itself: handled below
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
            if self.facts[0][2] is None and not chain:  # A itself
                chain = [(0, 1, (), {x: ("v", x) for x in self.full_subst(0, {})})]
            chain = [(f, -d, p, sb) for f, d, p, sb in reversed(st)] + chain + tt
            if max(size(s2), size(t2)) > MAX_SIZE:
                return "term size limit"
            if kbo_greater(s2, t2, self.prec):
                l, r, d = s2, t2, 1
            elif kbo_greater(t2, s2, self.prec):
                l, r, d = t2, s2, -1
            else:
                return f"cannot orient {show(s2)} = {show(t2)}"
            self.facts.append((s2, t2, chain))
            fid = len(self.facts) - 1
            new = (l, r, fid, d)
            keep = []
            for rule in self.rules:  # interreduce
                rl, rr, rf, rd = rule
                if match(l, rl, {}) is not None or any(match(l, u, {}) is not None for _, u in positions(rl)):
                    todo.append((rl, rr, [(rf, rd, (), self.full_subst(rf, {}))]))
                    continue
                keep.append(rule)
            self.rules = keep + [new]
            for k, (rl, rr, rf, rd) in enumerate(self.rules):
                nr, steps = self.normalize(rr)
                if nr != rr:
                    self.facts.append((rl, nr, [(rf, rd, (), self.full_subst(rf, {}))] + steps))
                    self.rules[k] = (rl, nr, len(self.facts) - 1, 1)
            if len(self.rules) > MAX_RULES:
                return "rule limit"
            n = len(self.rules) - 1
            for k in range(len(self.rules)):
                todo += self.critical_pairs(k, n)
                if k != n:
                    todo += self.critical_pairs(n, k)
        return "complete"


def show(t):
    if t[0] == "v":
        return f"v{t[1]}"
    return f"{t[0]}({','.join(show(c) for c in t[1:])})"


def main():
    laws_file, status_file, etp_file, retry_file, out, *cert_files = sys.argv[1:]
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    certs = [json.load(open(c)) for c in cert_files]
    pairs = open_pairs(entries, codes, json.load(open(etp_file)), json.load(open(retry_file)), certs)
    rows = {}
    for a, b in pairs:
        o = orient(laws[a])
        if o is not None and has_overlap(o[0]):
            rows.setdefault(a, []).append(b)
    sources, results, count = {}, {}, Counter()
    for a in sorted(rows):
        done = None
        for name, prec in (("f > *", {"f": 2, "m": 1}), ("* > f", {"f": 1, "m": 2})):
            c = Completion(laws[a], prec)
            outcome = c.run()
            print(f"law {a + 1} {texts[a]} ({name}): {outcome}, {len(c.rules)} rules, {len(c.facts)} equations",
                  flush=True)
            if outcome == "complete":
                done = (name, c)
                break
        if done is None:
            count["pairs whose source did not complete"] += len(rows[a])
            continue
        name, c = done
        sources[str(a)] = {
            "A": texts[a], "precedence": name,
            "facts": [{"left": show(l), "right": show(r),
                       "chain": None if ch is None else [
                           {"fact": f, "dir": d, "pos": list(p), "subst": {f"v{x}": show(u) for x, u in sb.items()}}
                           for f, d, p, sb in ch]}
                      for l, r, ch in c.facts],
            "rules": [{"fact": f, "dir": d, "rule": f"{show(l)} -> {show(r)}"} for l, r, f, d in c.rules]}
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
