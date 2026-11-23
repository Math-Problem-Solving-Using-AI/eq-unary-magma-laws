# 21. The 17 open pairs without `f`: one implication derived, 16 need infinite structures

- Date: 2026-11-23
- Status label: the implication `(x*(y*x))*x = y` implies `x*((y*x)*x) = y` has a stored derivation replayed by
  plain code, same level as steps 17 to 19: the `z3-only` level at most (no z3 is used; `docs/LOG.md`, "Decisions
  taken by the loop (run 8)"). The other 16 pairs stay `open` in this repository (the ETP says "does not imply"
  for all 16, label `known (ETP)`, not re-checked here).
- Commit(s): see `git log -- src/derive_open.py results/derivations_open.json steps/21-pairs-without-f-left.md`

## In plain words

1. **The question.** 17 pairs of laws without `f` were still open in this repository. For each pair (A, B): does
   every structure where law A holds also satisfy law B? The Equational Theories Project (ETP) has answered all
   17: 1 "yes" and 16 "no". This repository wants an answer that its own checks can re-run.

   Words used here:
   - A **magma** (or **structure**) is a set with an operation `*` that takes two elements and gives one. Here
     the structures also have an operation `f` with one input, but these 17 laws do not use it.
   - A **law** is an equation such as `(x*(y*x))*x = y` that must hold for every choice of the letters.
     A **model** of a law is a structure where it holds.
   - A **implies** B if every model of A is a model of B. A **counterexample** (or **witness**) is a model of A
     where B fails; it shows that A does **not** imply B. A law **collapses** if its only models have one element.
   - A **derivation** is a chain of steps, each replacing a piece of a formula by something equal to it
     according to A (or an equation already derived). If a chain leads from B's left side to B's right side,
     B holds in every model of A.
   - **Completion** (steps 17 and 18) turns a law into one-way replacement rules and adds rules until no two
     rules disagree. When it ends, the formulas no rule can shorten form an infinite model of A.
   - **z3** is an automatic solver. **Vampire** is another automatic prover, used by the ETP.
   - **Labels:** `z3-only` means only a solver (or, here, plain code resting on textbook theorems) backs the
     answer, nothing is checked in Lean; `known (ETP)` means the ETP has a Lean proof that this repository did
     not re-run; `open` means no answer here.

2. **What was done, in order.**
   1. **Listed the 17 pairs** from the stored table and the result files of steps 13 to 20. Their sources are
      7 laws (ids 86, 88, 143, 153, 508, 565, 598; ETP equations 274, 261, 229, 222, 118, 73, 65).
   2. **Completion with larger limits** (step 17 stopped at 14 symbols per formula). With 20, then 45 symbols
      and up to 80 rules, all 7 completions still stop at the size limit: the new equations keep getting longer
      (153 reached 74 rules in 5 minutes). So completion does not give an answer here. Scratch run, not kept.
   3. **Read how the ETP settles them** (local copy of the ETP, files listed under "Inputs").
      - The one "yes", law 153 `(x*(y*x))*x = y` implies law 508 `x*((y*x)*x) = y` (ETP 222 implies 118), has
        a 3-step Vampire proof in the ETP (`Equation222_implies_Equation118`).
      - All 16 "no" pairs are in the ETP's list of **Austin pairs** (`data/Austin_implications.txt`): B holds in
        every **finite** model of A, but some **infinite** model of A breaks B. That explains why no table up to 7
        elements was found in steps 06, 11 and 15. The ETP builds those infinite models step by step ("greedy"
        constructions): for ETP 118 (our 508) against 222 and 274, for ETP 73 (our 565) against 99, 203 and 255,
        and for ETP 65 (our 598) a model on the integers. The other "no" answers follow from these by chaining
        with known implications. The ETP's blueprint lists 73 and 118 among "refutations that required greedy
        methods".
   4. **Turned the ETP proof of the "yes" pair into a derivation** that this repository replays. In words: from
      A one gets `x*(y*x) = (x*y)*x` (E1); putting `y*x` for `y` in E1 and using A once more gives B. The script
      of step 19 (`src/derive_open.py`) now has this outline too and finds each single step; the checker of
      step 19 (`src/check_derivations.py`) replays it.
   5. **Fixed a small bug** in `src/derive_open.py` found on the way: when the step search looked inside a letter
      of the next formula it crashed instead of skipping. The 4 derivations of step 19 come out unchanged.

3. **A small example.** Take the 3 numbers `{0, 1, 2}` and let `x*y` be `x + y` with 3 counted as 0 (so
   `2*2 = 1`). Law 153: `(x*(y*x))*x = x + y + x + x = 3x + y = y`, true for all choices. Law 508:
   `x*((y*x)*x) = x + y + x + x = y`, also true. This agrees with the derivation (every model of 153 is a model
   of 508), but one example proves nothing; the derivation does. Step by step, with `x = 1, y = 2`:
   E1 says `1*(2*1) = (1*2)*1`, that is `1 + 0 = 0 + 1`, both 1.

4. **What it means and what it does NOT mean.**
   - It means: law 153 implies law 508, by a 4-step derivation that plain code replays. 20 pairs are still open
     here (4 with `f`, 16 without).
   - It does NOT mean anything new for the other 16 pairs: their answer is "no" according to the ETP, and the
     ETP proves it in Lean, but this repository has no check of its own for them yet. Their counterexamples are
     infinite and built step by step, which a finite table check cannot cover.
   - The derivation is not Lean-checked. It rests only on "replacing equals by equals", and the checker was
     mutation-tested (it rejects corrupted chains).
   - That completion did not finish with these limits does not mean it never finishes.

5. **How to re-check.**

   ```
   python src/derive_open.py data/laws_3.json results/status_matrix.npz results/derivations_open.json
   python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_open.json
   python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_open.json --selftest
   ```

   Expected: the first prints `law 153 (x*(y*x))*x = y implies law 508 x*((y*x)*x) = y: fact 2, 4 steps in all`
   and `pairs derived: 5` and rewrites the file byte for byte. The second prints `3 of 3 sources checked (28
   replacement steps replayed)`, `5 open pairs derived (implied)`, a control line about 97 small models and
   `ALL PASS`. The third ends with `selftest: 14 of 14 corrupted inputs rejected` and `ALL PASS`.

## Goal

Queue item 1 (open pairs, piece 4d): the 17 pairs without `f` that are open here and settled by the ETP. Retry
completion with higher limits, or read how the ETP settles them and build certificates our checkers re-check.

## Command(s)

- Scratch (not kept): completion of the 7 source laws with `src/complete_open.py`'s `Completion` class and limits
  (size, rules, equations) = (20, 80, 8000), then (45, 80, 6000).
- `python src/derive_open.py data/laws_3.json results/status_matrix.npz results/derivations_open.json`
- `python src/check_derivations.py ... results/derivations_open.json` and `--selftest`; 4 extra inline mutations of
  the new entry (substitution, direction, fact index, target shifted): all rejected.
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, the result files of steps 09 to 20. Local ETP clone at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), read only: `data/Austin_implications.txt`,
`data/full_entries.json`, `blueprint/src/chapter/hard.tex`, `blueprint/src/chapter/infinite_magma_constructions.tex`,
`equational_theories/Generated/VampireProven/Proofs4.lean` (line 2178), `equational_theories/Generated/Greedy/Eq118.lean`,
`equational_theories/ManuallyProved/Equation73.lean`, `equational_theories/Equations/Eqns1_999.lean`. No web access.
Python 3.12.10, Windows 10.

## Output

- `src/derive_open.py`: outlines per source law; new outline for law 153; `one_step` fix.
- `results/derivations_open.json`: new source `"152"` (3 facts) and pair `"152,507"`. The 4 entries of step 19 are
  unchanged (compared as JSON before and after: equal).
- The 17 pairs with their ETP numbers and ETP proof kind (`etp_crosscheck.json` values):

  | Our pair (ids) | ETP | ETP answer |
  |---|---|---|
  | 153 -> 508 | 222 -> 118 | implies (Vampire proof); now derived here |
  | 86 -> 137, 153, 492, 508, 559 | 274 -> 203, 222, 99, 118, 47 | not (derived), Austin |
  | 88 -> 579 | 261 -> 307 | not (derived), Austin |
  | 143 -> 498, 565 | 229 -> 125, 73 | not (derived), Austin |
  | 508 -> 86, 153 | 118 -> 274, 222 | not (greedy, `Generated/Greedy/Eq118.lean`), Austin |
  | 565 -> 70, 137, 492 | 73 -> 255, 203, 99 | not (greedy, `ManuallyProved/Equation73.lean`), Austin |
  | 565 -> 143, 498 | 73 -> 229, 125 | not (derived), Austin |
  | 598 -> 224 | 65 -> 359 | not (derived from the Asterix model, `Asterix.lean`), Austin |

- Open pairs: 20 (4 with `f`, 16 without). `results/status_matrix.npz` unchanged (the pair is still code 6).

## Checks done (and what each one can and cannot catch)

- `check_derivations.py`: replays all 28 steps, checks the pair is open, the texts match, fact 2 is B. Catches a
  wrong step, a wrong fact or a wrong pair. Cannot catch a bug shared with the parser of `check_laws_text.py`
  (itself a gate).
- Selftest 14 of 14 and 4 extra mutations aimed at the new entry: all rejected.
- Small-model control: all facts hold in the 97 models of the 3 sources with 2 or 3 elements.
- The 4 old derivations: unchanged after the script change (JSON equality).
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS; `check_term_rewriting.py`
  ALL PASS and selftest ALL PASS; `check_completion.py` on both files ALL PASS, both selftests ALL PASS;
  `check_derivations.py` ALL PASS, selftest 14 of 14.

## NOT verified

- No check of our own for the 16 "does not imply" pairs; their answer rests on the ETP's Lean files, not re-run here.
- Which chain of ETP facts gives each of the 9 "derived" non-implications was not traced (only that the ETP marks
  them `implicit_proof_false`).
- The Austin list was read from `data/Austin_implications.txt` in the local clone; the Lean proofs that the
  finite implications hold were not read.
- Completion with other orders (weights other than 1) was not tried.
- The derivation is not Lean-checked.

## Surprises, errors, dead ends

- Dead end: completion with up to 45 symbols per formula and 80 rules; every source still grows.
- Surprise: all 16 "no" pairs are Austin pairs. Any counterexample is infinite, and the ETP needed greedy
  step-by-step constructions for the base cases. No finite search can settle them.
- Bug found and fixed: `one_step` in `src/derive_open.py` crashed with `TypeError` when the position it looked at
  in the next formula ran through a letter. It did not show up in step 19 because the search never got there.
- Mistake caught at once: the first outline had a wrong middle formula for E1; the script stopped with "no step
  from ... to ...", as designed.

## Next

The 16 Austin pairs need certificates for infinite step-by-step constructions. First trace, for each pair, which
base ETP refutation (118 against 222 or 274, 73 against 99, 203 or 255, the Asterix model for 65) and which
implications it rests on, and check that this repository has those implications. Then see whether a base
construction can be checked by plain code (the starting finite piece plus a hand-checked extension rule), and
with what label.
