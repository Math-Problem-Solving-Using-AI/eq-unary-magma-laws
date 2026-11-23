# 30. The answer in plain words, and a count of every answer by kind of check

- Date: 2026-11-23
- Status label: bookkeeping only. The count is checked by plain code (`src/tally_answers.py`, mutation test 6 of 6).
  It adds no answer and raises no label: each answer keeps the label of the step that gave it.
- Commit(s): see `git log -- src/tally_answers.py README.md steps/30-plain-words-answer.md`

## In plain words

1. **The question.** Steps 01 to 29 gave every pair of laws an answer, but the answers are spread over one stored
   table and 15 result files. How many pairs are "implies", how many "does not imply", and with which kind of check?
   And can the README say that in words a non-mathematician can follow?

   Words used here:
   - A **structure** is a set with a two-input operation `*` and a one-input operation `f`. A **law** is an equation
     that must hold for every choice of its letters. Law A **implies** law B when B holds in every structure where A
     holds. A **pair** is an ordered pair (A, B) of different laws: 712 x 711 = 506,232 pairs.
   - The **stored table** is `results/status_matrix.npz`: one code per pair. Codes 1 and 2 mean "does not imply"
     with a small counterexample table; codes 3 and 4 mean "implies" by z3; code 5 (the 9 laws without small
     examples) and code 6 ("unresolved") mean the table itself leaves the pair open.
   - **z3** is a solver program that searches for proofs and counterexamples. The label **`z3-only`** means we trust
     z3 (or a check of about that strength); **`model-verified`** means a counterexample table was re-checked by plain
     code that tries every choice of the letters (`docs/shared/VERIFICATION_PROTOCOL.md`).
   - A **mutation test** damages the input on purpose and checks that the checker then complains.

2. **What was done, in order.**
   1. Wrote `src/tally_answers.py`. It reads the stored table and the result files of steps 09 to 29, and for every
      pair with code 5 or 6 collects all the answers the files give. It checks that each such pair gets at least one
      answer, that answers never disagree, that no file answers a pair the table already decides, and that the law
      texts stored with an answer match `data/laws_3.json`. For steps 13 and 14 it reuses the closure of
      `src/check_z3_retry.py`, so the 20 "implies" found by chaining are counted the same way as there. Needed
      because adding up the numbers of 20 steps by hand is easy to get wrong.
   2. Gave it a mutation test (`--selftest`): drop a certificate, drop a pair of step 26, answer one pair both ways,
      answer a pair the table already decides, swap the law texts of a derivation, mark a decided pair as open in
      the table. All 6 are rejected.
   3. Added both commands to the gates in `LOOP.md`, to the checks in the README and to CI.
   4. Wrote the section "The answer in plain words" at the top of the README, using the counts the script prints.
   5. Checked the finish line of `LOOP.md` (see "Output").

3. **A small example.** A = `x*y = x`, B = `x*y = y`. On the 2 elements {0, 1} let `x*y = x` and `f(x) = 0`. A holds
   by definition. B fails because `0*1 = 0`, not 1. So A does not imply B; it is one of the 337,304 pairs with a
   small counterexample. `python src/query.py "x*y = x" "x*y = y" --witness` prints this table as
   `{"size": 2, "mul": [[0, 0], [1, 1]], "f": [0, 0]}` with code 1 and label `model-verified`.

4. **What it means and what it does NOT mean.**
   - It means: the answers of all steps fit together. Every one of the 506,232 pairs has exactly one verdict, and the
     counts in the README come from code, not from hand addition. The script found no pair answered by two files.
   - It does NOT re-check any counterexample or derivation. The other gates do that, file by file.
   - It does NOT raise any label. 163,074 "implies" are still `z3-only`, and 3,662 "does not imply" rest on
     infinite structures checked at the `z3-only` level. Nothing is Lean-checked.
   - `src/query.py` still says "open" for the 5,874 pairs answered in steps 13 to 29: it reads only the stored table
     and steps 08 to 12.

5. **How to re-check.**

   ```
   python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results
   python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results --selftest
   ```

   The first ends with `total: 506,232 ordered pairs of different laws (712 x 711 = 506,232)` and `tally: OK`; the
   second with `selftest: ALL PASS`.

## Goal

Give the README a short plain-words answer for every kind of pair, with counts taken from code, and check the finish
line of `LOOP.md`.

## Command(s)

```
python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results
python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results --selftest
```

plus all gates of `LOOP.md` (37 commands, about 3 minutes).

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json` (used only through the closure of
`src/check_z3_retry.py`), and 15 result files: `witnesses_ffree_models.json`, `witnesses_etp_magmas.json`,
`z3_open_retry.json`, `refutations_term_rewriting.json`, `refutations_nine_laws.json`, `completions_open.json`,
`completions_new_symbols.json`, `derivations_open.json`, `derivations_nine_laws.json`,
`derivations_collapse_laws.json`, `derivations_ffree_laws.json`, `greedy_eq73.json`, `greedy_eq118.json`,
`asterix_eq65.json`, `label_extension_277.json`. Python with numpy.

## Output

```
implies: 165,266
    163,074  z3 proof (z3-only)
      2,192  derivation or completion replayed by plain code (z3-only level at most)
does not imply: 340,966
    337,304  finite counterexample re-checked by plain code (model-verified)
      3,662  infinite counterexample, z3-only level (parts rest on z3, or on ETP Lean proofs read, not re-run)
total: 506,232 ordered pairs of different laws (712 x 711 = 506,232)
tally: OK
```

These match the hand sum of the step records: 335,885 + 1,417 + 2 = 337,304; 2,828 + 682 + 132 + 10 + 4 + 2 + 4 =
3,662; 147,177 + 15,877 + 20 = 163,074; 1 + 32 + 4 + 1 + 16 + 2,133 + 5 = 2,192.

Finish line of `LOOP.md`: (1) every case has an answer: yes, the tally covers all 506,232 pairs; (2) every answer has
a machine check that the gates re-run: yes, 37 of 37 gates pass; (3) the README states the answer in plain words and
every step file starts with "In plain words": yes, checked by listing the first `## ` heading of steps 01 to 30.
So `STATE.md` now says `finished: yes`.

## Checks done (and what each one can and cannot catch)

- `src/tally_answers.py`: catches an open pair with no answer, two files that disagree, a file that answers a decided
  pair, and law texts that do not match. It cannot catch a wrong certificate or derivation; the per-file gates do.
- Mutation test, 6 of 6 rejected: shows each of those checks can fail.
- All 37 gates of `LOOP.md` re-run: 0 failures.
- The README example re-run with `src/query.py` (code 1, `model-verified`, same table).

## NOT verified

- No certificate, derivation or z3 answer was re-checked by this step beyond what the gates already do.
- The pairs of `results/z3_open_retry.json` are taken from the closure in `src/check_z3_retry.py`; the tally does not
  compute that closure itself.
- Which pairs counted as "infinite counterexample" rest on z3 and which on ETP Lean proofs is not split in the count.
- The plain-words text was not read by a non-mathematician.
- Nothing is Lean-checked; no label went up.

## Surprises, errors, dead ends

- None in the count: it matched the hand sum on the first run, and no pair is answered by two files.
- The README's earlier header line "Look up any pair" with `src/query.py` could mislead: for 5,874 answered pairs the
  tool still says "open". The new section says so.

## Next

Finished by the finish line of `LOOP.md`. Everything left is in "Optional later" in `STATE.md`, for the owner.
