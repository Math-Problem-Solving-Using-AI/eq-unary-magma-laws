"""Check results/completions_open.json (step 17): open pairs decided by completed rewrite systems.

For each source law A the file stores equations ("facts") and a rule set R. Fact 0 is A itself. Every
other fact carries a chain of steps from its left to its right side; a step names an earlier fact, a
direction, a position and a substitution, and replaces the instance of one side by the instance of the
other. This script does not import the search (src/complete_open.py). For each source it
  1. requires A to be the text of law a in data/laws_3.json and fact 0 to be A as parsed from its text
     (src/check_laws_text.py);
  2. replays every chain, so every fact follows from A by replacing equals by equals;
  3. requires every rule to be one of the facts, and its left side to be greater than its right side in
     the Knuth-Bendix order (weight 1 for f, * and variables, stated precedence): R terminates;
  4. computes every critical pair of R with its own unification and requires both sides to have the same
     normal form: with 3, R is confluent (critical pair lemma and Newman's lemma), normal forms unique;
  5. requires A's two sides to have the same normal form, so the structure T_R of normal forms over
     generators satisfies A.
For each pair entry it requires the pair to be open (code 6), the texts to match, and recomputes the
normal forms of B's sides (B's letters as distinct generators): different means B fails in T_R, so A does
not imply B; equal means B follows from A (each rule is a fact). Stored values and verdict must match.
Controls: for each source, the verdicts on all 712 targets must not contradict the table (codes 1, 2
counterexamples; codes 0, 3, 4 implications) nor the ETP verdicts for open pairs without f.

Usage: python src/check_completion.py laws_json status_npz etp_json completions_json [--selftest]
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402  (separate small parser)


# ---- terms: ('v', i), ('f', t), ('m', s, t); text form v0, f(t), m(s,t)

def parse(s):
    def go(i):
        if s[i] == "v":
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            assert j > i + 1, f"bad term {s!r}"
            return ("v", int(s[i + 1:j])), j
        head = s[i]
        assert head in "fm" and s[i + 1] == "(", f"bad term {s!r}"
        args, i = [], i + 2
        while True:
            a, i = go(i)
            args.append(a)
            if s[i] == ")":
                break
            assert s[i] == ",", f"bad term {s!r}"
            i += 1
        assert len(args) == (1 if head == "f" else 2), f"bad arity in {s!r}"
        return (head, *args), i + 1
    t, i = go(0)
    assert i == len(s), f"trailing text in {s!r}"
    return t


def text(t):
    return f"v{t[1]}" if t[0] == "v" else f"{t[0]}({','.join(text(c) for c in t[1:])})"


def variables(t):
    return {t[1]} if t[0] == "v" else set().union(*(variables(c) for c in t[1:]))


def count(t, x):
    return int(t == ("v", x)) if t[0] == "v" else sum(count(c, x) for c in t[1:])


def weight(t):
    return 1 if t[0] == "v" else 1 + sum(weight(c) for c in t[1:])


def kbo(s, t, prec):
    """True if s > t in the Knuth-Bendix order with all weights 1."""
    if s[0] == "v" or s == t:
        return False
    if any(count(s, x) < count(t, x) for x in variables(t)):
        return False
    if t[0] == "v":
        return True
    if weight(s) != weight(t):
        return weight(s) > weight(t)
    if s[0] != t[0]:
        return prec.index(s[0]) < prec.index(t[0])
    i = next((i for i in range(1, len(s)) if s[i] != t[i]), None)
    return i is not None and kbo(s[i], t[i], prec)


def substitute(t, s):
    if t[0] == "v":
        return s.get(t[1], t)
    return (t[0],) + tuple(substitute(c, s) for c in t[1:])


def get(t, pos):
    for i in pos:
        assert t[0] != "v" and 0 <= i < len(t) - 1, "position outside the term"
        t = t[1 + i]
    return t


def put(t, pos, u):
    if not pos:
        return u
    i = 1 + pos[0]
    assert t[0] != "v" and i < len(t), "position outside the term"
    return t[:i] + (put(t[i], pos[1:], u),) + t[i + 1:]


def all_positions(t, pos=()):
    out = [pos]
    if t[0] != "v":
        for i, c in enumerate(t[1:]):
            out += all_positions(c, pos + (i,))
    return out


def instance_of(p, t, s):
    if p[0] == "v":
        if p[1] in s:
            return s if s[p[1]] == t else None
        return {**s, p[1]: t}
    if p[0] != t[0]:
        return None
    for q, c in zip(p[1:], t[1:]):
        s = instance_of(q, c, s)
        if s is None:
            return None
    return s


def mgu(a, b):
    """Most general unifier as an idempotent substitution, or None."""
    s, todo = {}, [(a, b)]
    while todo:
        p, q = todo.pop()
        p, q = substitute(p, s), substitute(q, s)
        if p == q:
            continue
        if q[0] == "v":
            p, q = q, p
        if p[0] == "v":
            if p[1] in variables(q):
                return None
            s = {x: substitute(u, {p[1]: q}) for x, u in s.items()}
            s[p[1]] = q
        elif p[0] == q[0]:
            todo += list(zip(p[1:], q[1:]))
        else:
            return None
    return s


def normal_form(t, rules):
    """Innermost normalization (the search rewrites outermost first)."""
    if t[0] != "v":
        t = (t[0],) + tuple(normal_form(c, rules) for c in t[1:])
    for l, r in rules:
        s = instance_of(l, t, {})
        if s is not None:
            return normal_form(substitute(r, s), rules)
    return t


# ---- the checks

def check_source(a, src, texts):
    """Returns (problems, rules) for one source law."""
    if not (0 <= a < len(texts)) or src["A"] != texts[a]:
        return [f"source {a}: A is not the text of law {a + 1}"], None
    facts = []
    for k, fa in enumerate(src["facts"]):
        try:
            facts.append((parse(fa["left"]), parse(fa["right"])))
        except (AssertionError, IndexError) as e:
            return [f"source {a}: fact {k} does not parse ({e})"], None
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
        except (AssertionError, KeyError, ValueError, IndexError) as e:
            return [f"source {a}: derivation of fact {k} fails ({e})"], None
        if t != facts[k][1]:
            return [f"source {a}: derivation of fact {k} ends at {text(t)}, not at its right side"], None
    prec = {"f > *": "fm", "* > f": "mf"}.get(src["precedence"])
    if prec is None:
        return [f"source {a}: unknown precedence"], None
    rules = []
    for ru in src["rules"]:
        j, d = ru["fact"], ru["dir"]
        if not (0 <= j < len(facts)) or d not in (1, -1):
            return [f"source {a}: rule names no fact"], None
        l, r = facts[j] if d == 1 else facts[j][::-1]
        if f"{text(l)} -> {text(r)}" != ru["rule"]:
            return [f"source {a}: stored rule text {ru['rule']} is not fact {j}"], None
        if not kbo(l, r, prec):
            return [f"source {a}: rule {ru['rule']} is not decreasing in KBO ({src['precedence']})"], None
        rules.append((l, r))
    problems = []
    for i, (l1, r1) in enumerate(rules):
        for j, (l2, r2) in enumerate(rules):
            shift = 1 + max(variables(l2) | variables(r2))
            ren = {x: ("v", x + shift) for x in variables(l1) | variables(r1)}
            a1, b1 = substitute(l1, ren), substitute(r1, ren)
            for pos in all_positions(l2):
                u = get(l2, pos)
                if u[0] == "v" or (i == j and not pos):
                    continue
                s = mgu(a1, u)
                if s is None:
                    continue
                left = put(substitute(l2, s), pos, substitute(b1, s))
                right = substitute(r2, s)
                if normal_form(left, rules) != normal_form(right, rules):
                    problems.append(f"source {a}: critical pair of rules {i}, {j} at {pos} does not join")
    la = facts[0]
    if normal_form(la[0], rules) != normal_form(la[1], rules):
        problems.append(f"source {a}: the two sides of A have different normal forms")
    return problems, (None if problems else rules)


def verdict(lb, rules):
    left, right = normal_form(lb[0], rules), normal_form(lb[1], rules)
    return left, right, ("holds" if left == right else "fails")


def check(texts, codes, etp, data):
    problems, systems = [], {}
    for key, src in data["sources"].items():
        p, rules = check_source(int(key), src, texts)
        problems += p
        if rules is not None:
            systems[int(key)] = rules
    for key, e in data["pairs"].items():
        a, b = map(int, key.split(","))
        if a not in systems:
            problems.append(f"{key}: no checked rule set for law {a + 1}")
            continue
        if not (0 <= b < len(texts)) or (texts[a], texts[b]) != (e["A"], e["B"]):
            problems.append(f"{key}: law texts do not match data/laws_3.json")
            continue
        if codes[a, b] != 6:
            problems.append(f"{key}: pair is not open (code {codes[a, b]})")
        left, right, v = verdict(parse_law(e["B"]), systems[a])
        if (text(left), text(right), v) != (e["B_left"], e["B_right"], e["verdict"]):
            problems.append(f"{key}: stored normal forms or verdict differ from the recomputed ones")
    etp_says = {(r[0] - 1, r[1] - 1): r[3] for r in etp["settled_open_pairs"]}
    counts = {"fails": 0, "holds": 0}
    for a, rules in systems.items():
        for b, tb in enumerate(texts):
            v = verdict(parse_law(tb), rules)[2]
            counts[v] += 1
            if v == "fails" and codes[a, b] in (0, 3, 4):
                problems.append(f"{a},{b}: T_R refutes but the table says implies (code {codes[a, b]})")
            if v == "holds" and codes[a, b] in (1, 2):
                problems.append(f"{a},{b}: derived but the table has a counterexample")
            if (a, b) in etp_says and etp_says[(a, b)] != (v == "holds"):
                problems.append(f"{a},{b}: verdict {v} disagrees with the ETP")
    return problems, systems, counts


def selftest(texts, codes, etp, data):
    rejected, total = 0, 0

    def run(name, d):
        nonlocal rejected, total
        total += 1
        probs = check(texts, codes, etp, d)[0]
        rejected += bool(probs)
        print(f"mutation {name}: {'rejected' if probs else 'ACCEPTED'}" + (f" ({probs[0]})" if probs else ""))

    pairs = sorted(data["pairs"], key=lambda k: tuple(map(int, k.split(","))))
    k0 = next(k for k in pairs if data["pairs"][k]["verdict"] == "fails")
    a0 = k0.split(",")[0]
    two = next(a for a, s in data["sources"].items() if len(s["rules"]) >= 2)
    deep = next(a for a, s in data["sources"].items()
                if any(f["chain"] and len(f["chain"]) >= 2 for f in s["facts"]))
    d = copy.deepcopy(data); d["pairs"][k0]["B_left"] = d["pairs"][k0]["B_right"]
    run("value of B's left side replaced by the right one", d)
    d = copy.deepcopy(data); d["pairs"][k0]["verdict"] = "holds"
    run("verdict flipped", d)
    d = copy.deepcopy(data); e = d["pairs"][k0]; e["A"], e["B"] = e["B"], e["A"]
    run("A and B swapped", d)
    d = copy.deepcopy(data); a, b = map(int, k0.split(",")); d["pairs"][f"{a},{b + 1}"] = d["pairs"].pop(k0)
    run("key shifted to the next target", d)
    d = copy.deepcopy(data); d["sources"][a0]["facts"][0]["left"] = "m(v0,v1)"
    run("fact 0 is not A", d)
    d = copy.deepcopy(data)
    st = next(f["chain"][-1] for f in d["sources"][deep]["facts"] if f["chain"] and len(f["chain"]) >= 2)
    x = next(iter(st["subst"])); st["subst"][x] = "f(" + st["subst"][x] + ")"
    run(f"one substitution in a derivation changed (source {deep})", d)
    d = copy.deepcopy(data); d["sources"][two]["rules"].pop()
    run(f"last rule dropped (source {two}, critical pairs no longer join)", d)
    d = copy.deepcopy(data); ru = d["sources"][a0]["rules"][0]; ru["dir"] = -ru["dir"]
    ru["rule"] = " -> ".join(ru["rule"].split(" -> ")[::-1])
    run("a rule reversed (not decreasing)", d)
    d = copy.deepcopy(data)
    f0 = d["sources"][a0]["facts"][0]
    ident = {f"v{x}": f"v{x}" for x in variables(parse(f0["left"])) | variables(parse(f0["right"]))}
    d["sources"][a0]["facts"].append({"left": "m(v0,v1)", "right": "v0",
                                      "chain": [{"fact": 0, "dir": 1, "pos": [], "subst": ident}]})
    d["sources"][a0]["rules"].append({"fact": len(d["sources"][a0]["facts"]) - 1, "dir": 1, "rule": "m(v0,v1) -> v0"})
    run("an underived rule x*y -> x added", d)
    # an overlapping source with only its own rule: the critical pair check must see the failure
    d = {"sources": {}, "pairs": {}}
    for a, s in data["sources"].items():
        f0 = s["facts"][0]
        d["sources"][a] = {"A": s["A"], "precedence": s["precedence"],
                           "facts": [f0, {"left": f0["left"], "right": f0["right"], "chain": [
                               {"fact": 0, "dir": 1, "pos": [], "subst": {f"v{x}": f"v{x}" for x in
                                   variables(parse(f0["left"])) | variables(parse(f0["right"]))}}]}],
                           "rules": [{"fact": 1, "dir": 1, "rule": f"{f0['left']} -> {f0['right']}"}]}
    probs = [p for p in check(texts, codes, etp, d)[0] if "critical pair" in p]
    total += 1
    rejected += len(probs) == len(data["sources"])
    print(f"mutation each source with only its own rule: {len({p.split(':')[0] for p in probs})} of "
          f"{len(data['sources'])} rejected by the critical pair check")
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    laws_file, status_file, etp_file, comp_file = args
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    etp = json.load(open(etp_file))
    data = json.load(open(comp_file))
    if "--selftest" in sys.argv:
        ok = selftest(texts, codes, etp, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, systems, counts = check(texts, codes, etp, data)
    v = [e["verdict"] for e in data["pairs"].values()]
    print(f"{len(systems)} of {len(data['sources'])} rule sets checked (derivations, KBO, critical pairs, A joins)")
    print(f"{len(data['pairs'])} open pairs: {v.count('fails')} fail in T_R (not implied), "
          f"{v.count('holds')} derived (implied)")
    print(f"table and ETP control: {sum(counts.values())} pairs, {counts['fails']} fail, {counts['holds']} hold")
    for p in problems[:20]:
        print("PROBLEM", p)
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
