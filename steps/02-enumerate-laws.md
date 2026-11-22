# 02. Enumerate the laws

- Date: 2026-11-22
- Status label: independently recounted (counts), no mathematical claim
- Commit(s): 010c71f (code), b344b53 (checks)

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
