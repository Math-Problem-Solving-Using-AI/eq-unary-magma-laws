# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 894 open pairs (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

0c. **`query.py` reads `results/witnesses_etp_magmas.json`** (same pattern as step 10): for a code-6
   pair with a step 11 certificate, re-check it and print "NOT an implication, model-verified".
   2 pairs today. Changes no published format.
1. **894 open pairs (code 6 in `results/status_matrix.npz`), 71 source laws; 2 of them now have
   step 11 certificates, and 33 more (no `f`) are `known (ETP)` only.** ETP tables of size 4 and 5 with
   every `f` gave nothing for pairs with `f` (step 11); size 6 and up with a non-trivial `f` was not tried. Retry z3 with longer
   timeouts (10 s, 30 s, accumulate proofs, save state), search structures of size 6 and 7
   (`src/resolve_open.py` with larger MAXN), then analyze by hand the most frequent sources:
   `f(x)*f(y) = x` and `f(x)*f(y) = y` (38 open targets each). Every counterexample goes through
   `src/verify_witnesses.py`.
2. **The nine laws with no small model are settled** (2026-11-23, see
   https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models): 3 collapse, 2 have
   4-element models, 4 have infinite term models (`z3-only`). Update codes 5 from its results and
   re-export the table; its 2,828 certificates in `results/refutations_term_models.json` decide the rows
   of the four (707 targets each fail; the other 4 per law are instances of the law).

## Optional later (loop sessions never take these; only the owner moves one to the queue)

Moved here from the queue on 2026-11-23 (finish line in `LOOP.md`): they raise labels of answers
that already have a machine check, or extend the question.

1. **Derivations for implications (codes 3 and 4).** Replace "z3 said unsat" by a stored chain of
   rewriting steps and write a tiny independent checker with mutation tests. Start with the
   collapse laws (207), then the 15,877 others.
2. **Scale up to size 4** (8,805 laws, 8,093 new): generate laws, catalogue, prove. Needs saving and
   resuming everywhere (see lessons). Check memory and time first.
3. **Lean** for anything that survives, following `docs/shared/LEAN_CAVEATS.md`. Lean 4.36.0 (elan, no Mathlib) is installed on the
   owner's machine since 2026-11-23.

## Done

- 2026-11-22: steps 01 to 07, see `steps/`. All 506,232 pairs accounted for.
- 2026-11-22: step 08 (ETP cross-check: 0 disagreements, 1,256 open pairs settled), step 09 (1,417
  certificates for the two `f`-free laws with 4-element models), literature check (`docs/PRIOR_WORK.md`).
- 2026-11-23: step 10 (queue item 0, option "teach `query.py`"): `query.py` reports the 1,417 step 09
  certificates after re-checking them. Stored table unchanged; new table codes left to the owner (Blocked).
- 2026-11-23: step 11 (queue item 0b): ETP multiplication tables with every choice of `f`. The item as
  written applied to no open pair; widened at no cost. 2 open `f`-free pairs got 6-element certificates
  (`results/witnesses_etp_magmas.json`); nothing for pairs with `f`.

## Last iteration

2026-11-23, loop run 2, step 11: we tried the small example tables published by the Equational Theories
Project, with every possible choice of `f`, against the 894 open pairs; 2 pairs got a checked counterexample, the rest stay open.
Next: queue item 0c, make the lookup tool report those 2 answers; then queue item 1 (longer proof attempts, bigger searches).

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them.
