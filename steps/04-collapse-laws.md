# 04. Laws with no small model: do they collapse?

- Date: 2026-11-22
- Status label: z3-only
- Commit(s): ebdb14f

## In plain words

1. **The question.** 216 of the 712 laws hold in no structure with 2 or 3 elements (step 03). Do they hold only in
   one-element structures? Such a law is said to **collapse**: it forces any two elements to be equal, so it implies
   every other law (every law holds in a one-element structure).

   Words used here:
   - A **law** is an equation such as `x*y = z` that must hold for every choice of the letters; a **structure** is a set
     with a two-input operation `*` and a one-input operation `f` (step 01). A **model** of a law is a structure where
     it holds.
   - **z3** is an automatic solver (a program that decides logic questions). Asked "is there a structure, of any size,
     where A holds and two elements differ?", it can answer `unsat` (no), `sat` (yes) or `unknown` (it gave up in the
     time allowed).
   - The label **`z3-only`** means the answer rests on z3 alone, with no stored proof that other code checked. It is a
     lead, not a proof (`docs/shared/VERIFICATION_PROTOCOL.md`).

2. **What was done, in order.**
   1. Gave z3 each of the 216 laws, 5 seconds per law (one run with 60 seconds), asking for a structure with two
      different elements.
   2. Kept every `unsat` across runs, because z3 does not give the same answers twice (207 proofs at 5 seconds, 205 at
      60 seconds). A proof found once stays a proof; a time-out says nothing.
   3. Result: 207 laws collapse (`z3-only`). 9 laws stayed unresolved; they became their own question in a sibling
      repository. Two of them have models with 4 elements, so "no small model" does not mean "collapses".

3. **A small example.** `f(x) = y` collapses, by hand: put y := z to get `f(x) = z`; so y = f(x) = z for every y and
   z, and all elements are equal. Another: `x*y = z` gives `z = x*y = w` for every z and w. The table records both as
   "implies everything" (code 4). By contrast, `(x*y)*(y*z) = y`, one of the 9, has a 4-element model (shown in
   step 29), so it does not collapse.

4. **What it means and what it does NOT mean.**
   - It means: 207 laws are marked "forces one element", so the 207 x 711 = 147,177 pairs with such a law as A are
     marked "implies".
   - It does NOT mean: proved. These 207 rest on z3 alone; no proof is stored for any of them (step 28 later stored and
     replayed proofs for 3 of the 9 unresolved laws, which do collapse, not for these 207). Nothing is checked in Lean.
   - On 2026-11-23 (loop run 21) the command below was run again from an empty start: 203, then 205, then 207 proofs as
     they accumulated over three runs, the same 207 laws as in the table. Another example of z3 varying between runs.

5. **How to re-check.** From the repository root, after `python src/models.py data/laws_3.json data/o3`:
   - `python src/prove.py collapse data/laws_3.json data/o3 5000`, run several times (it adds to
     `data/o3_collapse.npy`). The expected first line is `zero-model laws: 216 proved collapse: N z3 sat: 0 ...`, with N
     growing to 207 after a few runs, followed by the laws not proved yet.
   - `python src/query.py "f(x) = y" "x*y = y*x"`; expected
     `code 4: implication, because law A forces a one-element structure` and `label: z3-only`.

## Goal
A law with no model of size 2 or 3 might force every structure to have one element ("collapse",
the law proves `x = y`). Such a law implies every other law. Find out which ones do.

## Command(s)
```
python src/prove.py collapse data/laws_3.json data/o3 5000
```
Run several times: proofs accumulate (see lessons).

## Inputs
216 laws with no model of size 2 or 3. z3, timeout 5 s per law (one run used 60 s).

## Output
`data/o3_collapse.npy`. 207 of 216 proved to collapse (`unsat`). 9 unresolved:
`((x*y)*z)*x = w`, `(f(x)*y)*z = y`, `(x*y)*(y*x) = y`, `(x*y)*(y*z) = y`, `(x*y)*f(z) = y`,
`f((x*y)*z) = y`, `f(x)*(y*z) = y`, `f(x*(y*z)) = y`, `x*(y*f(z)) = y`.

## Checks done
- None beyond z3 itself. A z3 `unsat` is trusted as a proof only as a lead. No proof object is
  stored and no independent checker has confirmed these 207.

## NOT verified
- All 207 collapse claims. Status stays `z3-only` until a derivation is stored and checked by an
  independent tiny checker, and later in Lean (see `docs/shared/VERIFICATION_PROTOCOL.md`).
- That the 9 unresolved laws do or do not collapse: see [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models).

## Surprises, errors, dead ends
- **Assumption broken:** "no model of size 2 or 3" does not mean "collapses". Two of the nine
  have a model of size 4.
- **z3 is not stable between runs:** 207 proofs at 5 s, 205 at 60 s (8 workers in parallel).
  Fix: accumulate proofs, never overwrite. Recorded in `docs/shared/LESSONS.md`.
- `CheckSatResult` is unhashable in z3 (code bug, fixed).

## Next
Step 05: try to prove the remaining candidate pairs.
