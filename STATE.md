# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Settle the 20 open pairs still open after step 21 (the finish line in `LOOP.md`: every pair answered with a machine check).

## Queue (take the first item)

1. **Open pairs, piece 4d-3: certificates for the 3 base constructions** (step 22 found that all 16 Austin pairs
   rest on them: ETP 73 with 3 seeds in `ManuallyProved/Equation73.lean`, 10 pairs; ETP 118 greedy in
   `Generated/Greedy/Eq118.lean`, 4 pairs; the Asterix model of ETP 65 in `Asterix.lean`, 2 pairs; chains in
   `results/austin_chains.json`). Start with ETP 73. See whether the starting finite piece of each construction plus
   its extension rule can be checked by plain code (the ETP blueprint, chapter "Infinite magma constructions", and
   the Lean files), and with what label. If only a Lean re-run of the ETP files would check them, write under Blocked what the owner must decide.
2. **Open pairs, piece 4f: the 4 pairs of `(x*y)*f(x) = y` and its mirror** (sources 277, targets 574 and 632;
   408, targets 122 and 128). Step 20 found no counterexample by adding one extra law of size up to 4, and the
   ETP rules out `f` given by a short formula. Needs a new idea: an infinite model built over the free model of
   277 and 632 (hand notes in `steps/20-counterexample-search-law-277.md`: the values of `f` must form a model of
   both laws on which `f` is one-to-one and not onto), or a longer derivation of 632.
3. **Open pairs, piece 5: pairs where z3 gave up at size 6 or 7** that pieces 4f and 4d do not settle (all 4
   pairs of piece 4f had `unknown` at sizes 6 and 7 in step 15; not the 16 Austin pairs of 4d, which have no finite counterexample): retry those sizes with a longer limit, or size 8 (check time per
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
- 2026-11-23: step 19 (open pairs, piece 4e, split): derivations aimed at the target. Law 483
  `f(x*y)*x = y` implies laws 550 and 544, its mirror 704 implies 195 and 189: 4 pairs, each a stored chain
  replayed by plain code (`results/derivations_open.json`, new checker `src/check_derivations.py`, mutation
  test 14 of 14, gate and CI; `z3-only` level at most, no z3 used). 21 pairs still open (4 with `f`, 17 without).
- 2026-11-23: step 20 (open pairs, piece 4f, first attempt): no counterexample for `(x*y)*f(x) = y` to
  `x*(y*f(x)) = y`: one extra law of size 1 to 4 (8,804 completions, 274 complete, the target holds in all;
  `src/scan_extra_laws.py`, `results/extra_laws_277.json`, positive control passed), ETP with `f` replaced by
  short formulas (all implications true), z3 with hints `unknown`. Hand notes on what a counterexample needs.
  Queue reordered (`docs/LOG.md`, decisions run 11). 21 pairs still open.

- 2026-11-23: step 21 (open pairs, piece 4d, split): the 17 pairs without `f`. Completion with larger limits
  still grows. The one "implies" (law 153 `(x*(y*x))*x = y` to law 508 `x*((y*x)*x) = y`) now has a derivation
  from the ETP's Vampire proof, replayed by `src/check_derivations.py` (`results/derivations_open.json`). The 16
  "does not imply" are ETP Austin pairs (only infinite counterexamples, greedy constructions); no own check yet.
  20 pairs still open (4 with `f`, 16 without).
- 2026-11-23: step 22 (open pairs, piece 4d-2): traced the 16 Austin pairs. All rest on 6 proven infinite ETP
  structures from 3 constructions (ETP 73: 10 pairs, ETP 118: 4, Asterix for ETP 65: 2), plus 7 implications of
  our table (code 3) and 2 short derivations replayed here (`results/austin_chains.json`,
  `src/trace_austin_pairs.py`, selftest 12 of 12). Nothing settled; 20 pairs still open.

## Last iteration

2026-11-23, loop run 13, step 22: for each of the 16 open pairs where the ETP says "no" but only infinite examples show it, the run found which infinite example of the ETP it rests on; all 16 rest on just 3 such constructions, and every other link of the argument is already in this repository; nothing new is settled, 20 pairs remain open.
Next: check whether those 3 infinite constructions (starting with the one for `x*(x*(y*x)) = y`, which covers 10 pairs) can be checked by this repository's own code, and with what label.

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them. The same holds for the 20
  `z3-only` implications of steps 13 and 14, the 682 non-implications of step 16, the 133 pairs of step 17, the 32 pairs of step 18 and the 5 pairs of steps 19 and 21 (still code 6).
