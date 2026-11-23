"""Mutation test for results/derivations_collapse_laws.json (step 28), run through src/check_derivations.py.

The selftest of src/check_derivations.py picks a pair whose own chain has 3 steps or more; here every pair has a
one-step chain from the fact x = y, so this script corrupts the file directly: the chains of x = y and of the
helper facts, the one-step chains of the targets, the source law and the pair entries.

Usage: python src/selftest_collapse_laws.py laws_json status_npz derivations_json
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_derivations as cd  # noqa: E402


def main():
    laws_file, status_file, der_file = sys.argv[1:]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(der_file))
    rejected, total = 0, 0

    def run(name, d):
        nonlocal rejected, total
        total += 1
        probs = cd.check(texts, codes, d, control=False)[0]
        rejected += bool(probs)
        print(f"mutation {name}: {'rejected' if probs else 'ACCEPTED'}" + (f" ({probs[0]})" if probs else ""))

    src = "283"  # (x*y)*f(z) = y: fact 1 is the helper, fact 2 is x = y (4 steps)
    k0 = next(k for k in sorted(data["pairs"]) if k.startswith(src + ","))
    kb = data["pairs"][k0]["fact"]
    d = copy.deepcopy(data); s = d["sources"][src]["facts"][2]["chain"][1]; s["subst"]["v0"] = "f(" + s["subst"]["v0"] + ")"
    run("x = y: one substitution changed", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][2]["chain"][3]["pos"] = [0]
    run("x = y: one position changed", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][2]["chain"][2]["dir"] = 1
    run("x = y: one direction flipped", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][2]["chain"].pop(2)
    run("x = y: one step dropped", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][1]["chain"][1]["fact"] = 2
    run("helper fact: a step names a later fact", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][1]["right"] = "f(v1)"
    run("helper fact: right side changed (chain kept)", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][kb]["chain"][0]["fact"] = 1
    run("target derived from the helper fact instead of x = y", d)
    d = copy.deepcopy(data); d["sources"][src]["facts"][kb]["chain"][0]["subst"].pop("v1")
    run("target: substitution does not cover x = y", d)
    d = copy.deepcopy(data); d["sources"]["109"]["facts"][1]["chain"][0]["subst"]["v2"] = "v1"
    run("law 110: x = y chain with a wrong substitution", d)
    d = copy.deepcopy(data); d["sources"]["414"]["facts"][0]["left"] = "m(f(v0),m(v2,v1))"
    run("law 415: fact 0 is not A", d)
    d = copy.deepcopy(data); d["sources"]["414"]["A"] = texts[413]
    run("law 415: A replaced by the text of law 414", d)
    d = copy.deepcopy(data); a = int(src)
    d["pairs"][f"{a},{a}"] = {"A": texts[a], "B": texts[a], "verdict": "holds", "fact": 0}
    run("the pair (A, A), code 0, claimed", d)
    d = copy.deepcopy(data); d["pairs"][k0]["fact"] = kb + 1
    run("pair points to the fact of another target", d)
    d = copy.deepcopy(data); a, b = map(int, k0.split(",")); d["pairs"][f"{a},{b + 1}"] = d["pairs"].pop(k0)
    run("key shifted to the next target", d)
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


if __name__ == "__main__":
    ok = main()
    print("ALL PASS" if ok else "SELFTEST FAILED")
    sys.exit(0 if ok else 1)
