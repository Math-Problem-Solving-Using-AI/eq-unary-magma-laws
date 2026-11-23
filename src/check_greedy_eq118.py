"""Check results/greedy_eq118.json (step 24): the finite seeds of the ETP's infinite models of law 508.

Law 508 is x*((y*x)*x) = y (ETP equation 118). The ETP (Generated/Greedy/Eq118.lean) builds models on the natural
numbers from a "partial solution": a finite set R of triples (x, y, z), read as x*y = z, that satisfies 11 rules
(rule_0 to rule_10 of the structure PartialSolution). Its Lean proof (PartialSolution.adjoin) says one more product
a*b = c with a brand-new element c, plus the triples the rule derives from it, gives again a partial solution; a
greedy chain over all pairs then gives a total operation satisfying ETP 118. This script does NOT re-check that
proof. It checks, in plain Python (no z3, no Lean, no ETP files):
  1. each seed satisfies the 11 rules as written in the Lean file (copied below) and its support lies in finsupp;
  2. for each pair (A, B): the pair is open (code 6), A is law 508 (or law 143 with the mirrored model x*y = y*x
     of R), and law B fails at the stored values of x and y using seed products only, so it fails in every model
     built from that seed;
  3. a bounded test of the extension rule (adjoin in the Lean file): from each seed it adds products first in the
     order of the Lean chain (complSeq), then for random pairs of elements, then whenever an evaluation needs one, checks the 11 rules and the
     one-value-per-product rule along the way, and evaluates law 508 and law 143 (mirrored) directly at all pairs
     of small numbers. A bounded test, not a proof of the theorem.
With --etp DIR it also checks that the 11 rules below are the ones in DIR's copy of the Lean file.
Usage: python src/check_greedy_eq118.py laws_json status_npz greedy_json [--selftest] [--etp DIR]
"""
import copy
import itertools
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402
from laws import VARS  # noqa: E402

LAW_A = {False: 508, True: 143}
LEAN_FILE = "equational_theories/Generated/Greedy/Eq118.lean"
# Lines 2443 to 2453 of the Lean file, structure PartialSolution, copied verbatim. "R X0 X1 X2" means X0*X1 = X2.
RULES = [
    "(∀ X0 X1 X2 X3, ¬ R X0 X1 X2 ∨ ¬ R X0 X1 X3 ∨ X2 = X3)",
    "(∀ X0 X1 X2 X3, ¬ R X0 X1 X2 ∨ ¬ R X2 X1 X3 ∨ R X1 X3 X0)",
    "(∀ X0 X1 X2, ¬ R X0 X1 X2 ∨ ¬ R X1 X1 X0 ∨ R X2 X1 X1)",
    "(∀ X0 X1, ¬ R X0 X1 X1 ∨ R X1 X0 X1)",
    "(∀ X0 X1 X2, ¬ R X0 X0 X1 ∨ ¬ R X1 X0 X2 ∨ R X0 X1 X2)",
    "(∀ X0 X1 X2, ¬ R X0 X0 X1 ∨ ¬ R X0 X1 X2 ∨ R X0 X2 X0)",
    "(∀ X0 X1 X2, ¬ R X0 X0 X1 ∨ ¬ R X0 X1 X2 ∨ R X2 X0 X0)",
    "(∀ X0 X1 X2 X3, ¬ R X0 X1 X2 ∨ ¬ R X1 X1 X0 ∨ ¬ R X3 X0 X1 ∨ R X0 X2 X3)",
    "(∀ X0 X1 X2 X3, ¬ R X0 X1 X2 ∨ ¬ R X3 X1 X2 ∨ X3 = X0)",
    "(∀ X0 X1 X2, ¬ R X0 X0 X1 ∨ ¬ R X2 X0 X0 ∨ R X1 X0 X2)",
    "(∀ X0 X1 X2, ¬ R X0 X0 X1 ∨ ¬ R X0 X1 X2 ∨ R X1 X0 X2)",
]
LEAN_ORDER_STEPS = 20000   # first products added in the order of the Lean chain (Nat.unpair of 0, 1, 2, ...)
RANDOM_STEPS = 5000        # then products of random elements (fixed random seed): the Lean proof allows any order
LAW_RANGE = 40             # laws evaluated at all x, y in 0 .. LAW_RANGE - 1
CHECK_EVERY = 5000


def parse_rule(text):
    """A clause: (premises, conclusion); a premise is a triple of variable names, the conclusion is
    ("R", triple) or ("=", u, v)."""
    m = re.fullmatch(r"\(∀ ([X0-9 ]+), (.*)\)", text)
    if not m:
        raise ValueError(f"rule not understood: {text}")
    premises, conclusion = [], None
    for lit in m.group(2).split(" ∨ "):
        parts = lit.split()
        if parts[:2] == ["¬", "R"] and len(parts) == 5:
            premises.append(tuple(parts[2:]))
        elif parts[0] == "R" and len(parts) == 4 and conclusion is None:
            conclusion = ("R", tuple(parts[1:]))
        elif len(parts) == 3 and parts[1] == "=" and conclusion is None:
            conclusion = ("=", parts[0], parts[2])
        else:
            raise ValueError(f"literal not understood: {lit}")
    return premises, conclusion


def rule_violations(triples, rules):
    """All (rule number, binding) where the premises hold in the finite set of triples and the conclusion fails."""
    index = {}
    for t in triples:
        for mask in itertools.product((0, 1), repeat=3):
            index.setdefault((mask, tuple(v for v, k in zip(t, mask) if k)), []).append(t)
    out = []
    for n, (premises, conclusion) in enumerate(rules):
        def search(i, env):
            if i == len(premises):
                if conclusion[0] == "R":
                    ok = tuple(env[v] for v in conclusion[1]) in triples
                else:
                    ok = env[conclusion[1]] == env[conclusion[2]]
                if not ok:
                    out.append((n, dict(env)))
                return
            p = premises[i]
            mask = tuple(int(v in env) for v in p)
            for t in index.get((mask, tuple(env[v] for v in p if v in env)), []):
                e = dict(env)
                if all(e.setdefault(v, x) == x for v, x in zip(p, t)):
                    search(i + 1, e)
        search(0, {})
        if len(out) > 20:
            break
    return out


class Partial:
    """A partial operation, grown by the extension rule of PartialSolution.adjoin."""

    def __init__(self, triples, skip=()):
        self.triples = set(map(tuple, triples))
        self.prod = {}
        self.by_yz = {}
        self.skip = set(skip)        # selftest only: derived triples left out on purpose
        self.fresh_is_a = False      # selftest only: reuse a instead of a brand-new element
        self.steps = 0
        for t in self.triples:
            self._index(t)
        self.top = max(v for t in self.triples for v in t)

    def _index(self, t):
        x, y, z = t
        self.prod.setdefault((x, y), set()).add(z)
        self.by_yz.setdefault((y, z), set()).add(x)

    def has(self, x, y, z):
        return (x, y, z) in self.triples

    def adjoin(self, a, b):
        """Lines 2462 to 2511: add a*b = c for a new c and the triples sP1 to sP8 built from the old R."""
        self.top = max(self.top, a, b) + 1
        c = a if self.fresh_is_a else self.top
        new = {0: [(a, b, c)],
               1: [(b, c, z) for z in self.by_yz.get((b, a), ())],
               2: [(c, b, b)] if self.has(b, b, a) else [],
               3: [(b, a, c)] if self.has(b, b, a) else [],
               4: [(a, c, a)] if self.has(a, a, b) else [],
               5: [(c, a, a)] if self.has(a, a, b) else [],
               6: [(a, c, z) for z in self.by_yz.get((a, b), ())] if self.has(b, b, a) else [],
               7: [(c, b, z) for z in self.by_yz.get((b, b), ())] if a == b else [],
               8: [(b, a, c)] if self.has(a, a, b) else []}
        for k, ts in new.items():
            if k not in self.skip:
                for t in ts:
                    if t not in self.triples:
                        self.triples.add(t)
                        self._index(t)
        self.steps += 1

    def op(self, x, y):
        if (x, y) not in self.prod:
            self.adjoin(x, y)
        vals = self.prod[(x, y)]
        if len(vals) != 1:
            raise ValueError(f"{x}*{y} has {len(vals)} values")
        return next(iter(vals))


def seed_op(triples):
    prod = {}
    for x, y, z in triples:
        prod.setdefault((x, y), set()).add(z)

    def op(x, y):
        vals = prod[(x, y)]
        if len(vals) != 1:
            raise ValueError(f"{x}*{y} has {len(vals)} values in the seed")
        return next(iter(vals))
    return op


def evaluate(t, env, op, mirror):
    if t[0] == "v":
        return env[t[1]]
    if t[0] != "m":
        raise ValueError("law uses f")
    x, y = evaluate(t[1], env, op, mirror), evaluate(t[2], env, op, mirror)
    return op(y, x) if mirror else op(x, y)


def unpair(n):
    """Mathlib's Nat.unpair, the order in which complSeq adds products."""
    s = math.isqrt(n)
    return (n - s * s, s) if n - s * s < s else (s, n - s * s - s)


def bounded_test(triples, texts, rules, skip=(), fresh_is_a=False):
    """Grow a seed by the extension rule; return (problems, report lines)."""
    ps = Partial(triples, skip)
    ps.fresh_is_a = fresh_is_a
    problems = []
    for n in range(LEAN_ORDER_STEPS):
        a, b = unpair(n)
        if (a, b) not in ps.prod:
            ps.adjoin(a, b)
            if ps.steps % CHECK_EVERY == 0:
                problems += [f"rule_{k} fails at {e}" for k, e in rule_violations(ps.triples, rules)[:3]]
        if problems:
            return problems, []
    rng = random.Random(118)
    for _ in range(RANDOM_STEPS):
        a, b = rng.randrange(ps.top + 1), rng.randrange(ps.top + 1)
        if (a, b) not in ps.prod:
            ps.adjoin(a, b)
            if ps.steps % CHECK_EVERY == 0:
                problems += [f"rule_{k} fails at {e}" for k, e in rule_violations(ps.triples, rules)[:3]]
    if problems:
        return problems, []
    report = []
    for mirror in (False, True):
        law = parse_law(texts[LAW_A[mirror] - 1])
        failures = 0
        for x, y in itertools.product(range(LAW_RANGE), repeat=2):
            env = {0: x, 1: y}
            try:
                failures += evaluate(law[0], env, ps.op, mirror) != evaluate(law[1], env, ps.op, mirror)
            except ValueError as err:
                problems.append(str(err))
                return problems, report
        if failures:
            problems.append(f"law {LAW_A[mirror]} fails {failures} times")
        report.append((LAW_A[mirror], LAW_RANGE * LAW_RANGE, failures))
    problems += [f"rule_{k} fails at {e}" for k, e in rule_violations(ps.triples, rules)[:3]]
    return problems, [(ps.steps, len(ps.triples), *r) for r in report]


def check(texts, codes, data, run_greedy=True, rules_text=RULES, **kw):
    rules = [parse_rule(r) for r in rules_text]
    problems, report, tests = [], [], []
    if len(rules) != 11:
        problems.append(f"{len(rules)} rules, the Lean file has 11")
    for name, s in data["seeds"].items():
        triples = set(map(tuple, s["triples"]))
        problems += [f"seed {name}: rule_{k} fails at {e}" for k, e in rule_violations(triples, rules)]
        support = {v for t in triples for v in t}
        if not support <= set(s["finsupp"]):
            problems.append(f"seed {name}: {sorted(support - set(s['finsupp']))} not in finsupp")
    for e in data["pairs"]:
        a, b = e["pair"]
        mirror, name = e["mirror"], e["seed"]
        tag = f"pair {a} -> {b}"
        if name not in data["seeds"]:
            problems.append(f"{tag}: unknown seed {name}")
            continue
        if codes[a - 1][b - 1] != 6:
            problems.append(f"{tag}: not open (code {codes[a - 1][b - 1]})")
        if a != LAW_A[mirror]:
            problems.append(f"{tag}: A is not law {LAW_A[mirror]}")
        law = parse_law(texts[b - 1])
        env = {VARS.index(k): v for k, v in e["env"].items()}
        op = seed_op(data["seeds"][name]["triples"])
        try:
            left, right = evaluate(law[0], env, op, mirror), evaluate(law[1], env, op, mirror)
        except KeyError as k:
            problems.append(f"{tag}: law {b} needs the product {k.args[0]}, not in seed {name}")
            continue
        except ValueError as err:
            problems.append(f"{tag}: {err}")
            continue
        if left == right:
            problems.append(f"{tag}: law {b} holds at {e['env']} in seed {name}")
        report.append(f"{tag}: seed {name}{' mirrored' if mirror else ''}, law {b} fails at {e['env']}: "
                      f"{left} != {right}")
    if run_greedy:
        for name, s in data["seeds"].items():
            p, lines = bounded_test(s["triples"], texts, rules, **kw)
            problems += [f"bounded test from {name}: {q}" for q in p[:5]]
            tests += [(name, *line) for line in lines]
    return problems, report, tests


def lean_rules(etp_dir):
    text = (Path(etp_dir) / LEAN_FILE).read_text(encoding="utf-8")
    block = text[text.index("structure PartialSolution"):text.index("finsupp : Finset G")]
    return re.findall(r"rule_\d+ : (\(.*\))\n", block)


def selftest(texts, codes, data):
    cases = []

    def mutate(fn):
        d = copy.deepcopy(data)
        fn(d)
        return d

    cases.append(("seed triple changed", mutate(lambda d: d["seeds"]["counter274"]["triples"].__setitem__(2, [1, 3, 2])), {}))
    cases.append(("seed triple removed", mutate(lambda d: d["seeds"]["counter222"]["triples"].pop(1)), {}))
    cases.append(("second value added", mutate(lambda d: d["seeds"]["counter222"]["triples"].append([1, 2, 4])), {}))
    cases.append(("finsupp too small", mutate(lambda d: d["seeds"]["counter222"].__setitem__("finsupp", [1, 2])), {}))
    cases.append(("mirror flag flipped", mutate(lambda d: d["pairs"][2].__setitem__("mirror", False)), {}))
    cases.append(("wrong seed for a pair", mutate(lambda d: d["pairs"][0].__setitem__("seed", "counter222")), {}))
    cases.append(("x and y swapped", mutate(lambda d: d["pairs"][1].__setitem__("env", {"x": 1, "y": 2})), {}))
    cases.append(("pair not open", mutate(lambda d: d["pairs"][0].__setitem__("pair", [508, 1])), {}))
    cases.append(("wrong law A", mutate(lambda d: d["pairs"][3].__setitem__("pair", [508, 565])), {}))
    cases.append(("rule_1 misread", data, {"rules_text": RULES[:1] + [RULES[1].replace("R X1 X3 X0)", "R X1 X0 X3)")] + RULES[2:]}))
    cases.append(("rule dropped", data, {"rules_text": RULES[:10]}))
    cases.append(("extension without derived triples", data, {"skip": range(1, 9)}))
    cases.append(("extension without sP1", data, {"skip": (1,)}))
    cases.append(("extension with c not new", data, {"fresh_is_a": True}))
    rejected = 0
    for label, d, kw in cases:
        try:
            problems, _, _ = check(texts, codes, d, **kw)
        except (ValueError, KeyError, IndexError) as err:
            problems = [str(err)]
        ok = bool(problems)
        rejected += ok
        print(f"mutation {label}: {'rejected' if ok else 'ACCEPTED'}")
    print(f"selftest: {rejected} of {len(cases)} corrupted inputs rejected")
    return rejected == len(cases)


def main():
    args = sys.argv[1:]
    etp = None
    if "--etp" in args:
        i = args.index("--etp")
        etp = args[i + 1]
        del args[i:i + 2]
    flags = [x for x in args if x.startswith("--")]
    laws_file, status_file, greedy_file = [x for x in args if not x.startswith("--")]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(greedy_file, encoding="utf-8"))
    if "--selftest" in flags:
        ok = selftest(texts, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, report, tests = check(texts, codes, data)
    if etp is not None:
        found = lean_rules(etp)
        same = found == RULES
        print(f"rules compared with {LEAN_FILE}: {len(found)} found, {'identical' if same else 'DIFFERENT'}")
        if not same:
            problems.append("rules differ from the Lean file")
    print(f"{len(data['seeds'])} seeds pass the 11 rules of the Lean file" if not
          any(p.startswith("seed") for p in problems) else "seed problems")
    for line in report:
        print(line)
    for name, steps, size, law, checked, failures in tests:
        print(f"bounded test from {name}: {steps} extension steps, {size} products; law {law}: {checked} instances "
              f"evaluated, {failures} failures")
    for p in problems[:20]:
        print("PROBLEM", p)
    print(f"{len(report)} open pairs with a seed certificate")
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
