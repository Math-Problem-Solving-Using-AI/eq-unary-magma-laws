"""Check results/z3_open_retry.json (step 13) against everything else we hold.

The file says which open (code 6) pairs z3 proved with a longer time limit. That is z3-only, and this
script does not change that. It checks that the claims fit the rest of the repository:
  1. every proved pair is code 6 in the stored table, and its law texts match data/laws_3.json;
  2. adding the proved pairs to the implications of the table (codes 0, 3, 4) and closing under
     "A implies C and C implies B gives A implies B" makes no pair that is refuted (code 1 or 2, or a
     certificate in the step 09 and step 11 files) an implication;
  3. for pairs without f, the ETP's verdict (results/etp_crosscheck.json) is "implies" for every pair
     that is now an implication;
and it prints the open pairs that the closure settles beyond the proved ones.
With --rerun, z3 is asked again, in a fresh process, about every proved pair (a bookkeeping check,
z3 checking z3).

Usage: python src/check_z3_retry.py laws_json status_npz etp_json retry_json cert_json... [--rerun]
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))


def implications_after(codes, proved):
    """Transitive closure of codes 0, 3, 4 plus the proved pairs."""
    L = len(codes)
    reach = np.isin(codes, [0, 3, 4])
    for a, b in proved:
        reach[a, b] = True
    for k in range(L):
        reach |= np.outer(reach[:, k], reach[k, :])
    return reach


def check(entries, codes, etp, retry, certs):
    """Return (list of problems, proved pairs, extra pairs settled by the closure)."""
    texts = [e["text"] for e in entries]
    problems = []
    proved = []
    for key, p in retry["pairs"].items():
        a, b = map(int, key.split(","))
        if (p["A"], p["B"]) != (texts[a], texts[b]):
            problems.append(f"{key}: law texts do not match data/laws_3.json")
        if codes[a, b] != 6:
            problems.append(f"{key}: not code 6 in the stored table (code {codes[a, b]})")
        if p.get("proved_ms"):
            if p["tries"].get(str(p["proved_ms"])) != "unsat":
                problems.append(f"{key}: proved_ms without an unsat answer at that time limit")
            proved.append((a, b))
    reach = implications_after(codes, proved)
    refuted = np.isin(codes, [1, 2])
    for cert in certs:
        for key in cert:
            refuted[tuple(map(int, key.split(",")))] = True
    for a, b in np.argwhere(reach & refuted):
        problems.append(f"{a},{b}: refuted, but the closure makes it an implication")
    etp_says = {(r[0] - 1, r[1] - 1): r[3] for r in etp["settled_open_pairs"]}
    new = reach & (codes == 6)
    for a, b in np.argwhere(new):
        if (a, b) in etp_says and not etp_says[(a, b)]:
            problems.append(f"{a},{b}: the ETP says this is NOT an implication")
    extra = [(int(a), int(b)) for a, b in np.argwhere(new) if (a, b) not in set(proved)]
    return problems, proved, extra


def selftest(entries, codes, etp, retry, certs):
    """Corrupted copies of the inputs must each produce at least one problem."""
    texts = [e["text"] for e in entries]
    etp_false = [(r[0] - 1, r[1] - 1) for r in etp["settled_open_pairs"] if r[2] == 6 and not r[3]]
    cert_keys = set().union(*[set(c) for c in certs])
    first_proved = next(k for k, p in retry["pairs"].items() if p.get("proved_ms"))
    a1, b1 = map(int, np.argwhere(codes == 1)[0])

    def claim(r, a, b):
        r["pairs"][f"{a},{b}"] = {"A": texts[a], "B": texts[b], "tries": {"10000": "unsat"}, "proved_ms": 10000}

    def m_etp_false(r):
        a, b = next(p for p in etp_false if f"{p[0]},{p[1]}" not in cert_keys)
        claim(r, a, b)

    def m_certified(r):
        a, b = map(int, sorted(cert_keys & {f"{a},{b}" for a, b in np.argwhere(codes == 6)})[0].split(","))
        claim(r, a, b)

    def m_swap_texts(r):
        p = r["pairs"][first_proved]
        p["A"], p["B"] = p["B"], p["A"]

    def m_no_unsat(r):
        r["pairs"][first_proved]["tries"]["10000"] = "unknown"

    def m_code1(r):
        claim(r, a1, b1)

    mutations = [("claim a pair the ETP refutes", m_etp_false),
                 ("claim a pair with a certificate", m_certified),
                 ("swap the law texts of a proved pair", m_swap_texts),
                 ("proved_ms without unsat", m_no_unsat),
                 ("claim a code-1 pair", m_code1)]
    ok = True
    for name, mutate in mutations:
        r = json.loads(json.dumps(retry))
        mutate(r)
        problems = check(entries, codes, etp, r, certs)[0]
        print(f"mutation {name}: {'rejected' if problems else 'NOT REJECTED'}"
              + (f" ({problems[0]})" if problems else ""))
        ok &= bool(problems)
    print("selftest:", "ALL PASS" if ok else "FAIL")
    return ok


def main():
    args = [x for x in sys.argv[1:] if x not in ("--rerun", "--selftest")]
    laws_file, status_file, etp_file, retry_file, *cert_files = args
    entries = json.load(open(laws_file))
    codes = np.load(status_file)["codes"]
    etp = json.load(open(etp_file))
    retry = json.load(open(retry_file))
    certs = [json.load(open(c)) for c in cert_files]
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest(entries, codes, etp, retry, certs) else 1)
    problems, proved, extra = check(entries, codes, etp, retry, certs)
    texts = [e["text"] for e in entries]
    etp_says = {(r[0] - 1, r[1] - 1): r[3] for r in etp["settled_open_pairs"]}
    print(f"pairs in file: {len(retry['pairs'])}, proved by z3: {len(proved)}, "
          f"settled in addition by the closure: {len(extra)}")
    for a, b in proved + extra:
        how = "z3" if (a, b) in proved else "closure"
        etp_note = {True: "ETP: implies", False: "ETP: NOT implied"}.get(etp_says.get((a, b)), "ETP: no data (has f)")
        print(f"  {a},{b} [{how}] {texts[a]}  =>  {texts[b]}   ({etp_note})")
    if "--rerun" in sys.argv:
        from prove import tuplify
        from retry_open_z3 import task
        for a, b in proved:
            ms = retry["pairs"][f"{a},{b}"]["proved_ms"]
            r = task((a, b, tuplify(entries[a]["law"]), tuplify(entries[b]["law"]), ms))[2]["result"]
            print(f"  rerun {a},{b} at {ms} ms: {r}")
            if r != "unsat":
                print(f"  (note: z3 did not repeat the proof this time; z3 outcomes vary between runs)")
    for p in problems:
        print("PROBLEM:", p)
    print("ALL PASS" if not problems else f"FAIL: {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
