"""Refute open pairs with infinite term structures built from the source law used as a rewrite rule.

Every open source law has the shape  t = v  with v a variable that occurs in t. Read it as a rule
t -> v. The structure T_A: elements are all formal terms over generators g0, g1, ... built with
F(.) and P(.,.); f(a) is F(a) and a*b is P(a,b), except when that new term is an instance t.s of the
rule's left side, in which case the result is s(v). If no proper non-variable subterm of t unifies
with a renamed copy of t (no "overlap"), T_A satisfies A (hand argument in steps/16; checked on all
terms by z3 in src/check_term_rewriting.py). Evaluating both sides of B with B's variables sent to
distinct generators gives two terms; if they differ, B fails in T_A, so A does not imply B.

Only the open pairs (as in src/search_open_larger.py) are tried. Writes one certificate per refuted
pair; pairs whose source law has an overlap are left out (counted in the printout).

Usage: python src/refute_by_rewriting.py laws_json status_npz etp_json retry_json out_json cert_json...
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import VARS, show  # noqa: E402
from prove import tuplify  # noqa: E402
from search_open_larger import open_pairs  # noqa: E402


def rename(t, k):
    if t[0] == "v":
        return ("v", t[1] + k)
    return (t[0],) + tuple(rename(c, k) for c in t[1:])


def walk(t, s):
    while t[0] == "v" and t[1] in s:
        t = s[t[1]]
    return t


def occurs(v, t, s):
    t = walk(t, s)
    if t[0] == "v":
        return t[1] == v
    return any(occurs(v, c, s) for c in t[1:])


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


def subterms(t):
    yield t
    if t[0] != "v":
        for c in t[1:]:
            yield from subterms(c)


def has_overlap(lhs):
    copy = rename(lhs, 100)
    return any(s[0] != "v" and unify(s, copy, {}) is not None for s in list(subterms(lhs))[1:])


def orient(law):
    """(t, v) with the law read as t -> v, or None if neither side is a variable occurring in the other."""
    for t, r in (law, law[::-1]):
        if r[0] == "v" and t[0] != "v" and any(s == r for s in subterms(t)):
            return t, r[1]
    return None


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


def value(term, lhs, v):
    """Value of a law side in T_A, variable i sent to generator gi. An element is kept as a term over
    ('g', i), ('f', a), ('m', a, b) so that the rule can be matched on it; text() prints F and P."""
    if term[0] == "v":
        return ("g", term[1])
    new = (term[0],) + tuple(value(c, lhs, v) for c in term[1:])
    s = match(lhs, new, {})
    return s[v] if s is not None else new


def text(e):
    if e[0] == "g":
        return f"g{e[1]}"
    return f"{'F' if e[0] == 'f' else 'P'}({','.join(text(c) for c in e[1:])})"


def main():
    laws_file, status_file, etp_file, retry_file, out, *cert_files = sys.argv[1:]
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    certs = [json.load(open(c)) for c in cert_files]
    pairs = open_pairs(entries, codes, json.load(open(etp_file)), json.load(open(retry_file)), certs)
    results, count = {}, Counter()
    for a, b in pairs:
        o = orient(laws[a])
        if o is None:
            count["source not of the form t = v"] += 1
            continue
        lhs, v = o
        if has_overlap(lhs):
            count["source rule has an overlap (not tried)"] += 1
            continue
        lb, rb = laws[b]
        left = value(lb, lhs, v)
        right = value(rb, lhs, v)
        if left == right:
            count["both sides of B equal in T_A (no refutation)"] += 1
            continue
        nb = len({s[1] for side in laws[b] for s in subterms(side) if s[0] == "v"})
        results[f"{a},{b}"] = {
            "A": texts[a], "B": texts[b], "rule": f"{show(lhs)} -> {VARS[v]}",
            "witness": {VARS[i]: f"g{i}" for i in range(nb)},
            "B_left": text(left), "B_right": text(right)}
        count["refuted"] += 1
    json.dump(results, open(out, "w"), indent=1)
    print(f"open pairs: {len(pairs)}")
    for k, n in count.items():
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
