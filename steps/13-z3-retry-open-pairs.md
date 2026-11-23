# 13. z3 again, with a 10-second limit, on the open pairs

- Date: 2026-11-23
- Status label: 18 implications `z3-only` (13 proved directly, 5 by chaining with older z3 proofs).
  Nothing for the other 874 open pairs (a timeout says nothing either way).
- Commit(s): see `git log -- src/retry_open_z3.py src/check_z3_retry.py results/z3_open_retry.json steps/13-z3-retry-open-pairs.md`

## In plain words

1. **The question.** 894 pairs of laws were still open in our table: we did not know whether the
   first law forces the second. 2 of them got an answer in step 11. In step 05, the solver z3 had
   been given 1 second per pair. Does it find more proofs if it gets 10 seconds?

   Words used here:
   - A **structure** (also: magma with a unary operation) is a set of elements with a two-input
     operation `*` and a one-input operation `f`. It may be finite or infinite.
   - A **law** is an equation such as `x*f(y) = x` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding (infinite structures
     included).
   - **z3** is an automatic solver. Asked "is there a structure where A holds and B fails?", it answers
     `unsat` (no: it claims a proof that A implies B), `sat` (yes, and it shows one) or `unknown`
     (it gave up when the time limit ran out).
   - **`z3-only`** is the label for an answer that rests on z3 alone. Nothing else re-checked the
     proof, and z3 does not hand over a proof we could check. It is not called "proved".
   - **Code 6** in the stored table `results/status_matrix.npz` means "open, nothing known yet".
   - **Closure** (transitive closure): if A implies C and C implies B, then A implies B.
   - The **ETP** (Equational Theories Project) settled every question of this kind for laws without
     `f`. We compare with its published answers (step 08) but did not re-check its proofs.
   - A **mutation test** feeds a checker deliberately broken input to make sure it says "no".

2. **What was done, in order.**
   1. Wrote `src/retry_open_z3.py`. For every code-6 pair without a certificate it asks z3 once, with
      a 10-second limit, and saves every answer to `results/z3_open_retry.json`. It saves every 10
      pairs and stops after a set time, so the job ran in three pieces of under ten minutes each, each
      continuing where the last stopped. Proofs are kept across runs, because z3 does not always
      repeat them (see 5 below).
   2. Tested it first on pairs whose answer is known: on three implications (code 3) z3 said `unsat`,
      on three pairs refuted by small tables (code 1) it said `sat` and the table it gave passed our
      plain re-check. So the program can find both kinds of answer.
   3. Ran it on all 892 pairs. Result: 13 `unsat`, 879 `unknown`, 0 `sat`.
   4. Combined the 13 new proofs with the implications already in the table (codes 3 and 4) and
      closed under chaining. That settles 5 more open pairs. It also turns no refuted pair into an
      implication, which would have meant an error somewhere.
   5. Asked z3 again about the 13 pairs, in a fresh process. It repeated 6 at once; with 30 seconds
      and a fresh set of workers it repeated 4 more; 3 were not repeated. z3's results depend on the
      state of the process (known, `docs/shared/LESSONS.md`, "z3 outcomes are not stable"). An
      `unsat` answer is still z3's claim of a proof, so all 13 are kept, with this noted.
   6. Compared with the ETP: 15 of the 18 pairs have no `f`, and for all 15 the ETP also says
      "implies". The 3 not repeated by z3 (in 5) are among these 15.
   7. Checked the 3 direct proofs with `f` by hand (see the example below). Hand arguments are leads,
      not proofs, but they agree.
   8. Wrote `src/check_z3_retry.py`, which re-does steps 4 and 6 from the files and checks that the
      claims fit the table, and gave it a mutation test. Both commands are now LOOP gates and run in
      CI.

3. **A small example.** A = `x*f(y*z) = x`, B = `x*f(y) = x`. z3 says A implies B. A hand argument
   that agrees:
   - A says: multiplying any `x` on the right by `f` of a product gives `x` back.
   - Take any element `y`. By A (with `x` = `y`), `y = y*f(a*b)` for any `a`, `b`. So `y` itself is a
     product of two elements.
   - So every element is a product, and A says `x*f(p) = x` for every product `p`, which is every
     element. That is B.

   Another of the 18: A = `(x*f(y))*z = z`. Put `e = a*f(b)` for any `a`, `b`; A says `e*z = z` for
   every `z`. Then A with `x` = `e` gives `(e*f(y))*z = z`, and `e*f(y) = f(y)`, so `f(y)*z = z`:
   every `f(y)` acts as "do nothing" from the left. The targets `f(x)*y = y`, `f(x*x)*y = y`,
   `f(x*y)*y = y` and `f(x*y)*z = z` all follow.

4. **What it means and what it does NOT mean.**
   - It means: 18 pairs that were open are now "implies", with label `z3-only`. The 15 without `f`
     agree with the ETP.
   - It does NOT mean these 18 are proved. z3 gives no proof we can check, and 3 of the 13 direct
     proofs were not repeated when z3 was asked again.
   - For the other 874 open pairs, z3 found nothing in 10 seconds. That says nothing about the answer.
     Many of them look like cases where the implication holds in every finite structure but may fail
     in an infinite one (for example A = `f(x*y) = x`: in a finite structure `f` must then be a
     one-to-one map, which is not forced in an infinite one). z3 can neither prove such a pair nor
     find a finite counterexample. This is a lead, not checked.
   - `results/status_matrix.npz` was not changed: it still says code 6 for the 18 pairs. Writing code
     3 there would need `export_status.py` and the z3 proof arrays of step 05, which are not in the
     repository (git-ignored); and `src/query.py` does not read the new file yet.

5. **How to re-check.**

   ```
   python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
   ```

   Expected: `pairs in file: 892, proved by z3: 13, settled in addition by the closure: 5`, the 18
   pairs listed (15 with `ETP: implies`, 3 with `ETP: no data (has f)`), then `ALL PASS`.
   Add `--selftest` for the mutation test (expected: 5 lines `rejected`, then `selftest: ALL PASS`),
   or `--rerun` to ask z3 again (its answers may differ from run to run).

   To redo the search (three runs of about 8 minutes on 8 cores; each run continues the last):

   ```
   python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 10000 480 results/z3_open_retry.json
   ```

## Goal

First piece of queue item 1: retry z3 with a longer time limit on the open (code 6) pairs, with saved,
resumable state.

## Command(s)

```
python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 10000 480 results/z3_open_retry.json
python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 10000 500 results/z3_open_retry.json
python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 10000 500 results/z3_open_retry.json
python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json --rerun
python src/check_z3_retry.py ... --selftest
```

plus the 30-second re-ask of the 7 pairs not repeated by `--rerun` (an inline pool of 8 workers calling
`retry_open_z3.task`), the positive control on codes 3 and 1 (inline, `task` with 5 s), and all gates of
`LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz` (code 6 = open), `results/witnesses_etp_magmas.json`
(the 2 pairs already certified are skipped), `results/etp_crosscheck.json`,
`results/witnesses_ffree_models.json`. Python 3.12, z3 version string `5.4.1` (from `z3.get_version_string()`),
8 worker processes, Windows 10.

## Output

- `results/z3_open_retry.json`: for each of the 892 pairs, the law texts and z3's answer at 10,000 ms;
  `proved_ms` for the 13 `unsat` pairs.
- The 13 direct proofs (law id minus 1, A => B): 75,209 77,94 142,491 152,69 152,85 152,491 164,203
  202,485 202,490 239,594 497,142 507,136 709,57. The 5 by closure: 75,594 202,33 202,466 239,209
  497,136. The texts are printed by the checker.
- Still open: 874 pairs from 64 source laws; 20 of them have no `f` and keep the ETP's answer
  (`known (ETP)`), 854 involve `f` and have no answer at all.

## Checks done (and what each one can and cannot catch)

- **Positive control** before the run: 3 known implications gave `unsat`, 3 known refutations gave a
  `sat` structure that passed `check_model`. Catches a program that cannot find either answer.
- **Consistency with the table** (`check_z3_retry.py`): every pair in the file is code 6 with matching
  law texts; the closure of codes 0, 3, 4 plus the 13 proofs contains no pair of code 1 or 2 and no
  pair with a certificate in the step 09 or step 11 files. Catches a bookkeeping error (wrong pair,
  wrong index) and a z3 claim contradicted by a checked counterexample. Cannot catch a wrong `unsat`
  on a pair nobody refuted.
- **ETP comparison**: all 15 `f`-free pairs among the 18 are "implies" in the ETP data. Independent of
  z3, but we did not re-check the ETP's proofs.
- **z3 asked again** (`--rerun`, fresh process): 6 of 13 repeated; with 30 s and a new pool, 4 more
  (152,491 164,203 497,142 507,136). Not repeated: 75,209 77,94 142,491 (all three `f`-free and
  "implies" in the ETP).
- **Hand arguments** for the 3 direct proofs with `f` (above). Leads only.
- **Mutation test** of the checker (`--selftest`), corrupted copies in memory: claim a pair the ETP
  refutes; claim a pair that has a certificate; swap the law texts of a proved pair; `proved_ms`
  without an `unsat`; claim a code-1 pair. 5 of 5 rejected, reasons printed and read.
- **Gates of `LOOP.md`**: law texts 712 ok; count MATCH; catalogue 335,177 refuted pairs; 335,177
  small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent (counts unchanged); `selftest_verifiers.py` ALL PASS; the two new commands ALL PASS.

## NOT verified

- None of the 18 implications is proved by anything other than z3 (and the ETP for 15 of them, whose
  proofs we did not re-check). 3 direct proofs were not repeated by z3.
- The hand arguments for the pairs with `f` were not machine-checked.
- `results/status_matrix.npz`, `README` counts of the stored table and `src/query.py` were not updated:
  the 18 pairs are still code 6 there. The z3 proof arrays needed by `export_status.py` are not in the
  repository.
- A mutation "claim an open pair whose closure contradicts a refutation of code 1 or 2" was planned
  but cannot be built: if B implies C and a structure refutes "A implies C", the same structure
  refutes "A implies B", so such an open pair cannot exist. Recorded so nobody looks for it again.
- The 30-second re-ask covered only the 7 pairs not repeated; no 30-second run on the 879 pairs with
  `unknown` (queue).
- The guess that many open pairs are "finite yes, infinite no" was not checked.

## Surprises, errors, dead ends

- z3 repeated only 6 of its 13 proofs when asked again in one process, but 4 more at once (0.05 s to
  1 s) in a fresh pool. Its success depends on what the process did before, not only on the time
  limit. Rule kept: proofs accumulate across runs; a missing proof is not evidence.
- The selftest's "closure contradicts a refutation" mutation found no example and crashed
  (`StopIteration`); the reason is the argument in "NOT verified", so the mutation was dropped.

## Next

Queue item 1, next piece: z3 at 30 s on the 879 pairs still `unknown` (same script, about an hour in
pieces), then structure searches of size 6 and 7, then the "finite yes, infinite no" analysis of the
most frequent sources (`f(x)*f(y) = x`, `f(x*y) = x` and similar).
