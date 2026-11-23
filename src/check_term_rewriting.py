"""Check results/refutations_term_rewriting.json (step 16): non-implications shown by infinite term structures.

An entry "a,b" claims: law A (id a+1) does not imply law B (id b+1), because of the structure T_A:
  elements: formal terms over generators g0, g1, ... built with F(.) and P(.,.);
  f(e) = F(e) and d*e = P(d,e), except when that new term is an instance of the left side t of the rule
  t -> v (A read as t = v), in which case the result is what the instance puts at v.
The entry stores the rule, the witness (B's variables sent to generators) and the values of B's two
sides there. This script does not import the search (src/refute_by_rewriting.py). For each entry it
  1. parses A and B from their texts (src/check_laws_text.py) and requires them to be the texts of
     laws a and b in data/laws_3.json, and the pair to be open (code 5 or 6) in results/status_matrix.npz;
  2. re-derives the rule from A (one side is a variable occurring in the other) and requires it to equal
     the stored rule, and requires that no proper non-variable subterm of t unifies with a renamed copy
     of t (the condition of the hand argument that T_A satisfies A);
  3. recomputes the values of B's sides at the witness and requires them to equal the stored ones and to
     differ (distinct terms are distinct elements, so B fails in T_A).
For each source law it also
  4. asks z3 whether A fails anywhere in T_A (terms as an algebraic datatype, so this covers ALL elements;
     quantifier-free, z3-only): it must answer unsat;
  5. evaluates A in plain Python on every assignment of the terms with at most 2 operations over g0, g1.
Finally, as a control against the rest of the table, for EVERY law of the list that gives an overlap-free
rule and every target, the verdict of T_A (B fails or not at the generators) must not contradict the
table: no refutation where the table has an implication (codes 0, 3, 4), no equality where it has a
finite counterexample (codes 1, 2). (Equal values at the generators come from rewriting steps, each an
instance of A, so they mean A implies B.)

Usage: python src/check_term_rewriting.py laws_json status_npz refutations_json [--selftest]
"""
import copy
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import z3

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402  (separate small parser)

LETTERS = "xyzwuvab"


# ---- terms. Law terms: ('v', i), ('f', t), ('m', t, s). Elements: ('g', i), ('F', e), ('P', d, e).

def law_text(t):
    if t[0] == "v":
        return LETTERS[t[1]]
    if t[0] == "f":
        return f"f({law_text(t[1])})"
    a, b = (law_text(c) if c[0] != "m" else f"({law_text(c)})" for c in t[1:])
    return f"{a}*{b}"


def elem_text(e):
    return f"g{e[1]}" if e[0] == "g" else f"{e[0]}({','.join(elem_text(c) for c in e[1:])})"


def parse_elem(s):
    def go(i):
        if s[i] == "g":
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            return ("g", int(s[i + 1:j])), j
        head = s[i]
        assert head in "FP" and s[i + 1] == "(", f"bad element {s!r}"
        args, i = [], i + 2
        while True:
            a, i = go(i)
            args.append(a)
            if s[i] == ")":
                break
            assert s[i] == ",", f"bad element {s!r}"
            i += 1
        assert len(args) == (1 if head == "F" else 2), f"bad arity in {s!r}"
        return (head, *args), i + 1
    e, i = go(0)
    assert i == len(s), f"trailing text in {s!r}"
    return e


def variables(t):
    return {t[1]} if t[0] == "v" else set().union(*(variables(c) for c in t[1:]))


def all_subterms(t):
    out = [t]
    for c in t[1:] if t[0] != "v" else ():
        out += all_subterms(c)
    return out


def rule_of(law):
    """Read the law as t -> v (v a variable inside t). None if it has no such side."""
    for t, r in ((law[0], law[1]), (law[1], law[0])):
        if r[0] == "v" and t[0] != "v" and r[1] in variables(t):
            return t, r[1]
    return None


def substitute(t, s):
    if t[0] == "v":
        return substitute(s[t[1]], s) if t[1] in s else t
    return (t[0],) + tuple(substitute(c, s) for c in t[1:])


def unifiable(a, b):
    """Robinson unification with an explicit list of equations; True if a solution exists."""
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
                return False
            s[p[1]] = q
        elif p[0] == q[0]:
            todo += list(zip(p[1:], q[1:]))
        else:
            return False
    return True


def overlap_free(t):
    shift = 1 + max(variables(t))
    copy_t = substitute(t, {i: ("v", i + shift) for i in variables(t)})
    return not any(s[0] != "v" and unifiable(s, copy_t) for s in all_subterms(t)[1:])


# ---- the structure T_A in plain Python

def instance(p, e, s):
    """Match law pattern p against element e; returns the bindings or None."""
    if p[0] == "v":
        if p[1] in s and s[p[1]] != e:
            return None
        return {**s, p[1]: e}
    if (p[0], e[0]) not in (("f", "F"), ("m", "P")):
        return None
    for q, c in zip(p[1:], e[1:]):
        s = instance(q, c, s)
        if s is None:
            return None
    return s


def make_ops(t, v, rewrite=True):
    def reduce(e):
        s = instance(t, e, {}) if rewrite else None
        return s[v] if s is not None else e
    return (lambda a: reduce(("F", a))), (lambda a, b: reduce(("P", a, b)))


def ev(term, env, ops):
    f, mul = ops
    if term[0] == "v":
        return env[term[1]]
    if term[0] == "f":
        return f(ev(term[1], env, ops))
    return mul(ev(term[1], env, ops), ev(term[2], env, ops))


def small_elements():
    level = [("g", 0), ("g", 1)]
    out = list(level)
    for _ in range(2):
        new = [("F", e) for e in out] + [("P", a, b) for a in out for b in out]
        out = list(dict.fromkeys(out + new))
    return [e for e in out if size(e) <= 2]


def size(e):
    return 0 if e[0] == "g" else 1 + sum(size(c) for c in e[1:])


def sample_holds(law, ops, elems):
    vs = sorted(variables(law[0]) | variables(law[1]))
    for vals in itertools.product(elems, repeat=len(vs)):
        env = dict(zip(vs, vals))
        if ev(law[0], env, ops) != ev(law[1], env, ops):
            return False
    return True


# ---- the structure T_A in z3: terms as an algebraic datatype, so the check covers every element

def z3_fails_somewhere(law, t, v, rewrite=True):
    T = z3.Datatype("T")
    T.declare("G", ("idx", z3.IntSort()))
    T.declare("F", ("arg", T))
    T.declare("P", ("left", T), ("right", T))
    T = T.create()

    def match(p, e, binds, conds):
        if p[0] == "v":
            if p[1] in binds:
                conds.append(binds[p[1]] == e)
            else:
                binds[p[1]] = e
            return
        if p[0] == "f":
            conds.append(T.is_F(e))
            match(p[1], T.arg(e), binds, conds)
        else:
            conds.append(T.is_P(e))
            match(p[1], T.left(e), binds, conds)
            match(p[2], T.right(e), binds, conds)

    def reduce(e):
        if not rewrite:
            return e
        binds, conds = {}, []
        match(t, e, binds, conds)
        return z3.If(z3.And(conds), binds[v], e)

    ops = (lambda a: reduce(T.F(a))), (lambda a, b: reduce(T.P(a, b)))
    env = {i: z3.Const(f"x{i}", T) for i in variables(law[0]) | variables(law[1])}
    s = z3.Solver()
    s.set("timeout", 60000)
    s.add(ev(law[0], env, ops) != ev(law[1], env, ops))
    return str(s.check())


# ---- the checks

def check(texts, codes, data, rewrite=True):
    problems = []
    sources = {}
    for key, e in data.items():
        a, b = map(int, key.split(","))
        if not (0 <= a < len(texts) and 0 <= b < len(texts)) or (texts[a], texts[b]) != (e["A"], e["B"]):
            problems.append(f"{key}: law texts do not match data/laws_3.json")
            continue
        if codes[a, b] not in (5, 6):
            problems.append(f"{key}: pair is not open (code {codes[a, b]})")
        la, lb = parse_law(e["A"]), parse_law(e["B"])
        rule = rule_of(la)
        if rule is None or f"{law_text(rule[0])} -> {LETTERS[rule[1]]}" != e["rule"]:
            problems.append(f"{key}: stored rule {e['rule']!r} is not the rule of A")
            continue
        if not overlap_free(rule[0]):
            problems.append(f"{key}: rule {e['rule']} has an overlap, T_A need not satisfy A")
            continue
        sources[a] = (la, rule)
        nb = len(variables(lb[0]) | variables(lb[1]))
        if e["witness"] != {LETTERS[i]: f"g{i}" for i in range(nb)}:
            problems.append(f"{key}: witness is not B's variables sent to distinct generators")
            continue
        env = {i: parse_elem(e["witness"][LETTERS[i]]) for i in range(nb)}
        ops = make_ops(*rule, rewrite)
        left, right = ev(lb[0], env, ops), ev(lb[1], env, ops)
        if (elem_text(left), elem_text(right)) != (e["B_left"], e["B_right"]):
            problems.append(f"{key}: stored values of B differ from the recomputed ones")
        if left == right:
            problems.append(f"{key}: both sides of B are equal in T_A, nothing refuted")
    elems = small_elements()
    for a, (la, (t, v)) in sorted(sources.items()):
        st = z3_fails_somewhere(la, t, v, rewrite)
        if st != "unsat":
            problems.append(f"law {a + 1} {texts[a]}: z3 says {st} to 'A fails somewhere in T_A'")
        if not sample_holds(la, make_ops(t, v, rewrite), elems):
            problems.append(f"law {a + 1} {texts[a]}: A fails in T_A on terms with at most 2 operations")
    return problems, sources


def table_control(texts, codes):
    """Verdicts of T_A for every overlap-free source law and every target, against the table."""
    problems, rows, n_ref, n_eq = [], 0, 0, 0
    laws = [parse_law(x) for x in texts]
    for a, la in enumerate(laws):
        rule = rule_of(la)
        if rule is None or not overlap_free(rule[0]):
            continue
        rows += 1
        ops = make_ops(*rule)
        for b, lb in enumerate(laws):
            env = {i: ("g", i) for i in variables(lb[0]) | variables(lb[1])}
            refuted = ev(lb[0], env, ops) != ev(lb[1], env, ops)
            n_ref += refuted
            n_eq += not refuted
            if refuted and codes[a, b] in (0, 3, 4):
                problems.append(f"{a},{b}: T_A refutes but the table says implies (code {codes[a, b]})")
            if not refuted and codes[a, b] in (1, 2):
                problems.append(f"{a},{b}: T_A gives an implication but the table has a counterexample")
    return problems, rows, n_ref, n_eq


def selftest(texts, codes, data):
    keys = sorted(data, key=lambda k: tuple(map(int, k.split(","))))
    k0 = keys[0]
    rejected = 0

    def run(name, d, rewrite=True, only_z3=False):
        nonlocal rejected
        probs, _ = check(texts, codes, d, rewrite)
        ok = bool(probs)
        rejected += ok
        print(f"mutation {name}: {'rejected' if ok else 'ACCEPTED'}" + (f" ({probs[0]})" if ok else ""))

    small = {k: data[k] for k in keys[:3]}
    d = copy.deepcopy(small); d[k0]["B_left"] = d[k0]["B_right"]
    run("value of B's left side replaced by the right one", d)
    d = copy.deepcopy(small); d[k0]["B_right"] = "F(" + d[k0]["B_right"] + ")"
    run("value of B's right side changed", d)
    d = copy.deepcopy(small); d[k0]["A"], d[k0]["B"] = d[k0]["B"], d[k0]["A"]
    run("A and B swapped", d)
    a, b = map(int, k0.split(","))
    d = copy.deepcopy(small); d[f"{a},{b + 1}"] = d.pop(k0)
    run("key shifted to the next target", d)
    k2 = next(k for k in keys if len(data[k]["witness"]) >= 2)  # with one variable this changes nothing
    d = {k2: copy.deepcopy(data[k2])}; d[k2]["witness"] = {x: "g0" for x in d[k2]["witness"]}
    run(f"all witness variables sent to g0 ({k2})", d)
    # a pair whose source has an overlap, with a made-up entry in the stored format
    ov = next((i, j) for i, j in np.argwhere(codes == 6)
              if rule_of(parse_law(texts[i])) and not overlap_free(rule_of(parse_law(texts[i]))[0]))
    i, j = map(int, ov)
    t, v = rule_of(parse_law(texts[i]))
    d = {f"{i},{j}": {"A": texts[i], "B": texts[j], "rule": f"{law_text(t)} -> {LETTERS[v]}",
                      "witness": {}, "B_left": "g0", "B_right": "g1"}}
    run("entry for a source law with an overlap", d)
    d = copy.deepcopy(small)
    run("checker's T_A never rewrites (z3 and sample must see A fail)", d, rewrite=False)
    # z3 encoding on its own: a source law with an overlap whose T_A really fails A
    hit = None
    for i in range(len(texts)):
        la = parse_law(texts[i])
        r = rule_of(la)
        if r and not overlap_free(r[0]) and z3_fails_somewhere(la, *r) == "sat":
            hit = texts[i]
            break
    ok = hit is not None
    rejected += ok
    print(f"mutation z3 encoding on overlapping rules: {'a law whose T_A fails it is found: ' + hit if ok else 'NONE FOUND'}")
    total = 8
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    laws_file, status_file, ref_file = args
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(ref_file))
    if "--selftest" in sys.argv:
        ok = selftest(texts, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, sources = check(texts, codes, data)
    print(f"{len(data)} certificates checked, from {len(sources)} source laws; "
          f"z3 and a plain sample check that each T_A satisfies its law")
    tp, rows, n_ref, n_eq = table_control(texts, codes)
    print(f"table control: {rows} overlap-free source laws, {n_ref} targets fail in T_A, {n_eq} hold; "
          f"{len(tp)} contradictions with the table")
    problems += tp
    for p in problems[:20]:
        print("PROBLEM", p)
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
