# Results

Nothing here counts as a finding until it carries a certificate anyone can re-check.

## Claim types and certificates

| Claim | Certificate | How to re-check |
|-------|-------------|-----------------|
| Law A does NOT imply law B | A finite structure (tables for `*` and `f`) satisfying A and failing B | evaluate both laws on every assignment, `src/findmodel.py: check_model` (independent of z3) |
| Law A implies law B | A proof | z3 `unsat` is a first filter only. Final status needs an independent prover or a Lean proof |
| Law forces a one-element structure | A proof of `x = y` from the law | as above |

## Status labels (use exactly these)

- `z3-only`: z3 said unsat or sat, nothing else checked it.
- `model-verified`: counterexample re-checked by plain evaluation. This is solid for non-implications.
- `independent-prover`: second prover confirmed.
- `lean-verified`: proof checked in Lean.
- `known`: already in the literature (cite it). Do not present as new.

## Files

- `zero_model_laws.json`: laws with no model of size 2 or 3, with the models of size 4 to 6
  we looked for. Status of each entry is in the file.

No `lean-verified` results yet.
