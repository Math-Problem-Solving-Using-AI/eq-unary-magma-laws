"""Turn open pairs into certified counterexamples.

For every pair (A, B) that is not refuted by the small catalogue, not in the transitive closure
of z3-proved implications, and whose source A has a small model and does not collapse, search a
structure of size 4..MAXN that satisfies A and fails B. Each structure found is re-checked by plain
evaluation (findmodel.check_model), independent of z3, before being kept as verified.

State is saved every 25 pairs and the run resumes from the saved file.

Usage: python resolve_open.py laws_json prefix MAXN TIMEOUT_MS out_json
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from findmodel import check_model, find_model  # noqa: E402
from prove import tuplify  # noqa: E402


def task(args):
    a, b, la, lb, maxn, timeout = args
    tried = {}
    for n in range(4, maxn + 1):
        m, st = find_model([la], n, violate=lb, timeout_ms=timeout)
        tried[str(n)] = st
        if m:
            ok = bool(check_model(m, la)) and not check_model(m, lb)
            return a, b, {"size": n, "model": m, "verified": ok, "tried": tried}
    return a, b, {"size": None, "tried": tried}


def open_pairs(prefix, L):
    S = np.load(prefix + "_sat.npy")
    R = np.load(prefix + "_refuted.npy")
    C = np.load(prefix + "_collapse.npy")
    PR = np.load(prefix + "_proven.npy")
    nm = S.sum(axis=1)
    reach = PR.copy()
    np.fill_diagonal(reach, True)
    for k in range(L):
        reach |= np.outer(reach[:, k], reach[k, :])
    cand = ~R
    np.fill_diagonal(cand, False)
    src = (nm > 0) & ~C
    return np.argwhere(cand & ~reach & src[:, None])


def main():
    laws_file, prefix, maxn, timeout, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    laws = [tuplify(e["law"]) for e in json.load(open(laws_file))]
    texts = [e["text"] for e in json.load(open(laws_file))]
    try:
        results = json.load(open(out))
    except FileNotFoundError:
        results = {}
    todo = []
    for a, b in open_pairs(prefix, len(laws)):
        key = f"{a},{b}"
        prev = results.get(key)
        if prev and (prev.get("size") or max(map(int, prev["tried"])) >= maxn):
            continue
        todo.append((int(a), int(b), laws[a], laws[b], maxn, timeout))
    print("open pairs to try:", len(todo), flush=True)

    def save():
        json.dump(results, open(out, "w"))

    t0 = time.time()
    done = 0
    with mp.Pool() as pool:
        try:
            for a, b, res in pool.imap_unordered(task, todo):
                res["A"], res["B"] = texts[a], texts[b]
                results[f"{a},{b}"] = res
                done += 1
                if done % 25 == 0:
                    save()
                    print(f"  {done}/{len(todo)}, {time.time()-t0:.0f}s", flush=True)
        finally:
            save()
    found = sum(1 for r in results.values() if r.get("size") and r.get("verified"))
    bad = sum(1 for r in results.values() if r.get("size") and not r.get("verified"))
    none = sum(1 for r in results.values() if not r.get("size"))
    print(f"verified counterexamples: {found}  solver model failed plain check: {bad}  none found up to size {maxn}: {none}")


if __name__ == "__main__":
    main()
