# 24. The ETP construction for `x*((y*x)*x) = y`: its 2 finite seeds checked here, 4 open pairs not implied

- Date: 2026-11-23
- Status label: same level as steps 17 and 23, never higher than `z3-only`. The finite part of each certificate
  (the seed meets the 11 rules, the target law fails using seed products only) is re-checked in full by plain
  Python here, no z3 used. The general construction it relies on, the ETP's Lean proof that a seed meeting the 11
  rules grows into a whole model (`PartialSolution.adjoin`, `complSeq`, `toMagma_equation118`), was **not** re-run
  here; it was read, and its extension rule was tested by plain code on a bounded range. No implication from our
  table is used (for all 4 pairs the law that fails is B itself). Not `model-verified` (that label is for finite
  tables), not Lean here, not reviewed, no literature check for these pairs.
- Commit(s): see `git log -- src/check_greedy_eq118.py results/greedy_eq118.json steps/24-seeds-eq118.md`

## In plain words

1. **The question.** 10 pairs of laws were still open after step 23. For 4 of them the source law is
   `x*((y*x)*x) = y` (law 508) or its mirror `(x*(x*y))*x = y` (law 143). The Equational Theories Project (ETP)
   says these source laws do not imply the 4 target laws, but only infinite examples show it. Can this repository
   check those infinite examples with its own code, as step 23 did for another law?

   Words used here:
   - A **magma** (or **structure**) is a set with an operation `*` that takes two elements and gives one.
   - A **law** is an equation that must hold for every choice of its letters. A **model** of a law is a structure
     where it holds. A **implies** B if every model of A is a model of B. A **counterexample** (or **witness**)
     is a model of A where B fails.
   - The **mirror** of a law reads every product the other way round (`x*(y*z)` becomes `(z*y)*x`). Reading a
     structure's operation the other way round turns a model of a law into a model of its mirror.
   - A **partial operation** is a table of products where some entries are still empty. The ETP writes it as a set
     of triples `(x, y, z)`, each meaning `x*y = z`.
   - A **seed** is a small partial operation to start from, here with 2 or 4 triples.
   - **z3** is an automatic solver. **Labels:** `z3-only` means nothing stronger than a solver (or a proof not
     re-run here) backs the answer; `known (ETP)` means the ETP has a Lean proof that was not re-run here; `open`
     means no answer here.
   - **Lean** is a proof checker. The ETP stores its proofs as Lean files.

2. **What was done, in order.**
   1. **Read the ETP file** `Generated/Greedy/Eq118.lean` (ETP commit `dbc9a2bf`): the definition of a partial
      solution and its 11 rules (lines 2441 to 2456), the extension step `adjoin` (lines 2462 to 2568), the
      greedy chain and the final model (lines 2570 to 2687), and the two seeds with their theorems (lines 2689
      to 2755). The 11 helper theorems `rule_k_preserved` (lines 11 to 2440, generated proofs) were not read
      line by line. The models live on the natural numbers 0, 1, 2, .... A partial solution is a finite set of
      triples that obeys 11 rules, for example rule 0 "a product has at most one value" and rule 1 "if `x*y = z`
      and `z*y = w` then `y*w = x`", which is law 508 itself in triple form. The Lean proof shows that one new
      product `a*b = c`, with c a number used nowhere so far, plus up to 8 kinds of triples derived from it
      (called sP1 to sP8 in the file), gives again a partial solution. Doing this for every pair (a, b) in turn
      fills the whole table; rules 0 and 1 then make law 508 hold everywhere.
   2. **Copied the 2 seeds** of the file (`counter222` and `counter274`) into `results/greedy_eq118.json`, and the
      11 rules verbatim into the checker. Why: the checker needs no ETP files to run.
   3. **Wrote a checker** (`src/check_greedy_eq118.py`). For each seed it checks the 11 rules on the seed's triples
      and that every number used is in the seed's stated support. With `--etp DIR` it also compares its 11 rules
      with the Lean file text (run once: `11 found, identical`).
   4. **For each of the 4 pairs**, it evaluates the target law B at the stored values of x and y using seed
      products only and finds two different numbers. Since every extension keeps the seed's products, B fails in
      every model built from that seed. For the 2 pairs from law 143 it reads the products mirrored (`x*y` is the
      seed's `y*x`).
   5. **A bounded test of the extension step.** From each seed it runs the extension step itself: 20,000 times in
      the order the Lean chain uses, 5,000 times on random pairs (the Lean step allows any order), and then
      whenever an evaluation needs a missing product. It checks the 11 rules every 5,000 steps and at the end, and
      evaluates law 508 and law 143 (mirrored) directly at all 1,600 pairs (x, y) with x, y from 0 to 39. 0
      failures. Why: it tests the step and the link from the rules to law 508 with code that does not follow the
      Lean proof. It is not a proof for all numbers.
   6. **A check of the checker** (`--selftest`): 14 corrupted inputs (a changed seed triple, a removed triple, a
      second value for a product, a support set too small, a flipped mirror flag, a wrong seed, x and y swapped, a
      pair that is not open, a wrong source law, rule 1 misread, a rule dropped, the extension step without its
      derived triples, without sP1 only, and with c not new). All 14 rejected.

3. **A small example.** Pair "does law 508 imply law 153, `(x*(y*x))*x = y`?", seed `counter222`: the two triples
   `1*2 = 3` and `2*3 = 1`. Put x = 2 and y = 1:
   - `y*x = 1*2 = 3`;
   - `x*(y*x) = 2*3 = 1`;
   - `(x*(y*x))*x = 1*2 = 3`.

   So the left side is 3 and the right side is y = 1: law 153 fails. Every model built from this seed satisfies
   law 508 (by the ETP construction) and fails law 153. No finite table can do this: every finite model of law
   508 satisfies law 153 (the pair is an ETP "Austin pair").

4. **What it means and what it does NOT mean.**
   - It means: the 4 pairs 508 -> 86, 508 -> 153, 143 -> 498 and 143 -> 565 now have an answer here, "does not
     imply", with a certificate whose finite part this repository re-checks on every run (a gate of `LOOP.md`
     and CI). Open pairs: 10 before, **6 after** (4 with `f`; 2 without `f`, which rest on the ETP's "Asterix"
     model).
   - It does NOT mean the pairs are proved here. The general construction is the ETP's Lean proof, not re-run
     and not re-proved here; the bounded test only shows that the step behaves on the first 26,000 or so steps.
   - One of the 8 kinds of derived triples (sP6) never occurred in the bounded test, in any of the three orders
     tried, so the test says nothing about it.
   - `results/status_matrix.npz` still says code 6 (open) for the 4 pairs: new codes are a published format change
     left to the owner (Blocked in `STATE.md`).

5. **How to re-check.** From the repository root:

   ```
   python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json
   python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json --selftest
   ```

   Expected: `2 seeds pass the 11 rules of the Lean file`, one line per pair (for example
   `pair 508 -> 153: seed counter222, law 153 fails at {'x': 2, 'y': 1}: 3 != 1`), four `bounded test` lines each
   with `1600 instances evaluated, 0 failures`, `4 open pairs with a seed certificate` and `ALL PASS` (about 10 s).
   The selftest prints 14 `rejected` lines, `selftest: 14 of 14 corrupted inputs rejected` and `ALL PASS` (about
   90 s). Adding `--etp ../_external/equational_theories` (a clone of the ETP at commit `dbc9a2bf`) also prints
   `rules compared with equational_theories/Generated/Greedy/Eq118.lean: 11 found, identical`.

## Goal

Queue item 1 (open pairs, piece 4d-3, rest), first piece: see whether the ETP 118 greedy construction (2 seeds, 4 of
the 6 Austin pairs left) can be checked by plain code here, and with what label. The Asterix model (2 pairs) is
split off as the next queue item.

## Command(s)

- `python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json --etp ../_external/equational_theories`
- `python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json --selftest`
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`. Local ETP clone at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), read only: `equational_theories/Generated/Greedy/Eq118.lean`
lines 1 to 10 and 2441 to 2791 read in full; lines 11 to 2440 (the 14 generated `rule_k_preserved` and
`rule_finite_k_preserved` theorems) seen only as headers. `equational_theories/Equations/Eqns1_999.lean` lines 123,
227 and 279 (equations 118, 222, 274). Results of step 22 (`results/austin_chains.json`) for the pair to seed map.
No web access. Python 3.12.10, Windows 10.

## Output

- `results/greedy_eq118.json` (new): source (repository, commit, file, line numbers), the 2 seeds as triples with
  their support, and the 4 pairs (seed, mirror flag, values of x and y).
- `src/check_greedy_eq118.py` (new): the checker, `--selftest` and `--etp`; a new gate in `LOOP.md`, in CI and in
  the README command list.
- The 4 pairs, all "does not imply":

  | Our pair | ETP base theorem | Seed | Mirror | B fails at | Value of left side | Right side |
  |---|---|---|---|---|---|---|
  | 508 -> 86 | `Equation118_not_implies_Equation274` | `counter274` | no | x = 1, y = 2 | 3 | 2 |
  | 508 -> 153 | `Equation118_not_implies_Equation222` | `counter222` | no | x = 2, y = 1 | 3 | 1 |
  | 143 -> 498 | `Equation118_not_implies_Equation222` | `counter222` | yes | x = 2, y = 1 | 3 | 1 |
  | 143 -> 565 | `Equation118_not_implies_Equation274` | `counter274` | yes | x = 1, y = 2 | 3 | 2 |

  This agrees with the chains of step 22 (base theorems, mirror flags, and r = B in all 4 rows) and with the Lean
  file's own evaluations (`specialize h 1 2` for 222, `specialize h 2 1` for 274, in ETP variable names).
- Bounded test: about 26,400 extension steps and 28,100 products per seed, 0 rule failures, 1,600 instances each of
  laws 508 and 143, 0 failures.
- Open pairs: 6 (4 with `f`, 2 without). `results/status_matrix.npz` unchanged.

## Hand reading of the construction (a lead, not a check)

`toMagma_equation118` (line 2679) only uses rule 1 and the fact that every product has exactly one value: with
`X0 = x`, `X1 = y`, `X2 = x*y`, `X3 = (x*y)*y`, rule 1 says `y*((x*y)*y) = x`, which is ETP 118 and our law 508 with
x and y renamed. Rules 2 to 10 are only there so that `adjoin` can keep rules 0 and 1 when a product is added. The
greedy chain (`complSeq`, line 2598) adds the pair numbered n at step n by `Nat.unpair`; `addArbitrary` picks c
outside the support and outside {a, b}. `of_R` (line 2671) says the final operation keeps every seed triple. This
was read, not re-proved.

## Checks done (and what each one can and cannot catch)

- The 11 rules on the 2 seeds, and support inside `finsupp`: catch a wrongly copied seed. Cannot catch an error in
  the Lean construction.
- Rule text compared with the Lean file (`--etp`, run once): catches a misread rule in the checker. Not run in CI
  (CI has no ETP clone).
- Failure of B from seed products only, normal and mirrored: catches a wrong seed, mirror flag or values of x and
  y. Relies on `of_R` (extensions keep the seed), read, not checked.
- Bounded test: catches a misread extension step (the selftest shows it rejects the step without derived triples,
  without sP1, and with a reused c) and a misread rule (rule 1 misread is rejected only through the bounded test:
  the misread rule happens to hold on both seeds). Cannot prove anything about products never reached, and never
  exercises sP6.
- Selftest: 14 of 14 corrupted inputs rejected.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS; `check_term_rewriting.py`
  ALL PASS and selftest ALL PASS; `check_completion.py` on both files ALL PASS, both selftests ALL PASS;
  `check_derivations.py` ALL PASS, selftest 14 of 14; `check_greedy_eq73.py` ALL PASS, selftest 13 of 13;
  `check_greedy_eq118.py` ALL PASS, selftest 14 of 14.

## NOT verified

- The ETP's Lean construction (`adjoin` and the 14 generated `*_preserved` theorems it calls, `complSeq`,
  `toMagma_equation118`): not re-run here; the generated theorems were not read line by line. The ETP's Lean build
  was not run.
- That an extension keeps the seed's products (`of_R`): read, not checked.
- The derived triples of kind sP6 never occurred in the bounded test (Lean order, random order and on-demand
  order all tried); whether they can occur at all was not decided.
- The order of the first 20,000 steps follows Mathlib's `Nat.unpair` as written in the checker from memory; the
  Mathlib source was not read. The test does not depend on it (the Lean step allows any order), but "the same order
  as the Lean chain" is unconfirmed.
- The bounded test covers about 26,000 steps per seed and laws at x, y below 40 only.
- The last 2 Austin pairs (Asterix model of ETP 65: 598 -> 224 and 88 -> 579) are not touched here.

## Surprises, errors, dead ends

- The first selftest ran its mutations without the bounded test, for speed, and accepted "rule 1 misread": the
  misread rule (`y*x = w` instead of `y*w = x`) happens to hold on both seeds. With the bounded test on (as in a
  normal run) it is rejected at once. All mutations now run the full check. Lesson (`docs/LOG.md`): a selftest must
  run the same checks as a normal run, or it tests a weaker checker.
- With a rule check every 500 steps the run took 84 s and the selftest would have taken about 20 minutes; checking
  every 5,000 steps (and at the end) brought it to 10 s and 90 s.

## Next

Queue item "piece 4d-3, Asterix": the Asterix model of ETP 65 (`Asterix.lean`, 547 lines), 2 pairs: 598 -> 224 and
88 -> 579 (mirrored), each with a 2-step derivation already replayed in step 22.
