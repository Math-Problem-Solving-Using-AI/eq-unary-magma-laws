"""Mutation tests: the verifiers must FAIL on corrupted input, otherwise "0 failed" means nothing.

Tests (each prints PASS or FAIL):
  1. verify_witnesses: flipping one table entry in each certificate must break many of them.
  2. verify_witnesses: swapping A and B in each certificate must break many of them.
  3. holds(): a structure that is known to satisfy a law passes, and known to violate it fails.
  4. verify_small_refutations: shifting the law list by one (so each pair checks the wrong laws)
     must produce many failures.
  5. verify_small_refutations: timing and amount of work actually done per pair.

Usage: python selftest_verifiers.py laws_json prefix certificates_json
"""
import copy
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_small_refutations as vs  # noqa: E402
from check_laws_text import parse_law  # noqa: E402
from verify_witnesses import check_entry, holds  # noqa: E402


def report(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" - " + detail if detail else ""))
    return ok


def main():
    laws_file, prefix, cert_file = sys.argv[1], sys.argv[2], sys.argv[3]
    certs = [e for e in json.load(open(cert_file)).values() if e.get("size")]
    rng = random.Random(7)
    allok = True

    # 1. flip one table entry
    broken = 0
    for e in certs:
        m = copy.deepcopy(e)
        n = m["size"]
        i, j = rng.randrange(n), rng.randrange(n)
        m["model"]["mul"][i][j] = (m["model"]["mul"][i][j] + 1) % n
        if not check_entry(m):
            broken += 1
    allok &= report("1 flipped table entry is caught", broken > 0.2 * len(certs), f"{broken}/{len(certs)} broken")

    # 2. swap A and B
    broken = 0
    for e in certs:
        m = copy.deepcopy(e)
        m["A"], m["B"] = m["B"], m["A"]
        if not check_entry(m):
            broken += 1
    allok &= report("2 swapped A and B is caught", broken > 0.5 * len(certs), f"{broken}/{len(certs)} broken")

    # 3. holds() on a hand example: 2-element structure x*y = x, f(x) = x
    mul, f = [[0, 0], [1, 1]], [0, 1]
    allok &= report("3a holds(x*y = x) true", holds(mul, f, parse_law("x*y = x")))
    allok &= report("3b holds(x*y = y) false", not holds(mul, f, parse_law("x*y = y")))
    allok &= report("3c holds(f(x) = x) true", holds(mul, f, parse_law("f(x) = x")))
    allok &= report("3d holds(x*y = y*x) false", not holds(mul, f, parse_law("x*y = y*x")))

    # 4. shifted law list in the small-refutation verifier
    vs.init(laws_file, prefix)
    R = vs.G["R"]
    good_laws = vs.G["laws"]
    sources = [int(a) for a in np.where(R.any(axis=1))[0][:60]]
    ok0 = bad0 = 0
    t = time.time()
    for a in sources:
        o, b = vs.work(a)
        ok0 += o
        bad0 += b
    dt = time.time() - t
    vs.G["laws"] = good_laws[1:] + good_laws[:1]
    ok1 = bad1 = 0
    for a in sources:
        o, b = vs.work(a)
        ok1 += o
        bad1 += b
    vs.G["laws"] = good_laws
    allok &= report("4a untouched: no failures on 60 source laws", bad0 == 0, f"{ok0} ok")
    allok &= report("4b shifted law list is caught", bad1 > 0.2 * (ok1 + bad1), f"{bad1} of {ok1 + bad1} failed")

    # 5. how much work per pair
    per = dt / max(ok0, 1) * 1e6
    report("5 timing (information)", True, f"{per:.0f} microseconds per pair, single process")
    print("ALL PASS" if allok else "SOME TESTS FAILED")
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
