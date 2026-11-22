"""Export the status of every ordered pair of laws to results/status_matrix.npz.

The arrays in data/ are git-ignored and some (z3 proofs) cannot be regenerated deterministically,
so the outcome of the whole computation is stored here as a small compressed table.

codes[a, b] describes "law a implies law b" (a, b = law id - 1 as in laws_3.json):
  0 same law
  1 NOT an implication, refuted by a structure of size 2 or 3 (regenerable, verified in plain Python)
  2 NOT an implication, refuted by a certificate of size 4 or 5 (results/witnesses_larger_models.json)
  3 implication proved by z3, with transitive closure        (z3-only)
  4 implication because law a forces a one-element structure (z3-only)
  5 law a is one of the 9 laws with no small model, collapse unproven (open)
  6 unresolved (open)

Usage: python export_status.py laws_json prefix witnesses_json out_npz
"""
import json
import sys

import numpy as np


def main():
    laws_file, prefix, wit_file, out = sys.argv[1:5]
    L = len(json.load(open(laws_file)))
    S = np.load(prefix + "_sat.npy")
    R = np.load(prefix + "_refuted.npy")
    C = np.load(prefix + "_collapse.npy")
    PR = np.load(prefix + "_proven.npy")
    W = json.load(open(wit_file))
    nm = S.sum(axis=1)
    src = (nm > 0) & ~C  # laws with a small model that do not collapse
    reach = PR.copy()
    np.fill_diagonal(reach, True)
    for k in range(L):
        reach |= np.outer(reach[:, k], reach[k, :])
    off = reach & ~np.eye(L, dtype=bool)
    assert not (R & off).any(), "a proved implication is refuted by a structure"

    codes = np.full((L, L), 6, dtype=np.uint8)
    codes[(nm == 0) & ~C, :] = 5
    codes[C, :] = 4
    codes[off & src[:, None]] = 3
    for key, v in W.items():
        if v.get("size") and v.get("verified"):
            a, b = map(int, key.split(","))
            assert codes[a, b] == 6, f"certificate for a pair that is already decided: {key}"
            codes[a, b] = 2
    codes[R] = 1
    np.fill_diagonal(codes, 0)
    np.savez_compressed(out, codes=codes)
    names = {0: "same law", 1: "refuted by size 2-3 structure", 2: "refuted by size 4-5 certificate",
             3: "implication, z3, closure", 4: "implication, source collapses", 5: "source is one of 9 open laws",
             6: "unresolved"}
    for c in range(7):
        print(c, int((codes == c).sum()), names[c])
    print("total", int(codes.size))


if __name__ == "__main__":
    main()
