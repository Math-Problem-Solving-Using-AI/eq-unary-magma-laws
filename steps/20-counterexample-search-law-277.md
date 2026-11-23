# 20. Looking for a counterexample to the last 4 open pairs with `f`: none found

- Date: 2026-11-23
- Status label: no answer. The 4 pairs stay `open`. The search outcome (`results/extra_laws_277.json`) is a
  "not found" record, not a certificate. The structural notes below are hand arguments (leads), not checked by
  machine.
- Commit(s): see `git log -- src/scan_extra_laws.py results/extra_laws_277.json steps/20-counterexample-search-law-277.md`

## In plain words

1. **The question.** Four pairs of laws with `f` are still open. They all come from one law,
   `(x*y)*f(x) = y` (law 277), and its mirror `f(x)*(y*x) = y` (law 408). Does law 277 force
   `x*(y*f(x)) = y` (law 632), and its special case `x*(x*f(x)) = x` (law 574)? The mirror pairs ask the same
   question read backwards (408 to 128 and 122).

   Words used here:
   - A **structure** is a set with a two-input operation `*` and a one-input operation `f`. A **law** is an
     equation such as `(x*y)*f(x) = y` that must hold for every choice of its letters. A **model** of a law is
     a structure where it holds.
   - Law A **implies** law B if every model of A is a model of B. To show it does **not**, one needs a
     **counterexample**: a model of A where B fails.
   - **Completion** (steps 17 and 18) turns laws into one-way replacement rules ("rewrite the left side as the
     right side") until no two rules disagree. When it finishes, the formulas that no rule can shorten form an
     infinite model, and B can be tested in it.
   - **z3** is an automatic solver; it answers `unsat` (proved), `sat` (counterexample) or `unknown` (gave up).
   - The **ETP** is the Equational Theories Project, which settled all laws of this size with one operation and
     no `f`.

2. **What was done, in order.**
   1. **z3 with hints.** z3 got law 277 plus three facts that follow from it (`y*f(x*y) = f(x)`,
      `f(x)*f(y) = f(x*y)`, `f(x*(y*f(x))) = f(y)`) and 120 seconds to prove law 632. It answered `unknown`.
   2. **Completion of law 277 alone** with larger limits (30 rules, term size 16) grows without end, as in step
      18. Reading the growing rules showed a pattern: the value `x*(y*f(x))` behaves like `y` in every rule
      found (same `f`, same products with values of `f`), yet the rule "`x*(y*f(x))` becomes `y`" never
      appears. This suggested a counterexample where `x*(y*f(x))` is a "copy" of `y`.
   3. **Completion of law 277 together with one extra law E.** If law 277 and E together complete and law 632
      still fails in the resulting model, that model is a counterexample (it satisfies 277). A new script,
      `src/scan_extra_laws.py`, tried every law E with 1 to 4 symbols (8,804 laws, besides 277 itself), both
      symbol orders of step 18 and its limits. 274 runs completed; in **every one of them law 632 holds**. The
      other 8,530 stopped (a rule could not be oriented, or a limit was hit). So no extra law of this size gives
      a counterexample this way.
   4. **Positive control** for that search: the same code, given a pair that step 17 refuted by completion,
      reports "fails" (pair `(x*f(y))*x = y` and `f((x*x)*x) = x`).
   5. **The ETP as a cross-check.** Replacing `f(x)` by `x`, `x*x`, `x*(x*x)` or `(x*x)*x` turns the pairs into
      pairs of laws without `f` (ETP equations 29 to 14, 170 to 66, 1492 to 477, 1695 to 680, and the special
      cases and mirrors). The ETP outcome table in the local ETP copy says each of these implications is true.
      A counterexample with `f` given by such a formula is therefore excluded.
   6. **Hand analysis** of what a counterexample would have to look like (section "Surprises"). In short: it
      must be infinite, the values of `f` must themselves form a model where law 632 holds, and inside that
      model `f` must be one-to-one but not onto, so that applying `f` again and again gives smaller and smaller
      copies.

3. **A small example.** Why finite structures cannot help. Take the 2-element structure on `{0, 1}` with
   `x*y = x + y` (adding with 1 + 1 = 0) and `f(x) = x`. Law 277: `(x + y) + x = y`, true. Law 632:
   `x + (y + x) = y`, also true. In any finite model of law 277, for fixed `x` the map `y -> x*y` cannot
   send two values to one (law 277 undoes it with `*f(x)`), so on a finite set it is a reshuffle of all values,
   and then law 632 follows (hand argument from step 19). So a counterexample, if one exists, is infinite.
   That is why steps 15 and this step look at infinite models.

4. **What it means and what it does NOT mean.**
   - It means: none of the cheap ways to build an infinite counterexample works here: no extra law of size up
     to 4, no replacement of `f` by a short formula, no z3 proof in 120 seconds even with hints.
   - It does NOT mean that law 277 implies law 632. "Not found" is not "does not exist". It also does not mean
     the opposite. The 4 pairs stay open (code 6), and the count of open pairs stays at 21.
   - The hand notes are leads for the next attempt, not results.
   - The search was run for law 277 only. Its mirror 408 asks the same question read backwards, but the search
     itself is not mirror-symmetric (the rule order compares from the left), so its outcome for 408 is unknown.

5. **How to re-check.** The search (about 25 minutes; it stops after about 500 seconds and resumes from the
   output file, so run it until it says 8804 of 8804):

   ```
   python src/scan_extra_laws.py data/laws_3.json 277 632,574 results/extra_laws_277.json
   ```

   Expected last line: `extra laws tried: 8804 of 8804; completed: 274; B fails in a completed run: 0`. With
   the stored file in place it only prints that line. The entry for E = law 632 (key `"632"`) is
   `[["f > *", ["holds", "holds"], 4]]`: law 277 and law 632 together complete to 4 rules.

## Goal

Queue item 1 (open pairs, piece 4f): the 4 pairs of `(x*y)*f(x) = y` (targets 574, 632) and its mirror
`f(x)*(y*x) = y` (targets 122, 128). Look for an infinite counterexample or a longer derivation.

## Command(s)

- `python src/scan_extra_laws.py data/laws_3.json 277 632,574 results/extra_laws_277.json` (run 3 times, each
  stops after about 500 s).
- Positive control (inline, not kept): `ExtraLawCompletion` on source 165 `(x*f(y))*x = y` of
  `results/completions_open.json` with E = A itself, target `f((x*x)*x) = x`: `complete fails`, as in step 17.
- Scratch only (not kept): z3 5.4.1, sort `U`, `m`, `f`, axioms law 277 and the three facts of item 2.1,
  goal `m(a, m(b, f(a))) != b`, timeout 120 s: `unknown`. Completion of law 277 alone with 30 rules, size 16
  (`src/complete_open.py` classes): term size limit at 25 rules. ETP lookup: `canon` from `src/etp_crosscheck.py`
  on the ETP `data/equations.txt`, outcomes from the ETP's `data/2024-11-10-outcomes.json.zip`, Lean proof of
  170 to 66 read in `Generated/VampireProven/Proofs3.lean` (it uses that `x*x` is a product, so it does not
  carry over to an arbitrary `f`).
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`; laws of size 4 generated by `src/laws.py` inside the script (8,805 laws, the first 712 are
`data/laws_3.json` in the same order). Local ETP clone `repos/_external/equational_theories` at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), read only, no web access in this step. Python 3.12.10,
z3 5.4.1, Windows 10.

## Output

- `src/scan_extra_laws.py` (search, resumable).
- `results/extra_laws_277.json`: for each extra law E (key = law id in the size-4 list) the outcome per symbol
  order tried: a stop reason, or `[order, [verdict for 632, verdict for 574], rules]`. 8,804 laws: 274 complete
  (all `holds`, `holds`), 8,238 stop at an equation that cannot be oriented, 194 at the term size limit, 98 at
  the rule limit.
- No change to `results/status_matrix.npz` or any certificate. Open pairs: still 21 (4 with `f`, 17 without).

## Checks done (and what each one can and cannot catch)

- Positive control: the completion code reports "fails" on a pair known to fail (step 17). Catches a search
  that can never say "fails". Cannot show that the limits were large enough.
- The entry for E = law 632 completes to the 4 rules `(x*y)*f(x) -> y`, `x*(y*f(x)) -> y`,
  `y*f(x*y) -> f(x)`, `f(x)*f(y) -> f(x*y)` (seen in a scratch run that printed them).
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS;
  `check_term_rewriting.py` ALL PASS and selftest 8 of 8; `check_completion.py` on both files ALL PASS, selftests
  10 of 10 and 15 of 15; `check_derivations.py` ALL PASS, selftest 14 of 14.

## NOT verified

- No answer for any of the 4 pairs; the search only says what does not work with these limits.
- A completion that stopped says nothing about the pair; a larger limit might complete some of the 8,530 runs.
- The search was not run for law 408 (the mirror).
- The hand notes below are not machine-checked.
- The ETP outcomes were read from the 2024-11-10 outcome file in the local clone, not from the newer
  `general_outcomes.json.gz` used in step 08 (not on disk). The Lean proofs behind them were not re-run.
- z3's `unknown` after 120 s carries no information either way.

## Surprises, errors, dead ends

- Dead end: extra laws of size up to 4 (274 complete, all make law 632 hold). Dead end: replacing `f(x)` by a
  one-letter formula (the ETP says all those magma implications hold). Dead end: z3 with hints, 120 s.
- Mistake caught on paper: an early hand argument claimed "a value outside F that shares the right product with
  a value of F is that value". It used one-to-one-ness of `z -> z*c` on F for an element outside F. Wrong; it was
  dropped before anything was built on it.
- Hand notes (leads only). Write F for the set of values of `f`, and assume a model of law 277 where law 632
  fails.
  1. F is closed under `*` and `f` (`f(x)*f(y) = f(x*y)`), so it is a model of 277 itself, and law 632 holds on
     F: from 277 one derives `y*(f(x)*f(y)) = f(x)`, which with `y` in F is law 632 on F.
  2. In a model of 277 and 632, `f` is one-to-one: if `f(a) = f(b)` then `a*y = b*y` for all `y` (both are
     undone by `*f(a)`, which 632 makes one-to-one), and with `y = f(z)` this gives `a = b`.
  3. So `f` is one-to-one on F, and F is not all of the model (if every value were in F, law 632 would hold,
     step 19). Take `v` outside F and any `u`. If some `q` in F had `q*f(u*v) = f(u)`, then
     `y*(f(x)*f(y)) = f(x)` with `y = u*v`, `f(x) = q` and law 277 give `v = q`, which is in F: impossible.
     If `f(u*v)` were in f(F), then `z -> z*f(u*v)` would be a reshuffle of F (by 1 and 2), and such a `q`
     would exist. So `f(u*v)` is never in f(F), hence f(F) is smaller than F: `f` is not onto F, and F, f(F),
     f(f(F)), ... is an endless chain of smaller and smaller copies. By the same kind of argument, two values
     with the same `f` must both lie outside F.
  4. The free model of 277 and 632 (the 4 rules above) has exactly such an `f`: one-to-one, and a letter is
     never a value of `f`. It is a natural candidate for F in a construction; how to add the values outside F
     consistently was not found (a first attempt with "pairs" outside F breaks law `y*(f(x)*f(y)) = f(x)` at
     values whose image lies in f(F)).
- Lesson (for the hub): a search with an extra law is cheap (8,804 completions in about 25 minutes) and gives a
  checkable certificate when it works; try it before building an infinite model by hand.

## Next

The 4 pairs of 277 and 408 need a new idea (an explicit infinite model built over the free model of 277 and 632,
or a longer derivation), so they move behind the 17 pairs without `f` (queue item 2), which the ETP has settled
and which may be reachable by reading how the ETP did it.
