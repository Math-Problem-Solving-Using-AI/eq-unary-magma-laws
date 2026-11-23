"""Ask z3 again, with a longer time limit, about the pairs that are still open (code 6).

For every pair (A, B) with code 6 in results/status_matrix.npz that has no certificate yet in
results/witnesses_etp_magmas.json, ask z3 whether A implies B (A as axiom, B negated, over an
uninterpreted set, so infinite structures count). Answers:
  unsat   = z3 proved the implication (z3-only, not checked by anything else);
  sat     = z3 found a structure; if it is finite it is turned into tables and re-checked by plain
            evaluation (findmodel.check_model) before it counts;
  unknown = nothing (a timeout says nothing either way).

Results accumulate in OUT_JSON across runs: a pair already proved, or already tried at this time
limit, is skipped. State is saved every 10 pairs. The run stops taking new pairs after BUDGET_S
seconds, saves and exits, so a long job is done in several runs of under ten minutes each.

Usage: python src/retry_open_z3.py laws_json status_npz certified_json TIMEOUT_MS BUDGET_S out_json
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np
import z3

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove  # noqa: E402
from findmodel import check_model  # noqa: E402
from prove import axiom, goal_neg, tuplify  # noqa: E402


def finite_model(m):
    """Tables for * and f from a z3 model over the sort S, or None if z3 gave no finite universe."""
    univ = m.get_universe(prove._S)
    if univ is None or len(univ) == 0:
        return None
    idx = {str(e): i for i, e in enumerate(univ)}
    try:
        mul = [[idx[str(m.eval(prove._mul(a, b), model_completion=True))] for b in univ] for a in univ]
        f = [idx[str(m.eval(prove._f(a), model_completion=True))] for a in univ]
    except KeyError:
        return None
    return {"mul": mul, "f": f}


def task(args):
    a, b, la, lb, timeout = args
    prove._init()
    s = z3.Solver()
    s.set("timeout", timeout)
    s.add(axiom(la))
    s.add(goal_neg(lb))
    t0 = time.time()
    r = str(s.check())
    out = {"result": r, "seconds": round(time.time() - t0, 2)}
    if r == "sat":
        model = finite_model(s.model())
        if model is not None:
            out["model"] = model
            out["verified"] = bool(check_model(model, la)) and not check_model(model, lb)
    return a, b, out


def main():
    laws_file, status_file, cert_file, timeout, budget, out = sys.argv[1:7]
    timeout, budget = int(timeout), float(budget)
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    texts = [e["text"] for e in entries]
    codes = np.load(status_file)["codes"]
    certified = set(json.load(open(cert_file)))
    try:
        state = json.load(open(out))
    except FileNotFoundError:
        state = {"about": __doc__.split("\n\n")[0], "z3_version": z3.get_version_string(), "pairs": {}}
    pairs = state["pairs"]

    todo = []
    for a, b in np.argwhere(codes == 6):
        key = f"{a},{b}"
        if key in certified:
            continue
        p = pairs.get(key)
        if p and (p.get("proved_ms") or str(timeout) in p["tries"]):
            continue
        todo.append((int(a), int(b), laws[a], laws[b], timeout))
    print(f"open pairs to try at {timeout} ms: {len(todo)}", flush=True)

    def save():
        json.dump(state, open(out, "w"), indent=1)

    t0 = time.time()
    done = 0
    pool = mp.Pool()
    try:
        for a, b, res in pool.imap_unordered(task, todo):
            key = f"{a},{b}"
            p = pairs.setdefault(key, {"A": texts[a], "B": texts[b], "tries": {}})
            p["tries"][str(timeout)] = res["result"]
            if res["result"] == "unsat":
                p["proved_ms"] = timeout
            if "model" in res:
                p["model"], p["verified"] = res["model"], res["verified"]
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
    tried = [p for p in pairs.values() if str(timeout) in p["tries"]]
    print(f"done this run: {done}; pairs tried at {timeout} ms so far: {len(tried)}; "
          f"proved (unsat, any run): {sum(1 for p in pairs.values() if p.get('proved_ms'))}; "
          f"sat with a verified finite structure: {sum(1 for p in pairs.values() if p.get('verified'))}; "
          f"sat not verified: {sum(1 for p in pairs.values() if 'verified' in p and not p['verified'])}")


if __name__ == "__main__":
    main()
