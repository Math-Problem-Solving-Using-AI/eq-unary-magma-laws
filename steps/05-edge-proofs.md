# 05. Prove the remaining candidate implications

- Date: 2026-11-22
- Status label: IN PROGRESS, nothing recorded yet
- Commit(s): ebdb14f (first version), fix in a later commit

## Goal
For the pairs (A, B) that no small structure refutes, try to prove A implies B with z3.
Pairs z3 cannot prove go to a larger-counterexample search.

## Command(s)
```
python src/prove.py edges data/laws_3.json data/o3 1000
```

## Attempt 1 (stopped, wasted)
- Ran for about 40 minutes with 8 workers and a 1 s timeout per pair, over about 24,000 pairs.
- Results were kept only in memory and written at the very end. When I saw it stuck on the last
  14 of 464 source laws, I stopped it and lost all results.
- Cause of the slowness: the last sources were the 9 unresolved zero-model laws. Each has about
  700 candidate targets (nothing refutes them), so z3 spent up to 1 s on each, for no gain.
- Fixes: save state every 10 sources and on exit, resume from saved state, skip sources with no
  small model (they belong to [eq-laws-without-small-models](https://github.com/MauroBCardoso/eq-laws-without-small-models)).

## Attempt 2 (after the fixes)

Run time 259 s, 455 source laws, 1 s per pair, 8 workers.

| Outcome | Pairs |
|---------|-------|
| z3 proved A implies B | 15,731 |
| ... plus transitive closure of those | 15,877 total |
| z3 answered `sat` (a counterexample exists, NOT yet verified) | 28 |
| unresolved (timeout or `unknown`), before closure | 1,720 |
| unresolved after closure | 1,602 (includes the 28) |

Accounting of all 506,232 ordered pairs (A different from B), each in exactly one row:

| Group | Pairs | Status |
|-------|-------|--------|
| not implications, refuted by a structure of size 2 or 3 | 335,177 | `model-verified (sampled)` |
| A collapses every structure (207 laws, 711 targets each) | 147,177 | `z3-only` |
| implications proved by z3 (with closure) | 15,877 | `z3-only` |
| A is one of the 9 laws of [eq-laws-without-small-models](https://github.com/MauroBCardoso/eq-laws-without-small-models) | 6,399 | open, see that problem |
| unresolved | 1,602 | open |

Check: 335,177 + 147,177 + 15,877 + 6,399 + 1,602 = 506,232.

Equivalence classes among the laws with a small model (mutual implication, all `z3-only`): 328
classes, the largest has 47 laws.

## Checks done
- **Cross-check of z3 against the model catalogue:** none of the 15,731 proved pairs (nor the
  closure) is refuted by any of the 335,177 structure-based refutations. A wrong z3 proof of a
  false implication would most likely have shown up here. This catches unsound proofs of
  implications that small structures can refute, it cannot catch other errors.
- Refutation propagation (A implies B and A does not imply C gives B does not imply C): zero new
  refutations. Expected: a structure that refutes A to C also satisfies B, so it already refutes
  B to C. Propagation only helps with refutations from larger structures.

## NOT verified
- All 15,877 + 147,177 implication claims: z3 only, no stored derivation, no independent checker,
  no Lean.
- The 28 `sat` answers. The solver did not return the structure, so there is nothing to check yet.
  Step 06 re-derives them with a finite model finder and verifies by plain evaluation.
- That 1 s timeouts say anything: z3 results vary between runs.

## Surprises, errors, dead ends
- Attempt 1 lost, see above, and in `docs/shared/LESSONS.md`.

## Next
Step 06: for the 1,602 unresolved pairs, search structures of size 4 and 5, verify each by plain
evaluation.
