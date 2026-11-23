# 09. Settle the rows of the two `f`-free laws that have 4-element models

- Date: 2026-11-22
- Status label: 1,417 non-implications `model-verified` (608 of them involve `f` and were open
  before; the other 809 had just been settled by the ETP in step 08 and now also have our own
  certificate). The 5 remaining pairs are implications, `known (ETP)`.
- Commit(s): see `git log -- steps/09-ffree-models-with-f.md`

## In plain words

1. **The question.** Two laws, `(x*y)*(y*x) = y` (law 250) and `(x*y)*(y*z) = y` (law 257), hold in no table with 2 or
   3 elements but do hold in a table with 4 elements. Their whole rows were still "open" in our table. Can those
   4-element tables answer the targets that use `f`?

   Words used here:
   - A **structure** is a set of elements with a table for a two-input operation `*` and a list for a one-input
     operation `f`.
   - A **law** is an equation that must hold for every choice of the letters. Law A **implies** law B if every
     structure where A holds also has B holding.
   - A **model** of a law is a structure where the law holds.
   - A **certificate** (or witness, counterexample) is one structure where A holds and B fails. It shows that A does
     not imply B.
   - A **row** of a law A is the list of all pairs (A, B) for the 711 other laws B.
   - The **ETP** is the Equational Theories Project, an outside project that decided all pairs of laws without `f`
     (step 08). The label **`known (ETP)`** means the answer comes from its published data and was not re-checked by us.
   - The label **`model-verified`** means: the certificate was re-checked by plain code that tries every choice of the
     letters.

2. **What was done, in order.**
   1. Noticed the key point: laws 250 and 257 do not mention `f`, so they hold in a table whatever `f` is. So the same
      `*` table can be paired with any of the 4 x 4 x 4 x 4 = 256 choices of `f`.
   2. Took the two 4-element tables from the sibling repository `eq-laws-without-small-models`, and had the script
      confirm that each satisfies its law.
   3. For each of the 711 targets B of each law, tried all 256 choices of `f` and kept the first structure where B
      fails. This took under 1 second.
   4. Stored the 1,417 certificates found in `results/witnesses_ffree_models.json` and re-checked them with the
      separate checker `src/verify_witnesses.py`, plus a mutation test (damage the input on purpose, check that the
      checker then fails).
   5. Compared with the ETP: no certificate contradicts an ETP "implies", and the 5 targets left without a certificate
      are exactly 5 pairs the ETP proves to be implications.

3. **A small example.** A = `(x*y)*(y*z) = y` (called the central groupoid law in the literature, step 08), B =
   `f(x) = x`. The `*` table on {0, 1, 2, 3} is

   ```
   *  | 0 1 2 3
   ---+--------
   0  | 0 2 0 2
   1  | 0 2 0 2
   2  | 1 3 1 3
   3  | 1 3 1 3
   ```

   A way to see why A holds: write each element as two bits, 0 = (0,0), 1 = (1,0), 2 = (0,1), 3 = (1,1). Then `x*y`
   is (second bit of x, first bit of y). So `(x*y)*(y*z)` is (second bit of `x*y`, first bit of `y*z`) = (first bit
   of y, second bit of y) = y. The checker also tries all 64 choices of x, y, z. Now take `f` with value 0 everywhere.
   B fails: `f(1) = 0`, not 1. So A does not imply B.

4. **What it means and what it does NOT mean.**
   - It means: 1,417 pairs are "does not imply", `model-verified`. 608 of them use `f` and were open before; the other
     809 were already answered by the ETP in step 08 and now also have our own certificate.
   - It does NOT mean that the 5 leftover pairs were proved here: at this step they rested only on the ETP data
     (`known (ETP)`). Step 29 later stored a short chain of steps for each, replayed by our own checker.
   - The stored table `results/status_matrix.npz` was not changed: it still says "open" (code 5) for these rows.
     `src/query.py` reports the certificates since step 10.

5. **How to re-check.** From the repository root:
   - `python src/verify_witnesses.py results/witnesses_ffree_models.json`; expected
     `1417 certificates checked, 0 failed, 0 entries without a certificate`.
   - `python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_ffree_models.json` (after
     `python src/models.py data/laws_3.json data/o3`); expected last line `ALL PASS`.
   - `python src/query.py "(x*y)*(y*z) = y" "f(x) = x"`; expected `code 5: OPEN` for the stored table, then
     `Step 09: NOT an implication. A structure with 4 elements satisfies A and fails B ... Label: model-verified.`

## Goal

Two of the nine laws with no model of size 2 or 3 do not mention `f`: `(x*y)*(y*x) = y` (#250) and
`(x*y)*(y*z) = y` (#257). Both have a verified model with 4 elements. In
`results/status_matrix.npz` their whole rows are still code 5 ("open"). Step 08 settled their
targets without `f` using the ETP data, but 304 targets per law contain `f`, and the ETP says
nothing about those.

## Idea (plain argument)

A law that does not mention `f` holds in a structure whatever `f` is. So take the 4-element table
for `*` and try every one of the 4^4 = 256 functions `f`. If target B fails for one of them, that
structure satisfies A and fails B, and that is a certificate that A does not imply B.

## Command(s)

```
python src/refute_from_ffree_models.py results/witnesses_ffree_models.json
python src/verify_witnesses.py results/witnesses_ffree_models.json
```

## Inputs

The two multiplication tables from `eq-laws-without-small-models/results/zero_model_laws.json`
(commit 95d7345), copied into the script. The script asserts that each one satisfies its law.
`results/status_matrix.npz` (to list the open targets). Run time under 1 s.

## Output

`results/witnesses_ffree_models.json`: 1,417 certificates, in the same format as
`witnesses_larger_models.json`.

| Law A | Open targets | Refuted by a 4-element certificate | Left | What the left ones are |
|-------|--------------|------------------------------------|------|------------------------|
| `(x*y)*(y*x) = y` (ETP Equation167) | 711 | 710 | 1 | `(x*x)*(x*x) = x`, which the ETP proves A implies |
| `(x*y)*(y*z) = y` (ETP Equation168, central groupoid law) | 711 | 707 | 4 | `(x*x)*(x*x) = x`, `(x*x)*(x*y) = x`, `(x*y)*(y*x) = y`, `(x*y)*(y*y) = y`, all four proved by the ETP |

So **both rows are now completely decided**: every target either has a certificate or is an
implication proved in the ETP.

## Checks done (and what each one can and cannot catch)

- `src/verify_witnesses.py` re-checked all 1,417 certificates, 0 failed. It is the independent
  verifier (its own parser and evaluator, no z3, no numpy).
- Mutation test on this file:
  `python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_ffree_models.json`
  gave ALL PASS. One flipped table entry broke 1,417 of 1,417 certificates, and swapping A and B
  broke 1,417 of 1,417.
- **Agreement with the ETP:** none of the 1,417 certificates is for a pair the ETP says is an
  implication (0 contradictions). On the 809 targets without `f`, our certificates and the ETP's
  "not an implication" agree. The leftovers are exactly the ETP's proved implications. This would
  catch a wrong model table or a wrong evaluator.

## NOT verified

- The 5 implications rest on the ETP data, not re-checked by us (see step 08).
- `results/status_matrix.npz` is unchanged (rule: do not edit stored results). `src/query.py` does
  not read this new file yet. Queue item: either teach `query.py` to read it, or regenerate the
  matrix with a documented new export step and keep the old one for comparison.

## Surprises, errors, dead ends

- This was cheap (under 1 s), and it was available since step 04. The earlier pipeline treated
  "law with no small model" as one bucket and never asked whether the law mentions `f`. Lesson
  added: split a stuck bucket by its simplest structural feature before giving it its own problem.

## Next

- Same trick for the other open laws (code 6) whose source law has a known larger model.
- Tell eq-laws-without-small-models: 3 of its 9 laws are now fully settled (step 08 and this step).
