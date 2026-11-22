"""Try to prove candidate implications A => B with z3.

Usage:
  python src/prove.py collapse data/laws_3.json data/o3 TIMEOUT_MS
      For laws with no small model: try to prove they collapse (A |- x = y).
  python src/prove.py edges data/laws_3.json data/o3 TIMEOUT_MS
      For every candidate pair (not refuted by small models, source not a collapse law):
      try to prove it. Writes <prefix>_proven.npy and <prefix>_unknown.npy.

z3 results: unsat = proved. sat = z3 found a model (a counterexample, to be re-checked
independently before use). unknown/timeout = unresolved.
"""
import json
import multiprocessing as mp
import sys
import time

import numpy as np
import z3

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import nvars  # noqa: E402


def tuplify(t):
    if isinstance(t, list):
        return tuple(tuplify(x) for x in t)
    return t


_S = _mul = _f = None


def _init():
    global _S, _mul, _f
    _S = z3.DeclareSort("S")
    _mul = z3.Function("mul", _S, _S, _S)
    _f = z3.Function("f", _S, _S)


def tz(t, env):
    if t[0] == "v":
        return env[t[1]]
    if t[0] == "f":
        return _f(tz(t[1], env))
    return _mul(tz(t[1], env), tz(t[2], env))


def axiom(law):
    n = nvars(law)
    vs = [z3.Const(f"a{i}", _S) for i in range(n)]
    if n == 0:
        return tz(law[0], {}) == tz(law[1], {})
    return z3.ForAll(vs, tz(law[0], dict(enumerate(vs))) == tz(law[1], dict(enumerate(vs))))


def goal_neg(law):
    n = nvars(law)
    cs = {i: z3.Const(f"c{i}", _S) for i in range(n)}
    return tz(law[0], cs) != tz(law[1], cs)


class _Code:
    """z3 CheckSatResult is unhashable; map by its string form."""
    _m = {"unsat": 1, "sat": 2, "unknown": 0}

    def __getitem__(self, r):
        return self._m[str(r)]


CODE = _Code()


def task_collapse(args):
    i, law, timeout = args
    _init()
    s = z3.Solver()
    s.set("timeout", timeout)
    s.add(axiom(law))
    x, y = z3.Const("cx", _S), z3.Const("cy", _S)
    s.add(x != y)
    return i, CODE[s.check()]


def task_edges(args):
    a, law_a, targets, timeout = args
    _init()
    s = z3.Solver()
    s.set("timeout", timeout)
    s.add(axiom(law_a))
    out = {}
    for b, law_b in targets:
        s.push()
        s.add(goal_neg(law_b))
        out[b] = CODE[s.check()]
        s.pop()
    return a, out


def main():
    mode, laws_file, prefix, timeout = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    laws = [tuplify(e["law"]) for e in json.load(open(laws_file))]
    L = len(laws)
    S = np.load(prefix + "_sat.npy")
    R = np.load(prefix + "_refuted.npy")
    nmodels = S.sum(axis=1)
    t0 = time.time()
    with mp.Pool() as pool:
        if mode == "collapse":
            zero = [i for i in range(L) if nmodels[i] == 0]
            res = pool.map(task_collapse, [(i, laws[i], timeout) for i in zero])
            collapse = np.zeros(L, dtype=bool)
            try:  # proofs (unsat) are facts: accumulate across runs, z3 outcomes are not stable
                collapse |= np.load(prefix + "_collapse.npy")
            except FileNotFoundError:
                pass
            for i, c in res:
                collapse[i] |= c == 1
            np.save(prefix + "_collapse.npy", collapse)
            print("zero-model laws:", len(zero), "proved collapse:", int(collapse.sum()),
                  "z3 sat:", sum(1 for _, c in res if c == 2), "unknown:", sum(1 for _, c in res if c == 0))
            for i, c in res:
                if c != 1:
                    print("  not proved collapse:", json.load(open(laws_file))[i]["text"], "code", c)
        else:
            # Sources with NO small model are skipped here: their candidate list is every law
            # (nothing refuted them), so grinding z3 on it is waste. They are handled in
            # the eq-laws-without-small-models repository (collapse laws imply everything).
            collapse = np.load(prefix + "_collapse.npy")
            cand = ~R
            np.fill_diagonal(cand, False)

            def load(name, dtype=bool):
                try:
                    return np.load(f"{prefix}_{name}.npy")
                except FileNotFoundError:
                    return np.zeros((L, L), dtype=dtype) if dtype is bool else np.zeros(L, dtype=dtype)

            # State is saved every few sources and on exit, and reloaded here, so a long run
            # that is stopped loses almost nothing. Proofs accumulate, see collapse mode.
            proven, z3sat = load("proven"), load("z3sat")
            done_t = load("edges_done", np.int64)
            tasks = []
            for a in range(L):
                if collapse[a] or nmodels[a] == 0 or done_t[a] >= timeout:
                    continue
                tg = [(b, laws[b]) for b in range(L) if cand[a, b] and not proven[a, b]]
                if tg:
                    tasks.append((a, laws[a], tg, timeout))
            print("source laws:", len(tasks), "pairs:", sum(len(t[2]) for t in tasks), flush=True)

            def save_state():
                np.save(prefix + "_proven.npy", proven)
                np.save(prefix + "_z3sat.npy", z3sat)
                np.save(prefix + "_edges_done.npy", done_t)

            done = 0
            try:
                for a, out in pool.imap_unordered(task_edges, tasks):
                    for b, c in out.items():
                        if c == 1:
                            proven[a, b] = True
                        elif c == 2:
                            z3sat[a, b] = True
                    done_t[a] = max(done_t[a], timeout)
                    done += 1
                    if done % 10 == 0:
                        save_state()
                        print(f"  {done}/{len(tasks)} sources, {time.time()-t0:.0f}s", flush=True)
            finally:
                save_state()
            unknown = cand & ~proven & ~z3sat & ~R & (nmodels[:, None] > 0) & ~collapse[:, None]
            np.save(prefix + "_unknown.npy", unknown)
            print("proved:", int(proven.sum()), "z3 sat:", int(z3sat.sum()),
                  "still unresolved (sources with a small model):", int(unknown.sum()))
    print(f"time {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
