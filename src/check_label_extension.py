"""Check results/label_extension_277.json (step 26): an infinite model of law 277 where laws 632 and 574 fail.

Law 277 is (x*y)*f(x) = y. The structure S is built in two layers.
  Base M: the normal forms over one letter g of a rewrite system R (4 rules, stored in the file). If every rule makes
  terms strictly smaller (size, with no variable occurring more often on the right) rewriting always stops, and if
  every critical pair (overlap of two left sides) rewrites to one result, the normal form of a term does not depend
  on the order of rewriting (Newman's lemma with the critical pair lemma). Then M with m*n = nf(m*n) and
  f(m) = nf(f(m)) is a structure, and every rule holds in it as an equation. F = normal forms starting with f: when
  no left side starts with f, these are exactly the values of f in M.
  Labels: S = {(m, k) : m in M, k = 0, 1, 2, ..., k = 0 when m is in F}, f(m, k) = (f(m), 0) and
      (m, k)*(n, l) = (m*n, l + push)          if n is not in F,
                      (m*n, 0)                 if m*n is in F,
                      (m*n, max(k - pop, 0))   otherwise.
Label lemma (hand argument, checked below over all cases): if M satisfies law 277 and "m*n in F implies n in F",
then S satisfies law 277. Proof: (x*y)*f(x) has first part (m*n)*f(m) = n by law 277 in M. Its label: if n is not
in F, then m*n is not in F, x*y has label l + 1 and multiplying by f(x) = (f(m), 0), whose first part is in F, gives
max(l + 1 - 1, 0) = l. If n is in F, then l = 0 and the result has first part n in F, so label 0. Both facts about M
hold when rule 1 is law 277 and rule 4 is f(x)*f(y) = f(x*y): if m*n = f(q) then n = (m*n)*f(m) = f(q)*f(m) =
f(q*m), which is in F.
This script checks, in plain Python (no z3, no imports of the search code):
  1. R: rule 1 is law 277 as stored in the law list, rule 4 is f(x)*f(y) = f(x*y), no left side starts with f,
     every rule shrinks terms, every critical pair joins;
  2. the label lemma over all cases (which of m, n, m*n lie in F, with "m*n in F implies n in F") and all labels
     up to a bound, with the stored push and pop;
  3. law 277 in S directly, and "m*n in F implies n in F" in M, at all pairs of elements whose term has at most
     max_size symbols and whose label is at most max_label (a bounded test, not a proof for all elements);
  4. for each pair (A, B): the pair is open (code 5 or 6), A is law 277 (law 408 for the mirrored structure,
     x*y read as y*x, and law 408 is checked to be the mirror of law 277), the stored values are elements of S, and
     law B gives two different elements there.
With --z3 it also asks z3 to prove, for an arbitrary model M of law 277, first f(x)*f(y) = f(x*y) and then (with
that fact given) the label lemma; this is the only z3 use. Without the fact z3 answered unknown in 60 s.
Usage: python src/check_label_extension.py laws_json status_npz label_json [--selftest] [--z3]
"""
import copy
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law, parse_term  # noqa: E402
from laws import VARS  # noqa: E402

LAW_A = {False: 277, True: 408}
RULE_4 = "f(x)*f(y) = f(x*y)"
LEMMA_LABELS = 12   # labels 0 .. LEMMA_LABELS in the case check of the lemma


def tsize(t):
    return 1 if t[0] == "v" else 1 + sum(tsize(c) for c in t[1:])


def varcount(t, c):
    if t[0] == "v":
        c[t[1]] = c.get(t[1], 0) + 1
    else:
        for x in t[1:]:
            varcount(x, c)
    return c


def mirror(t):
    if t[0] == "v":
        return t
    if t[0] == "f":
        return ("f", mirror(t[1]))
    return ("m", mirror(t[2]), mirror(t[1]))


def walk(t, s):
    while t[0] == "v" and t[1] in s:
        t = s[t[1]]
    return t


def unify(a, b, s):
    a, b = walk(a, s), walk(b, s)
    if a == b:
        return s
    if a[0] == "v" or b[0] == "v":
        if a[0] != "v":
            a, b = b, a
        if occurs(a[1], b, s):
            return None
        s = dict(s)
        s[a[1]] = b
        return s
    if a[0] != b[0]:
        return None
    for x, y in zip(a[1:], b[1:]):
        s = unify(x, y, s)
        if s is None:
            return None
    return s


def occurs(v, t, s):
    t = walk(t, s)
    if t[0] == "v":
        return t[1] == v
    return any(occurs(v, c, s) for c in t[1:])


def resolve(t, s):
    t = walk(t, s)
    if t[0] == "v":
        return t
    return (t[0],) + tuple(resolve(c, s) for c in t[1:])


def match(p, t, s):
    if p[0] == "v":
        if p[1] in s:
            return s if s[p[1]] == t else None
        s = dict(s)
        s[p[1]] = t
        return s
    if p[0] != t[0]:
        return None
    for a, b in zip(p[1:], t[1:]):
        s = match(a, b, s)
        if s is None:
            return None
    return s


def subst(t, s):
    if t[0] == "v":
        return s.get(t[1], t)
    return (t[0],) + tuple(subst(c, s) for c in t[1:])


def rename(t, k):
    return ("v", t[1] + k) if t[0] == "v" else (t[0],) + tuple(rename(c, k) for c in t[1:])


def positions(t, p=()):
    yield p, t
    if t[0] != "v":
        for i, c in enumerate(t[1:]):
            yield from positions(c, p + (i,))


def replace(t, p, u):
    if not p:
        return u
    i = p[0] + 1
    return t[:i] + (replace(t[i], p[1:], u),) + t[i + 1:]


class Base:
    """The normal forms of the rule list; variables of a term being normalized are constants."""

    def __init__(self, rules):
        self.rules = rules
        self.cache = {}

    def nf(self, t):
        if t[0] == "v":
            return t
        if t in self.cache:
            return self.cache[t]
        u = (t[0],) + tuple(self.nf(c) for c in t[1:])
        for l, r in self.rules:
            s = match(l, u, {})
            if s is not None:
                u = self.nf(subst(r, s))
                break
        self.cache[t] = u
        return u

    def is_normal(self, t):
        return all(match(l, u, {}) is None for _, u in positions(t) for l, _ in self.rules if u[0] != "v")


def check_rules(rules, law_a):
    problems = []
    if not rules or rules[0] != law_a:
        problems.append("rule 1 is not law 277")
    if parse_law(RULE_4) not in rules:
        problems.append(f"no rule {RULE_4}")
    for i, (l, r) in enumerate(rules, 1):
        if l[0] == "f":
            problems.append(f"rule {i}: left side starts with f")
        if l[0] == "v":
            problems.append(f"rule {i}: left side is a variable")
        cl, cr = varcount(l, {}), varcount(r, {})
        if tsize(l) <= tsize(r) or any(cr[v] > cl.get(v, 0) for v in cr):
            problems.append(f"rule {i}: does not shrink every instance")
    if problems:
        return problems, 0
    base = Base(rules)
    count = 0
    for i, (l1, r1) in enumerate(rules):
        for j, (l2, r2) in enumerate(rules):
            a1, b1 = rename(l1, 100), rename(r1, 100)
            for p, u in positions(l2):
                if u[0] == "v" or (i == j and p == ()):
                    continue
                th = unify(a1, u, {})
                if th is None:
                    continue
                count += 1
                left = resolve(replace(l2, p, b1), th)
                right = resolve(r2, th)
                if base.nf(left) != base.nf(right):
                    problems.append(f"critical pair of rules {i + 1} and {j + 1} at {p} does not join")
    return problems, count


def label(k, l, n_in_f, mn_in_f, push, pop):
    """Label of (m, k)*(n, l); None when the case is not allowed (n not in F but m*n in F)."""
    if not n_in_f:
        return None if mn_in_f else l + push
    if mn_in_f:
        return 0
    return max(k - pop, 0)


def check_lemma(push, pop):
    """Law 277 in S over every case, given (m*n)*f(m) = n and 'm*n in F implies n in F' in M."""
    problems, cases = [], 0
    for m_in_f, n_in_f, mn_in_f in itertools.product((False, True), repeat=3):
        if mn_in_f and not n_in_f:
            continue
        for k in [0] if m_in_f else range(LEMMA_LABELS + 1):
            for l in [0] if n_in_f else range(LEMMA_LABELS + 1):
                cases += 1
                lab = label(k, l, n_in_f, mn_in_f, push, pop)
                if lab is None or lab < 0 or (mn_in_f and lab != 0):
                    problems.append(f"lemma: x*y has no valid label ({m_in_f}, {n_in_f}, {mn_in_f}, {k}, {l})")
                    continue
                # (m*n, lab)*(f(m), 0): f(m) is in F, the product (m*n)*f(m) = n is in F iff n is
                res = label(lab, 0, True, n_in_f, push, pop)
                if res != l:
                    problems.append(f"lemma: (x*y)*f(x) has label {res}, not {l} ({m_in_f}, {n_in_f}, {mn_in_f}, "
                                    f"{k}, {l})")
    return problems, cases


class Model:
    def __init__(self, base, push, pop, mirrored=False):
        self.base, self.push, self.pop, self.mirrored = base, push, pop, mirrored

    @staticmethod
    def in_f(t):
        return t[0] == "f"

    def valid(self, e):
        m, k = e
        return self.base.is_normal(m) and isinstance(k, int) and k >= 0 and (k == 0 or not self.in_f(m))

    def op(self, x, y):
        if self.mirrored:
            x, y = y, x
        (m, k), (n, l) = x, y
        mn = self.base.nf(("m", m, n))
        lab = label(k, l, self.in_f(n), self.in_f(mn), self.push, self.pop)
        if lab is None:
            raise ValueError(f"{show(m)}*{show(n)} is in F but {show(n)} is not")
        return mn, lab

    def f(self, x):
        return self.base.nf(("f", x[0])), 0

    def evaluate(self, t, env):
        if t[0] == "v":
            return env[t[1]]
        if t[0] == "f":
            return self.f(self.evaluate(t[1], env))
        return self.op(self.evaluate(t[1], env), self.evaluate(t[2], env))


def show(t):
    if t[0] == "v":
        return VARS[t[1]]
    if t[0] == "f":
        return f"f({show(t[1])})"
    a, b = (show(c) if c[0] != "m" else f"({show(c)})" for c in t[1:])
    return f"{a}*{b}"


def small_terms(base, max_size, gen):
    by = {1: {gen}}
    for n in range(2, max_size + 1):
        out = {("f", a) for a in by[n - 1]}
        for i in range(1, n - 1):
            out |= {("m", a, b) for a in by[i] for b in by[n - 1 - i]}
        by[n] = {t for t in out if base.is_normal(t)}
    return sorted(set().union(*by.values()), key=lambda t: (tsize(t), show(t)))


def bounded_test(model, law_a, max_size, max_label, gen):
    terms = small_terms(model.base, max_size, gen)
    elems = [(t, k) for t in terms for k in ([0] if model.in_f(t) else range(max_label + 1))]
    problems, count = [], 0
    for x in elems:
        for y in elems:
            count += 1
            try:
                if model.evaluate(law_a[0], {0: x, 1: y}) != model.evaluate(law_a[1], {0: x, 1: y}):
                    problems.append(f"law 277 fails at x = {x}, y = {y}")
            except ValueError as err:
                problems.append(str(err))
            if len(problems) > 5:
                return problems, len(terms), len(elems), count
    return problems, len(terms), len(elems), count


def check(laws, codes, data, run_bounded=True):
    problems, report = [], []
    gen = parse_term(data["base"]["generator"], 0)[0]
    rules = [parse_law(r) for r in data["base"]["rules"]]
    law_a = laws[LAW_A[False] - 1]
    if mirror(law_a[0]) != laws[LAW_A[True] - 1][0] or mirror(law_a[1]) != laws[LAW_A[True] - 1][1]:
        problems.append("law 408 is not the mirror of law 277")
    p, cps = check_rules(rules, law_a)
    problems += p
    report.append(f"rules: {len(rules)}, all shrink terms, {cps} critical pairs, "
                  f"{'all join' if not p else 'PROBLEMS'}")
    if p:
        return problems, report, None
    push, pop = data["labels"]["push"], data["labels"]["pop"]
    p, cases = check_lemma(push, pop)
    problems += p
    report.append(f"label lemma: {cases} cases (labels up to {LEMMA_LABELS}), {'all hold' if not p else 'PROBLEMS'}")
    base = Base(rules)
    test = None
    if run_bounded:
        b = data["bounded"]
        p, nt, ne, count = bounded_test(Model(base, push, pop), law_a, b["max_size"], b["max_label"], gen)
        problems += [f"bounded test: {q}" for q in p]
        test = (nt, ne, count, len(p))
    for e in data["pairs"]:
        a, bb = e["pair"]
        mirrored = e["mirror"]
        tag = f"pair {a} -> {bb}"
        if codes[a - 1][bb - 1] not in (5, 6):
            problems.append(f"{tag}: not open (code {codes[a - 1][bb - 1]})")
        if a != LAW_A[mirrored]:
            problems.append(f"{tag}: A is not law {LAW_A[mirrored]}")
        model = Model(base, push, pop, mirrored)
        env = {}
        for letter, (text, k) in e["env"].items():
            el = (parse_term(text, 0)[0], k)
            if not model.valid(el):
                problems.append(f"{tag}: {letter} = ({text}, {k}) is not an element of S")
            env[VARS.index(letter)] = el
        law_b = laws[bb - 1]
        if set(varcount(law_b[0], varcount(law_b[1], {}))) != set(env):
            problems.append(f"{tag}: values given for {sorted(e['env'])}, law {bb} has other letters")
            continue
        left, right = (model.evaluate(side, env) for side in law_b)
        if left == right:
            problems.append(f"{tag}: law {bb} holds at {e['env']}")
        report.append(f"{tag}: S{' mirrored' if mirrored else ''}, law {bb} at {e['env']}: "
                      f"({show(left[0])}, {left[1]}) != ({show(right[0])}, {right[1]})")
    return problems, report, test


def z3_lemma(push, pop):
    """z3, two calls: f(x)*f(y) = f(x*y) follows from law 277; then the label lemma for an arbitrary model of law
    277 in which that fact holds (only F, the values of f, is described). Returns both answers."""
    import z3
    M = z3.DeclareSort("M")
    op = z3.Function("op", M, M, M)
    f = z3.Function("f", M, M)
    pre = z3.Function("pre", M, M)
    in_f = z3.Function("in_F", M, z3.BoolSort())  # exactly the values of f, by the two axioms below
    a, b = z3.Consts("a b", M)
    law = z3.ForAll([a, b], op(op(a, b), f(a)) == b)
    fact = z3.ForAll([a, b], op(f(a), f(b)) == f(op(a, b)))
    s = z3.Solver()
    s.set("timeout", 60000)
    s.add(law, z3.Not(fact))
    first = str(s.check())
    s = z3.Solver()
    s.set("timeout", 60000)
    s.add(law, fact)
    s.add(z3.ForAll([a], in_f(f(a))))
    s.add(z3.ForAll([a], z3.Implies(in_f(a), f(pre(a)) == a)))

    def lab(k, l, n_in_f, mn_in_f):
        return z3.If(z3.Not(n_in_f), l + push, z3.If(mn_in_f, 0, z3.If(k - pop > 0, k - pop, 0)))

    m, n = z3.Consts("m n", M)
    k, l = z3.Ints("k l")
    s.add(k >= 0, l >= 0, z3.Implies(in_f(m), k == 0), z3.Implies(in_f(n), l == 0))
    mn = op(m, n)
    lab1 = lab(k, l, in_f(n), in_f(mn))
    lab2 = lab(lab1, 0, True, in_f(op(mn, f(m))))
    # negation of: x*y is a valid element and (x*y)*f(x) = y
    s.add(z3.Or(z3.And(in_f(mn), lab1 != 0), op(mn, f(m)) != n, lab2 != l))
    return first, str(s.check())


def selftest(laws, codes, data):
    cases = []

    def mutate(fn):
        d = copy.deepcopy(data)
        fn(d)
        return d

    rules = data["base"]["rules"]
    cases.append(("rule 1 is not law 277", mutate(lambda d: d["base"]["rules"].__setitem__(0, "(x*y)*f(y) = x"))))
    cases.append(("rule 4 removed", mutate(lambda d: d["base"]["rules"].pop(3))))
    cases.append(("rule 3 removed", mutate(lambda d: d["base"]["rules"].pop(2))))
    cases.append(("rule 2 removed", mutate(lambda d: d["base"]["rules"].pop(1))))
    cases.append(("rule 3 with a wrong right side", mutate(lambda d: d["base"]["rules"].__setitem__(2, "y*f(x*y) = f(y)"))))
    cases.append(("rule 2 reversed", mutate(lambda d: d["base"]["rules"].__setitem__(1, "y = x*(y*f(x))"))))
    cases.append(("extra rule starting with f", mutate(lambda d: d["base"]["rules"].append("f(f(x)) = x"))))
    cases.append(("push 0", mutate(lambda d: d["labels"].__setitem__("push", 0))))
    cases.append(("push 2", mutate(lambda d: d["labels"].__setitem__("push", 2))))
    cases.append(("pop 0", mutate(lambda d: d["labels"].__setitem__("pop", 0))))
    cases.append(("value where law 632 holds", mutate(lambda d: d["pairs"][0]["env"].__setitem__("y", ["g", 1]))))
    cases.append(("label on a value of f", mutate(lambda d: d["pairs"][0]["env"].__setitem__("y", ["f(g)", 1]))))
    cases.append(("value not a normal form", mutate(lambda d: d["pairs"][1]["env"].__setitem__("x", ["g*(g*f(g))", 0]))))
    cases.append(("value missing", mutate(lambda d: d["pairs"][0]["env"].pop("y"))))
    cases.append(("pair not open", mutate(lambda d: d["pairs"][0].__setitem__("pair", [277, 1]))))
    cases.append(("wrong law A", mutate(lambda d: d["pairs"][2].__setitem__("pair", [277, 128]))))
    cases.append(("mirror flag flipped", mutate(lambda d: d["pairs"][2].__setitem__("mirror", False))))
    cases.append(("generator inside F", mutate(lambda d: d["pairs"][1]["env"].__setitem__("x", ["f(g)", 0]))))
    assert rules == data["base"]["rules"]
    rejected = 0
    for name, d in cases:
        try:
            problems, _, _ = check(laws, codes, d)
        except (ValueError, KeyError, IndexError, AssertionError, RecursionError) as err:
            problems = [repr(err)]
        ok = bool(problems)
        rejected += ok
        print(f"mutation {name}: {'rejected' if ok else 'ACCEPTED'}")
    print(f"selftest: {rejected} of {len(cases)} corrupted inputs rejected")
    return rejected == len(cases)


def main():
    args = sys.argv[1:]
    flags = [x for x in args if x.startswith("--")]
    laws_file, status_file, data_file = [x for x in args if not x.startswith("--")]
    laws = [parse_law(e["text"]) for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(data_file, encoding="utf-8"))
    if "--selftest" in flags:
        ok = selftest(laws, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, report, test = check(laws, codes, data)
    for line in report:
        print(line)
    if test:
        nt, ne, count, bad = test
        print(f"bounded test: {nt} normal forms with at most {data['bounded']['max_size']} symbols, {ne} elements "
              f"with labels up to {data['bounded']['max_label']}, law 277 at {count} pairs, {bad} failures")
    if "--z3" in flags:
        first, second = z3_lemma(data["labels"]["push"], data["labels"]["pop"])
        print(f"z3 (unsat = proved): law 277 gives f(x)*f(y) = f(x*y): {first}; "
              f"label lemma for every model of law 277: {second}")
    for p in problems[:20]:
        print("PROBLEM", p)
    print(f"{len(data['pairs'])} open pairs with a certificate")
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
