# 03. Small-model catalogue and first refutations

- Date: 2026-11-22
- Status label: model-verified (sampled)
- Commit(s): 010c71f (code), b344b53 (spot-check)

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
