"""Finite model finder with z3.

find_model(axioms, n, violate=None, timeout_ms): look for a structure of size n
(elements 0..n-1, table for *, table for f) satisfying every law in `axioms`
and, if `violate` is given, FAILING that law for some assignment.
Returns dict(mul=[[..]], f=[..]) or None (unsat or unknown, see status).
"""
import itertools
import sys

import z3

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import nvars  # noqa: E402


_calls = itertools.count()


def find_model(axioms, n, violate=None, timeout_ms=20000):
    # z3 forbids redeclaring an enum sort name, so make each call's names unique.
    k = next(_calls)
    E, els = z3.EnumSort(f"E{k}", [f"e{k}_{i}" for i in range(n)])
    mul = z3.Function("mul", E, E, E)
    f = z3.Function("f", E, E)

    def tz(t, env):
        if t[0] == "v":
            return env[t[1]]
        if t[0] == "f":
            return f(tz(t[1], env))
        return mul(tz(t[1], env), tz(t[2], env))

    s = z3.Solver()
    s.set("timeout", timeout_ms)
    for law in axioms:
        for tup in itertools.product(els, repeat=nvars(law)):
            env = dict(enumerate(tup))
            s.add(tz(law[0], env) == tz(law[1], env))
    if violate is not None:
        cs = {i: z3.Const(f"c{i}", E) for i in range(nvars(violate))}
        s.add(tz(violate[0], cs) != tz(violate[1], cs))
    r = s.check()
    if str(r) != "sat":
        return None, str(r)
    m = s.model()
    idx = {str(e): i for i, e in enumerate(els)}

    def val(expr):
        return idx[str(m.eval(expr, model_completion=True))]

    table = [[val(mul(a, b)) for b in els] for a in els]
    ftab = [val(f(a)) for a in els]
    return {"mul": table, "f": ftab}, "sat"


def check_model(model, law):
    """Independent check by direct evaluation: does `model` satisfy `law` for all assignments?"""
    n = len(model["f"])

    def ev(t, env):
        if t[0] == "v":
            return env[t[1]]
        if t[0] == "f":
            return model["f"][ev(t[1], env)]
        return model["mul"][ev(t[1], env)][ev(t[2], env)]

    for tup in itertools.product(range(n), repeat=nvars(law)):
        env = dict(enumerate(tup))
        if ev(law[0], env) != ev(law[1], env):
            return False
    return True
