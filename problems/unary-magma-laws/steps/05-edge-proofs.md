# 05. Prove the remaining candidate implications

- Date: 2026-11-22
- Status label: IN PROGRESS, nothing recorded yet
- Commit(s): 3afde82 (first version), fix in a later commit

## Goal
For the pairs (A, B) that no small structure refutes, try to prove A implies B with z3.
Pairs z3 cannot prove go to a larger-counterexample search.

## Command(s)
```
python problems/unary-magma-laws/src/prove.py edges problems/unary-magma-laws/data/laws_3.json problems/unary-magma-laws/data/o3 1000
```

## Attempt 1 (stopped, wasted)
- Ran for about 40 minutes with 8 workers and a 1 s timeout per pair, over about 24,000 pairs.
- Results were kept only in memory and written at the very end. When I saw it stuck on the last
  14 of 464 source laws, I stopped it and lost all results.
- Cause of the slowness: the last sources were the 9 unresolved zero-model laws. Each has about
  700 candidate targets (nothing refutes them), so z3 spent up to 1 s on each, for no gain.
- Fixes: save state every 10 sources and on exit, resume from saved state, skip sources with no
  small model (they belong to `../../laws-without-small-models`).

## Attempt 2
Started after the fixes. Results to be written into this file when finished.

## NOT verified
Everything. Any z3 `unsat` here is a lead, not a certificate. Any z3 `sat` is unverified until
the structure it found is re-checked by `findmodel.check_model`.

## Next
Close the implication graph under transitivity, search larger counterexamples for what is left.
