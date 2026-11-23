# 14. z3 again, with a 30-second limit, on the open pairs it could not decide

- Date: 2026-11-23
- Status label: 3 more implications `z3-only` (all three without `f`, all three "implies" in the ETP data).
  With chaining, 20 open pairs are now "implies" (`z3-only`), 2 more than after step 13. Nothing for the
  other 872 open pairs (a timeout says nothing either way).
- Commit(s): see `git log -- results/z3_open_retry.json steps/14-z3-30s-open-pairs.md`

## In plain words

1. **The question.** After step 13, 874 pairs of laws were still open: we did not know whether the first
   law forces the second. In step 13 the solver z3 had 10 seconds per pair and found 13 proofs. Does it
   find more if it gets 30 seconds?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a
     two-input operation `*` and a one-input operation `f`. It may be finite or infinite. A
     **table** writes down a finite structure: row `a`, column `b` holds `a*b`.
   - A **law** is an equation such as `x*(x*(y*y)) = y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding, infinite structures
     included.
   - **z3** is an automatic solver. Asked "is there a structure where A holds and B fails?", it answers
     `unsat` (no: it claims a proof that A implies B), `sat` (yes, and it shows one) or `unknown` (it
     gave up when the time limit ran out).
   - **`z3-only`** labels an answer that rests on z3 alone. z3 does not hand over a proof we could
     check, so it is not called "proved".
   - **Code 6** in the stored table `results/status_matrix.npz` means "open, nothing known yet".
   - **Chaining** (transitive closure): if A implies C and C implies B, then A implies B.
   - The **ETP** (Equational Theories Project) settled every question of this kind for laws without
     `f`. We compare with its published answers (step 08) but did not re-check its proofs.

2. **What was done, in order.**
   1. Ran the program of step 13, `src/retry_open_z3.py`, with a 30,000 ms limit. It skips the 13 pairs
      already proved and asks z3 about the other 879. It saves every 10 pairs and stops after about
      500 seconds, so the job ran in seven pieces of under ten minutes, each continuing where the last
      one stopped (the run is longer than one tool call may take).
   2. Result over the 879 pairs: 3 `unsat`, 876 `unknown`, 0 `sat`.
   3. Ran the checker of step 13, `src/check_z3_retry.py`, unchanged. It chains the 16 proofs with the
      implications already in the table and checks that the result contradicts no counterexample and
      no ETP answer. It reports 16 proofs plus 4 pairs by chaining, 20 in all. One of the 3 new proofs
      (`(x*y)*(x*x) = y` implies `(x*x)*(y*x) = y`) had already been settled by chaining in step 13, so
      only 2 pairs are newly settled.
   4. Asked z3 again (`--rerun`, a fresh process, one pair after another) about all 16 proofs, to see
      whether it repeats them. See "Checks done".
   5. Ran all gates of `LOOP.md`.

3. **A small example.** One of the new pairs: A = `x*(x*(y*y)) = y`, B = `x*(y*(y*x)) = x`.
   z3 says A implies B, and the ETP agrees.
   - The 2-element table "right projection", `a*b = b` (rows `[0, 1]` and `[0, 1]`), satisfies both:
     every product is its last factor, so the left side of A is `y` and the left side of B is `x`.
   - The 3-element table `a*b = (-a - b) mod 3` (rows `[0, 2, 1]`, `[2, 1, 0]`, `[1, 0, 2]`) also
     satisfies both (checked with `findmodel.check_model`).
   - The 2-element table "left projection", `a*b = a`, breaks A: the left side is `x`, and `x = y`
     fails when `x` and `y` differ. A law that fails in a table says nothing about what it implies.
   - Such examples only illustrate. They do not show that A implies B: that is a claim about every
     structure, and only z3 (and the ETP) say so here.

4. **What it means and what it does NOT mean.**
   - It means: 2 more open pairs are "implies" with label `z3-only` (20 in all since step 13). All three
     new proofs are for laws without `f`, where the ETP already had the answer. So, for the pairs with
     `f`, nothing changed: **854 pairs with `f` are still open, with no answer at all.**
   - It does NOT mean these pairs are proved: z3 gives no proof we can check, and z3 did not repeat one
     of the 3 new proofs when asked again.
   - z3 found no counterexample (`sat`) for any of the 879 pairs. That does not mean the implications
     hold. A finite counterexample would also have shown up in the searches of steps 03 and 06 if it had
     5 elements or fewer, so any counterexample is larger, or infinite.
   - The "unknown" answers say nothing either way. Tripling the time gave 3 proofs, all for laws without
     `f`. That suggests (a lead, not checked) that more time is not the way to settle the pairs with `f`.
   - `results/status_matrix.npz` was not changed: it still says code 6 for the 20 pairs (as in step 13).

5. **How to re-check.**

   ```
   python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
   ```

   Expected: `pairs in file: 892, proved by z3: 16, settled in addition by the closure: 4`, the 20 pairs
   listed (16 with `ETP: implies`, 4 with `ETP: no data (has f)`), then `ALL PASS`. Add `--selftest` for
   the mutation test (5 lines `rejected`, then `selftest: ALL PASS`), or `--rerun` to ask z3 again (its
   answers vary between runs).

   To redo the search (seven runs of about 8 minutes on 8 cores; each run continues the last):

   ```
   python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 30000 500 results/z3_open_retry.json
   ```

## Goal

Second piece of the open-pairs item: z3 with 30 s on the 879 open pairs that were `unknown` at 10 s.

## Command(s)

```
python src/retry_open_z3.py data/laws_3.json results/status_matrix.npz results/witnesses_etp_magmas.json 30000 500 results/z3_open_retry.json   # 7 times
python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
python src/check_z3_retry.py ... --rerun
python src/check_z3_retry.py ... --selftest
```

plus every gate of `LOOP.md`, and an inline call of `findmodel.check_model` for the tables in the example.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/witnesses_etp_magmas.json`,
`results/etp_crosscheck.json`, `results/witnesses_ffree_models.json`, and `results/z3_open_retry.json` from
step 13. Python 3.12, z3 version string `5.4.1` (from `z3.get_version_string()`), 8 worker processes,
Windows 10.

## Output

- `results/z3_open_retry.json`: every one of the 879 pairs now also has its answer at 30,000 ms
  (`tries["30000"]`); `proved_ms: 30000` for the 3 new proofs. Nothing from step 13 was removed or changed.
- Runs: 129, 132, 129, 129, 129, 131 and 100 pairs (879), about 500 s each, 3,400 s in all.
- New direct proofs (law id minus 1, A => B): 239,209 `(x*y)*(x*x) = y => (x*x)*(y*x) = y`;
  497,564 `x*((x*y)*x) = y => x*(x*(y*x)) = y`; 567,603 `x*(x*(y*y)) = y => x*(y*(y*x)) = x`.
- Settled by chaining: 4 (75,594 202,33 202,466 497,136); 239,209 moved from "chaining" to "direct".
- Still open: 872 pairs from 62 source laws; 18 have no `f` and keep the ETP's answer (`known (ETP)`), 854
  involve `f` and have no answer.

## Checks done (and what each one can and cannot catch)

- **Consistency with the table and the ETP** (`check_z3_retry.py`, unchanged since step 13): ALL PASS.
  All 16 `f`-free pairs among the 20 are "implies" in the ETP data. Catches bookkeeping errors and a z3
  claim contradicted by a checked counterexample or by the ETP; cannot catch a wrong `unsat` on a pair
  nobody refuted and the ETP does not cover.
- **Mutation test** of that checker (`--selftest`): 5 of 5 corrupted copies rejected. The checker was not
  changed in this step.
- **z3 asked again** (`--rerun`, one process, pairs in sequence, each at the limit it was proved with):
  repeated 8 of 16 (152,85 152,491 164,203 202,490 239,594 239,209 507,136 567,603).
  Not repeated this time: 75,209 77,94 142,491 152,69 202,485 497,142 497,564 709,57. 202,485 and 709,57
  were repeated in step 13 and not now; this matches "z3 outcomes are not stable"
  (`docs/shared/LESSONS.md`). Of the new proofs, 497,564 was not repeated; the ETP says "implies" for it.
- **Example tables** checked with `findmodel.check_model`: right projection and `(-a - b) mod 3` satisfy
  both laws of 567,603; left projection fails both.
- **Gates of `LOOP.md`**: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs;
  335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent (counts unchanged: 712, 335,177, 708, 15,877, 147,177, 6,399, 894); `selftest_verifiers.py`
  ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS.

## NOT verified

- None of the 20 implications is proved by anything other than z3 (and the ETP for 16 of them, whose
  proofs we did not re-check). 8 of the 16 direct proofs were not repeated in this step's `--rerun`.
- No hand argument for the 3 new pairs (the ETP covers them).
- `results/status_matrix.npz`, the stored-table counts in `README.md` and `src/query.py` were not
  updated: the 20 pairs are still code 6 there (as in step 13; `query.py` reading the file is in
  "Optional later").
- The 876 `unknown` answers carry no information. In particular they were not read as "does not imply".
- The lead that more z3 time will not settle the pairs with `f` was not tested beyond 30 s.
- The `--rerun` count above was read from the printed lines by hand.

## Surprises, errors, dead ends

- Tripling the time limit gave only 3 proofs, all for laws without `f`, and 0 counterexamples. For the
  854 pairs with `f`, z3 at 10 s and at 30 s found nothing. Recorded so the next sessions try something
  else (larger structures, or infinite counterexamples) instead of more z3 time.
- z3 did not repeat two proofs with `f` (202,485 and 709,57) that it had repeated in step 13. Same lesson
  as before: keep proofs across runs, never read a missing proof as evidence.

## Next

Open-pairs item, piece 3: structure search of size 6 and 7 on the 872 open pairs (check time per pair
first), then piece 4: the "finite yes, infinite no" analysis of the most frequent source laws.
