"""Cross-check the f-free part of our table against the Equational Theories Project (ETP) data.

Why this is a valid check
-------------------------
A law without `f` is an ordinary magma law. For two such laws A and B:
- if some structure (set, `*`, `f`) satisfies A and fails B, forgetting `f` gives a magma that
  satisfies A and fails B;
- if some magma satisfies A and fails B, adding `f(x) = x` gives a structure of our kind that
  satisfies A and fails B (A and B do not mention `f`).
So "A implies B" means the same in our setting and for magmas, and the ETP decided every
implication between its 4,694 magma laws with at most 4 operations. Our f-free laws have at most
3 operations, so each should be one of the ETP laws.

What the script does (each step prints what it found)
-----------------------------------------------------
1. Read the ETP law list (`equations.txt`, one law per line, `◇` is the operation) and parse it
   with a parser written here, NOT with this repository's parser.
2. Bring every law to a canonical form: name variables in order of first appearance, try both
   orientations of `=`, keep the smaller. Check that no two ETP laws get the same canonical form
   (if they did, our idea of how the ETP normalizes laws would be wrong).
3. Map each of our f-free laws (`data/laws_3.json`) to the ETP law with the same canonical form.
4. Read the ETP outcome matrix (`general_outcomes.json.gz`: entry [i][j] says whether Equation i+1
   implies Equation j+1). Sanity-check the orientation with laws whose answer is forced:
   `x = y` (Equation2) implies every law, every law implies `x = x` (Equation1).
5. Compare with `results/status_matrix.npz` for every ordered pair of distinct f-free laws.
   Report agreements, disagreements, and what the ETP says about pairs that are open for us.

Usage (from the repository root):
  python src/etp_crosscheck.py ETP_EQUATIONS_TXT ETP_GENERAL_OUTCOMES_JSON_GZ [OUT_JSON]

The ETP files are not stored here (they belong to the ETP and are large). Get them from
  https://github.com/teorth/equational_theories  (data/equations.txt)
  https://teorth.github.io/equational_theories/raw_data/general_outcomes.json.gz
and record the commit / download date and sha256, as in steps/08-etp-crosscheck.md.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

# Our status codes (results/README.md)
OURS_TRUE = {3, 4}      # implication (z3-only)
OURS_FALSE = {1, 2}     # non-implication (model-verified)
OURS_OPEN = {5, 6}


# ---------- a small parser for law texts, used for both sources ----------

def parse(text, op):
    """Parse 'lhs = rhs' where terms use variables (letters), parentheses, the binary operator
    `op`, and (for our laws) `f(...)`. Returns (lhs, rhs) as nested tuples:
    ('v', name) | ('f', t) | ('m', a, b)."""
    toks = []
    i = 0
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith(op, i):
            toks.append("*")
            i += len(op)
        elif c in "()=":
            toks.append(c)
            i += 1
        elif c.isalpha():
            toks.append(c)
            i += 1
        else:
            raise ValueError(f"bad character {c!r} in {text!r}")
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take(x=None):
        t = toks[pos[0]]
        if x is not None and t != x:
            raise ValueError(f"expected {x!r} got {t!r} in {text!r}")
        pos[0] += 1
        return t

    def atom():
        t = peek()
        if t == "(":
            take("(")
            e = expr()
            take(")")
            return e
        if t == "f" and pos[0] + 1 < len(toks) and toks[pos[0] + 1] == "(":
            take("f")
            take("(")
            e = expr()
            take(")")
            return ("f", e)
        if t is not None and t.isalpha():
            take()
            return ("v", t)
        raise ValueError(f"unexpected {t!r} in {text!r}")

    def expr():
        a = atom()
        if peek() == "*":
            take("*")
            b = atom()
            if peek() == "*":
                raise ValueError(f"ambiguous product without parentheses in {text!r}")
            return ("m", a, b)
        return a

    lhs = expr()
    take("=")
    rhs = expr()
    if pos[0] != len(toks):
        raise ValueError(f"trailing tokens in {text!r}")
    return lhs, rhs


def leaves(t, out):
    if t[0] == "v":
        out.append(t[1])
    elif t[0] == "f":
        leaves(t[1], out)
    else:
        leaves(t[1], out)
        leaves(t[2], out)
    return out


def relabel(t, names):
    if t[0] == "v":
        return ("v", names[t[1]])
    if t[0] == "f":
        return ("f", relabel(t[1], names))
    return ("m", relabel(t[1], names), relabel(t[2], names))


def canon(lhs, rhs):
    """Canonical form up to renaming variables and swapping sides."""
    forms = []
    for a, b in ((lhs, rhs), (rhs, lhs)):
        names = {}
        for v in leaves(a, []) + leaves(b, []):
            names.setdefault(v, len(names))
        forms.append(repr((relabel(a, names), relabel(b, names))))
    return min(forms)


def from_stored(t):
    """Our stored encoding ['m', a, b] / ['f', a] / ['v', i] -> parser encoding."""
    if t[0] == "v":
        return ("v", f"v{t[1]}")
    if t[0] == "f":
        return ("f", from_stored(t[1]))
    return ("m", from_stored(t[1]), from_stored(t[2]))


def has_f(t):
    return t[0] == "f" or (t[0] == "m" and (has_f(t[1]) or has_f(t[2])))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    eq_txt, outcomes_gz = sys.argv[1], sys.argv[2]
    out_json = sys.argv[3] if len(sys.argv) > 3 else None
    report = {"inputs": {"etp_equations_txt_sha256": sha256(eq_txt),
                         "etp_general_outcomes_sha256": sha256(outcomes_gz)}}

    # 1-2. ETP laws and their canonical forms
    etp_lines = [ln.strip() for ln in open(eq_txt, encoding="utf-8") if ln.strip()]
    etp_canon = {}
    clashes = []
    for k, ln in enumerate(etp_lines, start=1):
        c = canon(*parse(ln, "◇"))
        if c in etp_canon:
            clashes.append((etp_canon[c], k))
        etp_canon.setdefault(c, k)
    print(f"ETP laws read: {len(etp_lines)}; canonical-form clashes: {len(clashes)}")
    report["etp_laws"] = len(etp_lines)
    report["etp_canonical_clashes"] = clashes

    # 3. our f-free laws -> ETP number
    ours = json.load(open(ROOT / "data" / "laws_3.json", encoding="utf-8"))
    ffree = []
    for e in ours:
        lhs, rhs = from_stored(e["law"][0]), from_stored(e["law"][1])
        if has_f(lhs) or has_f(rhs):
            continue
        # second, independent reading: parse our text with the parser above
        lt, rt = parse(e["text"], "*")
        if canon(lt, rt) != canon(lhs, rhs):
            raise SystemExit(f"text and stored term disagree for law {e['id']}: {e['text']}")
        if "f(" in e["text"]:
            raise SystemExit(f"law {e['id']} has f in text but not in term")
        ffree.append((e["id"], e["text"], etp_canon.get(canon(lhs, rhs))))
    unmapped = [(i, t) for i, t, k in ffree if k is None]
    print(f"our f-free laws: {len(ffree)}; mapped to an ETP law: {len(ffree) - len(unmapped)}; "
          f"unmapped: {unmapped}")
    targets = [k for _, _, k in ffree if k is not None]
    if len(set(targets)) != len(targets):
        raise SystemExit("two of our laws map to the same ETP law: our laws are not distinct up to renaming/swap")
    report["mapping"] = [{"our_id": i, "text": t, "etp": k} for i, t, k in ffree]

    # 4. ETP outcomes and orientation check
    d = json.load(gzip.open(outcomes_gz, "rt", encoding="utf-8"))
    names, O = d["equations"], d["outcomes"]
    assert names == [f"Equation{k}" for k in range(1, len(names) + 1)], "unexpected equation order"
    assert len(names) == len(etp_lines) == len(O) == len(O[0])
    values = Counter(x for row in O for x in row)
    print("ETP outcome values:", dict(values))
    report["etp_outcome_values"] = dict(values)

    def etp_true(i, j):  # does Equation i imply Equation j? (1-based)
        v = O[i - 1][j - 1]
        if v.endswith("_true"):
            return True
        if v.endswith("_false"):
            return False
        raise SystemExit(f"ETP outcome for {i} => {j} is neither true nor false: {v}")

    n = len(names)
    assert etp_lines[0] == "x = x" and etp_lines[1] == "x = y"
    assert all(etp_true(2, j) for j in range(1, n + 1)), "orientation: x = y must imply everything"
    assert all(etp_true(i, 1) for i in range(1, n + 1)), "orientation: everything must imply x = x"
    assert not etp_true(1, 2), "orientation: x = x must not imply x = y"
    print("orientation checks passed: O[i][j] = 'Equation i+1 implies Equation j+1'")

    # 5. compare
    codes = np.load(ROOT / "results" / "status_matrix.npz")["codes"]
    stats, disagreements, settled_open = compare(ffree, codes, O)
    print("comparison:", dict(sorted(stats.items())))
    for x in disagreements[:50]:
        print("  DISAGREE:", x)

    # 6. self-test: the comparison must notice corrupted input (a checker that cannot fail
    #    proves nothing, docs/shared/VERIFICATION_PROTOCOL.md S2b)
    selftest = run_selftest(ffree, codes, O)
    for name, ok, detail in selftest:
        print(f"selftest {name}: {'detected' if ok else 'NOT DETECTED'} ({detail})")
    if not all(ok for _, ok, _ in selftest):
        raise SystemExit("self-test failed: the comparison did not notice a corruption")

    report["comparison"] = dict(sorted(stats.items()))
    report["disagreements"] = disagreements
    report["selftest"] = [{"corruption": n, "detected": ok, "detail": d} for n, ok, d in selftest]
    # compact list: [our id A, our id B, our code, ETP says A implies B, ETP outcome string]
    report["settled_open_pairs_columns"] = ["a_id", "b_id", "our_code", "etp_implies", "etp_value"]
    report["settled_open_pairs"] = [[x["a_id"], x["b_id"], x["our_code"], x["etp_implies"],
                                     x["etp_value"]] for x in settled_open]
    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            fh.write("{\n")
            items = list(report.items())
            for k, (key, val) in enumerate(items):
                sep = "," if k < len(items) - 1 else ""
                if key in ("mapping", "settled_open_pairs"):  # one row per line, readable diffs
                    fh.write(f" {json.dumps(key)}: [\n")
                    fh.write(",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in val))
                    fh.write(f"\n ]{sep}\n")
                else:
                    fh.write(f" {json.dumps(key)}: {json.dumps(val, ensure_ascii=False)}{sep}\n")
            fh.write("}\n")
        print("written", out_json)
    return 1 if disagreements else 0


def compare(ffree, codes, O):
    """Every ordered pair of distinct f-free laws: our code versus the ETP outcome."""
    stats = Counter()
    disagreements, settled_open = [], []
    for a_id, a_txt, a_k in ffree:
        for b_id, b_txt, b_k in ffree:
            if a_id == b_id:
                continue
            c = int(codes[a_id - 1, b_id - 1])
            v = O[a_k - 1][b_k - 1]
            if not (v.endswith("_true") or v.endswith("_false")):
                raise SystemExit(f"ETP outcome for {a_k} => {b_k} is neither true nor false: {v}")
            e = v.endswith("_true")
            stats["pairs"] += 1
            row = {"a": a_txt, "b": b_txt, "a_id": a_id, "b_id": b_id, "our_code": c,
                   "etp_a": a_k, "etp_b": b_k, "etp_implies": e, "etp_value": v}
            if c in OURS_OPEN:
                stats[f"ours_open_code{c}_etp_{'true' if e else 'false'}"] += 1
                settled_open.append(row)
            elif (c in OURS_TRUE and e) or (c in OURS_FALSE and not e):
                stats["agree"] += 1
                stats[f"agree_code{c}"] += 1
            else:
                stats["disagree"] += 1
                disagreements.append(row)
    return stats, disagreements, settled_open


def run_selftest(ffree, codes, O):
    out = []
    # (a) flip one of our non-implications (code 1) into an implication (code 3)
    c2 = codes.copy()
    a_id, b_id = next((a, b) for a, _, _ in ffree for b, _, _ in ffree
                      if a != b and codes[a - 1, b - 1] == 1)
    c2[a_id - 1, b_id - 1] = 3
    n = len(compare(ffree, c2, O)[1])
    out.append(("one of our codes flipped 1->3", n == 1, f"{n} disagreement(s), expected 1"))
    # (b) flip one of our implications (code 4) into a non-implication (code 1)
    c3 = codes.copy()
    a_id, b_id = next((a, b) for a, _, _ in ffree for b, _, _ in ffree
                      if a != b and codes[a - 1, b - 1] == 4)
    c3[a_id - 1, b_id - 1] = 1
    n = len(compare(ffree, c3, O)[1])
    out.append(("one of our codes flipped 4->1", n == 1, f"{n} disagreement(s), expected 1"))
    # (c) mapping shifted by one ETP number (wrong normalization guess)
    shifted = [(i, t, k + 1) for i, t, k in ffree]
    n = len(compare(shifted, codes, O)[1])
    out.append(("mapping shifted by one", n > 0, f"{n} disagreements, expected many"))
    # (d) ETP matrix read transposed (wrong orientation guess)
    OT = [list(r) for r in zip(*O)]
    n = len(compare(ffree, codes, OT)[1])
    out.append(("ETP matrix transposed", n > 0, f"{n} disagreements, expected many"))
    return out


if __name__ == "__main__":
    sys.exit(main())
