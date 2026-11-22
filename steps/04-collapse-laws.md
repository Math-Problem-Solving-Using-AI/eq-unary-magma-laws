# 04. Laws with no small model: do they collapse?

- Date: 2026-11-22
- Status label: z3-only
- Commit(s): 3afde82

## Goal
A law with no model of size 2 or 3 might force every structure to have one element ("collapse",
the law proves `x = y`). Such a law implies every other law. Find out which ones do.

## Command(s)
```
python problems/unary-magma-laws/src/prove.py collapse problems/unary-magma-laws/data/laws_3.json problems/unary-magma-laws/data/o3 5000
```
Run several times: proofs accumulate (see lessons).

## Inputs
216 laws with no model of size 2 or 3. z3, timeout 5 s per law (one run used 60 s).

## Output
`data/o3_collapse.npy`. 207 of 216 proved to collapse (`unsat`). 9 unresolved:
`((x*y)*z)*x = w`, `(f(x)*y)*z = y`, `(x*y)*(y*x) = y`, `(x*y)*(y*z) = y`, `(x*y)*f(z) = y`,
`f((x*y)*z) = y`, `f(x)*(y*z) = y`, `f(x*(y*z)) = y`, `x*(y*f(z)) = y`.

## Checks done
- None beyond z3 itself. A z3 `unsat` is trusted as a proof only as a lead. No proof object is
  stored and no independent checker has confirmed these 207.

## NOT verified
- All 207 collapse claims. Status stays `z3-only` until a derivation is stored and checked by an
  independent tiny checker, and later in Lean (see `docs/VERIFICATION_PROTOCOL.md`).
- That the 9 unresolved laws do or do not collapse: see `../../laws-without-small-models`.

## Surprises, errors, dead ends
- **Assumption broken:** "no model of size 2 or 3" does not mean "collapses". Two of the nine
  have a model of size 4.
- **z3 is not stable between runs:** 207 proofs at 5 s, 205 at 60 s (8 workers in parallel).
  Fix: accumulate proofs, never overwrite. Recorded in `docs/LESSONS.md`.
- `CheckSatResult` is unhashable in z3 (code bug, fixed).

## Next
Step 05: try to prove the remaining candidate pairs.
