"""Refute open pairs (code 6) with finite magmas published by the Equational Theories Project.

Background (steps/11-etp-magmas-with-f.md): the ETP repository stores many finite multiplication
tables (counterexamples it found for magma laws). Any such table, together with ANY choice of `f`,
is a structure of our kind. For each table of size 4 or 5 we try every choice of `f`
(4^4 = 256 or 5^5 = 3125 of them). If one structure satisfies law A and fails law B for an open
pair (A, B), it is a certificate that A does not imply B. For pairs where neither law mentions `f`,
`f` plays no role, so there we try every table of every size, with `f` the identity. The tables are only a source of
candidates: every certificate is re-checked here (findmodel.check_model) and afterwards by the
independent verifier:  python src/verify_witnesses.py results/witnesses_etp_magmas.json

Output has the same format as results/witnesses_larger_models.json.

Usage: python src/refute_from_etp_magmas.py <ETP repository> results/witnesses_etp_magmas.json [code]
code: which pairs of results/status_matrix.npz to attack, default 6 (open). Code 5 is used as a
positive control: step 09 refuted most of those rows with 4-element tables.
"""
import glob
import itertools
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from findmodel import check_model  # noqa: E402  (plain evaluator, no z3)
from laws import nvars  # noqa: E402
from models import sat_set, tuplify  # noqa: E402  (vectorized evaluator)

SOURCES = [
    "equational_theories/Generated/All4x4Tables/data/*.txt",
    "data/smallest_magma_examples.txt",
    "data/small_magma_examples.txt",
    "data/interesting_finite_magmas/order5_magmas.txt",
]
SIZES = (4, 5)


def read_tables(etp, sizes=SIZES):
    """All distinct square tables of the wanted sizes (None: all), with the first file each was seen in."""
    tables = {}
    for pattern in SOURCES:
        for fn in sorted(glob.glob(str(Path(etp) / pattern))):
            rel = Path(fn).relative_to(etp).as_posix()
            for line in open(fn, encoding="utf-8"):
                m = re.search(r"(\[\[.*?\]\])", line)
                if not m:
                    continue
                t = json.loads(m.group(1))
                n = len(t)
                if (sizes is None or n in sizes) and all(len(r) == n and all(0 <= v < n for v in r) for r in t):
                    tables.setdefault(json.dumps(t), rel)
    return tables


def has_f(t):
    """Does the term t mention f? (For a law, call it on each side.)"""
    return t[0] == "f" or (t[0] != "v" and any(has_f(c) for c in t[1:]))


def holds_on_table(law, mul):
    """Does an f-free law hold in one table? All assignments at once, by numpy broadcasting."""
    n, v = len(mul), nvars(law)
    mul = np.asarray(mul, dtype=np.int32)

    def ev(t):
        if t[0] == "v":
            shape = [1] * v
            shape[t[1]] = n
            return np.arange(n, dtype=np.int32).reshape(shape)
        return mul[ev(t[1]), ev(t[2])]

    # every variable occurs on some side, so the comparison broadcasts over all n^v assignments
    return bool(np.all(ev(law[0]) == ev(law[1])))


def main():
    etp, out = sys.argv[1], sys.argv[2]
    code = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    laws = json.load(open(ROOT / "data" / "laws_3.json", encoding="utf-8"))
    L = [tuplify(e["law"]) for e in laws]
    codes = np.load(ROOT / "results" / "status_matrix.npz")["codes"]
    tables = read_tables(etp)
    targets = {}
    for a, b in zip(*np.nonzero(codes == code)):
        targets.setdefault(int(a), []).append(int(b))
    print("open pairs:", sum(len(v) for v in targets.values()), "sources:", len(targets),
          "tables:", {n: sum(len(json.loads(t)) == n for t in tables) for n in SIZES}, flush=True)
    certs = {}
    for n in SIZES:
        t0 = time.time()
        tabs = [t for t in tables if len(json.loads(t)) == n]
        fs = np.array(list(itertools.product(range(n), repeat=n)), dtype=np.uint8)
        mul = np.repeat(np.array([json.loads(t) for t in tabs], dtype=np.uint8), len(fs), axis=0)
        f = np.tile(fs, (len(tabs), 1))
        origin = np.repeat(np.arange(len(tabs)), len(fs))
        for a, bs in targets.items():
            todo = [b for b in bs if f"{a},{b}" not in certs]
            if not todo:
                continue
            alive = sat_set(L[a], n, mul, f)
            if len(alive) == 0:
                continue
            for b in todo:
                keep = np.zeros(len(alive), dtype=bool)
                keep[sat_set(L[b], n, mul[alive], f[alive])] = True
                if keep.all():
                    continue
                i = alive[np.argmin(keep)]
                m = {"mul": mul[i].tolist(), "f": f[i].tolist()}
                ok = bool(check_model(m, L[a])) and not check_model(m, L[b])
                assert ok, f"vectorized and plain evaluators disagree on {a},{b}"
                certs[f"{a},{b}"] = {"size": n, "model": m, "verified": True,
                                     "source": "ETP multiplication table, f chosen by search",
                                     "etp_file": tables[tabs[origin[i]]],
                                     "A": laws[a]["text"], "B": laws[b]["text"]}
        print(f"size {n}: {len(tabs)} tables x {len(fs)} choices of f, certificates so far {len(certs)},"
              f" {time.time() - t0:.1f}s", flush=True)
        json.dump(certs, open(out, "w", encoding="utf-8"), indent=0)
    t0 = time.time()
    plain = [(a, b) for a, bs in targets.items() for b in bs
             if f"{a},{b}" not in certs and not any(has_f(side) for side in L[a] + L[b])]
    every = sorted(read_tables(etp, None).items(), key=lambda kv: len(json.loads(kv[0])))
    for a, b in plain:
        for t, rel in every:
            mul = json.loads(t)
            if holds_on_table(L[a], mul) and not holds_on_table(L[b], mul):
                m = {"mul": mul, "f": list(range(len(mul)))}
                ok = bool(check_model(m, L[a])) and not check_model(m, L[b])
                assert ok, f"broadcast and plain evaluators disagree on {a},{b}"
                certs[f"{a},{b}"] = {"size": len(mul), "model": m, "verified": True,
                                     "source": "ETP multiplication table, f the identity (no f in A or B)",
                                     "etp_file": rel, "A": laws[a]["text"], "B": laws[b]["text"]}
                break
    print(f"pairs without f: {len(plain)}, tried against {len(every)} tables of every size,"
          f" certificates so far {len(certs)}, {time.time() - t0:.1f}s", flush=True)
    json.dump(certs, open(out, "w", encoding="utf-8"), indent=0)
    print("certificates written:", len(certs), "->", out)


if __name__ == "__main__":
    main()
