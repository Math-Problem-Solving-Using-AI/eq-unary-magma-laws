# 29. Rows of laws 250 and 257: the last 5 pairs, each "implies" by a one-step derivation

- Date: 2026-11-23
- Status label: stored one-step derivations replayed by plain code (same level as steps 19, 27 and 28: `z3-only`
  level at most, no z3 used). Not Lean, not reviewed by a person. Agrees with the ETP, which lists all 5 as proved
  implications (`results/etp_crosscheck.json`).
- Commit(s): see `git log -- src/ffree_derivations.py src/selftest_ffree_laws.py results/derivations_ffree_laws.json steps/29-last-five-pairs-laws-250-257.md`

## In plain words

1. **The question.** Two of the nine laws with no small example, `(x*y)*(y*x) = y` (law 250) and `(x*y)*(y*z) = y`
   (law 257), have examples with 4 elements. Step 09 used those examples to show that 1,417 of the 1,422 other laws do
   NOT follow from them. The last 5 pairs were answered "implies" only by an outside project. Can this repository
   check those 5 itself?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a two-input operation
     `*` and a one-input operation `f`. A **magma** is the same thing without `f`.
   - A **law** is an equation such as `(x*y)*(y*z) = y` that must hold for every choice of the letters x, y, z.
   - Law A **implies** law B if every structure where A holds also has B holding (infinite structures count).
   - A **model** of A is a structure where A holds. A **certificate** (or witness) for "A does not imply B" is a
     finite model of A where B fails, given as tables.
   - A **derivation** is a chain of steps, each replacing a piece of an expression by an equal one according to law
     A. If it leads from B's left side to B's right side, B holds wherever A holds.
   - The **ETP** is the Equational Theories Project, an outside project that settled all implications between laws
     of magmas up to a certain size; step 08 compared our table with its data.
   - **Code 5** in `results/status_matrix.npz` means "A is one of the 9 laws with no model of size 2 or 3"; it is an
     open code. Law numbers here are the `id` in `data/laws_3.json`; the files use the index, which is id minus 1
     (law 250 is key 249).
   - **z3** is an automatic solver; **`z3-only`** labels an answer that rests on z3 with nothing else confirming it.
     This step does not use z3; the label only says a replayed derivation ranks no higher here.
   - A **mutation test** feeds a checker deliberately broken input to make sure it can say "no".

2. **What was done, in order.**
   1. **Listed the 5 pairs.** In the rows of laws 250 and 257, the laws with no step 09 certificate are: from 250,
      `(x*x)*(x*x) = x` (law 204); from 257, laws 204, `(x*x)*(x*y) = x` (206), `(x*y)*(y*x) = y` (250) and
      `(x*y)*(y*y) = y` (253). The ETP data lists all 5 as implications (step 08 file).
   2. **Noticed that each target is the source law itself with some letters made equal.** For example, putting z := x
      in `(x*y)*(y*z) = y` gives `(x*y)*(y*x) = y`. So each derivation is one step: replace B's left side by B's right
      side using A with that choice of letters. The choices were written by hand as data in `src/ffree_derivations.py`,
      which writes `results/derivations_ffree_laws.json` in the format of steps 19, 27 and 28. The script also asserts
      that these 5 are exactly the pairs of the two rows without a certificate. A second run gave a byte-identical file.
   3. **Replayed the 5 steps with the existing checker** `src/check_derivations.py` (unchanged). It checks A against
      the law's text, replays each step, checks the pair is open (code 5) and that the derived equation is B.
   4. **Wrote `src/selftest_ffree_laws.py`** for three more checks:
      - coverage: every pair of the two rows is answered exactly once, either by a step 09 certificate or by a
        derivation here (1,417 + 5 = 1,422, 0 gaps, 0 doubles);
      - control: every derived equation holds in the 4-element tables of the certificates (6 distinct tables, since
        the certificates differ in `f`). The checker's own control looks only at models with 2 or 3 elements, and these
        laws have none, so that control is empty;
      - mutation test: 10 broken copies (a changed letter choice, position or direction, an empty chain, a wrong source
        law, a pair pointing at the wrong equation, a pair with a certificate claimed as implied, the pair (A, A), one
        pair dropped, an unproved equation `x*y = x` added). All 10 rejected.
   5. Ran every gate of `LOOP.md` (35 commands, all pass) and added the two new commands to the gates, CI and README.
   6. Checked the finish line of `LOOP.md` (see "Finish line check" below): not reached yet, because steps 01 to 09 have
      no "In plain words" section.

3. **A small example.** Law 257 is `(x*y)*(y*z) = y`. One model of it has 4 elements 0, 1, 2, 3 and this table for `*`
   (row = left input, column = right input):

   ```
       | 0 1 2 3
     --+--------
     0 | 0 2 0 2
     1 | 0 2 0 2
     2 | 1 3 1 3
     3 | 1 3 1 3
   ```
   - Law 257 holds, for example at x = 0, y = 1, z = 3: `0*1 = 2`, `1*3 = 2`, `2*2 = 1`, which is y.
   - Target `(x*y)*(y*x) = y` (law 250) also holds, for example at x = 0, y = 1: `0*1 = 2`, `1*0 = 0`, `2*0 = 1` = y.
     It must, because it is law 257 with z replaced by x: that is the whole one-step derivation.
   - A law that does NOT follow, for contrast: `f(x) = x`. Take the same table with `f` sending everything to 0. Then
     `f(1) = 0`, not 1, so this structure obeys law 257 and breaks `f(x) = x`. That is one of the 1,417 certificates of
     step 09.

4. **What it means and what it does NOT mean.**
   - It means: all 1,422 pairs of the rows of laws 250 and 257 now have a machine check in this repository (1,417
     certificates checked by evaluation, 5 derivations replayed by plain code). With steps 27 and 28, the rows of all
     9 code 5 laws (6,399 pairs) have an answer with a check here, and since step 26 so do all pairs of code 6.
   - It does NOT mean: Lean-checked, or reviewed by a person. The checker is our own code, small and mutation-tested.
   - It does NOT change `results/status_matrix.npz`: these pairs still say code 5 there (published format, owner's
     decision, STATE.md "Blocked").
   - It does NOT mean the repository is finished: the finish line also asks for a plain-words section in every step
     file, and steps 01 to 09 do not have one yet.

5. **How to re-check it.** From the repository root:
   - `python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_ffree_laws.json`
     prints `2 of 2 sources checked (5 replacement steps replayed)`, `5 open pairs derived (implied)` and `ALL PASS`.
   - `python src/selftest_ffree_laws.py data/laws_3.json results/status_matrix.npz results/witnesses_ffree_models.json results/derivations_ffree_laws.json`
     prints `coverage: rows 250, 257: 1417 certificates + 5 derived pairs, 0 pairs answered not exactly once`,
     `control: every fact holds in all 6 distinct 4-element tables of the certificates, 0 failures`,
     `selftest: 10 of 10 corrupted inputs rejected` and `ALL PASS`.
   - To rebuild the file: `python src/ffree_derivations.py data/laws_3.json results/status_matrix.npz results/witnesses_ffree_models.json results/derivations_ffree_laws.json`
     prints `2 sources, 5 pairs written to ...`; the file comes out identical.

## Goal

Queue item 1 of `STATE.md`: give the 5 implications in the rows of laws 250 and 257 that rested on the ETP only a check
here, then check the finish line in `LOOP.md`.

## Command(s)

```
python src/ffree_derivations.py data/laws_3.json results/status_matrix.npz results/witnesses_ffree_models.json results/derivations_ffree_laws.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_ffree_laws.json
python src/selftest_ffree_laws.py data/laws_3.json results/status_matrix.npz results/witnesses_ffree_models.json results/derivations_ffree_laws.json
```
plus every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz` (unchanged; the 5 pairs have code 5), `results/witnesses_ffree_models.json`
(step 09, unchanged), `results/etp_crosscheck.json` (read to confirm the ETP's answer: ETP `explicit_proof_true` for
250 -> 204 and 257 -> 250, `implicit_proof_true` for 257 -> 204, 206, 253). No z3, no web.

## Output

- `results/derivations_ffree_laws.json`: 2 sources, 5 pairs, 5 replacement steps. Letter choices (source letters
  x, y, z written v0, v1, v2):
  - 250 -> 204 `(x*x)*(x*x) = x`: y := x.
  - 257 -> 204 `(x*x)*(x*x) = x`: y := x, z := x.
  - 257 -> 206 `(x*x)*(x*y) = x`: y := x, z := y.
  - 257 -> 250 `(x*y)*(y*x) = y`: z := x.
  - 257 -> 253 `(x*y)*(y*y) = y`: z := y.
- New: `src/ffree_derivations.py` (writes the file), `src/selftest_ffree_laws.py` (coverage, control, mutation test;
  gate and CI).
- `LOOP.md` gates, `.github/workflows/verify.yml` and the README command list: two new commands.

## Checks done (and what each one can and cannot catch)

- `check_derivations.py` (unchanged): replays the 5 steps, checks source text, codes and targets. Catches a wrong letter
  choice or target. Cannot catch a bug in the term functions it shares with the writer (`check_completion.py`,
  `check_laws_text.py`).
- Coverage check: catches a pair of the two rows left without an answer, or answered both ways.
- Control on the 4-element tables: every derived equation is evaluated on every assignment in a real model of A. Catches
  a wrong derived equation independently of the replay (it cannot show that an implication holds in every model).
- Mutation test 10 of 10 rejected.
- Agreement with the ETP on all 5 pairs.
- All 35 gates of `LOOP.md` pass.

## Finish line check (`LOOP.md`)

1. Every case has an answer: yes. Codes 1 and 2 (certificates), 3 and 4 (z3 proofs, `z3-only`), the 894 pairs of code 6
   (steps 08 to 26) and the 6,399 pairs of code 5 (steps 09, 27, 28, 29).
2. Every answer has a machine check: yes, at the labels stated (codes 3 and 4 are stored z3 results labelled `z3-only`;
   replacing them by derivations is "Optional later" item 1, a label raise).
3. Plain words: **no**. Steps 01 to 09 do not start with "In plain words" (checked with grep on 2026-11-23: steps 10 to 29
   have it, 01 to 09 do not). The README states the answers in its status table and step summaries, but has no short
   plain-words answer section.

So `finished` stays `no`. Two queue items added: plain-words sections for steps 01 to 09 (split in two), and a
plain-words answer section in the README; then check the finish line again.

## NOT verified

- No Lean, no person reviewed the 5 derivations; the only replay is our own checker.
- No independent second checker of our file.
- `results/status_matrix.npz` and `src/query.py` do not report these answers (published format, owner's decision).
- The ETP's own proofs of these 5 pairs were not read; only its outcome table (step 08) was compared.
- No literature check in this step (the implications are direct instances of the source law; no novelty is claimed).

## Surprises, errors, dead ends

- All 5 "ETP-only" implications were direct instances of the source law, one step each. They had stayed open since step
  09 because the nine laws were set aside as one bucket after the first z3 run (lessons "Skip work whose answer is
  already decided" and "Split a stuck bucket"), and the cheap syntactic check "is B an instance of A?" was not run on
  those rows. Lesson added to `docs/LOG.md`.
- Writing LOOP.md, README.md and the CI file with Python's `write_text` on Windows turned their line endings into CRLF;
  restored to LF before committing (the repository stores LF).

## Next

Queue: "In plain words" sections for steps 01 to 05, then 06 to 09; then a plain-words answer section in the README; then
check the finish line again.
