# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

finished: no   (`yes` when the finish line in `LOOP.md` holds; loop sessions then stop.)

## Focus

Every case the README asks about has an answer with a machine check since step 29 (all of code 6 since step 26, all
of code 5 since steps 27 to 29). Left for the finish line in `LOOP.md`: condition 3, plain words. Steps 06 to 09 have
no "In plain words" section, and the README has no short plain-words answer.

## Queue (take the first item)

1. **"In plain words" for steps 06 to 09.** Add the section (numbered, as in the owner's rule and steps 01 to 05 and 10
   to 29) right under the header lines of each file, defining every technical word. Change nothing else in those files.
2. **Plain-words answer in the README.** A short section near the top: the question, the answer for every kind of pair
   (how many "implies", how many "does not imply", with which check and label), what it does not mean (`z3-only` is not
   proved; nothing is Lean-checked), and how to re-check. Then check the finish line in `LOOP.md` again.

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

7. **Re-run the ETP's Lean file `ManuallyProved/Equation73.lean`** (theorem `exists_extension`), or re-prove the
   extension theorem here, for the 10 pairs of step 23. It raises the label of answered pairs.
8. **Re-run the ETP's Lean file `Generated/Greedy/Eq118.lean`** (`PartialSolution.adjoin` and its 14 generated
   helper theorems), or re-prove the extension step here, for the 4 pairs of step 24; and find out whether the
   derived triples of kind sP6 can occur at all (never seen in the bounded test). It raises the label of answered
   pairs.
9. **Re-run the ETP's Lean file `Asterix.lean`** (`move_rev_good`, `move_rev_bad`, `closure_prop`), or re-prove its
   extension step here, for the 2 pairs of step 25. It raises the label of answered pairs.

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
- 2026-11-23: step 23 (open pairs, piece 4d-3, split): the ETP construction for `x*(x*(y*x)) = y` (law 565). Its 3
  finite seeds pass the conditions of the ETP's extension theorem and make the target laws fail, checked by plain
  code with a bounded test of the extension rule (`results/greedy_eq73.json`, `src/check_greedy_eq73.py`, selftest
  13 of 13, gate and CI). 10 pairs (from 565 and its mirror 86) "does not imply", step 17 level; the ETP's Lean
  theorem is not re-run. 10 pairs still open (4 with `f`, 6 without).
- 2026-11-23: step 24 (open pairs, piece 4d-3, rest, split): the ETP construction for `x*((y*x)*x) = y` (law 508). Its
  2 seeds meet the 11 rules of the Lean file (rules copied verbatim and compared with it), the target laws fail
  using seed products only, and a bounded run of the extension step (about 26,000 steps per seed) keeps the rules
  and law 508 (`results/greedy_eq118.json`, `src/check_greedy_eq118.py`, selftest 14 of 14, gate and CI). 4 pairs
  (from 508 and its mirror 143) "does not imply", same label as step 23; the Lean construction is not re-run. The
  Asterix model went back to the queue as its own item. 6 pairs still open (4 with `f`, 2 without).
- 2026-11-23: step 25 (open pairs, piece 4d-3, last): the ETP's Asterix model of `x*(y*(x*y)) = y` (law 598). Its seed
  (18 products, 6 closed pairs) meets the 6 conditions of the Lean file (conditions, law text and seed compared with
  it), the target laws fail at x = 0 using seed products only, and a bounded run of the Lean extension step (about
  49,000 steps) keeps the conditions and law 598 (`results/asterix_eq65.json`, `src/check_asterix_eq65.py`, selftest
  16 of 16, gate and CI). 2 pairs (598 -> 224 and its mirror 88 -> 579) "does not imply", same label as step 23; the
  Lean construction is not re-run. All 16 Austin pairs now have a check here. 4 pairs still open, all with `f`.
- 2026-11-23: step 26 (open pairs, piece 4f): an infinite counterexample for `(x*y)*f(x) = y`: pairs (m, k) over the
  free model of laws 277 and 632 with a counter k that products add to and values of `f` take from. Law 277 holds
  (label lemma: plain code over 210 cases, z3 `unsat` for every model of 277, direct test on 30,625 pairs); laws 632
  and 574 fail at (g, 0). 4 pairs (277 -> 632, 574; 408 -> 128, 122) "does not imply", `z3-only` level
  (`results/label_extension_277.json`, `src/check_label_extension.py`, selftest 18 of 18, gate and CI). 0 pairs of
  the unresolved row (code 6) still open. Queue item "piece 5" (z3 gave up at size 6 or 7) removed: no pairs left.

- 2026-11-23: step 27 (queue item "the nine laws", first piece, split): the rows of the four code 5 laws with an
  infinite term model (laws 135, 336, 450, 639): the step 16 structure gives 2,828 "does not imply" (`z3-only`,
  `results/refutations_nine_laws.json`) and 16 "implies" (one-step derivations, `results/derivations_nine_laws.json`),
  checked by the step 16 and 19 checkers (now accepting codes 5 and 6), mutation test 7 of 7
  (`src/selftest_nine_laws.py`), gates and CI. Same verdicts as the sibling, 0 differences. Table unchanged.
- 2026-11-23: step 28 (queue item 1): the rows of the three collapse laws (110, 284, 415): `x = y` derived from each by a
  stored chain (2 or 6 steps), every other law in one more step; 2,133 pairs "implies"
  (`results/derivations_collapse_laws.json`, replayed by `src/check_derivations.py`, mutation test
  `src/selftest_collapse_laws.py` 14 of 14, gates and CI; `z3-only` level at most, no z3 used). Table unchanged.
- 2026-11-23: step 29 (queue item 1): the 5 pairs of laws 250 and 257 without a 4-element certificate are each the
  source law with letters made equal; 5 "implies" by one-step derivations (`results/derivations_ffree_laws.json`,
  replayed by `src/check_derivations.py`; `src/selftest_ffree_laws.py`: coverage 1,417 + 5 = 1,422, control on the
  4-element tables, mutation test 10 of 10; gates and CI). Agrees with the ETP. Finish line checked: condition 3 (plain
  words in steps 01 to 09 and in the README) not met; three queue items added.
- 2026-11-23: queue item "In plain words for steps 01 to 05": each of the five oldest step files now starts with a
  numbered plain-words section, words defined, one small example checked by `src/query.py`, re-check commands with
  their expected output. Nothing else in those files changed; gates 35 of 35. Re-running the step 04 z3 search from
  scratch gave 203, 205, then 207 proofs, the same 207 laws as the table (`docs/LOG.md`, run 21).

## Last iteration

2026-11-23, loop run 21: the first five step files (what the words mean, the list of 712 laws, the small tables, the laws that force a one-element set, the first solver proofs) now open with an explanation in plain words and a small worked example.
Next: the same explanation for step files 06 to 09, then a short plain-words answer at the top of the README, then a check of whether the repository is finished.

## Blocked

- Adding new codes to `results/status_matrix.npz` (for example 7 = `known (ETP)`, code 2 extended to the
  step 09 certificates) changes a published file format: the owner decides whether to do it. Until then
  `query.py` reports those answers and the table still says "open" for them. The same holds for the 20
  `z3-only` implications of steps 13 and 14, the 682 non-implications of step 16, the 133 pairs of step 17, the 32 pairs of step 18, the 5 pairs of steps 19 and 21, the 10 pairs of step 23, the 4 pairs of step 24, the 2 pairs of step 25 and the 4 pairs of step 26 (still code 6), the 2,844 pairs of step 27, the 2,133 pairs of step 28 and the 5 pairs of step 29 (still code 5).
