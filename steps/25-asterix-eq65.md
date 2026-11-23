# 25. The ETP "Asterix" construction for `x*(y*(x*y)) = y`: its finite seed checked here, 2 open pairs not implied

- Date: 2026-11-23
- Status label: same level as steps 17, 23 and 24, never higher than `z3-only`. The finite part of each certificate
  (the seed meets the 6 conditions, the target law fails using seed products only) is re-checked in full by plain
  Python here, no z3 used. The general construction it relies on, the ETP's Lean proof that a seed meeting the 6
  conditions grows into a whole model (`move_rev_good`, `move_rev_bad`, `act`, `add_e1`, `add_e0`, `closureSeq`,
  `closure_prop`), was **not** re-run here; it was read, and its extension step was tested by plain code on a bounded
  range. No implication from our table is used (for both pairs the law that fails is B itself). Not `model-verified`
  (that label is for finite tables), not Lean here, not reviewed, no literature check for these pairs.
- Commit(s): see `git log -- src/check_asterix_eq65.py results/asterix_eq65.json steps/25-asterix-eq65.md`

## In plain words

1. **The question.** 6 pairs of laws were still open after step 24. For 2 of them the source law is
   `x*(y*(x*y)) = y` (law 598) or its mirror `((x*y)*x)*y = x` (law 88). The Equational Theories Project (ETP) says
   these source laws do not imply the target laws `(x*x)*x = x*x` (law 224) and `x*(x*x) = x*x` (law 579), but only
   an infinite example shows it. Can this repository check that infinite example with its own code, as steps 23 and
   24 did for two other laws?

   Words used here:
   - A **magma** (or **structure**) is a set with an operation `*` that takes two elements and gives one.
   - A **law** is an equation that must hold for every choice of its letters. A **model** of a law is a structure
     where it holds. A **implies** B if every model of A is a model of B. A **counterexample** (or **witness**) is a
     model of A where B fails.
   - The **mirror** of a law reads every product the other way round (`x*(y*z)` becomes `(z*y)*x`). Reading a
     structure's operation the other way round turns a model of a law into a model of its mirror.
   - A **partial solution** (the ETP's name) is a table of products on the numbers 0, 1, 2, ... where only finitely
     many entries are filled in. Here it has two lists: **E1**, the filled-in products `a*b = v`, and **E0**, the
     pairs (a, b) that are already **closed**: the three products needed for `a*(b*(a*b))` are filled in and give b,
     so the law holds there.
   - A **seed** is the small partial solution to start from: here 18 products, 6 closed pairs.
   - An **Austin pair** (ETP word) is a pair A, B where B holds in every finite model of A, but not in every model:
     only an infinite counterexample exists.
   - **z3** is an automatic solver. **Labels:** `z3-only` means nothing stronger than a solver (or a proof not re-run
     here) backs the answer; `open` means no answer here.
   - **Lean** is a proof checker. The ETP stores its proofs as Lean files.

2. **What was done, in order.**
   1. **Read the ETP file** `equational_theories/Asterix.lean` (ETP commit `dbc9a2bf`, 547 lines) in full: the
      6 conditions of a partial solution (lines 16 to 25), the two ways to add a product (`move_rev_good`, line 44, and
      `move_rev_bad`, line 181), how the new number is chosen (`notMemFinset`, line 338: the smallest number not used
      yet), `act`, `add_e1`, `add_e0` (lines 400 to 466), the chain over all pairs and the final model (`closureSeq`,
      `closure`, `closure_prop`, lines 469 to 511), the seed `initial` (line 513) and the theorem `Equation65_facts`
      (line 532). The Lean proof steps (the `simp` and `rw` lines) were read for structure, not re-proved.
   2. **How the construction works**, as read. To fill in a missing product `y*x`, take a number z never used so far
      and set `y*x = z`. Set also `a*z = y` for the a that need it (`z*z = y`, and `a*z = y` whenever `a*y = x` is
      already in the table). Every pair (a, y) with `a*y = x` becomes closed, because now `a*(y*(a*y)) = a*(y*x) =
      a*z = y`. If `x*y = x` was already there (the "bad" case) the pair (y, x) itself is closed at once. `add_e0`
      fills in two products so that a chosen pair becomes closed; `closureSeq` does this for every pair in turn. The
      Lean proof shows that the 6 conditions survive each step, and that in the end every pair is closed, so law 598
      holds everywhere.
   3. **Copied the seed** (E0 and the 18 products of E1) into `results/asterix_eq65.json`, and the 6 conditions
      verbatim into the checker. Why: the checker needs no ETP files to run.
   4. **Wrote a checker** (`src/check_asterix_eq65.py`). It checks the 6 conditions on the seed. With `--etp DIR` it
      also compares, against the Lean file: the 6 condition lines, the text of ETP equation 65 (and that it is our
      law 598 up to renaming letters), the seed's E0 and E1, and the seed's values (it evaluates the Lean formula
      `f a b := if a = 0 then [...].getD b 0 else ...` itself). Run once: `identical`.
   5. **For each of the 2 pairs**, it evaluates law B at x = 0 using seed products only and finds two different
      numbers. Since every extension keeps the seed's products, B fails in every model built from the seed. For the
      pair from law 88 it reads the products mirrored (`x*y` is the seed's `y*x`).
   6. **A bounded test of the extension step.** From the seed it runs the Lean definitions themselves: 20,000 times
      `add_e0` in the order `closureSeq` uses, 5,000 times on random pairs (the Lean step allows any order), and then
      whenever an evaluation needs a missing product. After each `add_e0` it checks that the chosen pair is closed;
      every 5,000 steps and at the end it checks the 6 conditions and that the seed's products are unchanged; and it
      evaluates law 598 and law 88 (mirrored) directly at all 1,600 pairs (x, y) with x, y from 0 to 39. About
      49,400 single extension steps (8 of them the "bad" case, about 24,900 closing older pairs), 123,857 products,
      0 failures. Why: it tests the step and the link from the conditions to law 598 with code that does not follow
      the Lean proof. It is not a proof for all numbers.
   7. **A check of the checker** (`--selftest`): 16 corrupted inputs (a changed seed value, two seed products removed
      one at a time, a product given twice, a closed pair removed, a closed pair added, a flipped mirror flag, a wrong
      x, a pair that is not open, a wrong source law, one condition misread, and five broken extension steps: z not
      new, no `z*z = y`, no `a*z = y`, older pairs not closed, the bad case treated as the good one). All 16 rejected.
      Separately, the `--etp` comparison was run on a changed seed value, a removed closed pair and a misread
      condition: all three reported as different.

3. **A small example.** The seed has `0*0 = 1` and `1*0 = 2`. Law 224 says `(x*x)*x = x*x`. Put x = 0:
   - `x*x = 0*0 = 1`;
   - `(x*x)*x = 1*0 = 2`.

   So the left side is 2 and the right side is 1: law 224 fails. Law 598 holds at the closed pair (0, 1): `0*1 = 8`,
   `1*8 = 9`, `0*9 = 1`, so `x*(y*(x*y)) = 1 = y` with x = 0, y = 1. Every model built from this seed satisfies law
   598 (by the ETP construction) and fails law 224. No finite table can do this: every finite model of law 598
   satisfies law 224 (the ETP's `Finite.Equation65_implies_Equation359`).

4. **What it means and what it does NOT mean.**
   - It means: the 2 pairs 598 -> 224 and 88 -> 579 now have an answer here, "does not imply", with a certificate
     whose finite part this repository re-checks on every run (a gate of `LOOP.md` and CI). All 16 ETP Austin pairs
     of step 21 now have such a check (steps 23, 24, 25). Open pairs: 6 before, **4 after**, all with `f`.
   - It does NOT mean the pairs are proved here. The general construction is the ETP's Lean proof, not re-run and not
     re-proved here; the bounded test only shows that the step behaves on the first 49,000 or so steps.
   - `results/status_matrix.npz` still says code 6 (open) for the 2 pairs: new codes are a published format change
     left to the owner (Blocked in `STATE.md`).

5. **How to re-check.** From the repository root:

   ```
   python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json
   python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json --selftest
   ```

   Expected: `the seed passes the 6 conditions of the Lean file`, `pair 598 -> 224: seed, law 224 fails at {'x': 0}:
   2 != 1`, `pair 88 -> 579: seed mirrored, law 579 fails at {'x': 0}: 2 != 1`, a `bounded test` line with 49426
   extension steps, two lines `1600 instances evaluated, 0 failures`, `2 open pairs with a seed certificate` and
   `ALL PASS` (about 1 s). The selftest prints 16 `rejected` lines, `selftest: 16 of 16 corrupted inputs rejected`
   and `ALL PASS` (about 3 s). Adding `--etp ../_external/equational_theories` (a clone of the ETP at commit
   `dbc9a2bf`) also prints `conditions, Equation65 and seed compared with equational_theories/Asterix.lean:
   identical`.

## Goal

Queue item 1 (open pairs, piece 4d-3, last): see whether the ETP's Asterix model of ETP 65 (2 of the 6 open pairs)
can be checked by plain code here, and with what label.

## Command(s)

- `python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json --etp ../_external/equational_theories`
- `python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json --selftest`
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`. Local ETP clone at commit `dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15`
(2026-11-19), read only: `equational_theories/Asterix.lean` (547 lines, read in full); `equational_theories/Equations/
Basic.lean` lines 77 and 145 and `Eqns1_999.lean` line 364 (equations 65, 4065 and 359);
`Generated/FiniteImplicationSearch/theorems/Inverses1.lean` line 1526 (header of
`Finite.Equation65_implies_Equation359` only). Results of step 22 (`results/austin_chains.json`). No web access.
Python 3.12.10, Windows 10.

## Output

- `results/asterix_eq65.json` (new): source (repository, commit, file, line numbers), the seed (E0 and E1), and the
  2 pairs (mirror flag, value of x).
- `src/check_asterix_eq65.py` (new): the checker, `--selftest` and `--etp`; a new gate in `LOOP.md`, in CI and in the
  README command list.
- The 2 pairs, both "does not imply":

  | Our pair | ETP | Mirror | B fails at | Left side | Right side |
  |---|---|---|---|---|---|
  | 598 -> 224 | 65 -> 359 | no | x = 0 | 2 | 1 |
  | 88 -> 579 | 261 -> 307 | yes | x = 0 | 2 | 1 |

  The ETP theorem itself lists failures of equations 614, 817, 1426, 3862 and 4065 at x = 0, not 359. Step 22 linked
  the pairs through law r = ETP 4065 (`x*x = ((x*x)*x)*x`), which B implies in 2 steps. Here B itself fails at x = 0
  in the seed, so that link is not needed.
- Bounded test: 49,426 extension steps (8 bad, 24,913 closing older pairs), 123,857 products, 25,001 closed pairs
  in all, 0 condition failures, seed products unchanged, 1,600 instances each of laws 598 and 88, 0
  failures.
- Open pairs: 4 (all with `f`). `results/status_matrix.npz` unchanged.

## Checks done (and what each one can and cannot catch)

- The 6 conditions on the seed: catch a wrongly copied seed. Cannot catch an error in the Lean construction.
- Conditions, ETP 65 text, seed E0, E1 and values compared with the Lean file (`--etp`, run once, plus three
  corrupted inputs rejected by hand): catches a misread condition or a miscopied seed. Not run in CI (CI has no ETP
  clone).
- ETP 65 is law 598 up to renaming letters and swapping sides: checked in code (`--etp`).
- Failure of B from seed products only, normal and mirrored: catches a wrong mirror flag or value of x. Relies on the
  Lean ordering `le` (extensions keep E1's products), read, and tested on the bounded range only.
- Bounded test: catches a misread extension step (the selftest rejects five broken versions). Cannot prove anything
  about products never reached.
- Selftest: 16 of 16 corrupted inputs rejected.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS; `check_term_rewriting.py`
  ALL PASS and selftest ALL PASS; `check_completion.py` on both files ALL PASS, selftests 10 of 10 and 15 of 15;
  `check_derivations.py` ALL PASS, selftest 14 of 14; `check_greedy_eq73.py` ALL PASS, selftest 13 of 13;
  `check_greedy_eq118.py` ALL PASS, selftest 14 of 14; `check_asterix_eq65.py` ALL PASS, selftest 16 of 16.

## NOT verified

- The ETP's Lean construction (`move_rev_good`, `move_rev_bad` and their proofs of the 6 conditions, `closureSeq`,
  `closure_eq_of_mem_e1`, `closure_prop`): not re-run here, the proof steps not re-proved. The ETP's Lean build was
  not run.
- That an extension keeps the seed's products (`le_act`, `le_add_e0`, `closureSeq_mono`): read, and true on the
  bounded range, not proved here.
- The order of the 20,000 Lean-order steps follows Mathlib's `Nat.unpair` and the `Denumerable (ℕ × ℕ)` instance as
  written in the checker from memory; the Mathlib source was not read. The test does not depend on it (the Lean step
  allows any order).
- `notMemFinset` on the natural numbers is read as "the smallest number not in the set" (`Nat.find` with
  `Denumerable ℕ` the identity, from memory of Mathlib, not read). The checker's choice of z is that; a different
  fresh number would also be allowed by the Lean step (`move_rev_good` takes any z with the side conditions).
- The bounded test covers about 49,000 steps and laws at x, y below 40 only.
- That every finite model of law 598 satisfies law 224 (the ETP's `Finite.Equation65_implies_Equation359`): only the
  theorem header was seen; not used for the answer.
- The 4 pairs with `f` (`(x*y)*f(x) = y` and its mirror) are not touched here.

## Surprises, errors, dead ends

- The first run took 66 s: the fresh number z was searched from 0 at every step. Keeping the smallest unused number
  between steps brought it to 1 s with the same output.
- The first selftest accepted "seed product removed" for the product `0*3 = 4`: without it the seed still meets all 6
  conditions and B still fails, so it was not a corruption (that product serves other facts of the ETP theorem). The
  mutation was replaced by removing `1*0 = 2` and `8*0 = 10`, which matter; both rejected.

## Next

The 4 open pairs with `f` (queue item "piece 4f"): `(x*y)*f(x) = y` (law 277) to laws 574 and 632, and its mirror
law 408 to laws 122 and 128. They need a new idea (hand notes in `steps/20-counterexample-search-law-277.md`).
