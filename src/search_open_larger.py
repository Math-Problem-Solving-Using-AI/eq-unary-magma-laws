"""Search counterexample structures of size 6 and 7 for the pairs that are still open.

The open pairs are the code 6 pairs of results/status_matrix.npz minus those already settled:
a certificate in results/witnesses_etp_magmas.json (step 11), or an implication by z3 with chaining
in results/z3_open_retry.json (steps 13 and 14, computed with check_z3_retry.check).
For every open pair (A, B) and every size n in SIZES, z3 looks for a table of size n satisfying A and
failing B (findmodel.find_model). A table found is re-checked by plain evaluation
(findmodel.check_model) before it counts; results/verify_witnesses.py re-checks it again with its own
parser. unsat at size n means "no counterexample of exactly n elements" (z3-only); unknown means nothing.

Output format is the one of results/witnesses_larger_models.json ("a,b" -> {A, B, size, model,
verified, tried}), size null when nothing was found. Results accumulate across runs: a pair with a
counterexample, or already tried at every size at this time limit, is skipped. State is saved every
10 pairs. The run stops taking new pairs after BUDGET_S seconds, so a long job is done in several runs.

Usage: python src/search_open_larger.py laws_json status_npz etp_json retry_json TIMEOUT_MS BUDGET_S out_json cert_json...
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_z3_retry import check  # noqa: E402
from findmodel import check_model, find_model  # noqa: E402
from prove import tuplify  # noqa: E402

SIZES = (6, 7)


def task(args):
    a, b, la, lb, sizes, timeout = args
    tried = {}
    for n in sizes:
        m, st = find_model([la], n, violate=lb, timeout_ms=timeout)
        tried[str(n)] = st
        if m:
            ok = bool(check_model(m, la)) and not check_model(m, lb)
            return a, b, {"size": n, "model": m, "verified": ok, "tried": tried}
    return a, b, {"size": None, "tried": tried}


def open_pairs(entries, codes, etp, retry, certs):
    """Code 6 pairs not settled by a certificate file or by the z3 retry with chaining."""
    _, proved, extra = check(entries, codes, etp, retry, certs)
    settled = set(proved) | set(extra)
    for cert in certs:
        settled |= {tuple(map(int, k.split(","))) for k in cert}
    return [(int(a), int(b)) for a, b in np.argwhere(codes == 6) if (a, b) not in settled]


def main():
    laws_file, status_file, etp_file, retry_file, timeout, budget, out, *cert_files = sys.argv[1:]
    timeout, budget = int(timeout), float(budget)
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    certs = [json.load(open(c)) for c in cert_files]
    pairs = open_pairs(entries, codes, json.load(open(etp_file)), json.load(open(retry_file)), certs)
    try:
        results = json.load(open(out))
    except FileNotFoundError:
        results = {}
    todo = []
    for a, b in pairs:
        prev = results.get(f"{a},{b}")
        if prev and prev.get("size"):
            continue
        if prev and prev.get("timeout_ms") == timeout and all(str(n) in prev["tried"] for n in SIZES):
            continue
        todo.append((a, b, laws[a], laws[b], SIZES, timeout))
    print(f"open pairs: {len(pairs)}; to try at sizes {SIZES}, {timeout} ms each: {len(todo)}", flush=True)

    def save():
        json.dump(results, open(out, "w"), indent=1)

    t0 = time.time()
    done = 0
    pool = mp.Pool()
    try:
        for a, b, res in pool.imap_unordered(task, todo):
            res["A"], res["B"], res["timeout_ms"] = texts[a], texts[b], timeout
            results[f"{a},{b}"] = res
            done += 1
            if done % 10 == 0:
                save()
                print(f"  {done}/{len(todo)}, {time.time() - t0:.0f}s", flush=True)
            if time.time() - t0 > budget:
                print("time budget reached, stopping; run again to resume", flush=True)
                break
    finally:
        pool.terminate()
        save()
    found = sum(1 for r in results.values() if r.get("size") and r.get("verified"))
    bad = sum(1 for r in results.values() if r.get("size") and not r.get("verified"))
    full = [r for r in results.values() if not r.get("size") and all(str(n) in r["tried"] for n in SIZES)]
    print(f"done this run: {done}; verified counterexamples: {found}; solver table failed plain check: {bad}; "
          f"tried at every size with none found: {len(full)}")
    for n in SIZES:
        sts = [r["tried"][str(n)] for r in full]
        print(f"  size {n}: unsat {sts.count('unsat')}, unknown {sts.count('unknown')}")


if __name__ == "__main__":
    main()
