# 07. Full independent re-check of the 335,177 small-structure refutations

- Date: 2026-11-22
- Status label: `model-verified` (was `model-verified (sampled)`)
- Commit(s): c02383a (verifiers), selftest and this record in later commits

## Goal
Step 03 only spot-checked the model catalogue. Re-check every refuted pair with code that shares
nothing with the numpy catalogue, and prove that the checker can actually fail.

## Command(s)
```
P=problems/unary-magma-laws
.venv/Scripts/python.exe $P/src/verify_small_refutations.py $P/data/laws_3.json $P/data/o3
.venv/Scripts/python.exe $P/src/selftest_verifiers.py $P/data/laws_3.json $P/data/o3 $P/results/witnesses_larger_models.json
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
Work on the 894 open pairs and the six open laws of `../../laws-without-small-models`.
