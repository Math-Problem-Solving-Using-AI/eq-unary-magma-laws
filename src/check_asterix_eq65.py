"""Check results/asterix_eq65.json (step 25): the finite seed of the ETP's infinite "Asterix" model of law 598.

Law 598 is x*(y*(x*y)) = y (ETP equation 65, x = y*(x*(y*x))). The ETP (equational_theories/Asterix.lean) builds a
model on the natural numbers from a "partial solution": a finite set E1 of defined products a*b, and a subset E0 of
pairs (a, b) where the law is already closed, a*(b*(a*b)) = b, that meet 6 conditions (the fields of the structure
PartialSolution). Its Lean proof says one more product, added by act / add_e1 / add_e0 with a brand-new element z,
gives again a partial solution; closureSeq does this for every pair in turn, and closure_prop says the limit
satisfies ETP 65. This script does NOT re-check that proof. It checks, in plain Python (no z3, no Lean, no ETP files):
  1. the seed meets the 6 conditions as written in the Lean file (copied below);
  2. for each pair (A, B): the pair is open (code 6), A is law 598 (or law 88 with the mirrored model x*y = y*x),
     and law B fails at the stored values using seed products only, so it fails in every model built from the seed;
  3. a bounded test of the extension step (move_rev_good, move_rev_bad, act, add_e1, add_e0 as defined in the Lean
     file): from the seed it closes pairs first in the order of closureSeq, then random pairs, then adds products
     whenever an evaluation needs one, checks the 6 conditions along the way and that the seed's products are kept,
     and evaluates law 598 and law 88 (mirrored) directly at all pairs of small numbers. A bounded test, not a proof.
With --etp DIR it also checks the 6 conditions, the law and the seed against DIR's copy of the Lean file.
Usage: python src/check_asterix_eq65.py laws_json status_npz asterix_json [--selftest] [--etp DIR]
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

LAW_A = {False: 598, True: 88}
LEAN_FILE = "equational_theories/Asterix.lean"
# Lines 20 to 25 of the Lean file, structure PartialSolution, copied verbatim; conditions() below implements them.
# f is the operation, x a pair (x.1, x.2) of elements.
CONDITIONS = [
    "E0_subset_E1 : E0 ⊆ E1",
    "t_mem_of_mem_E0' : ∀ x ∈ E0, (x.2, f x.1 x.2) ∈ E1",
    "mem_2_of_mem_E0 : ∀ x ∈ E0, (x.1, f x.2 (f x.1 x.2)) ∈ E1",
    "eq_of_mem_E0 : ∀ x ∈ E0, f x.1 (f x.2 (f x.1 x.2)) = x.2",
    "undef_of_not_mem_E0' : ∀ x ∈ E1 \\ E0, (x.2, f x.1 x.2) ∉ E1",
    "strange: ∀ x ∈ E1, f x.1 x.2 = x.1 → ((x.2, x.2) ∈ E1 ∧ f x.2 x.2 = x.1)",
]
LAW_65 = "x = y ◇ (x ◇ (y ◇ x))"   # line 8, recall Equation65
LEAN_ORDER_STEPS = 20000   # pairs closed in the order of closureSeq (Nat.unpair of 0, 1, 2, ...)
RANDOM_STEPS = 5000        # then random pairs (fixed random seed): the Lean step allows any order
LAW_RANGE = 40             # laws evaluated at all x, y in 0 .. LAW_RANGE - 1
CHECK_EVERY = 5000


def conditions(E0, E1, misread=None):
    """The 6 fields of PartialSolution on a finite E0 and E1 (dict (a, b) -> a*b). Returns a list of problems."""
    out = []
    for a, b in E0:
        if (a, b) not in E1:
            out.append(f"E0_subset_E1 fails at {(a, b)}")
            continue
        ab = E1[(a, b)]
        if (b, ab) not in E1:
            out.append(f"t_mem_of_mem_E0' fails at {(a, b)}")
            continue
        w = E1[(b, ab)]
        if (a, w) not in E1:
            out.append(f"mem_2_of_mem_E0 fails at {(a, b)}")
            continue
        target = a if misread == "eq_of_mem_E0" else b
        if E1[(a, w)] != target:
            out.append(f"eq_of_mem_E0 fails at {(a, b)}")
    for (a, b), v in E1.items():
        if (a, b) not in E0 and (b, v) in E1:
            out.append(f"undef_of_not_mem_E0' fails at {(a, b)}")
        if v == a and not ((b, b) in E1 and E1[(b, b)] == a):
            out.append(f"strange fails at {(a, b)}")
    return out


class Partial:
    """A partial solution, grown by the definitions act, add_e1 and add_e0 of the Lean file."""

    def __init__(self, E0, E1, mutation=None):
        self.E0 = set(map(tuple, E0))
        self.E1 = {(a, b): v for a, b, v in E1}
        self.used = set()            # every first, second and value of E1
        self.by_bv = {}              # (b, a*b) -> set of a, for the filter of move_rev_good
        for (a, b), v in self.E1.items():
            self._index(a, b, v)
        self.low = 0                 # every number below it is in used
        self.mutation = mutation     # selftest only
        self.acts = self.bad = self.filtered = 0

    def _index(self, a, b, v):
        self.used.update((a, b, v))
        self.by_bv.setdefault((b, v), set()).add(a)

    def _set(self, a, b, v):
        self.E1[(a, b)] = v
        self._index(a, b, v)

    def act(self, x, y):
        """Lines 44 to 60, 181 to 195, 338 to 380 and 400 to 402: define y*x = z for a new z."""
        assert (y, x) not in self.E1
        bad = (x, y) in self.E1 and self.E1[(x, y)] == x
        while self.low in self.used:  # notMemFinset on the natural numbers: the least number not in the set
            self.low += 1
        z = self.low
        while z in self.used or z in (x, y):
            z += 1
        if self.mutation == "z not new":
            z = y
        hits = [y1 for y1 in self.by_bv.get((y, x), ())]   # E1.filter fun (y', x') => x' = y ∧ f y' x' = x
        self._set(y, x, z)
        if self.mutation != "no (z, z)":
            self._set(z, z, y)
        for y1 in hits:
            if self.mutation != "no (y', z)":
                self._set(y1, z, y)
            if self.mutation != "filter not added to E0":
                self.E0.add((y1, y))
        if bad and self.mutation != "bad treated as good":
            self.E0.add((y, x))
        self.acts += 1
        self.bad += bad
        self.filtered += bool(hits)

    def add_e1(self, x, y):
        """Line 427: make y*x defined."""
        if (y, x) not in self.E1:
            self.act(x, y)

    def add_e0(self, x, y):
        """Line 454: put (y, x) into E0."""
        self.add_e1(x, y)
        self.add_e1(self.E1[(y, x)], x)

    def op(self, a, b):
        if (a, b) not in self.E1:
            self.add_e1(b, a)
        return self.E1[(a, b)]


def evaluate(t, env, op, mirror):
    if t[0] == "v":
        return env[t[1]]
    if t[0] != "m":
        raise ValueError("law uses f")
    x, y = evaluate(t[1], env, op, mirror), evaluate(t[2], env, op, mirror)
    return op(y, x) if mirror else op(x, y)


def unpair(n):
    """Mathlib's Nat.unpair, the order in which closureSeq closes pairs."""
    s = math.isqrt(n)
    return (n - s * s, s) if n - s * s < s else (s, n - s * s - s)


def bounded_test(seed, texts, mutation=None, misread=None):
    """Grow the seed by the Lean extension step; return (problems, report)."""
    ps = Partial(seed["E0"], seed["E1"], mutation)
    problems = []

    def check_now():
        problems.extend(conditions(ps.E0, ps.E1, misread)[:3])
        kept = [(a, b) for a, b, v in seed["E1"] if ps.E1.get((a, b)) != v]
        if kept:
            problems.append(f"seed products changed at {kept[:3]}")

    for n in range(LEAN_ORDER_STEPS):
        a, b = unpair(n)
        ps.add_e0(b, a)
        if (a, b) not in ps.E0:
            problems.append(f"closureSeq step {n} left {(a, b)} outside E0")
        if (n + 1) % CHECK_EVERY == 0:
            check_now()
        if problems:
            return problems, None
    rng = random.Random(65)
    top = max(ps.used)
    for n in range(RANDOM_STEPS):
        a, b = rng.randrange(top + 1), rng.randrange(top + 1)
        ps.add_e0(b, a)
        if (n + 1) % CHECK_EVERY == 0:
            check_now()
    if problems:
        return problems, None
    laws = []
    for mirror in (False, True):
        law = parse_law(texts[LAW_A[mirror] - 1])
        failures = 0
        for x, y in itertools.product(range(LAW_RANGE), repeat=2):
            env = {0: x, 1: y}
            failures += evaluate(law[0], env, ps.op, mirror) != evaluate(law[1], env, ps.op, mirror)
        if failures:
            problems.append(f"law {LAW_A[mirror]} fails {failures} times")
        laws.append((LAW_A[mirror], LAW_RANGE * LAW_RANGE, failures))
    check_now()
    return problems, {"acts": ps.acts, "bad": ps.bad, "filtered": ps.filtered, "E1": len(ps.E1),
                      "E0": len(ps.E0), "laws": laws}


def check(texts, codes, data, run_greedy=True, **kw):
    seed = data["seed"]
    E1 = {}
    problems, report = [], []
    for a, b, v in seed["E1"]:
        if (a, b) in E1:
            problems.append(f"seed: {a}*{b} given twice")
        E1[(a, b)] = v
    E0 = set(map(tuple, seed["E0"]))
    problems += [f"seed: {p}" for p in conditions(E0, E1, kw.get("misread"))]
    for e in data["pairs"]:
        a, b = e["pair"]
        mirror = e["mirror"]
        tag = f"pair {a} -> {b}"
        if codes[a - 1][b - 1] != 6:
            problems.append(f"{tag}: not open (code {codes[a - 1][b - 1]})")
        if a != LAW_A[mirror]:
            problems.append(f"{tag}: A is not law {LAW_A[mirror]}")
        law = parse_law(texts[b - 1])
        env = {VARS.index(k): v for k, v in e["env"].items()}
        try:
            left, right = (evaluate(side, env, lambda p, q: E1[(p, q)], mirror) for side in law)
        except KeyError as k:
            problems.append(f"{tag}: law {b} needs the product {k.args[0]}, not in the seed")
            continue
        if left == right:
            problems.append(f"{tag}: law {b} holds at {e['env']} in the seed")
        report.append(f"{tag}: seed{' mirrored' if mirror else ''}, law {b} fails at {e['env']}: {left} != {right}")
    test = None
    if run_greedy:
        p, test = bounded_test(seed, texts, **kw)
        problems += [f"bounded test: {q}" for q in p[:5]]
    return problems, report, test


def lean_expr(text):
    """Evaluate the seed's 'f a b := ...' of the Lean file: if/then/else, numerals, [list].getD b default."""
    toks = re.findall(r"\[[^\]]*\]|\.getD|if|then|else|=|\d+|[a-z]+", text)

    def parse(i):
        if toks[i] == "if":
            var, eq, num, then = toks[i + 1:i + 5]
            assert eq == "=" and then == "then"
            yes, i = parse(i + 5)
            assert toks[i] == "else"
            no, i = parse(i + 1)
            return (lambda env: yes(env) if env[var] == int(num) else no(env)), i
        if toks[i].startswith("["):
            values = [int(v) for v in toks[i][1:-1].split(",")]
            assert toks[i + 1] == ".getD"
            var, default = toks[i + 2], int(toks[i + 3])
            return (lambda env: values[env[var]] if env[var] < len(values) else default), i + 4
        num = int(toks[i])
        return (lambda env: num), i + 1

    fn, end = parse(0)
    assert end == len(toks), "trailing tokens"
    return fn


def canonical(law):
    """A law up to renaming of variables and swapping sides."""
    def walk(t, names):
        if t[0] == "v":
            return "v%d" % names.setdefault(t[1], len(names))
        return "(" + walk(t[1], names) + "*" + walk(t[2], names) + ")"
    forms = []
    for l, r in ((law[0], law[1]), (law[1], law[0])):
        names = {}
        forms.append(walk(l, names) + "=" + walk(r, names))
    return min(forms)


def compare_with_lean(etp_dir, texts, data):
    text = (Path(etp_dir) / LEAN_FILE).read_text(encoding="utf-8")
    problems = []
    block = text[text.index("structure PartialSolution"):text.index("abbrev PartialSolution.g")]
    found = [line.strip() for line in block.splitlines()[4:] if line.strip()]
    if found != CONDITIONS:
        problems.append("the 6 conditions differ from the Lean file")
    m = re.search(r"recall Equation65 .*?:= ∀ x y : G, (.*)\n", text)
    if not m or m.group(1) != LAW_65:
        problems.append("Equation65 differs from the Lean file")
    if canonical(parse_law(LAW_65.replace(" ◇ ", "*").replace("◇", "*"))) != canonical(parse_law(texts[597])):
        problems.append("ETP 65 is not law 598")
    init = text[text.index("def initial"):text.index("E0_subset_E1 := by decide")]
    pairs = lambda s: {tuple(map(int, p)) for p in re.findall(r"\((\d+), (\d+)\)", s)}
    E0 = pairs(re.search(r"E0 := \{(.*?)\}", init, re.S).group(1))
    E1 = pairs(re.search(r"E1 := \{(.*?)\}", init, re.S).group(1))
    f = lean_expr(re.search(r"f a b :=(.*)", init, re.S).group(1))
    if E0 != set(map(tuple, data["seed"]["E0"])):
        problems.append("seed E0 differs from the Lean file")
    if E1 != {(a, b) for a, b, _ in data["seed"]["E1"]}:
        problems.append("seed E1 differs from the Lean file")
    wrong = [(a, b) for a, b, v in data["seed"]["E1"] if f({"a": a, "b": b}) != v]
    if wrong:
        problems.append(f"seed values differ from the Lean file at {wrong}")
    return problems


def selftest(texts, codes, data):
    cases = []

    def mutate(fn):
        d = copy.deepcopy(data)
        fn(d)
        return d

    cases.append(("seed value changed", mutate(lambda d: d["seed"]["E1"][1].__setitem__(2, 3)), {}))
    cases.append(("seed product 1*0 removed", mutate(lambda d: d["seed"]["E1"].pop(1)), {}))
    cases.append(("seed product 8*0 removed", mutate(lambda d: d["seed"]["E1"].pop(13)), {}))
    cases.append(("seed product given twice", mutate(lambda d: d["seed"]["E1"].append([0, 0, 2])), {}))
    cases.append(("seed E0 pair removed", mutate(lambda d: d["seed"]["E0"].pop(0)), {}))
    cases.append(("seed E0 pair added", mutate(lambda d: d["seed"]["E0"].append([1, 3])), {}))
    cases.append(("mirror flag flipped", mutate(lambda d: d["pairs"][1].__setitem__("mirror", False)), {}))
    cases.append(("wrong value of x", mutate(lambda d: d["pairs"][0].__setitem__("env", {"x": 8})), {}))
    cases.append(("pair not open", mutate(lambda d: d["pairs"][0].__setitem__("pair", [598, 1])), {}))
    cases.append(("wrong law A", mutate(lambda d: d["pairs"][1].__setitem__("pair", [598, 579])), {}))
    cases.append(("eq_of_mem_E0 misread", data, {"misread": "eq_of_mem_E0"}))
    cases.append(("extension with z not new", data, {"mutation": "z not new"}))
    cases.append(("extension without (z, z)", data, {"mutation": "no (z, z)"}))
    cases.append(("extension without (y', z)", data, {"mutation": "no (y', z)"}))
    cases.append(("extension without the E0 filter", data, {"mutation": "filter not added to E0"}))
    cases.append(("extension with bad treated as good", data, {"mutation": "bad treated as good"}))
    rejected = 0
    for label, d, kw in cases:
        try:
            problems, _, _ = check(texts, codes, d, **kw)
        except (ValueError, KeyError, IndexError, AssertionError) as err:
            problems = [repr(err)]
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
    laws_file, status_file, data_file = [x for x in args if not x.startswith("--")]
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(data_file, encoding="utf-8"))
    if "--selftest" in flags:
        ok = selftest(texts, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, report, test = check(texts, codes, data)
    if etp is not None:
        p = compare_with_lean(etp, texts, data)
        print(f"conditions, Equation65 and seed compared with {LEAN_FILE}: {'identical' if not p else 'DIFFERENT'}")
        problems += p
    print("the seed passes the 6 conditions of the Lean file" if not
          any(p.startswith("seed") for p in problems) else "seed problems")
    for line in report:
        print(line)
    if test:
        print(f"bounded test: {test['acts']} extension steps ({test['bad']} of kind move_rev_bad, {test['filtered']} "
              f"with a non-empty filter), {test['E1']} products, {test['E0']} closed pairs")
        for law, checked, failures in test["laws"]:
            print(f"bounded test: law {law}: {checked} instances evaluated, {failures} failures")
    for p in problems[:20]:
        print("PROBLEM", p)
    print(f"{len(report)} open pairs with a seed certificate")
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
