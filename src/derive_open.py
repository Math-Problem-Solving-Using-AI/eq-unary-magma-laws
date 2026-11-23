"""Derivations aimed at the target for open pairs whose completion keeps growing (steps 19 and 21).

Step 18 left 8 open pairs with f whose Knuth-Bendix completion does not finish. For two of their source laws,
f(x*y)*x = y (law 483) and its mirror x*f(y*x) = y (law 704), a short proof of the targets was found by hand:

  E1  f(y)*f(x*y) = x          A at x := f(x*y), y := x, then A inside
  E2  f(x)*f(y) = f(x*y)       A at x := f(y), y := f(x*y), then E1 inside
  E3  f(x*(f(y)*x)) = f(y)     E2 backwards at the top, then E1
  B   x*(f(y)*x) = y           E1 backwards (with y := x), E2 backwards, E3, E2, E1
  B'  x*(f(x)*x) = x           B with y := x

(In words: f turns products into products, and every z equals f(w)*f(z*w), so z is fixed by f(z); B's two
sides have the same image under f, hence are equal.) The hand proof is only an outline: each fact below is
written as a list of terms, and this script finds for every two consecutive terms one replacement step (an
earlier fact, a direction, a position, a substitution) that turns the first into the second. If a step
cannot be found the script stops. The mirror law gets the mirrored outline (s*t becomes t*s).

Step 21 adds one pair without f: law 153 (x*(y*x))*x = y implies law 508 x*((y*x)*x) = y (ETP equations 222
and 118; the outline follows the ETP's Vampire proof Equation222_implies_Equation118):

  E1  x*(y*x) = (x*y)*x        A backwards at the top (y := x*(y*x)), then A inside
  B   x*((y*x)*x) = y          E1 with y := y*x, then A

Output: {"sources": {a: {"A", "facts": [{"left", "right", "chain"}]}}, "pairs": {"a,b": {"A", "B",
"verdict": "holds", "fact": k}}}, fact 0 = A (chain null), terms written as in results/completions_open.json.
src/check_derivations.py replays every chain without importing this file.

Usage: python src/derive_open.py laws_json status_npz out_json
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from complete_open import match, positions, replace, show, subst, variables  # noqa: E402
from prove import tuplify  # noqa: E402

V0, V1 = ("v", 0), ("v", 1)


def m(a, b):
    return ("m", a, b)


def f(a):
    return ("f", a)


T = m(V0, m(f(V1), V0))  # left side of B: x*(f(y)*x)
OUTLINE = [  # (name, terms from left side to right side); fact 0 is A = f(x*y)*x = y
    ("E1", [m(f(V1), f(m(V0, V1))), m(f(m(f(m(V0, V1)), V0)), f(m(V0, V1))), V0]),
    ("E2", [m(f(V0), f(V1)), m(f(m(f(V1), f(m(V0, V1)))), f(V1)), f(m(V0, V1))]),
    ("E3", [f(T), m(f(V0), f(m(f(V1), V0))), f(V1)]),
    ("B", [T, m(f(V0), f(m(T, V0))), m(f(V0), m(f(T), f(V0))), m(f(V0), m(f(V1), f(V0))),
           m(f(V0), f(m(V1, V0))), V1]),
]
E1_153 = m(V0, m(V1, V0))  # left side of E1 for law 153: x*(y*x)
OUTLINE_153 = [  # fact 0 is A = (x*(y*x))*x = y
    ("E1", [E1_153, m(m(V0, m(E1_153, V0)), V0), m(m(V0, V1), V0)]),
    ("B", [m(V0, m(m(V1, V0), V0)), m(m(V0, m(V1, V0)), V0), V1]),
]
SOURCES = {  # law id: (outline, mirrored, {target law id: fact name}); 704 is the mirror of 483
    483: (OUTLINE, False, {550: "B", 544: "B'"}),
    704: (OUTLINE, True, {195: "B", 189: "B'"}),
    153: (OUTLINE_153, False, {508: "B"}),
}


def mirror(t):
    if t[0] == "v":
        return t
    if t[0] == "m":
        return m(mirror(t[2]), mirror(t[1]))
    return (t[0],) + tuple(mirror(c) for c in t[1:])


def one_step(s, t, facts):
    """A step (fact, dir, pos, subst) turning s into t, or None."""
    for p, u in positions(s):
        for j, (l, r) in enumerate(facts):
            for d, (frm, to) in ((1, (l, r)), (-1, (r, l))):
                th = match(frm, u, {})
                if th is None:
                    continue
                target = t  # the subterm of t at p, or None if t has no position p
                for i in p:
                    if target[0] == "v" or 1 + i >= len(target):
                        target = None
                        break
                    target = target[1 + i]
                if target is None:
                    continue
                th = match(to, target, th)
                if th is None or replace(s, p, subst(to, th)) != t:
                    continue
                if set(th) != variables(l) | variables(r):
                    continue
                return j, d, p, th
    return None


def derive(law, outline, mirrored, with_b_prime):
    facts = [law]
    chains = [None]
    names = {}
    outline = [(n, [mirror(x) for x in ts] if mirrored else ts) for n, ts in outline]
    for name, terms in outline:
        chain = []
        for s, t in zip(terms, terms[1:]):
            st = one_step(s, t, facts)
            if st is None:
                sys.exit(f"no step from {show(s)} to {show(t)} in {name}")
            chain.append(st)
        facts.append((terms[0], terms[-1]))
        chains.append(chain)
        names[name] = len(facts) - 1
    if with_b_prime:
        b = facts[names["B"]]
        inst = {0: V0, 1: V0}
        facts.append((subst(b[0], inst), subst(b[1], inst)))
        chains.append([(names["B"], 1, (), inst)])
        names["B'"] = len(facts) - 1
    out = [{"left": show(l), "right": show(r),
            "chain": None if ch is None else [{"fact": j, "dir": d, "pos": list(p),
                                                "subst": {f"v{x}": show(u) for x, u in sorted(th.items())}}
                                               for j, d, p, th in ch]}
           for (l, r), ch in zip(facts, chains)]
    return out, names, facts


def main():
    laws_file, status_file, out = sys.argv[1:]
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    sources, pairs = {}, {}
    for a_id, (outline, mirrored, targets) in SOURCES.items():
        a = a_id - 1
        facts, names, terms = derive(laws[a], outline, mirrored, "B'" in targets.values())
        sources[str(a)] = {"A": texts[a], "facts": facts}
        for b_id, name in targets.items():
            b = b_id - 1
            k = names[name]
            if terms[k] not in (laws[b], laws[b][::-1]):
                sys.exit(f"fact {name} of law {a_id} is not law {b_id}")
            if codes[a, b] != 6:
                sys.exit(f"pair {a_id}, {b_id} is not open (code {codes[a, b]})")
            pairs[f"{a},{b}"] = {"A": texts[a], "B": texts[b], "verdict": "holds", "fact": k}
            print(f"law {a_id} {texts[a]} implies law {b_id} {texts[b]}: fact {k}, "
                  f"{sum(len(x['chain'] or []) for x in facts)} steps in all")
    json.dump({"sources": sources, "pairs": pairs}, open(out, "w"), indent=1)
    print(f"pairs derived: {len(pairs)}")


if __name__ == "__main__":
    main()
