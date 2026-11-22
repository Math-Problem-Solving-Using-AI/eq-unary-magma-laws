"""S1 independent recount of the law enumeration, by a DIFFERENT algorithm.

laws.py: term shapes + set partitions of leaves + first-appearance renaming.
This file: brute force. Build every actual term over variables 0..m-1, pair them, and
canonicalize each pair as the minimum over ALL permutations of its variables and over
swapping the sides. Then compare counts and the exact set with laws.py.

Usage: python src/check_laws_count.py MAX_ORDER   (3 takes about a minute, 4 is slow)
"""
import itertools
import sys
from functools import lru_cache

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import enumerate_laws, ops  # noqa: E402


@lru_cache(None)
def terms(k, m):
    """All terms with exactly k operations over variables 0..m-1."""
    if k == 0:
        return tuple(("v", i) for i in range(m))
    out = [("f", t) for t in terms(k - 1, m)]
    for i in range(k):
        for a in terms(i, m):
            for b in terms(k - 1 - i, m):
                out.append(("m", a, b))
    return tuple(out)


def variables(t, acc):
    if t[0] == "v":
        acc.add(t[1])
    else:
        for c in t[1:]:
            variables(c, acc)


def apply(t, p):
    if t[0] == "v":
        return ("v", p[t[1]])
    if t[0] == "f":
        return ("f", apply(t[1], p))
    return ("m", apply(t[1], p), apply(t[2], p))


def canon(l, r, used):
    best = None
    for p in itertools.permutations(range(used)):
        a, b = apply(l, p), apply(r, p)
        for key in ((a, b), (b, a)):
            if best is None or key < best:
                best = key
    return best


def main():
    n = int(sys.argv[1])
    m = n + 2  # max distinct variables: all ops binary, n+1 leaves per side at most n+2 total
    found = {}
    for total in range(1, n + 1):
        for k1 in range(total + 1):
            for l in terms(k1, m):
                for r in terms(total - k1, m):
                    if l == r:
                        continue
                    vs = set()
                    variables(l, vs)
                    variables(r, vs)
                    k = len(vs)
                    if vs != set(range(k)):  # only prefix variable sets, others are renamings
                        continue
                    found[canon(l, r, k)] = total
    by = {}
    for key, o in found.items():
        by[o] = by.get(o, 0) + 1
    print("brute force by order:", dict(sorted(by.items())), "total", len(found))

    # exact comparison with laws.py, canonicalized with this file's method
    theirs = {}
    for law in enumerate_laws(n):
        vs = set()
        variables(law[0], vs)
        variables(law[1], vs)
        theirs[canon(law[0], law[1], len(vs))] = ops(law[0]) + ops(law[1])
    print("laws.py total", len(theirs))
    only_a = set(found) - set(theirs)
    only_b = set(theirs) - set(found)
    print("only brute force:", len(only_a), " only laws.py:", len(only_b))
    ok = not only_a and not only_b and found == theirs
    print("MATCH" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
