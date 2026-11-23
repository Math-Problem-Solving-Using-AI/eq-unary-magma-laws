# 02. Enumerate the laws

- Date: 2026-11-22
- Status label: independently recounted (counts), no mathematical claim
- Commit(s): 010c71f (code), b344b53 (checks)

## In plain words

1. **The question.** How many different laws of size at most 3 are there, and what are they? A **law** is an equation
   between two expressions in letters x, y, z, ... built with a two-input operation `*` and a one-input operation `f`,
   required to hold for every choice of the letters. Its **size** is the number of `*` and `f` symbols in it (step 01).

2. **What was done, in order.**
   1. `src/laws.py` listed every possible shape of expression with up to 3 symbols, filled the letter positions in
      every possible way, and dropped equations whose two sides are identical.
   2. It put every law into one standard form (letters renamed in order of first appearance, the two sides in a fixed
      order), so that the same law written two ways is counted once. Result: 712 laws, stored in `data/laws_3.json`
      (7 of size 1, 62 of size 2, 643 of size 3).
   3. A second program, `src/check_laws_count.py`, counted again in a different way (build every expression, try
      every renaming of the letters and both side orders, keep the smallest). Both lists are exactly the same. This was
      needed because a counting mistake would silently drop or double laws for every later step.
   4. A third program, `src/check_laws_text.py`, read the printed text of each law (for example `x*(y*z) = x`) back
      with a separate small reader and compared it with the stored form: 0 mismatches. This matters because the later
      checkers read laws from their text.
   5. The 7 laws of size 1 were also checked by hand.

3. **A small example.** The 7 laws of size 1 are: `x = f(x)`, `x = f(y)`, `x = x*x`, `x = x*y`, `x = y*x`,
   `x*x = y`, `x*y = z`. For instance `y*z = y` is not a new law: rename y to x and z to y and it is `x*y = x`, which
   is `x = x*y` with the sides swapped. Its mirror `x*y = y` is kept as a separate law (`x = y*x` in the list).

4. **What it means and what it does NOT mean.**
   - It means: the list of 712 laws is complete and has no duplicates, as far as two programs written in different
     ways agree.
   - It does NOT mean: that "same up to renaming and side swap" is the only sensible choice. Both programs share that
     choice, so they cannot catch a disagreement about it. Laws of size 4 were counted (8,093) but not stored or
     text-checked.

5. **How to re-check.** From the repository root:
   - `python src/check_laws_count.py 3`; the expected output ends with `only brute force: 0  only laws.py: 0` and
     `MATCH`.
   - `python src/check_laws_text.py data/laws_3.json`; expected output `712 laws checked, 0 mismatches`.

## Goal
List every law of size at most N up to renaming and side swap.

## Command(s)
```
python src/laws.py 3 data/laws_3.json
```

## Inputs
`src/laws.py`. Algorithm: enumerate term shapes with k operations, fill leaves with every set
partition of variable labels, drop `lhs = rhs`, canonicalize by first-appearance renaming and
the better of the two side orders.

## Output
`data/laws_3.json`. Counts by size: 1: 7, 2: 62, 3: 643, 4: 8,093. Cumulative: 712 up to size
3, 8,805 up to size 4.

Hand check of size 1 (7 laws): `x = f(x)`, `x = f(y)`, `x = x*x`, `x = x*y`, `x = y*x`,
`x*x = y`, `x*y = z`. Matches.

## Checks done
- `check_laws_count.py`: a different algorithm (build every real term over variables, canonicalize
  by minimum over ALL variable permutations and side swaps). Exact set match with `laws.py` for
  size up to 3 (<1 s) and size up to 4 (71 s). Catches: missing laws, duplicate laws, wrong
  canonicalization. Cannot catch: a shared misunderstanding of what "same law" means.
- `check_laws_text.py`: the printed text of all 712 laws parses back to the stored term with a
  separate small parser, 0 mismatches. Catches: a text that does not mean the stored term
  (the fidelity risk described in `docs/shared/LEAN_CAVEATS.md`, C1). Run on size 3 only.

## NOT verified
- Text round trip was not run on the 8,093 size-4 laws (not generated to file yet).
- Whether identifying only renamings and side swaps is the right equivalence for the questions we
  will ask (mirror laws are kept apart on purpose).

## Surprises, errors, dead ends
None in this step.

## Next
Step 03: small-model catalogue.
