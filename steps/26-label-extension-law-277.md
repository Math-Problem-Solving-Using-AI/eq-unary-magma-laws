# 26. An infinite counterexample for `(x*y)*f(x) = y`: the last 4 open pairs are "does not imply"

- Date: 2026-11-23
- Status label: same level as steps 17 and 23 to 25, never higher than `z3-only`. The structure is infinite, so it
  cannot be re-checked by evaluating a finite table (`model-verified` is for finite tables only). What is machine
  checked: the rewrite rules of the base (plain Python: every rule shrinks terms, all 13 critical pairs join), the
  label lemma over all cases with labels up to 12 (plain Python), the same lemma for every model of law 277 (z3
  `unsat`, two calls), law 277 directly on 175 elements (30,625 pairs, plain Python), and the failure of each target
  law at the stored values (plain Python). The step from "rules shrink terms and critical pairs join" to "normal forms
  are unique" is a textbook theorem (Newman's lemma with the critical pair lemma), not re-proved here. Not Lean, not
  reviewed by a person, no literature check for these pairs.
- Commit(s): see `git log -- src/check_label_extension.py results/label_extension_277.json steps/26-label-extension-law-277.md`

## In plain words

1. **The question.** After step 25, only 4 pairs of laws were still open. All come from the law
   `(x*y)*f(x) = y` (law 277) and its mirror `f(x)*(y*x) = y` (law 408). Does law 277 force `x*(y*f(x)) = y`
   (law 632) and `x*(x*f(x)) = x` (law 574)? Does law 408 force their mirrors `(f(x)*y)*x = y` (law 128) and
   `(f(x)*x)*x = x` (law 122)? **Answer found here: no, in all 4 cases.**

   Words used here:
   - A **structure** (here also called a **magma with `f`**) is a set with a two-input operation `*` and a
     one-input operation `f`.
   - A **law** is an equation that must hold for every choice of its letters. A **model** of a law is a
     structure where it holds. Law A **implies** law B if every model of A is a model of B.
   - A **counterexample** (or **witness**) for "A implies B" is a model of A where B fails somewhere. One
     counterexample shows that A does **not** imply B.
   - The **mirror** of a law reads every product the other way round (`x*y` becomes `y*x`). If a structure
     is a counterexample for a pair, the same set with `x*y` read as `y*x` is a counterexample for the mirrored pair.
   - A **rewrite rule** such as `(x*y)*f(x) -> y` says "wherever you see the left pattern, replace it by the right
     one". A **normal form** is a formula that no rule can change any more.
   - A **critical pair** is a formula where two rules can be applied in two overlapping places. If both ways always
     end at the same normal form, and every rule makes formulas shorter, then every formula has exactly one normal
     form, whatever order the rules are applied in (a textbook result called Newman's lemma).
   - **z3** is an automatic solver. `unsat` from z3 means it proved the statement; `unknown` means it gave up. The
     label **`z3-only`** means nothing stronger than a solver or a plain-code check of an infinite construction
     backs the answer; it is not a Lean proof.

2. **What was done, in order.**
   1. **Started from the hand notes of step 20.** They said: a counterexample must be infinite; the values of `f`
      must themselves form a model of both laws 277 and 632; and `f` must have a "never reached" part. Step 20 also
      found that the 4 rules `(x*y)*f(x) -> y`, `x*(y*f(x)) -> y`, `y*f(x*y) -> f(x)`, `f(x)*f(y) -> f(x*y)`
      describe the free model of laws 277 and 632 together. Why: this gave the "values of `f`" part ready-made.
   2. **Read the rules found by completion of law 277 alone** (run again with 40 rules; it grows without end). In
      every rule, the value `x*(y*f(x))` behaves exactly like `y`, but the two are never made equal. Why: this
      suggested that a counterexample needs one more piece of information next to each value, something that can
      tell `x*(y*f(x))` apart from `y`.
   3. **Built the structure S** (a "labelled extension"). The base M is the set of normal forms of the 4 rules,
      written with one letter `g`. F is the part of M that starts with `f` (the values of `f`). An element of S is
      a pair (m, k): a base element m and a whole number k = 0, 1, 2, ... (the **label**), with k = 0 whenever m
      is in F. The operations:
      - `f(m, k) = (f(m), 0)`;
      - `(m, k)*(n, l)` has base part m*n, and label l + 1 if n is not in F; label 0 if m*n is in F; label
        k - 1 otherwise (never below 0).
      Think of the label as a counter: multiplying by an ordinary element adds 1, multiplying by a value of `f`
      takes 1 away again.
   4. **Why law 277 holds in S (the label lemma).** Take x = (m, k) and y = (n, l). The base part of `(x*y)*f(x)`
      is `(m*n)*f(m) = n`, because law 277 holds in M (it is rule 1). For the label: if n is not in F, then m*n
      is not in F either, so `x*y` has label l + 1 and multiplying by `f(x) = (f(m), 0)` takes 1 away: label l.
      If n is in F, then l = 0, and the result has base part n in F, so its label is 0. Either way the result is
      y. The step "if m*n is in F then n is in F" uses rule 4: if m*n = f(q), then n = (m*n)*f(m) = f(q)*f(m) =
      f(q*m), which is in F.
   5. **Why law 632 fails in S.** Take x = y = (g, 0). First `f(x) = (f(g), 0)`. Then `y*f(x)` has base part
      `g*f(g)` (no rule changes it, and it does not start with `f`) and label 0 (k - 1 = -1 is raised to 0). Then
      `x*(y*f(x))` has base part `g*(g*f(g)) = g` (rule 2) and label 0 + 1 = 1. So `x*(y*f(x)) = (g, 1)`, which is
      not y = (g, 0). The same computation is law 574 at x = (g, 0). Read with `x*y` as `y*x`, S satisfies law 408
      and the same values break laws 128 and 122.
   6. **Wrote a checker** (`src/check_label_extension.py`) that checks, in plain Python: rule 1 is law 277 as stored,
      rule 4 is `f(x)*f(y) = f(x*y)`, no rule starts with `f`, every rule shrinks formulas, all 13 critical pairs
      join; the label lemma over all 210 cases (which of m, n, m*n are in F, labels up to 12); law 277 directly at
      all 30,625 pairs of the 175 elements whose base formula has at most 7 symbols and whose label is at most 3;
      that law 408 is the mirror of law 277; that the 4 pairs are open in the table; that the stored values are
      elements of S; and that each target law gives two different elements there. Why: the lemma and the direct
      test are two different routes to "law 277 holds in S".
   7. **Asked z3 for a second opinion on the lemma** (`--z3`, not part of the gate). z3 proved
      `f(x)*f(y) = f(x*y)` from law 277 (`unsat`), and then the label lemma for every model of law 277 in which
      that fact holds (`unsat`, 0.3 s). Asked the lemma directly without the fact, it answered `unknown` after 60 s.
      With a broken label rule (adding 0 or 2 instead of 1, or taking 0 away) it did not prove the lemma
      (`unknown`), as it should not.
   8. **A check of the checker** (`--selftest`): 18 corrupted inputs (rule 1 changed, rules 2, 3 or 4 removed, a
      wrong right side, a reversed rule, an extra rule starting with `f`, the counter changed in three ways, a value
      where law 632 holds, a label on a value of `f`, a value that is not a normal form, a missing value, a pair that
      is not open, a wrong source law, a flipped mirror flag, a value inside F). All 18 rejected, each for the
      intended reason (read one by one). The direct test alone also rejects the three broken counters.

3. **A small example.** The counter at work, with x = y = (g, 0):

   | step | value | why |
   |------|-------|-----|
   | `f(x)` | (f(g), 0) | `f` always gives label 0 |
   | `y*f(x)` | (g*f(g), 0) | right factor is a value of `f`: label 0 - 1, kept at 0 |
   | `x*(y*f(x))` | (g, 1) | right factor is not a value of `f`: label 0 + 1; `g*(g*f(g))` rewrites to `g` |

   Law 632 wants `x*(y*f(x)) = y = (g, 0)`, but the result is (g, 1). Law 277 survives because it always multiplies
   by `f(x)` last, which takes back the 1 just added: `(x*y)*f(x)` with x = y = (g, 0) is
   ((g*g)*f(g), 1 - 1) = (g, 0) = y.

4. **What it means and what it does NOT mean.**
   - It means: law 277 does not imply law 632 or law 574, and law 408 does not imply law 128 or law 122. With this,
     every one of the 506,232 pairs of the table has an answer with a machine check in this repository.
   - It does NOT mean these 4 answers are proved in Lean, or reviewed by a person. The label is `z3-only` level.
   - The checker tests law 277 directly only on small elements (a bounded test); for all elements it relies on the
     label lemma, which is checked over every case by plain code (labels up to 12) and in general by z3, and on
     the textbook fact that shrinking rules with joining critical pairs give unique normal forms.
   - It does NOT change the stored table (`results/status_matrix.npz`): the 4 pairs keep code 6 there until the
     owner decides on new codes (STATE.md, "Blocked").
   - No literature check was done for these pairs; nothing here claims they are new.

5. **How to re-check.** From the repository root:

   ```
   python src/check_label_extension.py data/laws_3.json results/status_matrix.npz results/label_extension_277.json
   ```

   Expected (about 1 minute): `rules: 4, all shrink terms, 13 critical pairs, all join`, `label lemma: 210 cases
   (labels up to 12), all hold`, four lines `law ... at ...: (g, 1) != (g, 0)`, `bounded test: 67 normal forms ...,
   law 277 at 30625 pairs, 0 failures`, and `ALL PASS`. Add `--z3` for the z3 lines (both `unsat`). Add
   `--selftest` instead for `selftest: 18 of 18 corrupted inputs rejected` and `ALL PASS`.

## Goal

Queue item 1 (open pairs, piece 4f): the 4 pairs of `(x*y)*f(x) = y` (targets 574, 632) and its mirror
`f(x)*(y*x) = y` (targets 122, 128). Find an infinite counterexample or a derivation.

## Command(s)

- Scratch (not kept): completion of law 277 alone with `src/complete_open.py` classes, 40 rules, size 20,
  precedence f > *: `rule limit`, 41 rules printed and read. A prototype of S (normal forms up to 7 symbols,
  labels up to 3): law 277 0 failures, law 632 at (g, 0) gives (g, 1).
- `python src/check_label_extension.py data/laws_3.json results/status_matrix.npz results/label_extension_277.json --z3`
- `python src/check_label_extension.py data/laws_3.json results/status_matrix.npz results/label_extension_277.json --selftest`
- Scratch: `z3_lemma` with broken counters (push 0, push 2, pop 0): second answer `unknown` each; the direct test
  with push 0, push 2, pop 0, pop 2 on elements up to 5 symbols: failures found each time.
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`. The 4 base rules from step 20 (`results/extra_laws_277.json`, key
`"632"`, rules seen in step 20's scratch run). Python 3.12.10, z3 5.4.1 (only for `--z3`), Windows 10. No web access.

## Output

- `results/label_extension_277.json`: the 4 base rules, the generator `g`, the label rule (push 1, pop 1), the
  bounds of the direct test, and the 4 pairs with the values where the target fails.
- `src/check_label_extension.py`: checker (gate in `LOOP.md` and CI, with `--selftest`).
- Open pairs: 0 (were 4). No change to `results/status_matrix.npz` or any other result file.

## Checks done (and what each one can and cannot catch)

- Rule checks (shrinking, 13 critical pairs join, rule 1 = law 277, rule 4 present, no rule starts with `f`). Catch
  a base that is not a well-defined structure or not a model of law 277. Cannot catch a bug in the textbook theorem
  they rely on, or in the critical pair code shared by the checker (no second implementation here; the same 4 rules
  were found complete by a different program in step 20).
- Label lemma, 210 cases, plain code. Catches a wrong label rule. Labels above 12 are covered by the arithmetic
  (l + 1 - 1 = l) and by z3, not by the enumeration.
- z3: two `unsat` answers. A second method for the lemma, independent of the base rules.
- Direct test of law 277 on 175 elements. Catches mistakes in the lemma's hand argument on small elements.
  Cannot cover all elements.
- Target failures: computed by plain evaluation at the stored values, for S and for the mirrored S.
- Selftest 18 of 18, each read for its reason.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs, re-verified,
  0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent; `selftest_verifiers.py` ALL PASS;
  `check_z3_retry.py`, `check_term_rewriting.py`, `check_completion.py` (both files), `check_derivations.py`,
  `check_greedy_eq73.py`, `check_greedy_eq118.py`, `check_asterix_eq65.py`, each with its selftest: ALL PASS.

## NOT verified

- Not Lean. The theorem "shrinking rules plus joining critical pairs give unique normal forms" is used, not
  re-proved; the critical pair code is the checker's own, written for this step.
- The direct test covers only elements with at most 7 symbols and labels up to 3.
- z3's two `unsat` answers were not replayed by another prover.
- No person has reviewed the label lemma.
- No literature check for these 4 pairs (whether this construction, or the answer, is known).
- `query.py` does not read the new file; it still says "open" for these 4 pairs. The stored table is unchanged.

## Surprises, errors, dead ends

- Surprise: after steps 15 and 20 (no finite counterexample possible, no extra law of size up to 4 helps, z3 gave
  up), the counterexample is short to write down. The idea came from reading the rules completion produced: one
  value behaves like another in every rule but is never made equal to it. A hidden counter can tell them apart.
- Dead end in this step: z3 could not prove the label lemma directly in 60 s (two encodings tried: "in F" as "there
  is a q with f(q) = m", then as a predicate with two axioms). Giving it the fact `f(x)*f(y) = f(x*y)`, which z3
  proved separately, made it immediate.
- A command was started without the 10-minute foreground limit and went to the background; it was stopped and run
  again in the foreground (`docs/LOG.md`).
- Lesson (for the hub, in `docs/LOG.md`): when completion produces an endless family in which some value `u`
  behaves like `v` in every rule, try a structure where elements carry an extra counter that tells `u` from `v`.

## Next

Every pair of the table now has an answer with a machine check. The finish line in `LOOP.md` is checked in
`STATE.md`.
