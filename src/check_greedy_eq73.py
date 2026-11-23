"""Check results/greedy_eq73.json (step 23): the finite seeds of the ETP's infinite models of law 565.

Law 565 is x*(x*(y*x)) = y (ETP equation 73). The ETP (ManuallyProved/Equation73.lean) builds models on the
free group: x*y = f(y * x^-1) * x, where f extends a finite "seed" (a partial function given as a list of
pairs) and satisfies f(f(f(a) * a^-1)) = a^-1 everywhere. Its Lean theorem exists_extension says that every seed
passing four finite conditions extends to such an f; this script does NOT re-check that theorem. It checks, in
plain Python with its own free group words (no z3, no Lean, no ETP files):
  1. each seed contains E0 and passes the four conditions of PreExtension.OK as fromList_ok states them:
     func (one value per argument), base (E0 inside), eq73 (if f(a) = b and f(b a^-1) = c are in the seed, then
     f(c) = a^-1 is in the seed), aux (a -> f(a) a^-1 is one-to-one on the seed);
  2. for each pair (A, B): the pair is open (code 6), A is law 565 (or law 86, its mirror, with the mirrored
     model x*y = f(x * y^-1) * y), the law r fails in the model at the stored x, using seed values of f only
     (so it fails in every extension of the seed), and B = r or the table says B implies r (code 3 or 4);
  3. a bounded test of the extension rule (Next in the Lean file): from each seed it adds values one argument at
     a time, with a fresh generator as the new value and the extra value the rule asks for, checks the four
     conditions after every step, and then evaluates law A directly in the partial model (normal and mirrored)
     at every pair of short words where all needed values exist. A bounded test, not a proof of the theorem.
Usage: python src/check_greedy_eq73.py laws_json status_npz greedy_json [--selftest]
"""
import copy
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_laws_text import parse_law  # noqa: E402

LAW_A = {False: 565, True: 86}
TEST_GENS = 4          # generators of the short words tried in the bounded test
TEST_LEN = 4           # arguments processed first: all reduced words up to this length
LAW_LEN = 2            # law A evaluated at all pairs of reduced words up to this length
MAX_STEPS = 20000


def reduce(w):
    out = []
    for g in w:
        if g == 0:
            raise ValueError("generator 0 is not used in these files")
        if out and out[-1] == -g:
            out.pop()
        else:
            out.append(g)
    return tuple(out)


def mul(u, v):
    return reduce(list(u) + list(v))


def inv(w):
    return tuple(-g for g in reversed(w))


def word(w):
    w = tuple(w)
    if reduce(w) != w:
        raise ValueError(f"word {list(w)} is not reduced")
    return w


def seed_dict(pairs):
    """Problems and the partial function of a seed (condition func)."""
    f, problems = {}, []
    for a, b in pairs:
        a, b = word(a), word(b)
        if a in f and f[a] != b:
            problems.append(f"func: two values at {list(a)}")
        f[a] = b
    return problems, f


def ok_problems(f, e0):
    """Conditions base, eq73 and aux of PreExtension.OK on a finite partial function (func holds for a dict)."""
    problems = [f"base: E0 value at {list(a)} missing" for a, b in e0 if f.get(a) != b]
    seen = {}
    for a, b in f.items():
        k = mul(b, inv(a))
        if k in f and f.get(f[k]) != inv(a):
            problems.append(f"eq73: a = {list(a)}")
        if k in seen and seen[k] != a:
            problems.append(f"aux: {list(a)} and {list(seen[k])}")
        seen[k] = a
    return problems


def op(f, x, y, mirror):
    """x*y in the (partial) model; KeyError if f is not defined where needed."""
    if mirror:
        return mul(f[mul(x, inv(y))], y)
    return mul(f[mul(y, inv(x))], x)


def evaluate(t, env, f, mirror):
    if t[0] == "v":
        return env[t[1]]
    if t[0] != "m":
        raise ValueError("law uses f")
    return op(f, evaluate(t[1], env, f, mirror), evaluate(t[2], env, f, mirror), mirror)


def short_words(gens, length):
    out = [()]
    layer = [()]
    for _ in range(length):
        layer = [w + (g,) for w in layer for g in list(range(1, gens + 1)) + list(range(-gens, 0))
                 if not w or w[-1] != -g]
        out += layer
    return out


def greedy(f0, e0, skip_extra=False):
    """Bounded run of the extension rule from a seed. Returns (problems, f, steps)."""
    f = dict(f0)
    rel = {mul(b, inv(a)): a for a, b in f.items()}   # f(a) a^-1 -> a  (one-to-one by aux)
    top = max([abs(g) for w in list(f) + list(f.values()) for g in w] + [TEST_GENS])
    queue = short_words(TEST_GENS, TEST_LEN)
    done, steps, problems = set(), 0, []
    i = 0
    while i < len(queue) and steps < MAX_STEPS:
        d = queue[i]
        i += 1
        if d in done:
            continue
        done.add(d)
        if d not in f:
            top += 1                      # fresh generator: appears in no word used so far
            c = (top,)
            new = [(d, c)]
            if d in rel and not skip_extra:
                new.append((c, inv(rel[d])))   # the Relevant a with f(a) a^-1 = d: f(c) = a^-1
            for a, b in new:
                f[a] = b
                rel[mul(b, inv(a))] = a
            steps += 1
            if steps % 200 == 0:
                problems += ok_problems(f, e0)
        nxt = mul(f[d], inv(d))
        if nxt not in done:
            queue.append(nxt)
    problems += ok_problems(f, e0)
    return problems, f, steps


def law_instances(law, f, mirror):
    """Evaluate law at all pairs of short words where every value exists: (checked, failures)."""
    words = short_words(TEST_GENS, LAW_LEN)
    checked = failures = 0
    for x, y in itertools.product(words, repeat=2):
        env = {0: x, 1: y}
        try:
            left, right = evaluate(law[0], env, f, mirror), evaluate(law[1], env, f, mirror)
        except KeyError:
            continue
        checked += 1
        failures += left != right
    return checked, failures


def check(texts, codes, data, run_greedy=True, skip_extra=False):
    problems, seeds, report = [], {}, []
    e0 = [(word(a), word(b)) for a, b in data["E0"]]
    if e0 != [((), (1,)), ((1,), (2,)), ((2,), ())]:
        problems.append("E0 is not E0List of the Lean file")
    for name, pairs in data["seeds"].items():
        p, f = seed_dict(pairs)
        p += ok_problems(f, e0)
        problems += [f"seed {name}: {q}" for q in p]
        seeds[name] = f
    for e in data["pairs"]:
        a, b = e["pair"]
        r, mirror, name = e["r"], e["mirror"], e["seed"]
        tag = f"pair {a} -> {b}"
        if name not in seeds:
            problems.append(f"{tag}: unknown seed {name}")
            continue
        if codes[a - 1][b - 1] != 6:
            problems.append(f"{tag}: not open (code {codes[a - 1][b - 1]})")
        if a != LAW_A[mirror]:
            problems.append(f"{tag}: A is not law {LAW_A[mirror]}")
        if not (b == r or codes[b - 1][r - 1] in (3, 4)):
            problems.append(f"{tag}: law {b} does not imply law {r} in the table")
        law = parse_law(texts[r - 1])
        try:
            left = evaluate(law[0], {0: word(e["x"])}, seeds[name], mirror)
            right = evaluate(law[1], {0: word(e["x"])}, seeds[name], mirror)
        except KeyError as k:
            problems.append(f"{tag}: law {r} needs f at {list(k.args[0])}, not in seed {name}")
            continue
        except (IndexError, ValueError) as err:
            problems.append(f"{tag}: law {r} cannot be evaluated ({err})")
            continue
        if left == right:
            problems.append(f"{tag}: law {r} holds at x = {e['x']} in seed {name}")
        report.append(f"{tag}: seed {name}{' mirrored' if mirror else ''}, law {r} fails at x = 1: "
                      f"{list(left)} != {list(right)}" + ("" if b == r else f"; law {b} implies law {r} (code 3)"))
    tests = []
    if run_greedy:
        for name, f0 in seeds.items():
            p, f, steps = greedy(f0, e0, skip_extra)
            problems += [f"greedy from {name}: {q}" for q in p[:5]]
            for mirror in (False, True):
                checked, failures = law_instances(parse_law(texts[LAW_A[mirror] - 1]), f, mirror)
                if failures or not checked:
                    problems.append(f"greedy from {name}: law {LAW_A[mirror]} fails {failures} times "
                                    f"in {checked} instances")
                tests.append((name, steps, len(f), LAW_A[mirror], checked, failures))
    return problems, report, tests


def selftest(texts, codes, data):
    cases = []

    def mutate(fn):
        d = copy.deepcopy(data)
        fn(d)
        return d

    cases.append(("seed value changed", mutate(lambda d: d["seeds"]["not_203"].__setitem__(4, [[3], [2]])), {}))
    cases.append(("seed entry removed", mutate(lambda d: d["seeds"]["not_203"].pop(4)), {}))
    cases.append(("E0 entry removed from a seed", mutate(lambda d: d["seeds"]["not_99_4380"].pop(1)), {}))
    cases.append(("conflicting value added", mutate(lambda d: d["seeds"]["not_203"].append([[1], [3]])), {}))
    cases.append(("aux broken", mutate(lambda d: d["seeds"]["not_255"].append([[5], [1, 5]])), {}))
    cases.append(("mirror flag flipped", mutate(lambda d: d["pairs"][5].__setitem__("mirror", False)), {}))
    cases.append(("wrong seed for a pair", mutate(lambda d: d["pairs"][0].__setitem__("seed", "not_203")), {}))
    cases.append(("wrong law r", mutate(lambda d: d["pairs"][1].__setitem__("r", 70)), {}))
    cases.append(("link B -> r not in table", mutate(lambda d: d["pairs"][2].__setitem__("r", 492)), {}))
    cases.append(("pair not open", mutate(lambda d: d["pairs"][0].__setitem__("pair", [565, 1])), {}))
    cases.append(("unreduced word", mutate(lambda d: d["seeds"]["not_255"].__setitem__(3, [[-1, 2, -2], [3]])), {}))
    cases.append(("greedy without the extra value", data, {"skip_extra": True}))
    rejected = 0
    for label, d, kw in cases:
        try:
            problems, _, _ = check(texts, codes, d, run_greedy=bool(kw), **kw)
        except (ValueError, KeyError, IndexError) as err:
            problems = [str(err)]
        ok = bool(problems)
        rejected += ok
        print(f"mutation {label}: {'rejected' if ok else 'ACCEPTED'}")
    # wrong operation: f(x * y^-1) * x instead of f(y * x^-1) * x must break law 565 in the bounded test
    global op
    real = op
    op = lambda f, x, y, mirror: mul(f[mul(x, inv(y))], x)  # noqa: E731
    try:
        problems, _, _ = check(texts, codes, data)
    finally:
        op = real
    rejected += bool(problems)
    print(f"mutation wrong operation: {'rejected' if problems else 'ACCEPTED'}")
    total = len(cases) + 1
    print(f"selftest: {rejected} of {total} corrupted inputs rejected")
    return rejected == total


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    laws_file, status_file, greedy_file = args
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    data = json.load(open(greedy_file))
    if "--selftest" in sys.argv:
        ok = selftest(texts, codes, data)
        print("ALL PASS" if ok else "SELFTEST FAILED")
        sys.exit(0 if ok else 1)
    problems, report, tests = check(texts, codes, data)
    print(f"{len(data['seeds'])} seeds pass the finite conditions of the Lean file" if not
          any(p.startswith("seed") for p in problems) else "seed problems")
    for line in report:
        print(line)
    for name, steps, size, law, checked, failures in tests:
        print(f"bounded test from {name}: {steps} extension steps, {size} values; law {law}: {checked} instances "
              f"evaluated, {failures} failures")
    for p in problems[:20]:
        print("PROBLEM", p)
    print(f"{len(report)} open pairs with a seed certificate")
    print("ALL PASS" if not problems else f"{len(problems)} PROBLEMS")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
