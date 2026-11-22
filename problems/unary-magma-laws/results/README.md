# Results

Nothing here counts as a finding until it carries a certificate anyone can re-check, and has
passed the stages in `docs/VERIFICATION_PROTOCOL.md`.

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

None yet. Generated data lives in `../data` (git-ignored except the law list). The models for the
nine laws with no small model are in `../../laws-without-small-models/results`.

Planned: one file per certified claim group, each with its certificate and re-check command.
