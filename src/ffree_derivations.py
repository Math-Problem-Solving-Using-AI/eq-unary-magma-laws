"""Rows of the two f-free laws with 4-element models (code 5): the 5 targets without a certificate, by derivation.

Laws 250 `(x*y)*(y*x) = y` and 257 `(x*y)*(y*z) = y` have 1,417 of their 1,422 pairs refuted by the 4-element
certificates of step 09 (results/witnesses_ffree_models.json). The other 5 targets are instances of the source law
itself (some letters made equal), so each is one replacement step from fact 0, with the substitution written by hand
below. This script writes them in the format of results/derivations_open.json (checked by src/check_derivations.py).
It asserts that the 5 targets are exactly the code 5 pairs of these rows that have no certificate.

The chains are data, not computed; nothing here checks them. src/check_derivations.py replays them.

Usage: python src/ffree_derivations.py laws_json status_npz witnesses_json derivations_out
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_completion import text  # noqa: E402
from check_laws_text import parse_law  # noqa: E402

# source law index (0-based) -> {target law index: substitution for the letters of the source}
TARGETS = {
    249: {  # (x*y)*(y*x) = y
        203: {"v0": "v0", "v1": "v0"},  # (x*x)*(x*x) = x
    },
    256: {  # (x*y)*(y*z) = y
        203: {"v0": "v0", "v1": "v0", "v2": "v0"},  # (x*x)*(x*x) = x
        205: {"v0": "v0", "v1": "v0", "v2": "v1"},  # (x*x)*(x*y) = x
        249: {"v0": "v0", "v1": "v1", "v2": "v0"},  # (x*y)*(y*x) = y
        252: {"v0": "v0", "v1": "v1", "v2": "v1"},  # (x*y)*(y*y) = y
    },
}


def main():
    laws_file, status_file, witnesses_file, out_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    certified = set(json.load(open(witnesses_file)))
    sources, pairs = {}, {}
    for a, targets in TARGETS.items():
        rest = {b for b in range(len(texts)) if b != a and f"{a},{b}" not in certified}
        assert rest == set(targets), (a, sorted(rest))
        lhs, rhs = parse_law(texts[a])
        facts = [{"left": text(lhs), "right": text(rhs), "chain": None}]
        for b, subst in targets.items():
            assert codes[a, b] == 5, (a, b, codes[a, b])
            lb, rb = parse_law(texts[b])
            facts.append({"left": text(lb), "right": text(rb),
                          "chain": [{"fact": 0, "dir": 1, "pos": [], "subst": subst}]})
            pairs[f"{a},{b}"] = {"A": texts[a], "B": texts[b], "verdict": "holds", "fact": len(facts) - 1}
        sources[str(a)] = {"A": texts[a], "facts": facts}
    json.dump({"sources": sources, "pairs": pairs}, open(out_file, "w"), indent=1)
    print(f"{len(sources)} sources, {len(pairs)} pairs written to {out_file}")


if __name__ == "__main__":
    main()
