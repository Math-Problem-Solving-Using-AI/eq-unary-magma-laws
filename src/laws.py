"""Enumerate equational laws over one binary op (*) and one unary op (f).

Law = lhs = rhs. Size ("order") = total count of * and f symbols in both sides.
Laws are deduplicated up to variable renaming and swapping the two sides.
Trivial laws (lhs == rhs) are dropped.

Term encoding (nested tuples):
    ('v', i)        variable number i
    ('f', t)        unary op applied to t
    ('m', t, s)     binary op t * s
"""
import json
import sys
from functools import lru_cache

VARS = "xyzwuvabcdefgh"


@lru_cache(None)
def shapes(k):
    """All term shapes with exactly k operation nodes; leaves are ('L',)."""
    if k == 0:
        return (("L",),)
    out = [("f", s) for s in shapes(k - 1)]
    for i in range(k):
        for a in shapes(i):
            for b in shapes(k - 1 - i):
                out.append(("m", a, b))
    return tuple(out)


def n_leaves(s):
    if s[0] == "L":
        return 1
    if s[0] == "f":
        return n_leaves(s[1])
    return n_leaves(s[1]) + n_leaves(s[2])


def fill(s, it):
    if s[0] == "L":
        return ("v", next(it))
    if s[0] == "f":
        return ("f", fill(s[1], it))
    a = fill(s[1], it)
    b = fill(s[2], it)
    return ("m", a, b)


def rgs(length):
    """Restricted growth strings = set partitions = variable labelings up to renaming."""
    def rec(prefix, mx):
        if len(prefix) == length:
            yield tuple(prefix)
            return
        for v in range(mx + 2):
            yield from rec(prefix + [v], max(mx, v))
    yield from rec([], -1)


def rename(l, r):
    """Relabel variables by order of first appearance in l then r."""
    mp = {}

    def go(t):
        if t[0] == "v":
            if t[1] not in mp:
                mp[t[1]] = len(mp)
            return ("v", mp[t[1]])
        if t[0] == "f":
            return ("f", go(t[1]))
        a = go(t[1])
        b = go(t[2])
        return ("m", a, b)

    return go(l), go(r)


def show(t):
    if t[0] == "v":
        return VARS[t[1]]
    if t[0] == "f":
        return "f(" + show(t[1]) + ")"
    a, b = t[1], t[2]
    sa = show(a) if a[0] != "m" else "(" + show(a) + ")"
    sb = show(b) if b[0] != "m" else "(" + show(b) + ")"
    return sa + "*" + sb


def show_law(law):
    return show(law[0]) + " = " + show(law[1])


def nvars(law):
    seen = set()

    def go(t):
        if t[0] == "v":
            seen.add(t[1])
        else:
            for c in t[1:]:
                go(c)

    go(law[0])
    go(law[1])
    return len(seen)


def ops(t):
    if t[0] == "v":
        return 0
    return 1 + sum(ops(c) for c in t[1:])


def enumerate_laws(max_order):
    """Return sorted list of canonical laws with 1 <= order <= max_order."""
    found = {}
    for total in range(1, max_order + 1):
        for k1 in range(total + 1):
            k2 = total - k1
            for s1 in shapes(k1):
                for s2 in shapes(k2):
                    nl = n_leaves(s1) + n_leaves(s2)
                    for part in rgs(nl):
                        it = iter(part)
                        l = fill(s1, it)
                        r = fill(s2, it)
                        if l == r:
                            continue
                        a = rename(l, r)
                        b = rename(r, l)
                        key = min(a, b)
                        found[key] = total
    laws = sorted(found, key=lambda law: (found[law], show_law(law)))
    return laws


def to_json(laws):
    return [
        {"id": i + 1, "text": show_law(l), "order": ops(l[0]) + ops(l[1]), "vars": nvars(l), "law": l}
        for i, l in enumerate(laws)
    ]


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    laws = enumerate_laws(n)
    by = {}
    for l in laws:
        o = ops(l[0]) + ops(l[1])
        by[o] = by.get(o, 0) + 1
    print("laws by order:", by, "total:", len(laws))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as fh:
            json.dump(to_json(laws), fh)
        print("wrote", sys.argv[2])
