# 06. Larger counterexamples for the unresolved pairs

- Date: 2026-11-22
- Status label: `model-verified` for the 708 pairs settled here
- Commit(s): 51459f3 (script), certificates in a later commit

## In plain words

1. **The question.** Step 05 left 1,602 pairs (A, B) without an answer: no table with 2 or 3 elements showed that A
   does not imply B, and z3 could not prove that it does. Is there a table with 4 or 5 elements that shows it?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a table for a two-input
     operation `*` and a list for a one-input operation `f`. Here the sets are finite: {0, 1, 2, 3} or {0, ..., 4}.
   - A **law** is an equation such as `(x*y)*x = y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding.
   - A **certificate** (also called a witness or counterexample) is one structure where A holds and B fails. One is
     enough to show that A does not imply B, with no proof program to trust.
   - **z3** is an automatic solver (step 05). Here it was used only to *search* for tables; every table it returned
     was re-checked by separate plain code.
   - The label **`model-verified`** means: the certificate was re-checked by plain code that tries every choice of the
     letters.

2. **What was done, in order.**
   1. For each of the 1,602 pairs, z3 was asked for a table of size 4 that satisfies A and fails B, then of size 5,
      with 5 seconds per size and pair. Larger tables were not tried here because the search grows very fast.
   2. Each table found was re-checked at once by plain evaluation (`findmodel.check_model`), so a wrong answer of z3
      could not slip in.
   3. All 708 tables found were stored in `results/witnesses_larger_models.json` and re-checked again by a separate
      program, `src/verify_witnesses.py`, which has its own reader for the law texts and does not use z3.
   4. The 28 pairs where z3 had said in step 05 "a counterexample exists" without giving one were compared: all 28 got
      a certificate here, so those z3 answers were right.

3. **A small example.** A = `(x*y)*x = y`, B = `(x*y)*y = x`. No table with 2 or 3 elements separates them. This one
   with 4 elements does (row = left input, column = right input; `f` plays no role, it is 2 everywhere):

   ```
   *  | 0 1 2 3
   ---+--------
   0  | 0 3 1 2
   1  | 2 1 3 0
   2  | 3 0 2 1
   3  | 1 2 0 3
   ```

   Law A holds: all 16 choices of x and y give `(x*y)*x = y`, for example x = 0, y = 1: `0*1 = 3`, `3*0 = 1` = y.
   Law B fails at x = 0, y = 1: `0*1 = 3`, `3*1 = 2`, and 2 is not x = 0. So A does not imply B.

4. **What it means and what it does NOT mean.**
   - It means: 708 pairs are "does not imply" (code 2 in `results/status_matrix.npz`), each with a stored table that
     two separate programs re-checked, label `model-verified`.
   - It does NOT mean anything for the other 894 pairs. "No table up to size 5 within 5 seconds" is not "no
     counterexample exists": the pair may be an implication, or its counterexamples may be larger or infinite. Those
     894 pairs were answered later, in steps 08 to 29.

5. **How to re-check.** From the repository root:
   - `python src/verify_witnesses.py results/witnesses_larger_models.json`; expected
     `708 certificates checked, 0 failed, 894 entries without a certificate`.
   - `python src/query.py "(x*y)*x = y" "(x*y)*y = x" --witness`; expected `code 2: NOT an implication: refuted by a
     certificate (structure with 4 or 5 elements)`, `label: model-verified`, and the table above as
     `"mul": [[0, 3, 1, 2], [2, 1, 3, 0], [3, 0, 2, 1], [1, 2, 0, 3]]`.
   - Re-running the search itself: the first command under "Command(s)" below. It takes a while (up to 5 seconds per
     size and pair), and z3 may find different tables than last time, which is fine as long as each one checks.

## Goal
For each of the 1,602 pairs left unresolved by step 05, look for a finite structure of size 4 or
5 that satisfies A and fails B. A structure found and re-checked is a certificate that A does not
imply B, with no prover to trust.

## Command(s)
```
P=.
python $P/src/resolve_open.py $P/data/laws_3.json $P/data/o3 5 5000 $P/results/witnesses_larger_models.json
python $P/src/verify_witnesses.py $P/results/witnesses_larger_models.json
```

## Inputs
z3 as a finite model finder (enumeration sort, laws instantiated on every assignment), timeout 5 s
per size and pair. Sizes 4 and 5.

## Output
`results/witnesses_larger_models.json` (certificates, tracked in git).

| Outcome | Pairs |
|---------|-------|
| certificate found, size 4 | 566 |
| certificate found, size 5 | 142 |
| none found up to size 5 | 894 (from 71 source laws) |

All 28 pairs that z3 had answered `sat` in step 05 are among the 708 certificates, so z3's `sat`
answers were right.

## Checks done
- During the run, each structure was re-checked by `findmodel.check_model` (plain evaluation).
  0 of 708 failed.
- `verify_witnesses.py` re-checks the stored file afterwards using its own parser and evaluator,
  no z3 and no numpy: 708 checked, 0 failed. The law texts in the file are parsed (not the stored
  terms), so a text that did not match its law would fail here.

## NOT verified
- The 894 open pairs: no structure up to size 5 within 5 s, and no proof within 1 s. This says
  nothing about truth. They may be implications, or have only larger or infinite counterexamples.
- That the verifier is correct. It is short (read it), and `verify_witnesses.py` shares the law
  text parser with `check_laws_text.py`.

## Next
Longer proof attempts on the 894, larger structures (6 and up), and a hand analysis of the
source laws that occur most (`f(x)*f(y) = x` and `f(x)*f(y) = y` have 38 open targets each).
