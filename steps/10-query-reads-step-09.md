# 10. `query.py` reads the certificates of step 09

- Date: 2026-11-23
- Status label: no new mathematical claim. The 1,417 certificates keep their label `model-verified`
  (step 09). This step only changes how the lookup tool reports them.
- Commit(s): see `git log -- src/query.py steps/10-query-reads-step-09.md`

## In plain words

1. **The question.** Step 09 found 1,417 answers of the form "law A does not imply law B". The
   lookup tool `src/query.py` did not know about them and still said "open" for those pairs. Can a
   reader who asks the tool about such a pair get the right answer, without changing the stored
   table that other people may already use?

   Words used here:
   - A **magma with a unary operation** (here just "structure") is a finite set of elements with a
     table for a two-input operation `*` and a list for a one-input operation `f`.
   - A **law** is an equation such as `f(x) = x` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding.
   - A **witness** (or certificate, or counterexample) is one structure where A holds and B does not.
     It proves that A does not imply B.
   - **Code 5** in the stored table `results/status_matrix.npz` means "open: A is one of 9 hard laws".
   - **`model-verified`** is the label for a non-implication whose witness was re-checked by plain
     code that tries every choice of the letters.

2. **What was done, in order.**
   1. Read the open queue item. It offered two ways: (a) teach `query.py` to read the step 09 file,
      or (b) add new codes to the stored table. Option (b) changes a published file format, which
      needs the owner. Option (a) changes no format, so the loop took (a) (recorded in `docs/LOG.md`
      under "Decisions taken by the loop").
   2. Checked that the file's entries line up with the law list: for all 1,417 entries, the law
      texts stored in the entry equal the texts of the laws at the positions named by its key
      (0 mismatches), and all 1,417 pairs are code 5 in the table.
   3. Changed `src/query.py`: when a pair is code 5, it looks for the pair in
      `results/witnesses_ffree_models.json`. Before reporting anything, it checks that the law texts
      match and re-checks the witness with the independent verifier's code
      (`check_entry` from `src/verify_witnesses.py`). Only if both pass does it print
      "NOT an implication ... model-verified". `--witness` prints the structure. `--list` prints how
      many code-5 targets of a law have such a witness.
   4. Tested that the tool rejects broken witnesses (a mutation test, see below).
   5. Ran all the gates of `LOOP.md` and added one query of this kind to CI.

3. **A small example.** A = `(x*y)*(y*x) = y`, B = `f(x) = x`. The witness has 4 elements 0, 1, 2, 3:

   ```
   *  | 0 1 2 3          f(0)=0  f(1)=0  f(2)=0  f(3)=0
   ---+--------
   0  | 1 2 2 3
   1  | 3 0 0 0
   2  | 1 2 2 1
   3  | 1 3 0 3
   ```

   Law A holds here: the verifier tries all 16 choices of `x` and `y`. Law B fails: `f(1) = 0`, not 1.
   So A does not imply B. Before this step the tool said "open" for this pair. Now it says
   "NOT an implication", gives the label `model-verified`, and prints this table.

4. **What it means and what it does NOT mean.**
   - It means: asking `query.py` about any of the 1,417 pairs of step 09 now gives the answer
     "does not imply", backed by a witness that was re-checked at the moment of asking.
   - It does NOT change `results/status_matrix.npz`. That file still says code 5 for these pairs, and
     the tool says so too. The counts in the README status table are unchanged.
   - It adds no new answer. The 1,417 answers were already found and checked in step 09.
   - The 5 other pairs in these two rows are implications known only from the Equational Theories
     Project (ETP) data. The tool already printed that (step 08). We did not re-check the ETP proofs.

5. **How to re-check.**

   ```
   python src/query.py "(x*y)*(y*x) = y" "f(x) = x" --witness
   ```

   Expected: `code 5: OPEN ...`, then a line starting `Step 09: NOT an implication.` with label
   `model-verified`, then `structure satisfying A and failing B: {"mul": [[1, 2, 2, 3], ...], "f": [0, 0, 0, 0]}`.

   ```
   python src/query.py --list "(x*y)*(y*z) = y"
   ```

   Expected last line: `Step 09: 707 of the open (code 5) targets above have a 4-element certificate ...`.

## Goal

Make the lookup tool report the 1,417 certificates of step 09 without changing the stored table
format.

## Command(s)

```
python src/query.py "(x*y)*(y*x) = y" "f(x) = x" --witness
python src/query.py "(x*y)*(y*z) = y" "(x*x)*(x*y) = x"
python src/query.py --list "(x*y)*(y*z) = y"
python src/query.py "x*y = x" "x*(y*z) = x"
```

plus all gates of `LOOP.md` and the in-process mutation test described below.

## Inputs

`results/witnesses_ffree_models.json` (step 09), `results/status_matrix.npz` (unchanged),
`data/laws_3.json`.

## Output

Changed `src/query.py` and one new CI line. No result file changed.

## Checks done (and what each one can and cannot catch)

- **Coverage:** all 1,417 entries are accepted by the new code path (1,417 of 1,417).
- **Mutation test of the new code path** (run in-process on modified copies, files untouched):
  - one `*` table entry changed in every witness: 0 of 1,417 accepted;
  - A and B texts swapped: 0 of 1,417 accepted;
  - keys shifted by one column (each witness attached to the wrong target): 0 of 1,415 accepted (the 2 entries with target 712 have no shifted partner);
  - `f` replaced by the identity: 1,397 accepted. This mutation does not have to break a witness
    (B can fail for many choices of `f`). A second, separate evaluator (`check_model` in
    `src/findmodel.py`) agreed with the tool on all 1,417 mutated entries (0 disagreements), so the
    1,397 accepted are genuinely valid and the 20 rejected genuinely invalid.
- **Gates of `LOOP.md`:** law texts 712 ok; law count MATCH; catalogue regenerated (335,177 refuted
  pairs); 335,177 small refutations re-verified, 0 failed; 708 and 1,417 certificates, 0 failed;
  status table consistent (counts unchanged); `selftest_verifiers.py` ALL PASS.
- **Other answers unchanged:** for a code-3 pair, an ETP code-5 implication and a code-1 pair, the old and the new `query.py` print byte-identical output.
- What these checks cannot catch: an error shared by the verifier's parser and the law list
  (both were checked in earlier steps by round trip and recount, not again here).

## NOT verified

- The stored table `results/status_matrix.npz` was not regenerated; it still says code 5 for these
  pairs. Adding a code for them is an owner decision (published format).
- `--list` counts the certificates but does not move those targets out of the "open" group in its
  listing.
- The 5 implications in these two rows rest on ETP data that we did not re-check (step 08).
- CI was not run here (the owner pushes); the new CI line was run locally only.

## Surprises, errors, dead ends

- The first mutation idea ("set `f` to identity") does not always break a witness. A mutation test
  must use changes that are sure to break the claim, or compare against a second evaluator. Here both
  were done.

## Next

Queue item 0b in `STATE.md`: ETP finite magmas plus a chosen `f` for code-6 pairs whose source law has
no `f`.
