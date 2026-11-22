"""Laws with no model of size 2 or 3 that z3 could not prove collapse (A |- x = y).

For each, search for a model of size 4..MAXN. A verified model shows the law does NOT
force a one-element structure. Output: results/zero_model_laws.json

Usage: python src/zero_model_laws.py data/laws_3.json data/o3 MAXN TIMEOUT_MS
"""
import json
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit("src", 1)[0] + "src")
from findmodel import check_model, find_model  # noqa: E402
from prove import tuplify  # noqa: E402


def main():
    laws_file, prefix, maxn, timeout = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    entries = json.load(open(laws_file))
    laws = [tuplify(e["law"]) for e in entries]
    S = np.load(prefix + "_sat.npy")
    collapse = np.load(prefix + "_collapse.npy")
    todo = [i for i in range(len(laws)) if S[i].sum() == 0 and not collapse[i]]
    report = []
    for i in todo:
        row = {"law": entries[i]["text"], "model": None, "size": None, "status": {}}
        for n in range(4, maxn + 1):
            t = time.time()
            m, st = find_model([laws[i]], n, timeout_ms=timeout)
            row["status"][str(n)] = st
            print(f"{entries[i]['text']:28s} size {n}: {st} ({time.time()-t:.1f}s)", flush=True)
            if m:
                row["model"], row["size"] = m, n
                row["independently_verified"] = check_model(m, laws[i])
                break
        report.append(row)
    out = __file__.rsplit("src", 1)[0] + "results/zero_model_laws.json"
    json.dump(report, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
