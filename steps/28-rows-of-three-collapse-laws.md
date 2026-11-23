# 28. Rows of the three collapse laws: 2,133 "implies", each from a replayed derivation of x = y

- Date: 2026-11-23
- Status label: stored chains of replacement steps replayed by plain code (same level as steps 19 and 27: `z3-only`
  level at most, no z3 used). Not Lean, not reviewed by a person. The chains follow the hand arguments of the sibling
  repository eq-laws-without-small-models, whose own checker also accepts its versions of them (run here, read only).
- Commit(s): see `git log -- src/collapse_derivations.py src/selftest_collapse_laws.py results/derivations_collapse_laws.json steps/28-rows-of-three-collapse-laws.md`

## In plain words

1. **The question.** Nine laws have no small example: no table with 2 or 3 elements obeys them. Their rows in the
   stored table say "open" (code 5). Step 27 answered the rows of four of them. This step answers the rows of three
   more: `((x*y)*z)*x = w` (law 110), `(x*y)*f(z) = y` (law 284) and `f(x)*(y*z) = y` (law 415). For each of these
   laws A and each of the 711 other laws B: does A force B?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a two-input operation
     `*` and a one-input operation `f`. It may be finite or infinite.
   - A **law** is an equation such as `(x*y)*f(z) = y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding. Infinite structures count.
   - A **model** of A is a structure where A holds.
   - A law **collapses** if it forces every model to have just one element, that is, it forces `x = y` for all x, y.
     In a one-element structure every law holds, so a collapsing law implies every law.
   - A **derivation** is a chain of steps, each replacing one piece of an expression by an equal one according to
     law A (or to an equation derived earlier in the same file). If the chain leads from the left side of an
     equation to its right side, the equation holds wherever A holds.
   - **Code 5** in `results/status_matrix.npz` means "A is one of the 9 laws with no small model"; it is an open code.
   - **z3** is an automatic solver; **`z3-only`** labels an answer that rests on z3 with nothing else confirming it.
     This step does not use z3; the label says only that a replayed derivation ranks no higher than that here.
   - A **mutation test** feeds a checker deliberately broken input to make sure it can say "no".

2. **What was done, in order.**
   1. **Wrote the derivation of `x = y` for each law** (`src/collapse_derivations.py`, chains written by hand as
      data). For law 110 it takes two steps (see the example below). For laws 284 and 415 it takes a helper
      equation of two steps and then four steps, following the sibling repository's hand proofs
      (`results/collapse_xy_fz.json`, `results/collapse_fx_yz.json` there): first "a product of the right shape equals
      `f(c)` for every c", then "every element equals some `f(c)`, so any two elements are equal".
   2. **Wrote every other law B as one more step.** Once `x = y` is derived, B follows in one step: replace B's left
      side by B's right side, using `x = y` with x := left side and y := right side. This gives 711 targets per law,
      2,133 pairs in all, every one "implies". Stored in the format of steps 19 and 27
      (`results/derivations_collapse_laws.json`). Running the script again gave a byte-identical file.
   3. **Replayed everything with the existing checker** `src/check_derivations.py` (step 19, unchanged). It does not
      import the script that wrote the file. It checks that A is the law's text, replays all 2,147 steps (14 for the
      three `x = y` derivations and helpers, 2,133 for the targets), and checks for each pair that it is open (code 5)
      and that the derived equation is B. Result: all pass.
   4. **Mutation test** (`src/selftest_collapse_laws.py`, new): 14 broken copies of the file (a changed
      substitution, position or direction, a dropped step, a step citing a later equation, a helper with a wrong
      right side, a target derived from the wrong equation, a wrong source law, a pair that is not open, a pair
      pointing at another target, a shifted key). All 14 rejected. The step 19 selftest cannot be used: it looks for a
      target whose own chain has 3 steps or more, and here each target has one step.
   5. **Second look at the sibling's proofs.** The sibling's checker `check_derivation.py` (a different program, with
      its own step format) was run on its two stored proofs, without writing anything there: both say
      `COLLAPSE DERIVED` and `ALL PASS`. Law 110 has no stored proof there; its two-step argument is in the hub's
      lessons (`docs/shared/LESSONS.md`, "Laws and solvers").
   6. Ran every gate of `LOOP.md` (33 commands, all pass) and added the two new commands to the gates and to CI.

3. **A small example.** A = `((x*y)*z)*x = w` (law 110).
   - Take any two elements a and b. Put x, y, z, w all equal to a: the law says `((a*a)*a)*a = a`. Put x, y, z equal
     to a and w equal to b: the law says `((a*a)*a)*a = b`. Both left sides are the same, so a = b.
   - As a chain: start at `a`, replace it by `((a*a)*a)*a` (law read right to left), then replace that by `b` (law read
     left to right). Two steps.
   - So every model has one element, and then every law B holds. For example B = `x*y = x`: from `x = y` with x := `x*y`
     and y := `x`, one step.
   - Why no small table shows anything: a table with 2 elements a ≠ b cannot satisfy law 110, by the two lines above.
     Likewise for law 284: in the 2-element table with `x*y = y` and `f(x) = x`, the left side `(x*y)*f(z)` equals z, not
     y, so the law fails there; by this step it must fail in every table with 2 or more elements.

4. **What it means and what it does NOT mean.**
   - It means: for the three laws 110, 284 and 415, all of their 2,133 pairs are "implies", each with a derivation
     replayed by plain code in this repository. With step 27, the rows of 7 of the 9 code 5 laws now have a check here.
   - It does NOT mean: Lean-checked, or reviewed by a person. The checker is small and mutation-tested, but it is our own
     code; no second, independent checker of our chains was run (the sibling's checker ran on the sibling's chains,
     which have a different format).
   - It does NOT change `results/status_matrix.npz`: those 2,133 pairs still say code 5 there. New codes would change a
     published format, which the owner decides (STATE.md, "Blocked").
   - The rows of the last 2 code 5 laws, `(x*y)*(y*x) = y` (law 250) and `(x*y)*(y*z) = y` (law 257), are not covered
     here: 1,417 of their 1,422 pairs have 4-element certificates since step 09, and 5 implications rest on the ETP only.
     That is the next queue item.

5. **How to re-check it.** From the repository root:
   - `python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json`
     prints `3 of 3 sources checked (2147 replacement steps replayed)`, `2133 open pairs derived (implied)`,
     `control: every fact holds in all 0 models of the sources with 2 or 3 elements` and `ALL PASS`.
   - `python src/selftest_collapse_laws.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json`
     prints `selftest: 14 of 14 corrupted inputs rejected` and `ALL PASS`.
   - To rebuild the file: `python src/collapse_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json`
     prints `3 sources, 2133 pairs written to ...`; the file comes out identical.

## Goal

Queue item 1 of `STATE.md`: give the rows of the three collapse laws with code 5 (laws 110, 284, 415; 2,133 pairs) an
answer with a machine check here, without changing `results/status_matrix.npz`.

## Command(s)

```
python src/collapse_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json
python src/selftest_collapse_laws.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json
cd ../eq-laws-without-small-models && python -B check_derivation.py results/collapse_xy_fz.json && python -B check_derivation.py results/collapse_fx_yz.json
```
plus every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz` (unchanged; all 3 x 711 pairs have code 5, checked by an assertion in
the script and by the checker). The sibling's `results/collapse_xy_fz.json` and `results/collapse_fx_yz.json` (sibling
commit `3ab6163`, 2026-11-23) were read and run with the sibling's checker, not changed (`python -B`, so no
`__pycache__` written; `git status` there clean afterwards). No z3.

## Output

- `results/derivations_collapse_laws.json`: 3 sources, 2,133 pairs, 2,147 replacement steps.
  - law 110 (key 109): fact 1 `v0 = v1` (2 steps), then 711 targets.
  - law 284 (key 283): fact 1 `v0*f(v1) = f(v2)` (2 steps), fact 2 `v0 = v1` (4 steps), then 711 targets.
  - law 415 (key 414): fact 1 `f(v0)*(v1*v2) = f(v3)` (2 steps), fact 2 `v0 = v1` (4 steps), then 711 targets.
- New: `src/collapse_derivations.py` (writes the file), `src/selftest_collapse_laws.py` (mutation test, gate and CI).
- `LOOP.md` gates and `.github/workflows/verify.yml`: two new commands.

## Checks done (and what each one can and cannot catch)

- `check_derivations.py` (unchanged since step 27): replays every step from the stored substitution and position,
  requires fact 0 to be A as parsed from its text, each pair to be code 5 or 6 and the derived equation to be B.
  Catches a wrong step, a wrong target, a pair that is not open. Cannot catch a bug in the term functions it shares
  with the writer (`check_completion.py`, `check_laws_text.py`; the writer uses them to parse laws and print terms).
- Its small-model control is empty here (0 models with 2 or 3 elements), as expected for collapse laws.
- Mutation test: 14 of 14 rejected; covers the `x = y` chain, the helper chain, the target chains, the source law and the
  pair entries.
- Sibling's checker on the sibling's two proofs: both pass. This confirms the argument, not our chains.
- Byte-identical rerun of the writer.
- All 33 gates of `LOOP.md` pass.

## NOT verified

- No Lean, no person reviewed the chains; the only replay of our chains is our own checker.
- No independent second checker of our file (the sibling's checker reads a different format and was run on the
  sibling's files only).
- `results/status_matrix.npz` and `src/query.py` do not report these answers (published format, owner's decision).
- The 5 pairs of laws 250 and 257 that rest on the ETP only are not covered by this step.
- No literature check for these pairs in this step (collapse of these laws is elementary; no novelty is claimed).

## Surprises, errors, dead ends

- None. The step 19 selftest cannot run on this file (it needs a target with a chain of 3 steps or more), as already
  seen in step 27; a separate mutation script was written from the start.

## Next

Queue: the 2 laws with 4-element models (laws 250 and 257): give the 5 implications that rest on the ETP only a check
here, then check the finish line in `LOOP.md`.
