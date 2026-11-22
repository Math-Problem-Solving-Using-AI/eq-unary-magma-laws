"""S1 fidelity check: the human-readable text of every law must parse back to the stored term.

Independent small parser. Grammar (exactly what laws.show prints):
    term   := factor ['*' factor]
    factor := VAR | 'f(' term ')' | '(' term ')'
Variables are single letters, index = position in laws.VARS.

Usage: python src/check_laws_text.py data/laws_3.json
"""
import json
import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from laws import VARS  # noqa: E402


def tuplify(t):
    return tuple(tuplify(x) for x in t) if isinstance(t, list) else t


def parse_term(s, i):
    a, i = parse_factor(s, i)
    if i < len(s) and s[i] == "*":
        b, i = parse_factor(s, i + 1)
        a = ("m", a, b)
    return a, i


def parse_factor(s, i):
    if s[i] == "(":
        t, i = parse_term(s, i + 1)
        assert s[i] == ")", f"expected ) at {i} in {s!r}"
        return t, i + 1
    if s.startswith("f(", i):
        t, i = parse_term(s, i + 2)
        assert s[i] == ")", f"expected ) at {i} in {s!r}"
        return ("f", t), i + 1
    assert s[i] in VARS, f"bad char {s[i]!r} in {s!r}"
    return ("v", VARS.index(s[i])), i + 1


def parse_law(text):
    lhs, rhs = text.split(" = ")
    l, i = parse_term(lhs, 0)
    assert i == len(lhs), f"trailing text in {lhs!r}"
    r, j = parse_term(rhs, 0)
    assert j == len(rhs), f"trailing text in {rhs!r}"
    return l, r


def main():
    entries = json.load(open(sys.argv[1]))
    bad = 0
    for e in entries:
        if parse_law(e["text"]) != tuplify(e["law"]):
            bad += 1
            print("MISMATCH", e["id"], e["text"])
    print(f"{len(entries)} laws checked, {bad} mismatches")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
