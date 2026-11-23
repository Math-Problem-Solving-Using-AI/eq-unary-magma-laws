# 07. Full independent re-check of the 335,177 small-structure refutations

- Date: 2026-11-22
- Status label: `model-verified` (was `model-verified (sampled)`)
- Commit(s): 5686e7e (verifiers), selftest and this record in later commits

## In plain words

1. **The question.** Step 03 marked 335,177 pairs (A, B) as "A does not imply B" because some table with 2 or 3
   elements satisfies A and fails B. At that point only a sample of them had been checked by a second program. Do all
   of them hold up when checked by code that shares nothing with the program that found them?

   Words used here:
   - A **structure** is a set of elements with a table for a two-input operation `*` and a list for a one-input
     operation `f`.
   - A **law** is an equation such as `x*y = x` that must hold for every choice of the letters. Law A **implies** law B
     if every structure where A holds also has B holding.
   - A **refutation** (or certificate, witness, counterexample) of "A implies B" is one structure where A holds and B
     fails.
   - The **catalogue** is the list, made in step 03 by `src/models.py`, of all structures with 2 or 3 elements and of
     which laws each one satisfies.
   - A **mutation test** deliberately damages the input (changes one table entry, swaps A and B, and so on) and checks
     that the checker then reports failures. A checker that never fails proves nothing.
   - The label **`model-verified`** means: the certificate was re-checked by plain code that tries every choice of the
     letters. Before this step the label was `model-verified (sampled)`.

2. **What was done, in order.**
   1. Wrote `src/verify_small_refutations.py`. For each of the 335,177 pairs it takes one structure from the catalogue,
      reads A and B again from their *text* with a separate reader, and tries every choice of the letters to confirm
      that A holds and B fails. The stored laws, their texts, the catalogue table and the structures all have to
      agree, or the pair fails.
   2. Ran it: all 335,177 passed, in about 5 seconds.
   3. Because "0 failed" means little if the checker cannot fail, wrote `src/selftest_verifiers.py`, which damages the
      input in several ways and confirms the failures are caught: one changed table entry in each of the 708 step 06
      certificates broke 698 of them (the other 10 changed a cell the laws never use); swapping A and B broke all 708;
      shifting the law list by one made 33,424 of 40,392 tested pairs fail; and hand examples gave the right answers.
   4. The run time looked too short, so it was measured: about 22 microseconds per pair. Plausible for small laws.

3. **A small example.** A = `x*y = x`, B = `x*y = y`, on the set {0, 1} with `x*y = x` for every x and y
   (table rows `0 0` and `1 1`). A holds by the way the table is made. B fails: `0*1 = 0`, not 1. The checker
   confirms this by trying all 4 choices of x and y for each law.

4. **What it means and what it does NOT mean.**
   - It means: every one of the 335,177 "does not imply" answers of code 1 was confirmed by a second, separate program,
     and that program was shown to catch damaged input. Their label is now `model-verified`.
   - It does NOT mean that the checker would catch every possible error: a mutation test shows that it reacts to the
     damage tried, not to all damage. The checker is short; reading it is the remaining check.
   - It says nothing about pairs that have no certificate.

5. **How to re-check.** From the repository root:
   - `python src/models.py data/laws_3.json data/o3` (rebuilds the catalogue; its last line is
     `laws: 712 refuted pairs: 335177 candidate implications left: 171055`).
   - `python src/verify_small_refutations.py data/laws_3.json data/o3`; expected
     `refutations re-verified: 335177, failed: 0` and a time of a few seconds.
   - `python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_larger_models.json`; expected last
     line `ALL PASS`.
   - `python src/query.py "x*y = x" "x*y = y" --witness`; expected `code 1`, `label: model-verified` and the structure
     `"mul": [[0, 0], [1, 1]]`.

## Goal
Step 03 only spot-checked the model catalogue. Re-check every refuted pair with code that shares
nothing with the numpy catalogue, and prove that the checker can actually fail.

## Command(s)
```
P=.
python $P/src/verify_small_refutations.py $P/data/laws_3.json $P/data/o3
python $P/src/selftest_verifiers.py $P/data/laws_3.json $P/data/o3 $P/results/witnesses_larger_models.json
```

## What the verifier does
For each refuted pair (A, B): take a witness structure from the satisfaction table, parse A and B
from their TEXT with the separate parser, and check by plain evaluation of every variable
assignment that the structure satisfies A and fails B. The stored law terms, the printed texts, the
numpy table and the structures all have to agree for a pair to pass.

## Output
```
refutations re-verified: 335177, failed: 0, time 5s
```

## Checks done
- All 335,177 refutations re-verified, 0 failed.
- **Mutation tests of the verifiers** (`selftest_verifiers.py`), so that "0 failed" can mean
  something:
  - flipping one table entry of each of the 708 larger certificates: 698 broke
  - swapping A and B in each certificate: 708 of 708 broke
  - evaluator on hand examples (`x*y = x` holds, `x*y = y` fails in a 2-element left-projection
    structure, and two more): all correct
  - shifting the law list by one so pairs are checked against the wrong laws: 33,424 of 40,392 failed
  - the 10 flipped entries that did not break a certificate are cases where the flipped table cell
    is never used by the laws involved, which is expected.
- The time of 5 s looked too fast, so it was checked: per pair about 22 microseconds in a single
  process on the 60 smallest source laws (few variables, cheap evaluation), plus parallel workers.
  Plausible. It is a reason to keep the mutation tests, not to trust the run time.

## NOT verified
- The mutation tests show the verifier reacts to corruption. They cannot show that every possible
  error would be caught. The verifier is about 60 lines (`verify_witnesses.py`), read it.
- Nothing here says anything about pairs without a certificate.
- The structure enumeration of sizes 2 and 3 is shared with the catalogue (`models.py`), which
  matters only for completeness, not for the correctness of a certificate: a certificate is
  self-contained.

## Next
Work on the 894 open pairs and the six open laws of [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models).
