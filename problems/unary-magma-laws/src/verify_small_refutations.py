"""Re-verify EVERY small-structure refutation (not a sample) with plain Python.

models.py marks pair (A, B) as refuted when some structure of size 2 or 3 satisfies A and fails B.
This script takes each refuted pair, finds a witness structure from the satisfaction table,
and re-checks it with the independent evaluator in verify_witnesses.py: the structure satisfies
the law A and fails the law B, where both laws are parsed from their TEXT (so the text, the
stored term and the table all have to agree).

Usage: python verify_small_refutations.py laws_json prefix
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402
from models import all_models, reduce_iso  # noqa: E402
from verify_witnesses import holds  # noqa: E402

G = {}


def init(laws_file, prefix):
    G["S"] = np.load(prefix + "_sat.npy")
    G["R"] = np.load(prefix + "_refuted.npy")
    G["laws"] = [parse_law(e["text"]) for e in json.load(open(laws_file))]
    pool = []
    for n in (2, 3):
        mul, f = all_models(n)
        if n >= 3:
            mul, f = reduce_iso(mul, f, n)
        pool.append((mul, f))
    G["pool"] = pool
    G["off"] = len(pool[0][0])


def structure(col):
    k = 0 if col < G["off"] else 1
    mul, f = G["pool"][k]
    i = col - (0 if k == 0 else G["off"])
    return mul[i].astype(int).tolist(), f[i].astype(int).tolist()


def work(a):
    S, R, laws = G["S"], G["R"], G["laws"]
    ok = bad = 0
    cache = {}
    for b in np.where(R[a])[0]:
        col = int(np.argmax(S[a] & ~S[b]))
        if not (S[a, col] and not S[b, col]):
            bad += 1
            continue
        mul, f = cache.get(col) or cache.setdefault(col, structure(col))
        if holds(mul, f, laws[a]) and not holds(mul, f, laws[b]):
            ok += 1
        else:
            bad += 1
    return ok, bad


def main():
    laws_file, prefix = sys.argv[1], sys.argv[2]
    L = len(json.load(open(laws_file)))
    t0 = time.time()
    ok = bad = 0
    with mp.Pool(initializer=init, initargs=(laws_file, prefix)) as pool:
        for o, b in pool.imap_unordered(work, range(L), chunksize=4):
            ok += o
            bad += b
    print(f"refutations re-verified: {ok}, failed: {bad}, time {time.time()-t0:.0f}s")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
