# Results

Nothing here counts as a finding until it carries a certificate anyone can re-check, and has
passed the stages in `docs/shared/VERIFICATION_PROTOCOL.md`.

## Claim types and certificates

| Claim | Certificate | How to re-check |
|-------|-------------|-----------------|
| Law A does NOT imply law B | A finite structure (tables for `*` and `f`) satisfying A and failing B | evaluate both laws on every assignment, `src/findmodel.py: check_model` (independent of z3 and numpy) |
| Law A implies law B | A derivation (chain of rewriting steps) | z3 `unsat` is a lead only. A stored derivation with an independent checker is planned |
| Law forces a one-element structure | Same as implication, a derivation of `x = y` | as above |

## Status labels (use exactly these, highest earned)

`unverified` < `z3-only` < `model-verified` (non-implications only) < `independent-prover`
< `lean-checked` < `lean-checked + fidelity-reviewed + literature-checked`

Only the last one may be called a result. `known` means already in the literature: cite it.

## Files

- `status_matrix.npz`: the outcome for every ordered pair of the 712 laws (array `codes`, row =
  law A, column = law B, index = law id minus 1 in `data/laws_3.json`). Codes:

  | Code | Meaning | Count | Label |
  |------|---------|-------|-------|
  | 0 | same law | 712 | - |
  | 1 | NOT an implication, refuted by a structure with 2 or 3 elements (regenerable) | 335,177 | `model-verified` |
  | 2 | NOT an implication, refuted by a certificate with 4 or 5 elements | 708 | `model-verified` |
  | 3 | implication proved by z3, with transitive closure | 15,877 | `z3-only` |
  | 4 | implication because A forces a one-element structure | 147,177 | `z3-only` |
  | 5 | A is one of the 9 laws with no small model, collapse unproven | 6,399 | open |
  | 6 | unresolved | 894 | open |

  Codes 3 and 4 cannot be regenerated deterministically (z3 varies between runs), which is why the
  table is stored. `src/check_status_matrix.py` checks codes 1 and 2 against what is regenerated.
- `witnesses_larger_models.json`: the 708 certificates of code 2 (plus the 894 pairs where none was
  found up to size 5). Re-check with `src/verify_witnesses.py`.
- Look things up with `src/query.py`, for example
  `python src/query.py "x*y = x" "x*(y*z) = x"`.

Planned: derivations for codes 3 and 4 that an independent checker can verify.
