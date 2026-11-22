"""Check that the stored status table agrees with what can be regenerated.

Needs data/o3_refuted.npy from models.py (regenerable, deterministic).
Checks:
  - every code is 0..6, code 0 only on the diagonal
  - code 1 positions equal the regenerated small-structure refutations, exactly
  - code 2 positions equal the verified certificates in witnesses_larger_models.json, exactly
  - no pair has code 1 or 2 and also an implication code (a pair cannot be both)
  - rows of source laws coded 4 or 5 are constant off the diagonal

Usage: python check_status_matrix.py laws_json prefix witnesses_json status_npz
"""
import json
import sys

import numpy as np


def main():
    laws_file, prefix, wit_file, npz = sys.argv[1:5]
    L = len(json.load(open(laws_file)))
    codes = np.load(npz)["codes"]
    R = np.load(prefix + "_refuted.npy")
    W = json.load(open(wit_file))
    errors = []
    if codes.shape != (L, L):
        errors.append(f"shape {codes.shape}")
    if codes.max() > 6:
        errors.append("code above 6")
    if not (np.diag(codes) == 0).all() or (codes[~np.eye(L, dtype=bool)] == 0).any():
        errors.append("code 0 not exactly on the diagonal")
    if not ((codes == 1) == R).all():
        errors.append(f"code 1 differs from regenerated refutations in {int(((codes == 1) != R).sum())} places")
    cert = np.zeros((L, L), dtype=bool)
    for key, v in W.items():
        if v.get("size") and v.get("verified"):
            a, b = map(int, key.split(","))
            cert[a, b] = True
    if not ((codes == 2) == cert).all():
        errors.append("code 2 differs from the verified certificates")
    for a in range(L):
        row = np.delete(codes[a], a)
        if row[0] in (4, 5) and not (row == row[0]).all():
            errors.append(f"row {a} mixes codes")
    counts = {c: int((codes == c).sum()) for c in range(7)}
    print("counts:", counts)
    if errors:
        print("ERRORS:\n  " + "\n  ".join(errors))
        sys.exit(1)
    print("status table consistent")


if __name__ == "__main__":
    main()
