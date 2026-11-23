"""Coverage, control and mutation test for results/derivations_ffree_laws.json (step 29).

1. Coverage: for laws 250 and 257 (keys 249 and 256), every other law is either a certificate of step 09
   (results/witnesses_ffree_models.json) or a derived pair here, never both, so each row is fully answered.
2. Control: every derived fact holds in the 4-element tables of A stored in the certificates (plain evaluation,
   every f of the certificates). This is a real model of A, unlike the empty 2- and 3-element control of
   src/check_derivations.py.
3. Mutation test: the selftest of src/check_derivations.py needs a chain of 3 steps or more, and the chains here have
   one step each, so this script corrupts the file directly and expects src/check_derivations.py (or the coverage
   or control checks) to reject each copy.

Usage: python src/selftest_ffree_laws.py laws_json status_npz witnesses_json derivations_json
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_derivations as cd  # noqa: E402
from check_completion import parse  # noqa: E402

ROWS = (249, 256)


def coverage(texts, wit, ders):
    problems = []
    for a in ROWS:
        for b in range(len(texts)):
            if b == a:
                continue
            n = (f"{a},{b}" in wit) + (f"{a},{b}" in ders["pairs"])
            if n != 1:
                problems.append(f"{a},{b}: answered {n} times")
    return problems


def control(wit, ders):
    problems, tables = [], 0
    for a in ROWS:
        models = {json.dumps(e["model"], sort_keys=True) for k, e in wit.items() if k.startswith(f"{a},")}
        for m in map(json.loads, sorted(models)):
            tables += 1
            n = len(m["mul"])
            for i, x in enumerate(ders["sources"][str(a)]["facts"]):
                if not cd.holds((parse(x["left"]), parse(x["right"])), n, m["mul"], m["f"]):
                    problems.append(f"{a}: fact {i} fails in a 4-element table of A")
    return problems, tables


def main():
    laws_file, status_file, wit_file, der_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    wit, ders = json.load(open(wit_file)), json.load(open(der_file))

    cov = coverage(texts, wit, ders)
    print(f"coverage: rows {', '.join(str(a + 1) for a in ROWS)}: {len(wit)} certificates + {len(ders['pairs'])} "
          f"derived pairs, {len(cov)} pairs answered not exactly once")
    con, tables = control(wit, ders)
    print(f"control: every fact holds in all {tables} distinct 4-element tables of the certificates, "
          f"{len(con)} failures")
    for p in (cov + con)[:20]:
        print("PROBLEM", p)

    rejected, total = 0, 0

    def run(name, probs):
        nonlocal rejected, total
        total += 1
        rejected += bool(probs)
        print(f"mutation {name}: {'rejected' if probs else 'ACCEPTED'}" + (f" ({probs[0]})" if probs else ""))

    def der(d):
        return cd.check(texts, codes, d, control=False)[0]

    k0 = "256,249"
    a0, k = k0.split(",")[0], ders["pairs"][k0]["fact"]
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"][0]["subst"]["v2"] = "v1"
    run("one substitution changed", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"][0]["pos"] = [0]
    run("one position changed", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"][0]["dir"] *= -1
    run("one direction flipped", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"] = []
    run("chain emptied", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["A"] = texts[249]
    run("wrong source law", der(d))
    d = copy.deepcopy(ders); d["pairs"][k0]["fact"] = 1
    run("pair pointing at another fact", der(d))
    d = copy.deepcopy(ders); d["pairs"]["256,250"] = {**ders["pairs"][k0], "B": texts[250]}
    run("a pair with a certificate claimed as implied", der(d) + coverage(texts, wit, d))
    d = copy.deepcopy(ders); d["pairs"]["256,256"] = {"A": texts[256], "B": texts[256], "verdict": "holds", "fact": 0}
    run("the pair (A, A), code 0, claimed through fact 0", der(d))
    d = copy.deepcopy(ders); del d["pairs"][k0]
    run("one pair dropped (coverage)", coverage(texts, wit, d))
    d = copy.deepcopy(ders); d["sources"]["249"]["facts"].append(
        {"left": "m(v0,v1)", "right": "v0", "chain": None})
    run("an underived fact x*y = x added (control)", control(wit, d)[0])
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return not cov and not con and rejected == total


if __name__ == "__main__":
    ok = main()
    print("ALL PASS" if ok else "SELFTEST FAILED")
    sys.exit(0 if ok else 1)
