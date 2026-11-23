# 12. `query.py` reads the certificates of step 11

- Date: 2026-11-23
- Status label: no new mathematical claim. The 2 certificates of step 11 keep their label
  `model-verified`. This step only changes how the lookup tool reports them.
- Commit(s): see `git log -- src/query.py steps/12-query-reads-step-11.md`

## In plain words

1. **The question.** Step 11 found 2 answers of the form "law A does not imply law B" for pairs that
   our stored table still calls "open". The lookup tool `src/query.py` did not know about them. Can a
   reader who asks the tool about one of those 2 pairs get the right answer, without changing the
   stored table?

   Words used here:
   - A **structure** (also: magma with a unary operation) is a finite set of elements with a table for
     a two-input operation `*` and a list for a one-input operation `f`.
   - A **law** is an equation such as `x*(y*y) = x*y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding.
   - A **witness** (or certificate, or counterexample) is one structure where A holds and B does not.
     It proves that A does not imply B.
   - **Code 6** in the stored table `results/status_matrix.npz` means "open, nothing known yet".
     **Code 5** means "open: A is one of 9 hard laws".
   - **`model-verified`** is the label for a non-implication whose witness was re-checked by plain
     code that tries every choice of the letters.
   - A **mutation test** feeds a checker deliberately broken input to make sure it says "no".

2. **What was done, in order.**
   1. Read the queue item: same job as step 10, for the file of step 11
      (`results/witnesses_etp_magmas.json`). It changes no published file format, so no owner decision
      was needed.
   2. Saved the tool's output for 7 pair questions and 2 `--list` questions before changing anything,
      to compare afterwards.
   3. Changed `src/query.py`: the code that read only the step 09 file became one small table
      `CERTIFICATE_FILES` that says "for code 5 look in the step 09 file, for code 6 look in the step 11
      file". The rest is the step 10 logic, unchanged: the law texts in the entry must match the law
      list, and the witness is re-checked with the independent verifier's code (`check_entry` from
      `src/verify_witnesses.py`) before anything is printed. `--list` now also counts code-6 targets
      that have a step 11 witness.
   4. Compared the new output with the saved one, ran a mutation test, ran all gates of `LOOP.md`, and
      added one query of this kind to CI.

3. **A small example.** A = `(x*(x*y))*y = x`, B = `x*(y*y) = x*y`. The witness from step 11 has 6
   elements 0 to 5 (`f` is not used by these laws; it is stored as "do nothing"):

   ```
   *  | 0 1 2 3 4 5
   ---+------------
   0  | 0 2 3 5 5 2
   1  | 4 4 4 4 4 4
   2  | 5 3 2 0 0 3
   3  | 2 0 5 3 3 0
   4  | 1 1 1 1 1 1
   5  | 3 5 0 2 2 5
   ```

   Law B fails at `x = 0`, `y = 1`: `y*y = 1*1 = 4` and `x*(y*y) = 0*4 = 5`, but `x*y = 0*1 = 2`.
   Law A holds for all 36 choices of `x` and `y` (the tool re-checks this each time it is asked).
   Before this step the tool said only "code 6: OPEN" and the ETP's opinion. Now it adds a line
   "Step 11: NOT an implication ... Label: model-verified" and, with `--witness`, prints this table.

4. **What it means and what it does NOT mean.**
   - It means: asking `query.py` about either of the 2 pairs of step 11 now gives the answer "does not
     imply", backed by a witness that is re-checked at the moment of asking.
   - It does NOT change `results/status_matrix.npz`. That file still says code 6 for the 2 pairs, and
     the tool says so too. The counts in the README status table are unchanged.
   - It adds no new answer and settles nothing new. The other 892 open pairs stay open.
   - All other answers of the tool are unchanged: 6 of the 9 saved outputs are byte-identical, and the
     3 that changed (the 2 step 11 pairs and one `--list`) only gained the new lines.

5. **How to re-check.**

   ```
   python src/query.py "(x*(x*y))*y = x" "x*(y*y) = x*y" --witness
   ```

   Expected: `code 6: OPEN: unresolved`, the ETP line, then a line starting
   `Step 11: NOT an implication. A structure with 6 elements satisfies A and fails B`, then
   `structure satisfying A and failing B: {"mul": [[0, 2, 3, 5, 5, 2], ...], "f": [0, 1, 2, 3, 4, 5]}`.

   ```
   python src/query.py --list "(x*(x*y))*y = x"
   ```

   Expected last line: `Step 11: 1 of the open (code 6) targets above have a 6-element certificate in results/witnesses_etp_magmas.json (model-verified). Ask about one pair to see it.`

## Goal

Make the lookup tool report the 2 certificates of step 11 without changing the stored table format.

## Command(s)

```
python src/query.py "(x*(x*y))*y = x" "x*(y*y) = x*y" --witness
python src/query.py "x*((x*y)*y) = y" "(x*x)*y = x*y" --witness
python src/query.py --list "(x*(x*y))*y = x"
python src/query.py --list "(x*y)*(y*z) = y"
python src/query.py "(x*y)*(y*x) = y" "f(x) = x" --witness
python src/query.py "(x*y)*(y*z) = y" "(x*x)*(x*y) = x"
python src/query.py "x*y = x" "x*(y*z) = x"
python src/query.py "f(x)*f(y) = x" "f(x) = x"
python src/query.py "x*y = x" "f(x) = x" --witness
```

each run before and after the change, plus all gates of `LOOP.md` and the in-process mutation test
below.

## Inputs

`results/witnesses_etp_magmas.json` (step 11), `results/witnesses_ffree_models.json` (step 09),
`results/status_matrix.npz` (unchanged), `data/laws_3.json`.

## Output

Changed `src/query.py` and one new CI line in `.github/workflows/verify.yml`. No result file changed.

## Checks done (and what each one can and cannot catch)

- **Before/after comparison:** of the 9 saved outputs, 6 are byte-identical (a code-3 pair, a step 09
  certificate pair with `--witness`, a code-5 pair that the ETP calls an implication, a code-1 pair with
  `f`, a code-1 pair with `--witness`, and `--list "(x*y)*(y*z) = y"` with its step 09 count). The 2 step 11 pair questions and `--list "(x*(x*y))*y = x"` only gained
  the new lines. Catches a change to answers that should not move.
- **Coverage:** both step 11 entries and all 1,417 step 09 entries are accepted by the new code path,
  and every key is code 6 (respectively code 5) in the table.
- **Mutation test of the new code path** (in-process, on modified copies; files untouched), for each of
  the two files:
  - one `*` table entry changed: 0 of 2 (step 11) and 0 of 1,417 (step 09) accepted;
  - every table row reversed: 0 of 2 and 0 of 1,417 accepted;
  - A and B texts swapped: 0 of 2 and 0 of 1,417 accepted;
  - entry stored under the transposed key (B, A): 0 of 2 and 0 of 1,417 accepted.
  The first two reach the re-check by `check_entry` (the texts still match); the last two are caught by
  the text comparison.
- **Gates of `LOOP.md`:** law texts 712 ok, 0 mismatches; law count MATCH; catalogue regenerated
  (335,177 refuted pairs); 335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2
  certificates, 0 failed; status table consistent (counts unchanged: code 6 is still 894);
  `selftest_verifiers.py` ALL PASS.
- What these checks cannot catch: an error shared by the verifier's parser and the law list (checked
  in earlier steps by round trip and recount, not again here).

## NOT verified

- The stored table `results/status_matrix.npz` was not regenerated; it still says code 6 for the 2
  pairs. Adding a code for them is an owner decision (published format, `STATE.md`, Blocked).
- `--list` counts the certificates but still lists those targets in the "open" group.
- The "one `*` entry changed" mutation is not guaranteed to break a witness in general; here it broke
  all of them, which was checked by the verifier, not assumed.
- CI was not run here (the owner pushes); the new CI line was run locally only.

## Surprises, errors, dead ends

- A first scripted edit of `query.py` silently skipped one replacement (the `--list` block) because
  of an escaped newline in the search text; `grep` for the old function name showed it, and the block
  was changed by hand. Rule kept: after a scripted edit, search for the old names.

## Next

Queue item 1 in `STATE.md`: the 894 open pairs (longer z3 runs with saved state, larger structure
searches).
