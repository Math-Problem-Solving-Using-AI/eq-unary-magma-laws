# 17. Completing the overlapping rules settles 133 of the 190 open pairs

- Date: 2026-11-23
- Status label: the ladder in `docs/shared/VERIFICATION_PROTOCOL.md` has no rung for this kind of
  certificate (a rewrite system re-checked by plain code; no z3 is used). It is recorded at the `z3-only`
  level, never higher: the certificate is re-checked in full by plain Python, but two textbook theorems it
  relies on (the critical pair lemma and Newman's lemma, below) are not machine-checked here. Not
  `model-verified` (that label is for finite tables), not Lean, not reviewed, no literature check for
  these pairs.
- Commit(s): see `git log -- src/complete_open.py src/check_completion.py results/completions_open.json steps/17-completion-overlapping-rules.md`

## In plain words

1. **The question.** After step 16, 190 pairs of laws (A, B) were still open: we did not know whether
   law A forces law B. Each of these laws A has the form "a term = one of its letters". Step 16 could not
   use them because the pattern of A can overlap with itself. Can that overlap be repaired, so that the
   same kind of infinite structure as in step 16 decides the pairs?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a
     two-input operation `*` and a one-input operation `f`. It may be infinite.
   - A **law** is an equation such as `(x*y)*f(z) = z` that must hold for every choice of the letters.
   - A **model** of a law is a structure where the law holds.
   - Law A **implies** law B if every model of A is a model of B. One model of A where B fails (a
     **counterexample**, or **witness**) shows that A does NOT imply B.
   - A **term** is a formal expression such as `f(x*y)`. In the files, `m(s,t)` stands for `s*t` and
     `v0, v1, ...` for letters.
   - A **rewrite rule** `l -> r` says: wherever a piece of an expression has the shape `l`, it may be
     replaced by the matching `r`. A **normal form** is an expression where no rule applies any more.
   - An **overlap** (or **critical pair**) is an expression where two rules (or one rule twice) can be
     applied in two different places, so that the order of replacements might matter.
   - **Completion** (the Knuth-Bendix method) turns each overlap into a new equation and adds it as a
     new rule, until every overlap gives the same result whichever rule is used first.
   - **KBO** (Knuth-Bendix order) is a fixed way to compare two terms, mainly by counting symbols. If
     every rule's left side is larger than its right side in this order, replacing can never go on
     forever.
   - **z3** is an automatic solver; **`z3-only`** labels an answer that rests on such a tool alone.
     **Code 6** in `results/status_matrix.npz` means "open". A **mutation test** gives a checker
     deliberately broken input to make sure it can say "no".

2. **What was done, in order.**
   1. **Wrote the completion** (`src/complete_open.py`). For each of the 26 source laws, start with A as a
      rule. Repeatedly: find every overlap, compute the two results, simplify both with the current
      rules; if they differ, orient the new equation with KBO (bigger side on the left) and add it as a
      rule; drop or simplify old rules that the new rule makes redundant. Stop with success when every
      overlap gives the same result, and give up when an equation cannot be oriented, a term gets longer
      than 14 symbols, or there are more than 40 rules. Each law was tried with `f` ranked above `*`, then
      the other way round.
   2. **Kept a derivation of every new rule.** Each new equation is stored with the exact chain of
      replacements, starting from A, that proves it: "at this place, replace this instance of that
      earlier equation's side by its other side". So every rule follows from A, and anyone can replay it.
   3. **Result:** 7 of the 26 source laws complete, in under a second. They are the sources of 133 open
      pairs. The other 19 stop, mostly because an equation cannot be oriented (for example the
      completion of `f(x*x)*y = x` produces `f(x)*z = f(x*x)`, whose left side has a letter `z` the right
      side does not have, so neither side can be replaced by the other).
   4. **Built the structure T_R** from each completed rule set R: its elements are the normal forms of
      terms over infinitely many starting elements `g0, g1, ...`; to multiply or apply `f`, write the new
      term and simplify it to its normal form. Because the rules always terminate (KBO) and every overlap
      joins, simplifying gives the same normal form whatever order is used (critical pair lemma and
      Newman's lemma, two standard theorems of rewriting). A's two sides simplify to the same thing, so
      A holds in T_R.
   5. **Decided each target B**: send B's letters to `g0, g1, ...` and simplify both sides. Different
      normal forms: B fails in T_R, so A does NOT imply B (132 pairs). Equal normal forms: the
      replacements used are all consequences of A, so A implies B (1 pair).
   6. **Wrote a separate checker** (`src/check_completion.py`, it does not import the search). For each
      source it replays every derivation step by step, checks each rule is a derived equation and is
      decreasing in KBO (its own KBO code), recomputes every overlap of the rule set with its own
      unification code and checks both results simplify to the same normal form (its own simplifier,
      innermost first, where the search works outermost first), and checks A's sides join. For each pair
      it checks the pair is open (code 6), the law texts, and recomputes B's normal forms and verdict.
   7. **Checked against everything already known.** For the 7 completed sources, the verdict on all 712
      targets each (4,984 pairs) contradicts no finite counterexample (codes 1, 2), no z3 implication
      (codes 0, 3, 4) and no answer of the Equational Theories Project (ETP) for pairs without `f`. The one
      implication, `(x*(y*y))*y = x` implies `(x*y)*(y*y) = x`, has no `f` and the ETP also says "implies".
   8. **Mutation test**: 10 broken inputs (changed values, flipped verdict, swapped laws, shifted key, a
      wrong first equation, a changed derivation step, a dropped rule, a reversed rule, an underived rule,
      and every source with only its own uncompleted rule); all 10 rejected. A corrupted file makes the
      checker exit with 1. Running the search again gave a byte-identical file.

3. **A small example.** A = `(x*y)*f(z) = z`, B = `f(x*y) = y` (pair 284,38 in the file, law ids 285 and 39).
   - The rule `(x*y)*f(z) -> z` overlaps itself: in `((a*b)*f(c))*f(e)` the inner piece `(a*b)*f(c)` gives
     `c`, so the whole is `c*f(e)`; the whole expression also matches the rule at the top (x = `a*b`,
     y = `f(c)`, z = `e`), which gives `e`. So A forces `c*f(e) = e` for
     every `c` and `e`.
   - The new rule `x*f(y) -> y` contains the old one as a special case, and it has no overlap with itself.
     Completion stops with R = {`x*f(y) -> y`}.
   - In T_R a product `d*e` is the formal `P(d,e)`, except that `d*F(c)` is `c`. A holds:
     `(x*y)*f(z) = (x*y)*F(z) = z`.
   - B with `x = g0`, `y = g1`: `f(g0*g1)` is the formal `F(P(g0,g1))`, which is not `g1`. B fails, so A
     does not imply B.

4. **What it means and what it does NOT mean.**
   - It means: 132 more open pairs are "does not imply", each with an infinite counterexample built from
     a rule set, and 1 more is "implies" with a stored derivation. Everything in the certificate is
     re-checked by plain code.
   - It does NOT mean machine-proved from first principles: that "terminating + all overlaps join" gives
     unique normal forms is a textbook theorem we use without a machine proof. Hence the label is not
     raised above the `z3-only` level.
   - It says nothing about finite structures: for many of these pairs, every finite model of A may still
     satisfy B.
   - It does NOT settle the other 57 open pairs (19 source laws whose completion stopped): 40 pairs with
     `f`, which have no answer, and 17 without `f`, which have an ETP answer (16 "does not imply", 1
     "implies") but no certificate here. "Completion stopped" does not mean anything about those pairs.
   - The stored table `results/status_matrix.npz` was not changed (still code 6; a new code is the owner's
     decision, `STATE.md`, Blocked). `src/query.py` does not read the new file.

5. **How to re-check.**

   ```
   python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_open.json
   ```

   Expected (about a second): `7 of 7 rule sets checked (derivations, KBO, critical pairs, A joins)`,
   `133 open pairs: 132 fail in T_R (not implied), 1 derived (implied)`,
   `table and ETP control: 4984 pairs, 4940 fail, 44 hold`, `ALL PASS`. Add `--selftest` for the mutation
   test: `selftest: 10 of 10 corrupted inputs rejected`, `ALL PASS`. To regenerate:

   ```
   python src/complete_open.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/completions_open.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json results/refutations_term_rewriting.json
   ```

   Expected: one line per source law and precedence, then `open pairs: 190; from sources with an overlap: 190`,
   `sources completed: 7 of 26`, `pairs whose source did not complete: 57`, `B holds in T_R: 1`,
   `B fails in T_R: 132`.

## Goal

Queue item 1 (open pairs, piece 4b): Knuth-Bendix completion of the 26 overlapping source rules, and the
step 16 term structure built from every completed rule set, with a checker that checks every rule and that
each rule follows from A.

## Command(s)

The two commands under "How to re-check" (with `--selftest` once more), plus every gate of `LOOP.md`, a
regeneration into the scratch directory compared byte for byte, and a corrupted copy of the file (one
stored normal form changed) to check the exit code (1).

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json`, `results/z3_open_retry.json`,
`results/witnesses_ffree_models.json`, `results/witnesses_etp_magmas.json`,
`results/refutations_term_rewriting.json` (passed as a certificate file, so its 682 pairs count as settled
and the open list is the 190 of step 16). Limits: 40 rules, 14 symbols per term, 4,000 equations. Python
3.12.10, Windows 10. No z3.

## Output

- `src/complete_open.py` (search), `src/check_completion.py` (checker, `--selftest`), both in the gates and CI.
- `results/completions_open.json`: `sources` (7 rule sets with all derived equations and their
  derivations) and `pairs` (133 entries `"a,b": {A, B, verdict, B_left, B_right}`, law index = id minus 1).
- Completed sources (law id, rule set): 165 `(x*(y*y))*y = x` (2 rules, 1 pair, the implication); 195
  `(x*f(y))*x = y` (2 rules, 4 pairs); 285 `(x*y)*f(z) = z` -> `x*f(y) -> y` (31); 355 `f(f(x)*y) = y` ->
  `f(x*y) -> y` (31); 414 `f(x)*(y*z) = x` -> `f(x)*y -> x` (31); 454 `f(x*f(y)) = x` -> `f(x*y) -> x` (31);
  550 `x*(f(y)*x) = y` (2 rules, 4).
- By step 15's z3 answers at sizes 6/7 the 133 were 28 `unsat`/`unsat`, 97 `unsat`/`unknown`,
  8 `unknown`/`unknown`.
- Not completed (19 sources, 57 pairs). `cannot orient` (both precedences): 354, 455, 466, 483, 485, 489,
  691, 704, 707, 712 (36 pairs, all with `f`; 466 and 707 have 10 pairs each). `term size limit`: 277
  `(x*y)*f(x) = y` and 408 `f(x)*(y*x) = y` (with `f`, 2 pairs each), and 86, 88, 143, 153, 508, 565, 598
  (no `f`, 17 pairs). Total with `f`: 40.

## Checks done (and what each one can and cannot catch)

- Replay of every derivation (each step must apply exactly, substitution covering the equation used, only
  earlier equations). Catches an underived or wrongly derived rule. Cannot catch an error in the parser
  shared with `src/verify_witnesses.py` (`parse_law` from `src/check_laws_text.py`, itself a gate).
- KBO check of every rule with the checker's own code. Catches a rule that is not decreasing (mutation).
  Relies on KBO being a terminating order (textbook, not machine-checked).
- All critical pairs recomputed with the checker's own unification, and joined with an innermost
  simplifier (the search simplifies outermost first). Catches a missing rule (mutations "dropped rule" and
  "only its own rule": 7 of 7 sources rejected). Relies on the critical pair lemma and Newman's lemma.
- A's sides join; B's normal forms and verdict recomputed and compared.
- Control: 4,984 verdicts against codes 0 to 4 of the table and the ETP verdicts: 0 contradictions.
- Mutation test 10 of 10; exit code 1 on a corrupted file; regeneration byte-identical.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs;
  335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent (counts unchanged); `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and
  selftest ALL PASS; `check_term_rewriting.py` ALL PASS and selftest ALL PASS.

## NOT verified

- The critical pair lemma, Newman's lemma and the termination of KBO are used as textbook facts; none is
  machine-checked here, and no source was re-read for their exact statements in this step.
- That KBO with weight 1 for `f` (a one-input symbol) and either precedence is a valid reduction order is
  taken from the textbook definition (a one-input symbol of weight 0 would need special care; ours has 1).
- The checker was written in the same session as the search, by the same author, and is not reviewed.
- No second prover and no Lean for any of the 133 pairs. No literature check for these pairs.
- The 57 pairs whose completion stopped were not decided; "completion stopped" says nothing about them.
- `results/status_matrix.npz` and `src/query.py` do not use the new file.

## Surprises, errors, dead ends

- Four of the large rows (31 pairs each) complete to a single rule without overlap after one round: the
  overlap shows that one letter of A does not matter (for example `(x*y)*f(z) = z` gives `x*f(y) = y`).
- Most of the 19 failures are equations with a letter on one side only, such as `f(x)*z = f(x*x)`
  (`f(x)*z` does not depend on `z`) or `x*(y*x) = z*(y*z)`. Plain completion cannot orient them; a new
  function symbol for "the value that does not depend on z" or ordered completion might.

## Next

The 57 open pairs left: the 40 with `f` (completion with a new symbol for equations like `f(x)*z = f(x*x)`,
or ordered completion; and higher limits for 277 and 408), then the 17 without `f`, which the ETP answers but
which have no re-checkable certificate here.
