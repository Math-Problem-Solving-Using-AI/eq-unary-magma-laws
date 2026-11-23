"""Check results/derivations_open.json (step 19): open pairs where A implies B by a stored derivation.

For each source law A the file stores equations ("facts"); fact 0 is A, every other fact has a chain of steps
from its left side to its right side. A step names an earlier fact, a direction, a position and a
substitution covering the fact's letters, and replaces the instance of one side of that fact by the instance
of the other side. Replacing equals by equals is sound in every structure, so every fact holds in every model
of A. No rewrite theory (orders, critical pairs) and no solver is involved. This script does not import the
search (src/derive_open.py). It
  1. requires A to be the text of law a in data/laws_3.json and fact 0 to be A as parsed from its text
     (src/check_laws_text.py);
  2. replays every chain;
  3. for each pair "a,b": requires the pair to be open (code 6), the texts to match, the verdict to be
     "holds", and the named fact to be B as parsed from its text (either orientation).
Control: every fact must hold in every model of A with 2 or 3 elements, all of them enumerated here by plain
evaluation. (Every finite model of these A satisfies the targets anyway, so this control can only catch a
wrong fact, not a wrong verdict.)

Usage: python src/check_derivations.py laws_json status_npz derivations_json [--selftest]
"""
import copy
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_completion import get, parse, put, substitute, text, variables  # noqa: E402  (checker code)
from check_laws_text import parse_law  # noqa: E402


def evaluate(t, env, mul, fun):
    if t[0] == "v":
        return env[t[1]]
    if t[0] == "f":
        return fun[evaluate(t[1], env, mul, fun)]
    return mul[evaluate(t[1], env, mul, fun)][evaluate(t[2], env, mul, fun)]


def holds(law, n, mul, fun):
    xs = sorted(variables(law[0]) | variables(law[1]))
    for vals in itertools.product(range(n), repeat=len(xs)):
        env = dict(zip(xs, vals))
        if evaluate(law[0], env, mul, fun) != evaluate(law[1], env, mul, fun):
            return False
    return True


def small_models(law):
    """All structures with 2 or 3 elements satisfying law (plain enumeration)."""
    out = []
    for n in (2, 3):
        for cells in itertools.product(range(n), repeat=n * n):
            mul = [cells[i * n:(i + 1) * n] for i in range(n)]
            for fun in itertools.product(range(n), repeat=n):
                if holds(law, n, mul, fun):
                    out.append((n, mul, fun))
    return out


def check_source(a, src, texts):
    """Returns (problems, facts) for one source law."""
    if not (0 <= a < len(texts)) or src["A"] != texts[a]:
        return [f"source {a}: A is not the text of law {a + 1}"], None
    facts = []
    for k, fa in enumerate(src["facts"]):
        try:
            facts.append((parse(fa["left"]), parse(fa["right"])))
        except (AssertionError, IndexError) as e:
            return [f"source {a}: fact {k} does not parse ({e})"], None
        if any(g not in ("v", "f", "m") for g in fa["left"] + fa["right"] if g.isalpha()):
            return [f"source {a}: fact {k} uses a symbol other than f and *"], None
    if not facts or facts[0] != parse_law(src["A"]) or src["facts"][0]["chain"] is not None:
        return [f"source {a}: fact 0 is not A"], None
    for k in range(1, len(facts)):
        chain = src["facts"][k]["chain"]
        if not chain:
            return [f"source {a}: fact {k} has no derivation"], None
        t = facts[k][0]
        try:
            for st in chain:
                j, d = st["fact"], st["dir"]
                assert 0 <= j < k and d in (1, -1), "step names a later fact or a bad direction"
                sb = {int(x[1:]): parse(u) for x, u in st["subst"].items()}
                lj, rj = facts[j]
                assert set(sb) == variables(lj) | variables(rj), "substitution does not cover the fact"
                frm, to = (lj, rj) if d == 1 else (rj, lj)
                pos = tuple(st["pos"])
                assert get(t, pos) == substitute(frm, sb), "step does not apply"
                t = put(t, pos, substitute(to, sb))
        except (AssertionError, KeyError, ValueError, IndexError, TypeError) as e:
            return [f"source {a}: derivation of fact {k} fails ({e})"], None
        if t != facts[k][1]:
            return [f"source {a}: derivation of fact {k} ends at {text(t)}, not at its right side"], None
    return [], facts


def check(texts, codes, data, control=True):
    problems, checked = [], {}
    for key, src in data["sources"].items():
        p, facts = check_source(int(key), src, texts)
        problems += p
        if facts is not None:
            checked[int(key)] = facts
    for key, e in data["pairs"].items():
        a, b = map(int, key.split(","))
        if a not in checked:
            problems.append(f"{key}: no checked derivations for law {a + 1}")
            continue
        if not (0 <= b < len(texts)) or (texts[a], texts[b]) != (e["A"], e["B"]):
            problems.append(f"{key}: law texts do not match data/laws_3.json")
            continue
        if codes[a, b] != 6:
            problems.append(f"{key}: pair is not open (code {codes[a, b]})")
        if e["verdict"] != "holds":
            problems.append(f"{key}: verdict is not 'holds'")
        k, lb = e["fact"], parse_law(e["B"])
        if not (isinstance(k, int) and 0 <= k < len(checked[a])) or checked[a][k] not in (lb, lb[::-1]):
            problems.append(f"{key}: fact {k} is not B")
    models = 0
    if control:
        for a, facts in checked.items():
            for n, mul, fun in small_models(facts[0]):
                models += 1
                for k, fact in enumerate(facts):
                    if not holds(fact, n, mul, fun):
                        problems.append(f"source {a}: fact {k} fails in a model of A with {n} elements")
                        break
    return problems, checked, models


def selftest(texts, codes, data):
    rejected, total = 0, 0

    def run(name, d):
        nonlocal rejected, total
        total += 1
        probs = check(texts, codes, d, control=False)[0]
        rejected += bool(probs)
        print(f"mutation {name}: {'rejected' if probs else 'ACCEPTED'}" + (f" ({probs[0]})" if probs else ""))

    k0 = next(k for k in sorted(data["pairs"])  # a pair whose fact has a chain of 3 steps or more
              if len(data["sources"][k.split(",")[0]]["facts"][data["pairs"][k]["fact"]]["chain"]) >= 3)
    a0 = k0.split(",")[0]
    kb = data["pairs"][k0]["fact"]
    d = copy.deepcopy(data); st = d["sources"][a0]["facts"][kb]["chain"][1]
    x = next(iter(st["subst"])); st["subst"][x] = "f(" + st["subst"][x] + ")"
    run("one substitution changed", d)
    d = copy.deepcopy(data); st = d["sources"][a0]["facts"][kb]["chain"][2]; st["pos"] = st["pos"][:-1]
    run("one position changed", d)
    d = copy.deepcopy(data); st = d["sources"][a0]["facts"][kb]["chain"][2]; st["dir"] = -st["dir"]
    run("one direction flipped", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"][kb]["chain"].pop(2)
    run("one step dropped", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"][2]["chain"][0]["fact"] = 2
    run("a step names the fact it derives", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"][kb]["right"] = "v0"
    run("right side of B's fact changed (chain kept)", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"][0]["left"] = "m(v0,v1)"
    run("fact 0 is not A", d)
    d = copy.deepcopy(data); d["pairs"][k0]["fact"] = kb - 1
    run("pair points to a fact that is not B", d)
    d = copy.deepcopy(data); d["pairs"][k0]["verdict"] = "fails"
    run("verdict changed", d)
    d = copy.deepcopy(data); e = d["pairs"][k0]; e["A"], e["B"] = e["B"], e["A"]
    run("A and B swapped", d)
    d = copy.deepcopy(data); a, b = map(int, k0.split(",")); d["pairs"][f"{a},{b + 1}"] = d["pairs"].pop(k0)
    run("key shifted to the next target", d)
    d = copy.deepcopy(data); a = int(a0); b = int(np.argwhere(codes[a] == 1)[0][0])
    d["pairs"][f"{a},{b}"] = {**data["pairs"][k0], "B": texts[b]}
    run("a pair with a counterexample in the table claimed", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"].append(
        {"left": "m(v0,v1)", "right": "v0", "chain": [{"fact": 0, "dir": 1, "pos": [], "subst": {"v0": "v0", "v1": "v1"}}]})
    run("an underived fact x*y = x added", d)
    # the control must see a wrong fact even when no chain is replayed: a fact x = y fails in every model
    d = copy.deepcopy(data); d["sources"][a0]["facts"].append({"left": "v0", "right": "v1", "chain": None})
    total += 1
    facts = [(parse(x["left"]), parse(x["right"])) for x in d["sources"][a0]["facts"]]
    bad = any(not holds(facts[-1], n, mul, fun) for n, mul, fun in small_models(facts[0]))
    rejected += bad
    print(f"mutation fact x = y seen by the small-model control: {'rejected' if bad else 'ACCEPTED'}")
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    laws_file, status_file, der_file = args
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(der_file))
    if "--selftest" in sys.argv:
        ok = selftest(texts, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, checked, models = check(texts, codes, data)
    steps = sum(len(f["chain"] or []) for s in data["sources"].values() for f in s["facts"])
    print(f"{len(checked)} of {len(data['sources'])} sources checked ({steps} replacement steps replayed)")
    print(f"{len(data['pairs'])} open pairs derived (implied)")
    print(f"control: every fact holds in all {models} models of the sources with 2 or 3 elements")
    for p in problems[:20]:
        print("PROBLEM", p)
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
