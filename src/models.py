"""Small-model catalogue.

Enumerate every (magma, unary map) of size 2 and 3 (size 3 reduced up to
relabeling), compute which laws each satisfies, and mark every implication
A => B that is REFUTED by some small model (model satisfies A but not B).

Usage: python models.py laws_3.json out_prefix
Writes: <prefix>_sat.npy (laws x models, bool), <prefix>_refuted.npy (laws x laws, bool)
"""
import itertools
import json
import sys
import time

import numpy as np


def all_models(n):
    nm = n * n
    total = n ** (nm + n)
    c = np.arange(total, dtype=np.int64)
    digits = np.empty((total, nm + n), dtype=np.uint8)
    for i in range(nm + n):
        digits[:, i] = c % n
        c //= n
    mul = digits[:, :nm].reshape(total, n, n)
    f = digits[:, nm:]
    return mul, f


def reduce_iso(mul, f, n):
    """Keep one representative per relabeling class."""
    total = len(mul)
    own = np.arange(total, dtype=np.int64)
    best = own.copy()
    pw = (n ** np.arange(n * n + n, dtype=np.int64))
    ar = np.arange(total)
    for p in itertools.permutations(range(n)):
        p = np.array(p, dtype=np.uint8)
        new_mul = np.empty_like(mul)
        new_f = np.empty_like(f)
        for i in range(n):
            for j in range(n):
                new_mul[:, p[i], p[j]] = p[mul[:, i, j]]
            new_f[:, p[i]] = p[f[:, i]]
        digits = np.concatenate([new_mul.reshape(total, n * n), new_f], axis=1).astype(np.int64)
        code = digits @ pw
        best = np.minimum(best, code)
    keep = best == own
    return mul[keep], f[keep]


def ev(t, assign, mA, fA, ar):
    if t[0] == "v":
        return np.full(len(ar), assign[t[1]], dtype=np.intp)
    if t[0] == "f":
        a = ev(t[1], assign, mA, fA, ar)
        return fA[ar, a].astype(np.intp)
    a = ev(t[1], assign, mA, fA, ar)
    b = ev(t[2], assign, mA, fA, ar)
    return mA[ar, a, b].astype(np.intp)


def sat_set(law, n, mul, f):
    from laws import nvars
    v = nvars(law)
    alive = np.arange(len(mul))
    mA, fA = mul, f
    for assign in itertools.product(range(n), repeat=v):
        if len(alive) == 0:
            break
        ar = np.arange(len(alive))
        l = ev(law[0], assign, mA, fA, ar)
        r = ev(law[1], assign, mA, fA, ar)
        keep = l == r
        if not keep.all():
            alive = alive[keep]
            mA = mA[keep]
            fA = fA[keep]
    return alive


def tuplify(t):
    if isinstance(t, list):
        return tuple(tuplify(x) for x in t)
    return t


def main():
    laws_file, prefix = sys.argv[1], sys.argv[2]
    laws = [tuplify(e["law"]) for e in json.load(open(laws_file))]
    L = len(laws)
    cols = []
    for n in (2, 3):
        t0 = time.time()
        mul, f = all_models(n)
        if n >= 3:
            mul, f = reduce_iso(mul, f, n)
        M = len(mul)
        S = np.zeros((L, M), dtype=bool)
        for i, law in enumerate(laws):
            S[i, sat_set(law, n, mul, f)] = True
        cols.append(S)
        print(f"size {n}: {M} models, {time.time()-t0:.1f}s", flush=True)
    S = np.concatenate(cols, axis=1)
    np.save(prefix + "_sat.npy", S)
    P = np.packbits(S, axis=1)
    refuted = np.zeros((L, L), dtype=bool)
    for a in range(L):
        refuted[a] = ((P[a][None, :] & ~P) != 0).any(axis=1)
    np.save(prefix + "_refuted.npy", refuted)
    cand = ~refuted
    np.fill_diagonal(cand, False)
    print("laws:", L, "refuted pairs:", int(refuted.sum()), "candidate implications left:", int(cand.sum()))


if __name__ == "__main__":
    main()
