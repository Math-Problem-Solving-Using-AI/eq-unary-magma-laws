# 19. Derivations aimed at the target: 4 more open pairs with `f` are implications

- Date: 2026-11-23
- Status label: same level as steps 17 and 18, the `z3-only` level at most (no z3 is used). Each of the 4
  answers is "implies" and rests only on a chain of replacement steps from A that plain code replays in
  full: no rewrite theory, no definitions, no solver. The ladder in `docs/shared/VERIFICATION_PROTOCOL.md`
  has no rung for this; the loop keeps the step 17 convention (`docs/LOG.md`, "Decisions taken by the loop",
  run 8). Not Lean, not reviewed, no literature check for these pairs.
- Commit(s): see `git log -- src/derive_open.py src/check_derivations.py results/derivations_open.json steps/19-derivations-aimed-at-target.md`

## In plain words

1. **The question.** After step 18, 8 pairs of laws (A, B) with `f` were still open: nobody here knew
   whether law A forces law B. Their source laws are `(x*y)*f(x) = y` (law 277), `f(x)*(y*x) = y` (408),
   `f(x*y)*x = y` (483) and `x*f(y*x) = y` (704), each with 2 open targets. The rule-building method of steps
   17 and 18 never finished for them. Is there another way in?

   Words used here:
   - A **structure** is a set with a two-input operation `*` and a one-input operation `f`. A **law** is an
     equation such as `f(x*y)*x = y` that must hold for every choice of its letters. A **model** of a law is
     a structure where it holds.
   - Law A **implies** law B if every model of A is a model of B. A **derivation** shows this: a list of
     equations, each obtained from earlier ones by replacing a piece of a formula by something equal to it.
   - A **term** is a formal expression such as `f(x*y)`. In the files, `m(s,t)` stands for `s*t` and
     `v0, v1, ...` for the letters `x, y, ...`.
   - The **mirror** of a law reads every product backwards: `s*t` becomes `t*s`. Law 704 is the mirror of
     law 483, and law 408 the mirror of law 277. A derivation for a law, mirrored, is a derivation for its
     mirror.
   - **z3** is an automatic solver; **`z3-only`** labels an answer that rests on such a tool alone.
     **Code 6** in `results/status_matrix.npz` means "open". A **mutation test** gives a checker broken input
     on purpose, to make sure it can say "no".

2. **What was done, in order.**
   1. **Worked on paper on law 483, `f(x*y)*x = y`.** The aim was to reach the targets directly instead of
      building a complete rule set. Three facts came out, each in two replacement steps:
      - E1: `f(y)*f(x*y) = x` (put `f(x*y)` for `x` and `x` for `y` in A, then use A inside).
      - E2: `f(x)*f(y) = f(x*y)`: `f` turns products into products.
      - E3: `f(x*(f(y)*x)) = f(y)`: the left side of the target and `y` have the same `f`.
      With E1 read backwards, every value `z` equals `f(w)*f(z*w)`, which by E2 is `f(w)*(f(z)*f(w))`. So a
      value is fixed by its `f`. Since E3 says the target's two sides have the same `f`, they are equal.
   2. **Turned the outline into a stored, replayable proof.** The paper proof is only an outline: a list of
      terms for each fact. A new script, `src/derive_open.py`, finds for every two neighbouring terms one
      replacement step (which earlier fact, which direction, where, with which values for its letters) and
      stops if it cannot. It writes `results/derivations_open.json`. For law 704 it uses the mirrored outline.
   3. **Wrote a separate checker**, `src/check_derivations.py`. It does not import the script above. It
      replays every step of every chain, requires fact 0 to be A as read from its text, and requires each
      claimed pair to be open in the table and its named fact to be exactly B. As a control it lists every
      model of A with 2 or 3 elements (16 in all) and evaluates every stored fact in each of them.
   4. **Mutation test**: 14 broken inputs (a changed substitution, position or direction; a dropped step; a
      step that cites the fact it is proving; a changed end of a chain; A not fact 0; a pair pointing to the
      wrong fact; a flipped verdict; A and B swapped; a shifted pair key; a claimed pair that has a
      counterexample in the table; an underived fact `x*y = x`; a false fact `x = y` that only the model
      control can see). All 14 rejected. A corrupted file makes the checker exit with 1. Running the script
      again gives a byte-identical file.
   5. **Looked at law 277** (and so 408) with the same idea. It gives the same kind of facts
      (`f(x)*f(y) = f(x*y)` and `f(x*(y*f(x))) = f(y)`, both already in step 18's rule lists), but the step
      "a value is fixed by its `f`" is missing there. The pairs of 277 and 408 stay open (section "Surprises").

3. **A small example.** A = `f(x*y)*x = y` (law 483), B = `x*(f(y)*x) = y` (law 550). Write `t` for
   `x*(f(y)*x)`.
   - `t` = `f(x)*f(t*x)` (E1 read backwards, with `x` as the helper letter),
   - = `f(x)*(f(t)*f(x))` (E2 backwards inside),
   - = `f(x)*(f(y)*f(x))` (E3: `f(t)` is `f(y)`),
   - = `f(x)*f(y*x)` (E2),
   - = `y` (E1 with the letters exchanged).
   This is fact 4 of source `482` in the file (law index = law id minus 1), 5 steps; the facts it uses take
   2 steps each. A tiny model to see it at work: on `{0, 1}` let `x*y = x + y` (adding with 1 + 1 = 0) and
   `f(x) = x`. Then `f(x*y)*x = x + y + x = y`, so A holds, and `x*(f(y)*x) = x + y + x = y`, so B holds too,
   as the derivation says it must.

4. **What it means and what it does NOT mean.**
   - It means: 4 more open pairs are answered "implies": law 483 implies laws 550 and 544
     (`x*(f(x)*x) = x`, the case `y = x`), and its mirror law 704 implies laws 195 and 189. Each answer is a
     chain of replacements that plain code replays step by step.
   - It does NOT mean machine-proved in Lean, and the checker was written in the same session as the
     derivations, by the same author, not reviewed. That is why the label stays at the `z3-only` level.
   - It does NOT settle the 4 pairs of laws 277 and 408 (targets 574, 632 and 122, 128), nor the 17 pairs
     without `f`. The notes about 277 below are a hand argument, not checked by machine.
   - The stored table `results/status_matrix.npz` was not changed (still code 6; a new code is the owner's
     decision, `STATE.md`, Blocked). `src/query.py` does not read the new file.

5. **How to re-check.**

   ```
   python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_open.json
   ```

   Expected (about 8 seconds, most of it listing the small models): `2 of 2 sources checked (24 replacement
   steps replayed)`, `4 open pairs derived (implied)`,
   `control: every fact holds in all 16 models of the sources with 2 or 3 elements`, `ALL PASS`. Add
   `--selftest`: `selftest: 14 of 14 corrupted inputs rejected`, `ALL PASS`. To regenerate (under a second):

   ```
   python src/derive_open.py data/laws_3.json results/status_matrix.npz results/derivations_open.json
   ```

   Expected: four lines `law 483 ... implies law 550 ...` and so on, then `pairs derived: 4`.

## Goal

Queue item 1 (open pairs, piece 4e): the 8 open pairs with `f` whose completion keeps growing (sources 277,
408, 483, 704). Try a derivation aimed at the target, or an infinite model.

## Command(s)

The commands under "How to re-check" (with `--selftest`), every gate of `LOOP.md`, a regeneration into the
scratch directory compared byte for byte, a corrupted copy (one substitution of source 703 changed, exit code
1). Scratch only (not kept): the step 18 search re-run on law 277 with limits 30 rules and 16 symbols to print
the growing rules; a z3 search for models of laws 277 and 483 with 2 to 5 elements whose `f` misses a value.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz` (the 4 pairs must be code 6). Python 3.12.10, Windows 10.
z3 5.4.1 only in the scratch search, not in the result.

## Output

- `src/derive_open.py` (outline and step finder), `src/check_derivations.py` (checker, 14 mutations); new gate
  lines in `LOOP.md`, `README.md` and CI.
- `results/derivations_open.json`: `sources` `"482"` (law 483) and `"703"` (law 704), 6 facts each (A, E1, E2,
  E3, B, B with `y = x`), 24 replayed steps; `pairs` `"482,549"`, `"482,543"`, `"703,194"`, `"703,188"`, all
  `holds`.
- Open pairs left: 21 (4 with `f`: 277 to 574 and 632, 408 to 122 and 128; 17 without `f`).

## Checks done (and what each one can and cannot catch)

- Replay of every chain (each step must apply exactly, substitutions must cover the fact's letters, steps may
  cite only earlier facts). Catches any wrong step. Cannot catch an error in `parse_law` or in the term
  helpers taken from `src/check_completion.py` (both gates themselves, mutation-tested).
- Pair checks: open in the table, texts equal to `data/laws_3.json`, the named fact equal to B (either
  orientation). Catches a result attached to the wrong pair.
- Control: every fact evaluated in all 16 models of the two sources with 2 or 3 elements, 0 failures. Weak:
  every finite model of these sources satisfies the targets anyway; it catches a false fact, not a wrong
  verdict.
- Consistency with earlier steps: step 15 found no counterexample table of 6 or 7 elements for these 4 pairs
  (2 `unsat` at size 6, the rest `unknown`), which fits "implies".
- Mutation test 14 of 14; exit code 1 on a corrupted file; regeneration byte-identical.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs;
  335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent; `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS;
  `check_term_rewriting.py` ALL PASS and selftest 8 of 8; `check_completion.py` on both files ALL PASS, selftests
  10 of 10 and 15 of 15; `check_derivations.py` ALL PASS, selftest 14 of 14.

## NOT verified

- The outline was found by hand in this session; only the replayed chains are checked. The checker shares its
  term parser and position helpers with `src/check_completion.py` (same author), not reviewed by anyone else.
- No second prover, no Lean, no literature check for the 4 pairs. z3 was not asked to confirm them.
- The hand notes on law 277 below (one-to-one `f`, onto `f`, finite models) are not machine-checked.
- The z3 search for models of 277 and 483 with `f` not onto covered only 2 to 5 elements and is `z3-only`.
- `results/status_matrix.npz` and `src/query.py` do not use the new file.

## Surprises, errors, dead ends

- Plain completion could not finish for law 483, yet its targets follow in 11 steps once the target is
  aimed at directly. Completion not finishing said nothing about the answer, as step 18 warned.
- First outline had a wrong middle term (`f(f(y))` instead of `f(y)` after E3); the step finder stopped with
  "no step from ... to ..." and the term was corrected. The finder works as a guard against slips in outlines.
- Law 277 `(x*y)*f(x) = y`, target 632 `x*(y*f(x)) = y` (hand notes, leads only). The facts
  `y*f(x*y) = f(x)`, `f(x)*f(y) = f(x*y)` and `f(x*(y*f(x))) = f(y)` hold (they are rules in step 18's runs).
  From them, on paper: in a model where `f` is one-to-one, the target holds; in a model where every value is
  some `f(z)`, the target holds; and in a finite model it holds (`y -> x*y` is one-to-one, hence onto). So a
  counterexample, if one exists, is infinite with `f` neither one-to-one nor onto. Dead ends tried on paper:
  models of the form `x*y = a(x) + b(y) + c` on a group, and models built from a group by a
  translation-invariant rule, all force `f` to be one-to-one. A "layered" construction (a model Q of A with
  extra copies stacked over the values outside `f(Q)`) would give a counterexample if some model Q of A has an
  `f` that misses a value; z3 found no such Q with 2 to 5 elements (for 277 and for 483).

## Next

The 4 pairs of laws 277 and 408 (queue item 1): look for an infinite model of `(x*y)*f(x) = y` whose `f` is
not onto (for the layered construction), or a longer derivation; then the 17 pairs without `f` (queue item 2).
