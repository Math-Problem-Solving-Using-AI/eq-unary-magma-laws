"""Ask: does law A imply law B, how do we know, and how sure are we?

Usage:
  python query.py "x*y = x" "x*(y*z) = x"
  python query.py "x*y = x" "x*(y*z) = x" --witness     (print a structure when one exists)
  python query.py --list "f(x) = x"                       (all other laws, grouped by status, for A)

Law syntax: variables are the letters x y z w u v a b c d e g h (f is NOT a variable, it is the
unary operation). `*` is the binary operation, `f(...)` the unary one. A product that is an
operand of another product needs parentheses: `x*(y*z) = x`, not `x*y*z = x`.
Laws are matched up to renaming of variables and swapping the two sides.
Only laws of size <= 3 are in the table, size = number of `*` and `f` symbols on both sides
(see README). Anything larger is refused with a message.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from check_laws_text import parse_law  # noqa: E402
from laws import rename  # noqa: E402

MEANING = {
    0: ("same law", "-"),
    1: ("NOT an implication: refuted by a structure with 2 or 3 elements", "model-verified"),
    2: ("NOT an implication: refuted by a certificate (structure with 4 or 5 elements)", "model-verified"),
    3: ("implication, proved by z3 (with transitive closure)", "z3-only"),
    4: ("implication, because law A forces a one-element structure", "z3-only"),
    5: ("OPEN: A is one of 9 laws with no small model, collapse unproven", "open"),
    6: ("OPEN: unresolved", "open"),
}


def tuplify(t):
    return tuple(tuplify(x) for x in t) if isinstance(t, list) else t


def load():
    entries = json.load(open(ROOT / "data" / "laws_3.json"))
    index = {tuplify(e["law"]): i for i, e in enumerate(entries)}
    codes = np.load(ROOT / "results" / "status_matrix.npz")["codes"]
    return entries, index, codes


def find_law(text, index):
    l, r = parse_law(text)
    key = min(rename(l, r), rename(r, l))
    if key not in index:
        raise SystemExit(f"law not in the table (size > 3, or text not understood): {text!r}")
    return index[key]


def witness(a, b, entries):
    """A structure of size 2 or 3 satisfying A and failing B, found by search."""
    from models import all_models, reduce_iso, sat_set

    for n in (2, 3):
        mul, f = all_models(n)
        if n >= 3:
            mul, f = reduce_iso(mul, f, n)
        sa = set(sat_set(tuple_law(entries[a]), n, mul, f).tolist())
        sb = set(sat_set(tuple_law(entries[b]), n, mul, f).tolist())
        for i in sorted(sa - sb):
            return {"size": n, "mul": mul[i].astype(int).tolist(), "f": f[i].astype(int).tolist()}
    return None


def tuple_law(e):
    return tuplify(e["law"])


def etp_note(a, b, c):
    """For two laws without f: what the Equational Theories Project data says (step 08)."""
    path = ROOT / "results" / "etp_crosscheck.json"
    if not path.exists():
        return None
    r = json.load(open(path, encoding="utf-8"))
    num = {m["our_id"]: m["etp"] for m in r["mapping"]}
    ia, ib = a + 1, b + 1
    if ia not in num or ib not in num:
        return None
    head = f"ETP: A is Equation{num[ia]}, B is Equation{num[ib]} in the Equational Theories Project. "
    for row in r["settled_open_pairs"]:
        if row[0] == ia and row[1] == ib:
            verdict = "implies" if row[3] else "does NOT imply"
            return (head + f"Open in our table; the ETP data says A {verdict} B ({row[4]}). "
                    "Label: known (ETP; proofs are Lean-checked there, not re-checked by us). "
                    "See steps/08-etp-crosscheck.md")
    if c == 0:
        return head
    return head + "Our answer agrees with the ETP data (steps/08-etp-crosscheck.md)."


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    entries, index, codes = load()
    if "--list" in flags:
        a = find_law(args[0], index)
        print(f"A = #{entries[a]['id']}: {entries[a]['text']}")
        for c in range(1, 7):
            ids = np.where(codes[a] == c)[0]
            print(f"\n{MEANING[c][1]:15s} {MEANING[c][0]}  [{len(ids)} laws]")
            for b in ids[:10]:
                print(f"   B = #{entries[b]['id']}: {entries[b]['text']}")
            if len(ids) > 10:
                print(f"   ... {len(ids) - 10} more")
        return
    if len(args) != 2:
        raise SystemExit(__doc__)
    a, b = find_law(args[0], index), find_law(args[1], index)
    c = int(codes[a, b])
    print(f"A = #{entries[a]['id']}: {entries[a]['text']}")
    print(f"B = #{entries[b]['id']}: {entries[b]['text']}")
    print(f"code {c}: {MEANING[c][0]}")
    print(f"label: {MEANING[c][1]}  (labels are defined in docs/shared/VERIFICATION_PROTOCOL.md)")
    etp = etp_note(a, b, c)
    if etp:
        print(etp)
    if "--witness" in flags and c in (1, 2):
        if c == 1:
            w = witness(a, b, entries)
        else:
            w = json.load(open(ROOT / "results" / "witnesses_larger_models.json"))[f"{a},{b}"]["model"]
        print("structure satisfying A and failing B:", json.dumps(w))


if __name__ == "__main__":
    main()
