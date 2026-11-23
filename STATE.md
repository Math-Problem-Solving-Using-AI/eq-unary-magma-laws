# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 894 open pairs (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

0. **Make `query.py` and the status table use steps 08 and 09.** `results/status_matrix.npz` still says
   "open" for the 1,256 pairs the ETP settles and for the 1,417 pairs certified in step 09.
   `query.py` already reads `results/etp_crosscheck.json`, but not `results/witnesses_ffree_models.json`.
   Options: teach `query.py` to read that file, or add codes to `export_status.py` (for example 7 =
   `known (ETP)`, and code 2 extended to the new certificates), regenerate, keep the old matrix for
   comparison, and update the README counts. Owner's choice: a new code changes the published format.
0b. **ETP models for pairs that involve `f`.** For a code-6 pair A => B where A has no `f`, an ETP
   counterexample magma for A plus a chosen `f` may refute B. Same trick as step 09, with the ETP's
   finite magmas (`data/smallest_magma_examples.txt` in the ETP repository).
1. **894 open pairs (code 6 in `results/status_matrix.npz`), 71 source laws.** Retry z3 with longer
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

## Last iteration

2026-11-22, research session: steps 08 and 09,
literature check. Next: queue item 0 (make the table and `query.py` reflect steps 08 and 09).

## Blocked

(nothing)
