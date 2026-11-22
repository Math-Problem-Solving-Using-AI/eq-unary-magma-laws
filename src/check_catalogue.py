"""S2 spot-check of the numpy model catalogue with plain-Python evaluation.

models.py computes satisfaction with vectorized numpy. This file re-evaluates random
(law, model) pairs, and random refuted pairs, with the simple evaluator in findmodel.py
(no numpy, no z3) and compares.

Usage: python src/check_catalogue.py data/laws_3.json data/o3 [SAMPLES]
"""
import json
import random
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("src", 1)[0] + "src")
from findmodel import check_model  # noqa: E402
from models import all_models, reduce_iso  # noqa: E402
from prove import tuplify  # noqa: E402


def model_dict(mul, f, idx, n):
    return {"mul": mul[idx].astype(int).tolist(), "f": f[idx].astype(int).tolist()}


def main():
    laws_file, prefix = sys.argv[1], sys.argv[2]
    samples = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    laws = [tuplify(e["law"]) for e in json.load(open(laws_file))]
    S = np.load(prefix + "_sat.npy")
    R = np.load(prefix + "_refuted.npy")
    pool = []  # (n, mul, f) in the same column order as models.py
    for n in (2, 3):
        mul, f = all_models(n)
        if n >= 3:
            mul, f = reduce_iso(mul, f, n)
        pool.append((n, mul, f))
    offsets = [0, len(pool[0][1])]

    def locate(col):
        k = 0 if col < offsets[1] else 1
        n, mul, f = pool[k]
        return n, mul, f, col - offsets[k]

    rng = random.Random(1)
    pos = np.argwhere(S)
    neg = np.argwhere(~S)
    bad = 0
    for kind, arr in (("satisfied", pos), ("not satisfied", neg)):
        for j in rng.sample(range(len(arr)), min(samples, len(arr))):
            a, col = arr[j]
            n, mul, f, idx = locate(col)
            got = check_model(model_dict(mul, f, idx, n), laws[a])
            if got != bool(S[a, col]):
                bad += 1
                print("DISAGREE", kind, "law", a, "model col", col)
    ref = np.argwhere(R)
    for j in rng.sample(range(len(ref)), min(samples, len(ref))):
        a, b = ref[j]
        col = int(np.argmax(S[a] & ~S[b]))
        assert S[a, col] and not S[b, col]
        n, mul, f, idx = locate(col)
        m = model_dict(mul, f, idx, n)
        if not (check_model(m, laws[a]) and not check_model(m, laws[b])):
            bad += 1
            print("BAD WITNESS", a, b)
    print(f"checked {2*min(samples,len(pos))} satisfaction entries (+ refuted witnesses), disagreements: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
