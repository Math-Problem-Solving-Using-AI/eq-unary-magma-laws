# 11. ETP multiplication tables, with every choice of `f`, against the open pairs

- Date: 2026-11-23
- Status label: 2 non-implications `model-verified` (pairs that were open in our table, code 6, and
  `known (ETP)` since step 08). For the other 892 open pairs: no counterexample in this source, which
  is not evidence either way.
- Commit(s): see `git log -- src/refute_from_etp_magmas.py results/witnesses_etp_magmas.json steps/11-etp-magmas-with-f.md`

## In plain words

1. **The question.** 894 pairs of laws are still open in our table: we do not know whether the first
   law forces the second. The Equational Theories Project (ETP, a large online project that settled
   all such questions for laws without `f`) publishes many small multiplication tables it found. Do
   any of those tables, with a suitable `f` added, settle some of our open pairs?

   Words used here:
   - A **structure** (also: magma with a unary operation) is a finite set of elements, a table for a
     two-input operation `*`, and a list for a one-input operation `f`. A **magma** is the same
     without `f`: just the `*` table.
   - A **law** is an equation such as `x*(y*y) = x*y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding.
   - A **witness** (certificate, counterexample) is one structure where A holds and B fails. It proves
     that A does NOT imply B.
   - **Code 6** in our stored table `results/status_matrix.npz` means "open, nothing known yet".
   - **`model-verified`**: a non-implication whose witness was re-checked by plain code that tries
     every choice of the letters.
   - **`known (ETP)`**: the ETP's data gives the answer; we did not re-check the ETP's proofs.

2. **What was done, in order.**
   1. Read the queue item. It proposed: for an open pair whose first law A has no `f`, take an ETP
      table that satisfies A and choose `f` so that B fails. Counting first showed that **no open pair
      has A without `f` and B with `f`**. All 35 open pairs with A free of `f` have B free of `f` too,
      and the ETP had already answered them (step 08: 18 "does not imply", 17 "implies").
   2. So the idea was widened in two ways that cost nothing:
      - For **all 894 open pairs**: take every distinct ETP table of size 4 (527 tables) and size 5
        (203 tables), add every possible `f` (256 or 3,125 choices), and look for a structure where A
        holds and B fails. Sizes 2 and 3 are not needed: step 03 already tried every structure of
        those sizes.
      - For the **35 pairs without `f`**, `f` plays no role. Every ETP table of every size (1,411
        tables, up to 65 elements) was tried with `f` = "do nothing".
   3. Every hit was re-checked on the spot by a second, plain evaluator, then by the independent
      verifier `src/verify_witnesses.py`.
   4. The first run found nothing at all, in 4 seconds. That looked too clean, so the search was
      tested before believing it (see "Checks done"): the evaluators agree, and pointed at rows where
      answers are known, the same search finds them.
   5. A bug was found and fixed on the way: the first test "does this law mention `f`?" looked only
      at the right side of the law. It was caught because the program crashed on the first law with
      `f` on the left side.

3. **A small example.** A = `(x*(x*y))*y = x`, B = `x*(y*y) = x*y`. The witness has 6 elements
   0 to 5 (`f` is not used by these laws; it is stored as "do nothing"):

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

   Law A holds: the verifier tries all 36 choices of `x` and `y`. One of them, `x = 0`, `y = 1`:
   `x*y = 2`, then `x*(x*y) = 0*2 = 3`, then `3*y = 3*1 = 0`, which is `x`.
   Law B fails at `x = 0`, `y = 1`: `y*y = 4` and `x*(y*y) = 0*4 = 5`, but `x*y = 2`.
   So A does not imply B. This table is in the ETP file `plan.txt`.

4. **What it means and what it does NOT mean.**
   - It means: 2 pairs that were open in our table now have our own checked witness. Both agree with
     the ETP's answer. Their label is `model-verified`.
   - It does NOT settle any pair that involves `f`. For those, no ETP table of size 4 or 5, with any
     `f`, gives a counterexample. That is **not** evidence that the implications hold: the ETP tables
     were collected for laws without `f`, so they are a narrow sample. "Not found" is not "does not
     exist".
   - 16 of the 18 "does not imply" answers that the ETP gives for our open `f`-free pairs still have no
     witness of ours. The ETP's own reasons for them are not in the table files we used.
   - `results/status_matrix.npz` was not changed (it still says code 6 for the 2 pairs). `query.py`
     does not read the new file yet (queue item).

5. **How to re-check.**

   ```
   python src/verify_witnesses.py results/witnesses_etp_magmas.json
   ```

   Expected: `2 certificates checked, 0 failed, 0 entries without a certificate`.

   To redo the search (needs a copy of the ETP repository, see "Inputs"):

   ```
   python src/refute_from_etp_magmas.py <ETP repository> results/witnesses_etp_magmas.json
   ```

   Expected last lines: `size 5: 203 tables x 3125 choices of f, certificates so far 0, ...`,
   `pairs without f: 35, tried against 1411 tables of every size, certificates so far 2, ...`,
   `certificates written: 2 -> results/witnesses_etp_magmas.json`.

## Goal

Use the ETP's published finite magmas, with every choice of `f`, as counterexample candidates for the
894 open (code 6) pairs.

## Command(s)

```
python src/refute_from_etp_magmas.py <ETP> results/witnesses_etp_magmas.json
python src/verify_witnesses.py results/witnesses_etp_magmas.json
python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_etp_magmas.json
python src/refute_from_etp_magmas.py <ETP> <scratch>/control_code5.json 5     # positive control
python src/verify_witnesses.py <scratch>/control_code5.json
```

plus all gates of `LOOP.md`.

## Inputs

ETP repository `teorth/equational_theories`, local clone at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), the same commit as step 08. Table files read
(a table is the first `[[...]]` on a line; only square tables with entries in range are kept):

| File | sha256 |
|------|--------|
| `equational_theories/Generated/All4x4Tables/data/cancellative-manual.txt` | `a0798d83270dc6e37ac3e7e559611d55573bca8b409ca5d7c1c4a9df4d41f4ea` |
| `.../extra.txt` | `4f0e2fde1739122301b360669dcb9df29705f5c7afca571b07e0be9cbab1a363` |
| `.../manual-11x11.txt` | `80355153000411a0af0694803516960d85baeb8ccf9f963545cbd66fe8baaadf` |
| `.../manual-13x13.txt` | `407e4189bad393210bba20d1466c58f53089901e6af90f5919b940c37cc5ac4e` |
| `.../manual-5x5.txt` | `6a150c0372598a770d36c276e60cac3f43408cb85e3848a9dc6795ad6e4522b6` |
| `.../plan.txt` | `6f95db79fccaa44677453d9b3ed154fdd11a5d894ef5a1f5c9bb9aa79af80dd5` |
| `.../refutations2x2.txt` | `8ad047243a9a6f200298bd590a2710a098faccfaaa858122b2688f3ceb92e445` |
| `.../refutations3x3.txt` | `b13e704ad6ac3a5e16fd72bdb643166465793c03c7d7fa533c17f26be4e89f62` |
| `.../refutations4x4.txt` | `4f556eb537df46f2e1e55619d53a4e551d77f935a33131dcb4fd33be6e5efd7b` |
| `.../vampire-generated.txt` | `a9a6f705fa2b61d6a2fdab1dac25a87cd85a0e3c7edee97c9a2f06ccfe655e97` |
| `.../z3-generated.txt` | `f66ee2d090785d2adb6ca5fa8b3fa89d97b438d0b6c12fad08d4126cf6d49e62` |
| `data/smallest_magma_examples.txt` | `071b3d97f6a0110ae8efb7822631d20cc03e55d9727db5302dc122eb7d188b01` |
| `data/small_magma_examples.txt` | not hashed (2 lines, the same 7-element table twice) |
| `data/interesting_finite_magmas/order5_magmas.txt` | `11dcc3af7e0327375150d7c2e281eb345515ef35aed2fec856f942d672280e93` |

Distinct tables by size: 2: 16, 3: 305, 4: 527, 5: 203, 6: 101, 7: 58, 8: 85, 9: 64, larger: 52
(1,411 in all). What these files are for in the ETP was read only from file names, the ETP README
("The smallest magma satisfying a given equation (up to N=5) ... and the magmas themselves") and the
first lines of `scripts/gather_small_magmas.py`. It does not matter for correctness: every table is
only a candidate, and every certificate is checked by our own code.

Also `data/laws_3.json`, `results/status_matrix.npz` (code 6 = open), `results/etp_crosscheck.json`
(to compare with the ETP's verdicts). Run time about 6 s.

## Output

`results/witnesses_etp_magmas.json`, 2 certificates, both of size 6, both from ETP `plan.txt`:

| Pair (ids) | A | B | ETP verdict (step 08) |
|------------|---|---|-----------------------|
| 145 => 652 | `(x*(x*y))*y = x` | `x*(y*y) = x*y` | `implicit_proof_false` |
| 501 => 230 | `x*((x*y)*y) = y` | `(x*x)*y = x*y` | `explicit_proof_false` |

(The keys in the file are ids minus 1: `144,651` and `500,229`.)

| Search | Pairs | Structures tried | Certificates |
|--------|-------|------------------|--------------|
| ETP tables of size 4, every `f` | 894 | 527 x 256 = 134,912 | 0 |
| ETP tables of size 5, every `f` | 894 | 203 x 3,125 = 634,375 | 0 |
| every ETP table, `f` = identity, pairs without `f` | 35 | 1,411 per pair | 2 |

All 71 source laws of the open pairs hold in at least one of the size-4 structures (for example
`f(x*x) = x` in 169 of them, `(x*(y*y))*y = x` in 2,816), and 39 of them in some size-5 structure. So
the search did reach structures where A holds; B held in all of them.

## Checks done (and what each one can and cannot catch)

- **Independent verifier:** `src/verify_witnesses.py` re-checked both certificates, 0 failed. It has
  its own parser and evaluator (no numpy, no code from `models.py` or `findmodel.py`).
- **Mutation test on the new file:** `selftest_verifiers.py ... results/witnesses_etp_magmas.json`
  ALL PASS: one flipped table entry broke 2 of 2 certificates, swapping A and B broke 2 of 2.
- **Positive control (could the search find anything at all?):** the same script pointed at the
  code-5 rows (`... 5`) found exactly 1,417 certificates, all accepted by the verifier, and their
  pairs are exactly the 1,417 pairs of step 09. Step 09 used tables from another repository; here the
  tables came from the ETP files. This catches a search that silently tries nothing.
- **Agreement with the ETP:** both certificates are for pairs the ETP calls "not an implication". None
  of the 17 ETP implications among the 35 pairs got a certificate (a certificate there would mean a
  bug on one side).
- **Two evaluators inside the script:** the fast evaluators (vectorized `sat_set` from `models.py`,
  and a new broadcasting one for single tables) must agree with the plain `check_model` on every hit,
  or the script stops. Separately, on 3,000 random (table, law) pairs (tables up to 9 elements, laws
  without `f`) the broadcasting evaluator and `check_model` agreed every time (66 of the 3,000 held).
- **Gates of `LOOP.md`:** law texts 712 ok; law count MATCH; catalogue regenerated (335,177 refuted
  pairs); 335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed;
  status table consistent (counts unchanged); `selftest_verifiers.py` ALL PASS.
- What these checks cannot catch: an open pair that has a counterexample among these tables but was
  missed because both fast evaluators share a bug that hides it (the 0-found result is backed by the
  positive control and the random agreement test, not by a second full search).

## NOT verified

- That the 892 other open pairs have no counterexample of size 4 or 5. Only ETP tables were tried,
  not all tables of those sizes (there are 4^16 tables of size 4).
- ETP tables of size 6 and more with a non-trivial `f`, for pairs that involve `f` (6^6 = 46,656
  choices of `f` per table; not tried).
- The ETP's reasons for the other 16 "does not imply" answers among the 35 `f`-free pairs, and the 17
  "implies" answers: still `known (ETP)` only, with no check of ours that the gates re-run.
- What the ETP files were made for (read only from names and two short texts, see "Inputs").
- `results/status_matrix.npz` not regenerated (the z3 arrays it is built from are not in the
  repository, and a new code is an owner decision); `query.py` does not read the new file yet.
- CI was not run here (the owner pushes); the new CI line was run locally only.

## Surprises, errors, dead ends

- **The queue item, read literally, had no work in it.** No open pair has A without `f` and B with
  `f`. Counting before building saved a script that would have found nothing. Rule recorded in
  `docs/LOG.md`: count the cases an idea applies to before writing code for it.
- **Bug: "does this law mention `f`?" looked at one side only.** A law is stored as a pair (left,
  right); the helper walked it like a term and skipped the left side. The crash it caused showed it;
  the fixed helper gives 408 laws without `f`, the known count.
- **A clean, fast "nothing found" was not trusted until a positive control found the known answers.**

## Next

- Queue: `query.py` reads `results/witnesses_etp_magmas.json` (same pattern as step 10).
- Queue item 1 (z3 with longer timeouts, larger searches, hand analysis) for the 892 open pairs.
