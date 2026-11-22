"""Refute open pairs whose source law has no `f`, using a known model of that law and every choice of `f`.

Background (steps/09-ffree-models-with-f.md): two of the nine laws with no model of size 2 or 3 do
not mention `f`: `(x*y)*(y*x) = y` and `(x*y)*(y*z) = y`. Both have a model with 4 elements (found
and verified in the eq-laws-without-small-models repository, results/zero_model_laws.json). A law
without `f` holds in a structure whatever `f` is. So for every target law B that is open in our
table (code 5), we try all 4^4 = 256 choices of `f` on the 4-element table. If B fails for one of
them, that structure is a certificate that A does not imply B.

Output has the same format as results/witnesses_larger_models.json, so the independent verifier
re-checks it:  python src/verify_witnesses.py results/witnesses_ffree_models.json

Usage: python src/refute_from_ffree_models.py results/witnesses_ffree_models.json
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from findmodel import check_model  # noqa: E402  (plain evaluator, no z3)

# Copied from eq-laws-without-small-models/results/zero_model_laws.json (commit 95d7345).
# Only "mul" matters: these laws do not mention f.
MODELS = {
    "(x*y)*(y*x) = y": [[1, 2, 2, 3], [3, 0, 0, 0], [1, 2, 2, 1], [1, 3, 0, 3]],
    "(x*y)*(y*z) = y": [[0, 2, 0, 2], [0, 2, 0, 2], [1, 3, 1, 3], [1, 3, 1, 3]],
}


def tuplify(t):
    return tuple(tuplify(x) for x in t) if isinstance(t, list) else t


def main():
    out = sys.argv[1]
    laws = json.load(open(ROOT / "data" / "laws_3.json", encoding="utf-8"))
    by_text = {e["text"]: i for i, e in enumerate(laws)}
    codes = np.load(ROOT / "results" / "status_matrix.npz")["codes"]
    fs = list(itertools.product(range(4), repeat=4))
    certs, summary = {}, {}
    for a_text, mul in MODELS.items():
        a = by_text[a_text]
        law_a = tuplify(laws[a]["law"])
        assert check_model({"mul": mul, "f": [0, 0, 0, 0]}, law_a), "stored table is not a model of A"
        open_targets = [b for b in range(len(laws)) if codes[a, b] == 5]
        found = 0
        for b in open_targets:
            law_b = tuplify(laws[b]["law"])
            for f in fs:
                m = {"mul": mul, "f": list(f)}
                if not check_model(m, law_b):
                    certs[f"{a},{b}"] = {"size": 4, "model": m, "verified": True,
                                         "source": "known model of A, f chosen by search",
                                         "A": a_text, "B": laws[b]["text"]}
                    found += 1
                    break
        summary[a_text] = {"open_targets": len(open_targets), "refuted": found,
                           "still_open": len(open_targets) - found}
        print(a_text, summary[a_text])
    json.dump(certs, open(out, "w", encoding="utf-8"), indent=0)
    print("certificates written:", len(certs), "->", out)


if __name__ == "__main__":
    main()
