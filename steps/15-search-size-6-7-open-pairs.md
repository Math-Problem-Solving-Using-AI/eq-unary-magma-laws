# 15. Search for counterexample tables of size 6 and 7 on the open pairs

- Date: 2026-11-23
- Status label: nothing settled. 0 counterexamples found. For 395 pairs z3 says there is no counterexample
  of exactly 6 and none of exactly 7 elements (`z3-only`); for the other 477 it gave up at size 6 or 7.
- Commit(s): see `git log -- src/search_open_larger.py results/witnesses_open_6_7.json steps/15-search-size-6-7-open-pairs.md`

## In plain words

1. **The question.** 872 pairs of laws are still open: we do not know whether the first law forces the
   second. Earlier searches (steps 03 and 06) found no small counterexample table with 5 elements or
   fewer for them. Is there one with 6 or 7 elements?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a
     two-input operation `*` and a one-input operation `f`. It may be finite or infinite. A **table**
     writes down a finite structure: row `a`, column `b` holds `a*b`, and a separate list holds `f(a)`.
     The **size** of a table is its number of elements.
   - A **law** is an equation such as `f(x)*y = x` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding, infinite structures
     included.
   - A **counterexample** (or **witness**) for "A implies B" is a structure where A holds and B fails.
     One counterexample is enough to show that A does NOT imply B.
   - **z3** is an automatic solver. Asked "is there a table of exactly n elements where A holds and B
     fails?", it answers `sat` (yes, and it shows one), `unsat` (it claims there is none of that size) or
     `unknown` (it gave up when the time limit ran out).
   - **`z3-only`** labels an answer that rests on z3 alone, with nothing else checking it.
   - **Code 6** in the stored table `results/status_matrix.npz` means "open, nothing known yet".
   - **Positive control**: running the search on cases whose answer is already known, to make sure it
     can find something at all.

2. **What was done, in order.**
   1. Listed the open pairs: code 6 in the stored table, minus the 2 pairs with a certificate from
     step 11 and minus the 20 pairs z3 settled in steps 13 and 14 (computed with the checker of step 13).
     That gives the 872 pairs of `STATE.md`.
   2. Timed a few pairs first (10 seconds limit per size): z3 answers `unsat` at size 6 in 0 to 3
     seconds for most, but often gives up at size 7. So the whole job was estimated at about 25 minutes
     on 8 cores, small enough to do now.
   3. Wrote `src/search_open_larger.py`. For each pair it asks z3 for a table of size 6 and then size 7
     (10 seconds each), saves every 10 pairs and stops after about 500 seconds, so it ran in three pieces
     of under ten minutes, each continuing where the last stopped. Any table found would be re-checked
     by plain evaluation before being kept, and again by `src/verify_witnesses.py`.
   4. Result: 0 tables found. Size 6: 718 `unsat`, 154 `unknown`. Size 7: 395 `unsat`, 477 `unknown`.
   5. Positive control: the same search function on the 2 pairs that have a known 6-element certificate
     (step 11) found a 6-element table for both within 0.1 seconds, and both pass `verify_witnesses.py`.
     So the search can find tables of this size when they exist.
   6. Ran all gates of `LOOP.md` and `verify_witnesses.py` on the new file.

3. **A small example: why tables cannot settle many of these pairs.** Take A = `f(x)*y = x` and
   B = `f(x*x) = x` (an open pair; z3 says `unsat` at sizes 6 and 7, so no counterexample of those sizes).
   - The 3-element table with `f(a) = a+1 mod 3` (list `[1, 2, 0]`) and `a*b = a-1 mod 3` whatever `b`
     is (rows `[2, 2, 2]`, `[0, 0, 0]`, `[1, 1, 1]`) satisfies A: `f(x)*y = (x+1)-1 = x`. It also
     satisfies B: `x*x = x-1`, and `f(x-1) = x`. Checked with `findmodel.check_model`.
   - Why every finite table that satisfies A also satisfies B (a hand argument, a **lead**, not checked
     by machine): if `f(u) = f(v)` then `u = f(u)*u = f(v)*u = v`, so `f` never sends two elements to the
     same one. In a finite set such a map reaches every element. So every `x` is `f(u)` for some `u`, then
     `x*x = f(u)*x = u`, and `f(x*x) = f(u) = x`: B holds.
   - In an infinite structure this can fail. On the numbers 0, 1, 2, ... put `f(n) = n+1`, `n*y = n-1`
     when `n` is at least 1, and `0*y = 5`. Then A holds (`f(x)*y = (x+1)-1 = x`), but at `x = 0`,
     `f(0*0) = f(5) = 6`, not 0, so B fails. This is also a hand argument (a lead): a quick evaluation
     for x and y from 0 to 59 agreed, which is not a proof for all numbers. If it is right, A does NOT
     imply B, and no finite search can ever show it. This is what queue item "piece 4" is about.

4. **What it means and what it does NOT mean.**
   - It means: no counterexample table of size 6 or 7 was found for any of the 872 pairs. For 395 pairs,
     z3 claims there is none of size 6 and none of size 7 (`z3-only`, not checked otherwise).
   - It does NOT mean any of these implications holds. "Not found" is not "does not exist": a
     counterexample may have 8 or more elements, or be infinite (like the example above).
   - For the 477 pairs where z3 gave up at size 6 or 7, nothing at all is known about those sizes.
   - The table `results/status_matrix.npz` was not changed: the 872 pairs stay code 6.
   - Many open pairs have the pattern of the example (the source law forces `f` to be one-to-one, and in
     a finite set that makes it reach everything). For those, a larger finite search is a dead end, and
     infinite counterexamples are the way forward. That is a lead from the hand argument, not checked
     for each source law.

5. **How to re-check.**

   ```
   python src/verify_witnesses.py results/witnesses_open_6_7.json
   ```

   Expected: `0 certificates checked, 0 failed, 872 entries without a certificate`.

   To redo the search (three runs of at most about 8 minutes on 8 cores; each run continues the last;
   the third prints the totals):

   ```
   python src/search_open_larger.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json 10000 500 results/witnesses_open_6_7.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
   ```

   Expected at the end: `verified counterexamples: 0`, then `size 6: unsat 718, unknown 154` and
   `size 7: unsat 395, unknown 477` (z3 answers vary between runs, so these two lines can differ a little).
   To redo it from scratch, delete `results/witnesses_open_6_7.json` first or give another output name.

## Goal

Open-pairs item, piece 3: look for counterexample structures of size 6 and 7 for the 872 open pairs.

## Command(s)

```
python src/search_open_larger.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json 10000 500 results/witnesses_open_6_7.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json   # 3 times
python src/verify_witnesses.py results/witnesses_open_6_7.json
```

plus every gate of `LOOP.md`, an inline timing of 6 pairs before the run, an inline positive control
(`search_open_larger.task` on the 2 pairs of `results/witnesses_etp_magmas.json`), and an inline
`findmodel.check_model` call for the tables in the example.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json`, `results/z3_open_retry.json`,
`results/witnesses_ffree_models.json`, `results/witnesses_etp_magmas.json`. Python 3.12.10, z3 version
string `5.4.1`, 8 worker processes, Windows 10. Time limit 10,000 ms per size per pair.

## Output

- `results/witnesses_open_6_7.json`: one entry per open pair (872), format of
  `results/witnesses_larger_models.json`: `size` null (none found), `tried` = z3's answer at size 6 and 7,
  `timeout_ms` 10000.
- Runs: 410 pairs in 501 s, 306 in about 500 s, 156 in about 110 s.
- Size 6 / size 7: `unsat`/`unsat` 395 (391 with `f`, 4 without), `unsat`/`unknown` 323 (309 with `f`,
  14 without), `unknown`/`unknown` 154 (all with `f`). 0 `sat`.
- Pairs whose rows are `unsat`/`unsat` for every target include the sources `f(x)*y = x`, `x*f(y) = y`,
  `f(f(x))*y = x`, `x*f(f(y)) = y`, `f(x*x)*y = x`, `x*f(y*y) = y`. The sources with the most
  `unknown`/`unknown` are `f((x*y)*z) = z` (32), `f(x*(y*z)) = x` (33), `f((x*y)*z) = x` (25),
  `f(x*(y*z)) = z` (24).

## Checks done (and what each one can and cannot catch)

- **Plain re-check of found tables**: built in (`findmodel.check_model`) and `verify_witnesses.py`. Nothing
  was found, so they had nothing to check: `0 certificates checked, 0 failed, 872 entries without a
  certificate`. They would catch a wrong table from z3; they cannot catch a table z3 missed.
- **Positive control**: the search finds 6-element tables for both pairs of step 11 (0.1 s each; `verified`
  True; `verify_witnesses.check_entry` True). Catches a search that can never find anything (wrong law
  passed, wrong size). Cannot show that z3's `unsat` answers are right.
- **Open-pair list**: 872, equal to the count in `STATE.md` after step 14, computed from the stored table
  with the step 13 checker's own function (`check_z3_retry.check`).
- **Example**: the 3-element and the 2-element (left projection, `f` the identity) tables satisfy both
  laws of 32,35 (`findmodel.check_model`). The infinite structure was evaluated for x, y from 0 to 59 only.
- **Gates of `LOOP.md`**: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs;
  335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent (counts unchanged: 712, 335,177, 708, 15,877, 147,177, 6,399, 894); `selftest_verifiers.py`
  ALL PASS; `check_z3_retry.py` ALL PASS (16 proved, 4 by closure) and selftest ALL PASS.
- No new checker was written, so no new mutation test. `src/search_open_larger.py` is a search, not a
  checker; whatever it finds goes through the unchanged `verify_witnesses.py`.

## NOT verified

- z3's `unsat` answers at sizes 6 and 7 ("no table of that size") are `z3-only`: not re-run, not checked
  by an independent search. They are not stored as a claim anywhere else.
- The claim that steps 03 and 06 covered sizes 2 to 5 for all 872 pairs was taken from `STATE.md` and
  step 06, not re-checked in this step.
- The 477 pairs with `unknown` at size 6 or 7 were not retried with a longer time limit.
- Sizes 8 and more were not searched.
- The hand argument "finite implies B, infinite does not" for `f(x)*y = x` => `f(x*x) = x` is a lead only.
  The infinite structure has not been checked by any certificate checker. Whether the same pattern covers
  the other open pairs was not checked.
- `results/witnesses_open_6_7.json` is not in the gates or CI (it holds no certificate).

## Surprises, errors, dead ends

- Dead end: sizes 6 and 7 gave nothing. For whole rows (`f(x)*y = x`, `x*f(y) = y`, `f(f(x))*y = x`, ...)
  z3 even says no table of size 6 or 7 works for any target. The hand argument in the example explains
  why (a lead): those laws make `f` one-to-one, which in a finite table means every element is a value of
  `f`, and that forces the targets. A larger finite search will not help such pairs; infinite structures
  are needed.

## Next

Open-pairs item, piece 4: infinite counterexamples for the source laws that force `f` to be one-to-one
or onto, with a certificate format that plain code can check (as in the sibling repository
eq-laws-without-small-models, step 11 there). Start with `f(x)*y = x` and `x*f(y) = y` (31 open pairs each,
all `unsat` at sizes 6 and 7).
