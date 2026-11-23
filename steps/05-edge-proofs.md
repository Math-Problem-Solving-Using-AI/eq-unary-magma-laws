# 05. Prove the remaining candidate implications

- Date: 2026-11-22
- Status label: IN PROGRESS, nothing recorded yet
- Commit(s): ebdb14f (first version), fix in a later commit

## In plain words

1. **The question.** After steps 03 and 04, 17,479 pairs (A, B) were not refuted by a small table, and A is not one
   of the 216 laws without a small model. For those pairs: can z3 prove that A implies B?

   Words used here:
   - A **law** is an equation such as `x*y = x` that must hold for every choice of the letters. A **implies** B if
     every structure (a set with a two-input operation `*` and a one-input operation `f`) where A holds also has B
     holding (step 01).
   - **z3** is an automatic solver. Asked "is there a structure where A holds and B fails?", it answers `unsat` (no,
     so A implies B), `sat` (yes) or `unknown` / time-out.
   - The label **`z3-only`** means the answer rests on z3 alone, with no stored proof checked by other code.
   - **Transitive closure**: if A implies B and B implies C, then A implies C, with no new z3 call.
   - **Open** or **unresolved** means no answer yet.
   - The status line above says "IN PROGRESS": that line was written before attempt 2 and not updated afterwards.
     Attempt 2 finished; its numbers are below.

2. **What was done, in order.**
   1. **Attempt 1** ran z3 for about 40 minutes and kept results only in memory. It was stopped by hand and everything
      was lost. Lesson: save results every few tasks and be able to resume.
   2. **Attempt 2** (with saving) skipped the 9 laws with no small model and no collapse proof (each would have about
      700 pairs that nothing refutes) and gave z3 1 second per pair: 15,731 pairs proved, 15,877 after transitive
      closure, 28 answered `sat` (z3 says a counterexample exists but did not return it, so there was nothing to check
      yet; step 06 looked for them).
   3. Cross-checked: none of the proved pairs is refuted by a small table. A wrong z3 proof would likely have shown up
      here.
   4. Counted every one of the 506,232 ordered pairs into exactly one group: 335,177 refuted by a small table,
      147,177 with a collapsing law as A, 15,877 proved by z3, 6,399 with one of the 9 unresolved laws as A, and
      1,602 unresolved. These groups are the codes stored in `results/status_matrix.npz`.

3. **A small example.** A = `x*y = x`, B = `(x*y)*z = x`. z3 proved that A implies B. By hand: A with x := x*y and
   y := z gives `(x*y)*z = x*y`, and A again gives `x*y = x`, so `(x*y)*z = x`. The reverse does not hold: on {0, 1}
   take `0*y = 1` and `1*y = 0` for every y. Then `(x*y)*z = x` holds (x is switched twice), but `0*0 = 1`, so
   `x*y = x` fails.

4. **What it means and what it does NOT mean.**
   - It means: 15,877 pairs are marked "implies" (code 3, `z3-only`) and 1,602 were left for a search with larger
     tables (step 06).
   - It does NOT mean: proved. No proof is stored for these pairs and no other program checked them. z3 also varies
     between runs, so a pair it timed out on this time may be proved next time. "Unresolved" means z3 gave up, not that
     the pair is false.

5. **How to re-check.** From the repository root, after `python src/models.py data/laws_3.json data/o3`:
   - `python src/check_status_matrix.py data/laws_3.json data/o3 results/witnesses_larger_models.json results/status_matrix.npz`;
     expected `counts: {0: 712, 1: 335177, 2: 708, 3: 15877, 4: 147177, 5: 6399, 6: 894}` and
     `status table consistent` (code 2 and the smaller unresolved count 894 come from step 06). It checks the table
     against the small tables of step 03, not the z3 proofs.
   - `python src/query.py "x*y = x" "(x*y)*z = x"`; expected `code 3: implication, proved by z3 (with transitive
     closure)` and `label: z3-only`. `python src/query.py "(x*y)*z = x" "x*y = x" --witness` shows the 2-element table
     above (`"mul": [[1, 1], [0, 0]]`).
   - Re-running z3 itself: `python src/prove.py edges data/laws_3.json data/o3 1000` (about 4 to 5 minutes with 8
     workers; it needs `data/o3_collapse.npy` from step 04). Its counts can differ a little from run to run.

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
  small model (they belong to [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models)).

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
| A is one of the 9 laws of [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models) | 6,399 | open, see that problem |
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
