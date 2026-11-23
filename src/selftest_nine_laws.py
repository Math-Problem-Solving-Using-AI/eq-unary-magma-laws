"""Mutation test for the step 27 files (results/refutations_nine_laws.json, results/derivations_nine_laws.json).

The selftest of src/check_derivations.py needs a chain of 3 steps or more, and the chains of step 27 have one
step each, so this script corrupts the step 27 derivations directly. It also checks that both checkers still
reject a pair that is not open (their code check was widened from code 6 to codes 5 and 6 in step 27).
The selftest of src/check_term_rewriting.py runs on results/refutations_nine_laws.json as it is.

Usage: python src/selftest_nine_laws.py laws_json status_npz refutations_json derivations_json
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_derivations as cd  # noqa: E402
import check_term_rewriting as ct  # noqa: E402


def main():
    laws_file, status_file, ref_file, der_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    refs, ders = json.load(open(ref_file)), json.load(open(der_file))
    rejected, total = 0, 0

    def run(name, probs):
        nonlocal rejected, total
        total += 1
        rejected += bool(probs)
        print(f"mutation {name}: {'rejected' if probs else 'ACCEPTED'}" + (f" ({probs[0]})" if probs else ""))

    def der(d):
        return cd.check(texts, codes, d, control=False)[0]

    k0 = sorted(ders["pairs"])[0]
    a0, k = k0.split(",")[0], ders["pairs"][k0]["fact"]
    d = copy.deepcopy(ders); st = d["sources"][a0]["facts"][k]["chain"][0]
    x = next(iter(st["subst"])); st["subst"][x] = "f(" + st["subst"][x] + ")"
    run("one substitution changed", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"][0]["pos"] = [0]
    run("one position changed", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"][0]["dir"] *= -1
    run("one direction flipped", der(d))
    d = copy.deepcopy(ders); d["sources"][a0]["facts"][k]["chain"] = []
    run("chain emptied", der(d))
    a = int(a0)
    kr = next(x for x in sorted(refs) if x.startswith(f"{a},"))
    d = copy.deepcopy(ders); d["pairs"][kr] = {"A": texts[a], "B": refs[kr]["B"], "verdict": "holds", "fact": k}
    run("a pair refuted in T_A claimed as implied", der(d))
    d = copy.deepcopy(ders); d["pairs"][f"{a},{a}"] = {"A": texts[a], "B": texts[a], "verdict": "holds", "fact": 0}
    run("the pair (A, A), code 0, claimed through fact 0", der(d))
    e = {**refs[kr], "B": texts[a]}
    run("a refutation entry on the pair (A, A), code 0", ct.check(texts, codes, {f"{a},{a}": e})[0])
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


if __name__ == "__main__":
    ok = main()
    print("ALL PASS" if ok else "SELFTEST FAILED")
    sys.exit(0 if ok else 1)
