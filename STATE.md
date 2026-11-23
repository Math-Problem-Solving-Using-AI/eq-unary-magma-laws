# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 872 open pairs (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

1. **872 open pairs left (code 6, 62 source laws; 854 with `f`), piece 3: structure search of size 6
   and 7** (`src/resolve_open.py` with larger MAXN, or a resumable variant; check time per pair first).
   Skip the 20 pairs settled in `results/z3_open_retry.json`. Every counterexample goes through
   `src/verify_witnesses.py`. Steps 03 and 06 searched sizes up to 5, so any finite counterexample has at
   least 6 elements; z3 at 10 s and 30 s (steps 13, 14) found none.
2. **Open pairs, piece 4: "finite yes, infinite no" analysis** of the most frequent sources
   (`f(x)*f(y) = x`, `f(x)*f(y) = y`, `f(x*y) = x`, `x*f(y) = y` ...): in a finite structure these force
   `f` to be one-to-one or onto, which an infinite structure need not be. Look for infinite
   counterexamples with a certificate format that plain code can check, as in the sibling repository
   eq-laws-without-small-models (step 11 there).
3. **The nine laws with no small model are settled** (2026-11-23, see
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
4. **`query.py` reads `results/z3_open_retry.json`** (step 13), so the tool reports the 18 `z3-only`
   implications. It reports an answer that already has a machine check, so it is not loop work.

## Done

- 2026-11-22: steps 01 to 07, see `steps/`. All 506,232 pairs accounted for.
- 2026-11-22: step 08 (ETP cross-check: 0 disagreements, 1,256 open pairs settled), step 09 (1,417
  certificates for the two `f`-free laws with 4-element models), literature check (`docs/PRIOR_WORK.md`).
- 2026-11-23: step 10 (queue item 0, option "teach `query.py`"): `query.py` reports the 1,417 step 09
  certificates after re-checking them. Stored table unchanged; new table codes left to the owner (Blocked).
- 2026-11-23: step 11 (queue item 0b): ETP multiplication tables with every choice of `f`. The item as
  written applied to no open pair; widened at no cost. 2 open `f`-free pairs got 6-element certificates
  (`results/witnesses_etp_magmas.json`); nothing for pairs with `f`.
- 2026-11-23: step 12 (queue item 0c): `query.py` reports the 2 step 11 certificates after re-checking
  them. Stored table unchanged; other answers of the tool unchanged.
- 2026-11-23: step 13 (queue item 1, first piece): z3 with 10 s on the 892 open pairs without a
  certificate: 13 proofs, 18 pairs with chaining, label `z3-only`, consistent with the table and the ETP
  (`src/check_z3_retry.py`, mutation-tested, now a gate). 874 pairs still open.
- 2026-11-23: step 14 (open pairs, piece 2): z3 with 30 s on the 879 pairs still `unknown`: 3 proofs, all
  without `f` and agreeing with the ETP; 20 pairs `z3-only` with chaining, 0 counterexamples. 872 pairs
  still open (854 with `f`).

## Last iteration

2026-11-23, loop run 5, step 14: the solver z3 got 30 seconds on each of the 879 open pairs it could not decide in 10;
it settled 2 more pairs as "implies" (z3's word only, all without `f`), so 872 pairs are still open, 854 of them with `f`.
Next: search for counterexample tables with 6 and 7 elements on the open pairs (queue item 1), timing one pair first.

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them.
