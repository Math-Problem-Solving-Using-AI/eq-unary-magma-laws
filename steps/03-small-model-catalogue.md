# 03. Small-model catalogue and first refutations

- Date: 2026-11-22
- Status label: model-verified (sampled)
- Commit(s): 010c71f (code), b344b53 (spot-check)

## In plain words

1. **The question.** For each ordered pair of laws (A, B), can a small table show that A does NOT imply B? A **law** is
   an equation such as `x*y = x` that must hold for every choice of the letters. A **implies** B if every structure
   where A holds also has B holding (step 01). One structure where A holds and B fails is enough to show "A does not
   imply B".

   Words used here:
   - A **structure** is a set with a two-input operation `*` and a one-input operation `f`, given here by tables.
   - A **witness** (or **counterexample**) for the pair (A, B) is a structure where A holds and B fails.
   - "**Refuted**" means a witness was found.
   - A **candidate** is a pair not refuted yet. It may be an implication, or it may need a bigger witness.
   - The label **`model-verified (sampled)`** means: the answers come from evaluating tables, and a random sample of
     them was re-evaluated by separate code. Labels are defined in `docs/shared/VERIFICATION_PROTOCOL.md`.

2. **What was done, in order.**
   1. `src/models.py` listed every structure with 2 elements (64) and with 3 elements (531,441 tables, 88,722 after
      treating tables that differ only by renaming the elements as one). Renaming the elements cannot change which
      laws hold, so nothing is lost.
   2. For each of the 712 laws and each structure, it computed whether the law holds (it tries every choice of the
      letters).
   3. For each pair (A, B), it looked for a structure where A holds and B fails: 335,177 pairs refuted, 171,055 left
      as candidates.
   4. `src/check_catalogue.py` re-did 9,000 random entries in plain Python, sharing no code with the fast computation:
      0 disagreements. This was needed because the fast computation packs results into bits, a place where bugs hide.
   5. Noticed that 216 laws hold in no structure with 2 or 3 elements, so nothing could refute them: they made most of
      the candidates. Step 04 deals with them.

3. **A small example.** A = `x*y = x`, B = `x*y = y*x`. Witness on {0, 1}: `*` is "take the left input" (row 0 is
   `0 0`, row 1 is `1 1`), and `f` sends everything to 0. A holds everywhere; B fails at x = 0, y = 1, since
   `0*1 = 0` but `1*0 = 1`. So the pair (A, B) is refuted. The reverse pair (B, A) is also refuted, by another table.

4. **What it means and what it does NOT mean.**
   - It means: 335,177 pairs are "does not imply", each backed by a concrete table. An error can go one way only: a
     table missed by mistake loses a refutation but never creates a false one.
   - It does NOT mean: that every one of them was re-checked in this step (only a sample; step 07 later re-checked all
     335,177 with separate code). And a pair left as a candidate is NOT shown to be an implication: its witness may
     just need more than 3 elements. "Not found" is not "does not exist".

5. **How to re-check.** From the repository root:
   - `python src/models.py data/laws_3.json data/o3` (about 5 to 15 seconds); the expected output ends with
     `laws: 712 refuted pairs: 335177 candidate implications left: 171055`.
   - `python src/check_catalogue.py data/laws_3.json data/o3 3000`; expected
     `checked 6000 satisfaction entries (+ refuted witnesses), disagreements: 0`.

## Goal
Find, for as many ordered pairs (A, B) as possible, a finite structure that satisfies A and
fails B. That proves A does not imply B with no prover involved.

## Command(s)
```
python src/models.py data/laws_3.json data/o3
python src/check_catalogue.py data/laws_3.json data/o3 3000
```

## Inputs
712 laws. Every structure of size 2 (64 of them) and size 3 (3^12 = 531,441 tables, reduced
to 88,722 up to relabeling elements). Total 88,786 structures.

## Output (generated, git-ignored)
- `data/o3_sat.npy`: 712 x 88,786 table, does law i hold in structure j.
- `data/o3_refuted.npy`: 712 x 712 table, pair (A, B) refuted by some structure.
- Numbers: 335,177 refuted pairs, 171,055 candidates left (+712 diagonal = 506,944). Run time about 15 s.

## Checks done
- `check_catalogue.py`: re-evaluates 3,000 random satisfied entries, 3,000 random unsatisfied
  entries, and 3,000 random refuted pairs (finding the witness structure from the table and
  re-checking that it satisfies A and fails B) with plain Python, no numpy, no z3. 0 disagreements.
  Catches: errors in the vectorized evaluation or the bit packing, for the sampled entries.
- Direction of error: wrongly missing a structure can only lose refutations, never create a
  false one. Soundness of "refuted" depends only on the evaluation being right.

## NOT verified
- Only a sample was re-evaluated, not all 335,177 refutations. Full re-check is planned (each
  refutation becomes a stored witness with its own plain-Python check).
- The count 88,722 for size 3 up to relabeling was not independently derived (for example by
  counting orbits another way). Error direction is safe, see above.
- "Not refuted" says nothing about truth: a pair may still be a non-implication with only larger
  counterexamples (the Equational Theories Project met this).

## Surprises, errors, dead ends
- First run of `models.py` failed: numpy was missing from the virtual environment. Fixed,
  recorded in `docs/shared/LESSONS.md`.
- 216 laws have no model of size 2 or 3 and made 153,576 of the 171,055 candidates look open.
  That is an artifact, see step 04.

## Next
Step 04: collapse laws.
