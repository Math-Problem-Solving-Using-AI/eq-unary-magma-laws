"""Trace the 16 open pairs without `f` that the ETP calls "Austin pairs" (step 22).

For each open pair (A, B) of laws without `f` where the ETP says "A does not imply B", find how the ETP's
answer is built: one infinite counterexample that the ETP proves in Lean (a "facts" entry of
`data/full_entries.json` with `finite: false`: a structure satisfying law s and failing law r), possibly
read in the mirror (swap the two sides of every product: the mirror of a model of s is a model of the mirror
of s), plus two implications "s implies A" and "B implies r". Then that structure satisfies A and fails B.

A chain is kept only if s is a law of this repository and "s implies A" is in our own table (codes 3 or 4,
`z3-only`) or s = A, and "B implies r" is either in our table (or r = B) or, when r has more than 3 products
and so is not one of our laws, has a short derivation found and replayed here (each step replaces an
instance of one side of B by the same instance of the other side). So a chain says: "this pair is settled
once the base ETP structure is checked"; the only thing taken from the ETP is that one base structure.

The mirror is not taken from the ETP's `duals.json` alone: each mirror used is recomputed here from the
law text (parser of src/etp_crosscheck.py) and must agree with `duals.json`.

Usage (from the repository root):
  python src/trace_austin_pairs.py ETP_DIR laws_json status_npz etp_crosscheck_json [OUT_JSON] [--selftest]
ETP_DIR is a local clone of https://github.com/teorth/equational_theories (read only). With OUT_JSON the
chains are written there; with --selftest the chain check is run on corrupted chains, which it must reject.
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from etp_crosscheck import canon, parse  # noqa: E402

OURS_TRUE = {3, 4}
DIAMOND = "◇"   # the ETP's operation symbol


def mirror(t):
    if t[0] == "v":
        return t
    return ("m", mirror(t[2]), mirror(t[1]))


class Data:
    def __init__(self, etp_dir, laws_json, status_npz, cross_json):
        etp = Path(etp_dir)
        self.eqs = [ln.strip() for ln in open(etp / "data" / "equations.txt", encoding="utf-8") if ln.strip()]
        self.austin = set()
        for ln in open(etp / "data" / "Austin_implications.txt", encoding="utf-8"):
            if "→" in ln:
                a, b = (s.strip().replace("Equation", "") for s in ln.split("→"))
                self.austin.add((int(a), int(b)))
        self.duals = {}
        for a, b in json.load(open(etp / "data" / "duals.json", encoding="utf-8")):
            self.duals[a], self.duals[b] = b, a
        self.facts = {}
        for e in json.load(open(etp / "data" / "full_entries.json", encoding="utf-8")):
            v = e["variant"].get("facts")
            if v is not None and e["proven"] and not v["finite"]:
                self.facts[(e["filename"], e["name"])] = {
                    "line": e["line"],
                    "sat": [int(s.replace("Equation", "")) for s in v["satisfied"]],
                    "ref": [int(s.replace("Equation", "")) for s in v["refuted"]]}
        self.laws = {e["id"]: e for e in json.load(open(laws_json, encoding="utf-8"))}
        self.codes = np.load(status_npz)["codes"]
        cross = json.load(open(cross_json, encoding="utf-8"))
        self.to_etp = {m["our_id"]: m["etp"] for m in cross["mapping"]}
        self.to_ours = {k: i for i, k in self.to_etp.items()}
        cols = cross["settled_open_pairs_columns"]
        self.pairs, self.not_austin = [], []
        for row in cross["settled_open_pairs"]:
            r = dict(zip(cols, row))
            if self.codes[r["a_id"] - 1][r["b_id"] - 1] == 6 and not r["etp_implies"]:
                ab = (r["a_id"], r["b_id"])
                (self.pairs if (self.to_etp[ab[0]], self.to_etp[ab[1]]) in self.austin
                 else self.not_austin).append(ab)

    def mirror_of(self, n):
        """ETP number of the mirror of ETP law n, recomputed from the text; None if not in the list."""
        if not 1 <= n <= len(self.eqs):
            return None
        c = canon(*(mirror(t) for t in self.etp_law(n)))
        for k in (n, self.duals.get(n, n)):
            if 1 <= k <= len(self.eqs) and canon(*self.etp_law(k)) == c:
                return k
        return None

    def etp_law(self, n):
        return parse(self.eqs[n - 1], DIAMOND)

    def our_law(self, i):
        return parse(self.laws[i]["text"], "*")

    def implies(self, x, y):
        """Our table: law x implies law y (ids), or x = y."""
        return x == y or int(self.codes[x - 1][y - 1]) in OURS_TRUE


# ---------- derivations of a law with more than 3 products from B ----------

def size(t):
    return 0 if t[0] == "v" else 1 + size(t[1]) + size(t[2])


def show(t, top=True):
    if t[0] == "v":
        return t[1]
    x = f"{show(t[1], False)}*{show(t[2], False)}"
    return x if top else f"({x})"


def match(p, t, sub):
    if p[0] == "v":
        if p[1] in sub:
            return sub if sub[p[1]] == t else None
        return {**sub, p[1]: t}
    if t[0] != "m":
        return None
    sub = match(p[1], t[1], sub)
    return None if sub is None else match(p[2], t[2], sub)


def subst(p, sub):
    return sub[p[1]] if p[0] == "v" else ("m", subst(p[1], sub), subst(p[2], sub))


def variables(t):
    return {t[1]} if t[0] == "v" else variables(t[1]) | variables(t[2])


def one_step(t, law):
    """Every term obtained from t by one application of law (either orientation, any position) whose new
    side has no letter that the old side lacks."""
    out = []
    for frm, to in (law, law[::-1]):
        if not variables(to) <= variables(frm):
            continue
        sub = match(frm, t, {})
        if sub is not None:
            out.append(subst(to, sub))
    if t[0] == "m":
        out += [("m", u, t[2]) for u in one_step(t[1], law)] + [("m", t[1], u) for u in one_step(t[2], law)]
    return out


def derive(law, goal, max_ops, max_steps=6):
    """Shortest chain of terms from goal's right side to goal's left side, each one step of law apart, all
    terms with at most max_ops products; None if none is found within max_steps steps."""
    start, end = goal[1], goal[0]
    prev, layer = {start: None}, [start]
    for _ in range(max_steps):
        nxt = []
        for t in layer:
            for u in one_step(t, law):
                if u not in prev and size(u) <= max_ops:
                    prev[u] = t
                    nxt.append(u)
        if end in prev:
            chain = [end]
            while prev[chain[-1]] is not None:
                chain.append(prev[chain[-1]])
            return chain[::-1]
        layer = nxt
    return None


def replay(law, goal, chain):
    """None if chain goes from goal's right side to its left side by single steps of law, else the reason."""
    if not chain or chain[0] != show(goal[1]) or chain[-1] != show(goal[0]):
        return "derivation does not start and end at the two sides of the target law"
    for x, y in zip(chain, chain[1:]):
        tx, ty = parse(f"{x} = {x}", "*")[0], parse(f"{y} = {y}", "*")[0]
        if ty not in one_step(tx, law):
            return f"no single step of B from {x} to {y}"
    return None


# ---------- chains ----------

def find_chains(D, a, b):
    chains = []
    for (fname, name), F in sorted(D.facts.items()):
        for mir in (False, True):
            for s0 in F["sat"]:
                s = D.mirror_of(s0) if mir else s0
                if s is None or s not in D.to_ours or not D.implies(D.to_ours[s], a):
                    continue
                for r0 in F["ref"]:
                    r = D.mirror_of(r0) if mir else r0
                    if r is None or not 1 <= r <= len(D.eqs):   # beyond the 4,694 laws of equations.txt
                        continue
                    c = {"pair": [a, b], "base_file": fname, "base_name": name, "base_line": F["line"],
                         "base_satisfies": s0, "base_fails": r0, "mirror": mir,
                         "s_etp": s, "r_etp": r, "s_id": D.to_ours[s], "r_id": D.to_ours.get(r)}
                    if r in D.to_ours:
                        if D.implies(b, D.to_ours[r]):
                            chains.append(c)
                        continue
                    # r is not one of our laws (more than 3 products): look for a short derivation from B
                    goal = D.etp_law(r)
                    chain = derive(D.our_law(b), goal, size(goal[0]) + size(goal[1]) + 1)
                    if chain is not None:
                        c["r_text"] = D.eqs[r - 1].replace(DIAMOND, "*")
                        c["B_implies_r"] = [show(t) for t in chain]
                        chains.append(c)
    return chains


def check_chain(D, c):
    """Re-check one stored chain from scratch; return None if it holds, else the reason."""
    a, b = c["pair"]
    if (a, b) not in D.pairs:
        return "pair is not an open Austin pair the ETP refutes"
    F = D.facts.get((c["base_file"], c["base_name"]))
    if F is None:
        return "no proven infinite facts entry with that file and name"
    if c["base_satisfies"] not in F["sat"] or c["base_fails"] not in F["ref"]:
        return "base entry does not list those laws"
    s, r = c["base_satisfies"], c["base_fails"]
    if c["mirror"]:
        s, r = D.mirror_of(s), D.mirror_of(r)
        if s is None or r is None or D.duals.get(c["base_satisfies"], c["base_satisfies"]) != s \
                or D.duals.get(c["base_fails"], c["base_fails"]) != r:
            return "mirror recomputed from the text disagrees with duals.json"
    if (s, r) != (c["s_etp"], c["r_etp"]) or D.to_ours.get(s) != c["s_id"] or D.to_ours.get(r) != c["r_id"]:
        return "laws s, r or their ids do not match"
    if not D.implies(c["s_id"], a):
        return f"our table does not have {c['s_id']} implies {a}"
    if c["r_id"] is not None:
        return None if D.implies(b, c["r_id"]) else f"our table does not have {b} implies {c['r_id']}"
    if c.get("r_text") != D.eqs[r - 1].replace(DIAMOND, "*"):
        return "text of r does not match the ETP list"
    return replay(D.our_law(b), D.etp_law(r), c.get("B_implies_r", []))


def selftest(D, chains):
    """Corrupt stored chains and inputs; the check must reject every corruption."""
    c0 = next(c for c in chains if c["mirror"] and c["r_id"] is not None)
    c1 = next(c for c in chains if c["r_id"] is not None and c["r_id"] != c["pair"][1])
    c2 = next(c for c in chains if c["r_id"] is None)
    bad = []

    def mut(c, **kw):
        x = copy.deepcopy(c)
        x.update(kw)
        bad.append((", ".join(f"{k}={v}" for k, v in kw.items()), x))
    mut(c0, mirror=False)
    mut(c0, base_name=c0["base_name"] + "_x")
    mut(c0, base_satisfies=c0["base_fails"])
    mut(c0, s_id=c0["s_id"] + 1)
    mut(c1, pair=[c1["pair"][0], c1["pair"][1] + 1])
    mut(c1, pair=[c1["pair"][1], c1["pair"][0]])
    mut(c1, r_etp=c1["r_etp"] + 1)
    mut(c2, B_implies_r=c2["B_implies_r"][:1] + c2["B_implies_r"][2:])
    mut(c2, B_implies_r=c2["B_implies_r"][::-1])
    mut(c2, pair=[c2["pair"][0], c1["pair"][1]])
    results = [(name, check_chain(D, x)) for name, x in bad]
    # corrupted table: the implication B -> r of c1 removed
    b, r = c1["pair"][1], c1["r_id"]
    saved = D.codes[b - 1][r - 1]
    D.codes[b - 1][r - 1] = 1
    results.append(("table: B does not imply r", check_chain(D, c1)))
    D.codes[b - 1][r - 1] = saved
    # corrupted duals.json: the mirror of the base law swapped for another law
    saved = D.duals.get(c0["base_satisfies"])
    D.duals[c0["base_satisfies"]] = c0["base_satisfies"] + 1
    results.append(("duals.json shifted", check_chain(D, c0)))
    D.duals[c0["base_satisfies"]] = saved
    return results


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    D = Data(*args[:4])
    out = args[4] if len(args) > 4 else None
    print(f"open pairs without f refuted by the ETP: {len(D.pairs) + len(D.not_austin)}; Austin pairs among them: "
          f"{len(D.pairs)}; not Austin: {D.not_austin}; proven infinite facts entries: {len(D.facts)}")
    all_chains, report = [], []
    for a, b in sorted(D.pairs):
        ch = find_chains(D, a, b)
        for c in ch:
            why = check_chain(D, c)
            if why:
                raise SystemExit(f"chain found but rejected by the check: {why}: {c}")
        all_chains += ch
        bases = sorted({(c["base_name"], c["mirror"]) for c in ch})
        print(f"law {a} {D.laws[a]['text']}  does not imply  law {b} {D.laws[b]['text']}  "
              f"(ETP {D.to_etp[a]} -> {D.to_etp[b]}): {len(ch)} chains; bases: "
              + "; ".join(f"{n}{' (mirror)' if m else ''}" for n, m in bases))
        report.append({"pair": [a, b], "A": D.laws[a]["text"], "B": D.laws[b]["text"],
                       "etp": [D.to_etp[a], D.to_etp[b]], "chains": len(ch)})
    no_chain = [r["pair"] for r in report if r["chains"] == 0]
    print(f"pairs with at least one chain: {len(report) - len(no_chain)} of {len(report)}; without: {no_chain}")
    for c in all_chains:
        if c["r_id"] is None:
            print(f"  derivation of ETP {c['r_etp']} {c['r_text']} from law {c['pair'][1]}: "
                  + " = ".join(c["B_implies_r"]))
    used = sorted({(c["base_file"], c["base_name"]) for c in all_chains})
    print(f"base ETP structures used: {len(used)}")
    for f, n in used:
        print(f"  {f}  {n}")
    ok = True
    if "--selftest" in sys.argv:
        res = selftest(D, all_chains)
        for name, why in res:
            print(f"  corruption [{name}]: {'rejected: ' + why if why else 'NOT REJECTED'}")
        n_rej = sum(1 for _, why in res if why)
        print(f"selftest: {n_rej} of {len(res)} corrupted inputs rejected")
        ok = n_rej == len(res)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write('{\n "pairs": [\n')
            fh.write(",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in report))
            fh.write('\n ],\n "chains": [\n')
            fh.write(",\n".join("  " + json.dumps(c, ensure_ascii=False) for c in all_chains))
            fh.write("\n ]\n}\n")
        print("written", out)
    print("ALL PASS" if ok and not no_chain else "NOT ALL PASS")
    return 0 if ok and not no_chain else 1


if __name__ == "__main__":
    sys.exit(main())
