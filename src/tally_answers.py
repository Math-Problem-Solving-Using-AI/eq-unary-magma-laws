"""Count the answers for all 506,232 ordered pairs, with the label each one carries (README, "The answer").

The stored table results/status_matrix.npz decides the pairs with codes 1 to 4. The pairs it leaves open (code 5,
the 9 laws without small models, and code 6, unresolved) are answered by the result files of steps 09 to 29. This
script reads them all and checks the bookkeeping:
  1. every code 5 or 6 pair gets at least one answer, and all answers for one pair agree;
  2. no result file answers a pair that is not code 5 or 6;
  3. the law texts stored with an answer (where the file stores them) match data/laws_3.json.
It does not re-check any certificate or derivation: the gates in LOOP.md do that, file by file.
It then prints the counts of "implies" and "does not imply" by kind of check.

Usage: python src/tally_answers.py laws_json status_npz etp_json results_dir [--selftest]
"""
import copy
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_z3_retry import check as z3_retry_check  # noqa: E402

IMPLIES, NOT = "implies", "does not imply"
MODEL, Z3, REPLAY, INFINITE = ("finite counterexample re-checked by plain code (model-verified)",
                               "z3 proof (z3-only)",
                               "derivation or completion replayed by plain code (z3-only level at most)",
                               "infinite counterexample, z3-only level "
                               "(parts rest on z3, or on ETP Lean proofs read, not re-run)")
TABLE = {1: (NOT, MODEL), 2: (NOT, MODEL), 3: (IMPLIES, Z3), 4: (IMPLIES, Z3)}

# file, kind of entries, verdict and label of each entry (None: read "verdict" holds/fails from the entry)
KEYED = [("witnesses_ffree_models.json", NOT, MODEL), ("witnesses_etp_magmas.json", NOT, MODEL),
         ("refutations_term_rewriting.json", NOT, INFINITE), ("refutations_nine_laws.json", NOT, INFINITE)]
PAIRS = [("completions_open.json", None, None), ("completions_new_symbols.json", None, None),
         ("derivations_open.json", None, REPLAY), ("derivations_nine_laws.json", None, REPLAY),
         ("derivations_collapse_laws.json", None, REPLAY), ("derivations_ffree_laws.json", None, REPLAY)]
LISTED = ["greedy_eq73.json", "greedy_eq118.json", "asterix_eq65.json", "label_extension_277.json"]


def collect(results, texts, codes, etp):
    """Return a list of (a, b, verdict, label, file) answers for the open pairs, and the problems found."""
    answers, problems = [], []

    def add(a, b, verdict, label, name, entry=None):
        if entry is not None and "A" in entry and (entry["A"], entry["B"]) != (texts[a], texts[b]):
            problems.append(f"{name} {a},{b}: law texts do not match data/laws_3.json")
        answers.append((a, b, verdict, label, name))

    for name, verdict, label in KEYED:
        for key, e in results[name].items():
            add(*map(int, key.split(",")), verdict, label, name, e)
    for name, verdict, label in PAIRS:
        for key, e in results[name]["pairs"].items():
            v = {"holds": IMPLIES, "fails": NOT}[e["verdict"]]
            # a completion that fails gives an infinite structure; one that holds is a replayed derivation
            add(*map(int, key.split(",")), v, label or (REPLAY if v == IMPLIES else INFINITE), name, e)
    for name in LISTED:
        for e in results[name]["pairs"]:
            a, b = e["pair"]
            add(a - 1, b - 1, NOT, INFINITE, name)
    certs = [results["witnesses_ffree_models.json"], results["witnesses_etp_magmas.json"]]
    z3_problems, proved, extra = z3_retry_check([{"text": t} for t in texts], codes, etp,
                                                results["z3_open_retry.json"], certs)
    problems += [f"z3_open_retry.json {p}" for p in z3_problems]
    for a, b in proved + extra:
        add(a, b, IMPLIES, Z3, "z3_open_retry.json")
    return answers, problems


def tally(answers, codes):
    """Check coverage and agreement; return (problems, counts by (verdict, label), files answering more than once)."""
    problems = []
    by_pair = {}
    for a, b, verdict, label, name in answers:
        if codes[a, b] not in (5, 6):
            problems.append(f"{name} {a},{b}: answers a pair that is code {codes[a, b]}, not open")
        by_pair.setdefault((a, b), []).append((verdict, label, name))
    counts = Counter()
    for a, b in np.argwhere(np.isin(codes, [1, 2, 3, 4])):
        counts[TABLE[int(codes[a, b])]] += 1
    twice = Counter()
    for a, b in np.argwhere(np.isin(codes, [5, 6])):
        got = by_pair.get((int(a), int(b)))
        if not got:
            problems.append(f"{a},{b}: open (code {codes[a, b]}) and no answer in any result file")
            continue
        if len({v for v, _, _ in got}) > 1:
            problems.append(f"{a},{b}: answers disagree: {got}")
            continue
        # one answer per pair in the counts: the strongest label (a finite counterexample first)
        order = [MODEL, Z3, REPLAY, INFINITE]
        verdict, label, _ = min(got, key=lambda g: order.index(g[1]))
        counts[(verdict, label)] += 1
        if len(got) > 1:
            twice[" + ".join(sorted(n for _, _, n in got))] += 1
    return problems, counts, twice


def run(results, texts, codes, etp):
    answers, problems = collect(results, texts, codes, etp)
    more, counts, twice = tally(answers, codes)
    return problems + more, counts, twice


def selftest(results, texts, codes, etp):
    """Corrupted copies must each produce at least one problem."""
    def m_drop(r):
        r["refutations_term_rewriting.json"].pop(next(iter(r["refutations_term_rewriting.json"])))

    def m_flip(r):
        # a derived "implies" pair also claimed as a refutation
        r["refutations_term_rewriting.json"][next(iter(r["derivations_open.json"]["pairs"]))] = {}

    def m_code1(r):
        a, b = map(int, np.argwhere(codes == 1)[0])
        r["witnesses_ffree_models.json"][f"{a},{b}"] = {}

    def m_texts(r):
        e = next(iter(r["derivations_collapse_laws.json"]["pairs"].values()))
        e["A"], e["B"] = e["B"], e["A"]

    def m_listed(r):
        r["label_extension_277.json"]["pairs"].pop()

    def m_codes(_):
        return "codes"

    mutations = [("drop one certificate", m_drop), ("one pair answered both ways", m_flip),
                 ("answer a code-1 pair", m_code1), ("swap the law texts of one derivation", m_texts),
                 ("drop one pair of step 26", m_listed), ("mark an answered pair as code 6 in the table", m_codes)]
    ok = True
    for name, mutate in mutations:
        r, c = copy.deepcopy(results), codes
        if mutate(r) == "codes":
            c = codes.copy()
            c[tuple(np.argwhere(codes == 3)[0])] = 6
        problems = run(r, texts, c, etp)[0]
        print(f"mutation {name}: {'rejected' if problems else 'NOT REJECTED'}"
              + (f" ({problems[0][:100]})" if problems else ""))
        ok &= bool(problems)
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return ok


def main():
    args = [x for x in sys.argv[1:] if x != "--selftest"]
    laws_file, status_file, etp_file, results_dir = args
    texts = [e["text"] for e in json.load(open(laws_file))]
    codes = np.load(status_file)["codes"]
    etp = json.load(open(etp_file))
    names = [n for n, _, _ in KEYED + PAIRS] + LISTED + ["z3_open_retry.json"]
    results = {n: json.load(open(Path(results_dir) / n)) for n in names}
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest(results, texts, codes, etp) else 1)
    problems, counts, twice = run(results, texts, codes, etp)
    for p in problems[:20]:
        print("PROBLEM:", p)
    for verdict in (IMPLIES, NOT):
        print(f"{verdict}: {sum(n for (v, _), n in counts.items() if v == verdict):,}")
        for (v, label), n in sorted(counts.items(), key=lambda kv: -kv[1]):
            if v == verdict:
                print(f"  {n:>9,}  {label}")
    total = sum(counts.values())
    print(f"total: {total:,} ordered pairs of different laws (712 x 711 = {712 * 711:,})")
    for files, n in sorted(twice.items()):
        print(f"answered by more than one file (counted once): {n:,} pairs, {files}")
    ok = not problems and total == 712 * 711
    print("tally:", "OK" if ok else f"FAIL ({len(problems)} problems)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
