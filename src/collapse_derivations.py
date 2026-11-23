"""Rows of the three collapse laws with no small model (code 5): every target by the derivation of x = y.

Laws 110 `((x*y)*z)*x = w`, 284 `(x*y)*f(z) = y` and 415 `f(x)*(y*z) = y` force every structure to one element.
For each of them this script writes, in the format of results/derivations_open.json (checked by
src/check_derivations.py), the fact x = y as a chain of replacement steps written by hand below, and then
every other law B as a fact derived from x = y in one step (B's left side replaced by B's right side, with
x := left side, y := right side). The chains for laws 284 and 415 follow the sibling repository
eq-laws-without-small-models (results/collapse_xy_fz.json, results/collapse_fx_yz.json): first "any product
with the right shape equals f(c) for every c", then "every element equals f(c)". Law 110 has the letter w on
one side only, as that whole side: two steps.

The chains are data, not computed; nothing here checks them. src/check_derivations.py replays them.

Usage: python src/collapse_derivations.py laws_json status_npz derivations_out
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_completion import text  # noqa: E402
from check_laws_text import parse_law  # noqa: E402


def st(fact, d, pos, **subst):
    return {"fact": fact, "dir": d, "pos": pos, "subst": subst}


# law index (0-based) -> facts after fact 0 (A) as (left, right, chain); the last one is x = y
CHAINS = {
    109: [  # ((x*y)*z)*x = w
        ("v0", "v1", [st(0, -1, [], v0="v0", v1="v0", v2="v0", v3="v0"),
                      st(0, 1, [], v0="v0", v1="v0", v2="v0", v3="v1")]),
    ],
    283: [  # (x*y)*f(z) = y
        ("m(v0,f(v1))", "f(v2)", [st(0, -1, [0], v0="v3", v1="v0", v2="v2"),
                                  st(0, 1, [], v0="m(v3,v0)", v1="f(v2)", v2="v1")]),
        ("v0", "v1", [st(0, -1, [], v0="v2", v1="v0", v2="v3"),
                      st(1, 1, [], v0="m(v2,v0)", v1="v3", v2="v3"),
                      st(1, -1, [], v0="m(v2,v1)", v1="v3", v2="v3"),
                      st(0, 1, [], v0="v2", v1="v1", v2="v3")]),
    ],
    414: [  # f(x)*(y*z) = y
        ("m(f(v0),m(v1,v2))", "f(v3)", [st(0, -1, [1], v0="v3", v1="m(v1,v2)", v2="v4"),
                                        st(0, 1, [], v0="v0", v1="f(v3)", v2="m(m(v1,v2),v4)")]),
        ("v0", "v1", [st(0, -1, [], v0="v2", v1="v0", v2="v3"),
                      st(1, 1, [], v0="v2", v1="v0", v2="v3", v3="v4"),
                      st(1, -1, [], v0="v2", v1="v1", v2="v3", v3="v4"),
                      st(0, 1, [], v0="v2", v1="v1", v2="v3")]),
    ],
}


def main():
    laws_file, status_file, out_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    sources, pairs = {}, {}
    for a, extra in CHAINS.items():
        lhs, rhs = parse_law(texts[a])
        facts = [{"left": text(lhs), "right": text(rhs), "chain": None}]
        facts += [{"left": l, "right": r, "chain": c} for l, r, c in extra]
        k = len(facts) - 1  # the fact x = y
        for b in range(len(texts)):
            if b == a:
                continue
            assert codes[a, b] == 5, (a, b, codes[a, b])
            lb, rb = parse_law(texts[b])
            assert lb != rb
            facts.append({"left": text(lb), "right": text(rb),
                          "chain": [st(k, 1, [], v0=text(lb), v1=text(rb))]})
            pairs[f"{a},{b}"] = {"A": texts[a], "B": texts[b], "verdict": "holds", "fact": len(facts) - 1}
        sources[str(a)] = {"A": texts[a], "facts": facts}
    json.dump({"sources": sources, "pairs": pairs}, open(out_file, "w"), indent=1)
    print(f"{len(sources)} sources, {len(pairs)} pairs written to {out_file}")


if __name__ == "__main__":
    main()
