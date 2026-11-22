"""Independent verifier for counterexample certificates.

Reads only a certificate file and re-checks every entry with its own tiny parser and evaluator
(no z3, no numpy, no code from models.py or findmodel.py). An entry claims:
    structure M (tables for * and f) satisfies law A and fails law B,  so  A does not imply B.

Certificate format (results/witnesses_larger_models.json), a dict:
    "a,b": {"A": "<law text>", "B": "<law text>", "size": n,
            "model": {"mul": [[...]], "f": [...]}, "verified": bool, ...}
Entries with size null are "none found" and are skipped.

Usage: python verify_witnesses.py results/witnesses_larger_models.json
"""
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402  (separate small parser)


def n_vars(t, acc):
    if t[0] == "v":
        acc.add(t[1])
    else:
        for c in t[1:]:
            n_vars(c, acc)
    return acc


def ev(t, env, mul, f):
    if t[0] == "v":
        return env[t[1]]
    if t[0] == "f":
        return f[ev(t[1], env, mul, f)]
    return mul[ev(t[1], env, mul, f)][ev(t[2], env, mul, f)]


def holds(mul, f, law):
    """True if the law holds for every assignment of its variables in the structure."""
    vs = sorted(n_vars(law[0], set()) | n_vars(law[1], set()))
    n = len(f)
    for vals in itertools.product(range(n), repeat=len(vs)):
        env = dict(zip(vs, vals))
        if ev(law[0], env, mul, f) != ev(law[1], env, mul, f):
            return False
    return True


def well_formed(model):
    n = len(model["f"])
    return (len(model["mul"]) == n and all(len(r) == n for r in model["mul"])
            and all(0 <= v < n for r in model["mul"] for v in r) and all(0 <= v < n for v in model["f"]))


def check_entry(entry):
    m = entry["model"]
    if not well_formed(m):
        return False
    la, lb = parse_law(entry["A"]), parse_law(entry["B"])
    return holds(m["mul"], m["f"], la) and not holds(m["mul"], m["f"], lb)


def main():
    data = json.load(open(sys.argv[1]))
    checked = bad = skipped = 0
    for key, e in data.items():
        if not e.get("size"):
            skipped += 1
            continue
        checked += 1
        if not check_entry(e):
            bad += 1
            print("FAILED", key, e["A"], "=>", e["B"])
    print(f"{checked} certificates checked, {bad} failed, {skipped} entries without a certificate")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
