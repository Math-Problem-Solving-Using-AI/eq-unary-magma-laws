# 09. Settle the rows of the two `f`-free laws that have 4-element models

- Date: 2026-11-22
- Status label: 1,417 non-implications `model-verified` (608 of them involve `f` and were open
  before; the other 809 had just been settled by the ETP in step 08 and now also have our own
  certificate). The 5 remaining pairs are implications, `known (ETP)`.
- Commit(s): see `git log -- steps/09-ffree-models-with-f.md`

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
