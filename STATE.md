# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 190 open pairs left after step 16 (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

1. **Open pairs, piece 4b: the 190 pairs whose source rule overlaps itself** (step 16). Step 16 settled the
   682 pairs whose source law, read as a rule "term -> letter", has no overlap. For the 26 source laws left
   (rows of 31: `(x*y)*f(z) = z`, `f(f(x)*y) = y`, `f(x)*(y*z) = x`, `f(x*f(y)) = x`; rows of 10:
   `f(x*x)*y = x`, `x*f(y*y) = y`; 20 small rows), compute the overlaps, add the equations they produce
   (Knuth-Bendix completion, with a step limit), and where this ends in a rule set without unresolved
   overlaps, build the term structure from it as in step 16 (the checker must then check every rule of the
   set and that each added rule follows from A). 18 of the 190 have no `f` and an ETP answer.
2. **Open pairs, piece 5: pairs where z3 gave up at size 6 or 7** that piece 4b does not settle (of the 190,
   131 had `unknown` at size 7 in step 15): retry those sizes with a longer limit, or size 8 (check time per
   pair first).
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
5. **`query.py` reads `results/refutations_term_rewriting.json`** (step 16) and re-checks an entry before
   reporting it. Same reason as item 4.
6. **Derivations for the 546 "holds in T_A" verdicts** of the step 16 table control (implications obtained by
   rewriting): store them as chains of steps for a derivation checker. Raises labels of answered pairs.

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
- 2026-11-23: step 15 (open pairs, piece 3): z3 looked for counterexample tables of size 6 and 7 on the
  872 open pairs: none found (395 pairs `unsat` at both sizes, `z3-only`; 477 `unknown` at one size or
  both). Positive control passed. 872 pairs still open.
- 2026-11-23: step 16 (open pairs, piece 4, first part): infinite term structures built from each source law
  read as a rewrite rule without overlap: 682 of the 872 open pairs are "does not imply" (`z3-only`;
  `results/refutations_term_rewriting.json`, checker `src/check_term_rewriting.py`, mutation test 8 of 8,
  now a gate and in CI). 190 pairs still open (172 with `f`).

## Last iteration

2026-11-23, loop run 7, step 16: for 682 of the 872 open pairs an infinite structure, made of formal expressions built from the first law, satisfies the first law but not the second, so the first law does not force the second; z3 and separate plain code check this.
Next: the 190 pairs left come from laws whose pattern can overlap itself; the next run tries to repair those patterns (queue item 1).

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them. The same holds for the 20
  `z3-only` implications of steps 13 and 14 and the 682 non-implications of step 16 (still code 6).
