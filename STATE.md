# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 25 open pairs left after step 18 (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

1. **Open pairs, piece 4e: the 8 pairs with `f` whose completion keeps growing** (step 18). Sources 277
   `(x*y)*f(x) = y` (targets 574, 632), 408 `f(x)*(y*x) = y` (122, 128), 483 `f(x*y)*x = y` (544, 550), 704
   `x*f(y*x) = y` (189, 195). Completion, with or without new symbols, does not finish at 24 symbols and 60
   rules. Try: a derivation search aimed at the target (rewrite B's sides with A's consequences, store the
   chain for `src/check_completion.py`), or an infinite model guessed from the pattern of the growing rule set
   and checked by plain code.
2. **Open pairs, piece 4d: the 17 pairs without `f` left** (step 17; the ETP says 16 "does not imply", 1
   "implies", but this repository has no certificate it re-checks). Retry completion with higher limits for
   their 7 source laws, or read how the ETP settles them and build a certificate our checkers can re-check.
3. **Open pairs, piece 5: pairs where z3 gave up at size 6 or 7** that pieces 4e and 4d do not settle (all 8
   pairs of piece 4e had `unknown` at size 7 in step 15): retry those sizes with a longer limit, or size 8 (check time per
   pair first).
4. **The nine laws with no small model are settled** (2026-11-23, see
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
- 2026-11-23: step 17 (open pairs, piece 4b): Knuth-Bendix completion of the 26 overlapping source rules; 7
  complete. 133 of the 190 open pairs decided: 132 "does not imply", 1 "implies" (agrees with the ETP)
  (`results/completions_open.json`, checker `src/check_completion.py`, mutation test 10 of 10, gate and CI;
  `z3-only` level at most, no z3 used). 57 pairs still open (40 with `f`).
- 2026-11-23: step 18 (open pairs, piece 4c, split): completion with new symbols for values that ignore a
  letter; 8 of the 19 stopped sources complete; 32 of the 40 open pairs with `f` are "implies", each with a
  replayed derivation (`results/completions_new_symbols.json`, checker `src/check_completion.py` extended,
  mutation test 15 of 15, gate and CI). 25 pairs still open (8 with `f`, 17 without).

## Last iteration

2026-11-23, loop run 9, step 18: where a law forced a value to ignore one of its letters, the loop gave that value its own name and finished the rule-building; this showed that 32 more pairs with `f` are "implies", each by a step-by-step chain that separate plain code replays.
Next: 25 pairs remain (8 with `f`, 17 without); the next run tries the 8 pairs with `f` whose rule-building keeps growing (queue item 1).

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them. The same holds for the 20
  `z3-only` implications of steps 13 and 14, the 682 non-implications of step 16, the 133 pairs of step 17 and the 32 pairs of step 18 (still code 6).
