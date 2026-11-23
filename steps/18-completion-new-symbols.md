# 18. Completion with new symbols: 32 open pairs with `f` are implications

- Date: 2026-11-23
- Status label: same level as step 17, the `z3-only` level at most (no z3 is used). Each of the 32 answers
  is "implies", and each rests on a chain of replacement steps from A that plain code replays in full, plus
  the textbook fact that defining a new symbol by a term adds no new equations between old terms. The
  ladder in `docs/shared/VERIFICATION_PROTOCOL.md` has no rung for this; the loop keeps the step 17
  convention (`docs/LOG.md`, "Decisions taken by the loop", run 8). Not Lean, not reviewed, no literature
  check for these pairs.
- Commit(s): see `git log -- src/complete_new_symbols.py src/check_completion.py results/completions_new_symbols.json steps/18-completion-new-symbols.md`

## In plain words

1. **The question.** After step 17, 57 pairs of laws (A, B) were still open: we did not know whether law A
   forces law B. 40 of them involve `f`. For their source laws A, the method of step 17 stopped at an
   equation it could not turn into a rule, such as `f(x)*z = f(x*x)`. Can that obstacle be removed?

   Words used here (most as in step 17):
   - A **structure** is a set with a two-input operation `*` and a one-input operation `f`. A **law** is an
     equation such as `f(f(x)*y) = x` that must hold for every choice of its letters. A **model** of a law
     is a structure where it holds.
   - Law A **implies** law B if every model of A is a model of B. One model of A where B fails (a
     **counterexample**) shows that A does NOT imply B.
   - A **term** is a formal expression such as `f(x*y)`. In the files, `m(s,t)` stands for `s*t` and
     `v0, v1, ...` for letters.
   - A **rewrite rule** `l -> r` allows replacing any piece of the shape `l` by the matching `r`.
     **Completion** (the Knuth-Bendix method) adds new rules until the order of replacements never matters.
     **KBO** (Knuth-Bendix order) is a fixed way to compare terms, mainly by size; when every rule makes
     terms smaller in it, replacing always stops.
   - A **new symbol** (here `h0`, `h1`, ...) is a name for a value that is already determined by A. Its
     **definition** says what it stands for, for example `h0(x) = f(x*x)`.
   - **z3** is an automatic solver; **`z3-only`** labels an answer that rests on such a tool alone.
     **Code 6** in `results/status_matrix.npz` means "open". A **mutation test** gives a checker broken
     input on purpose, to make sure it can say "no".

2. **What was done, in order.**
   1. **Looked at why step 17 stopped.** The equation `f(x)*z = f(x*x)` has the letter `z` on the left only.
      Neither side can be turned into the other by a rule: a rule must not create letters from nothing,
      and replacing `f(x*x)` by `f(x)*z` would do that. But the equation says something useful: the value
      `f(x)*z` does not depend on `z` at all.
   2. **Gave that value a name.** A new symbol `h0(x)` is defined as `f(x*x)`, and the two rules
      `f(x)*z -> h0(x)` and `f(x*x) -> h0(x)` are added. In general, for an equation `s = t` whose sides
      share the letters V but each has letters of its own, the definition is `h(V) = s` with the other
      letters of `s` replaced by the first letter of V. Such a definition only names something; it cannot
      make A say more than it already says about `*` and `f` (a standard fact of logic).
   3. **Ran completion again** (`src/complete_new_symbols.py`, built on step 17's code) for the 19 source
      laws whose completion had stopped, with the same limits (40 rules, terms of 14 symbols). Every new
      equation is stored with the chain of replacements, starting from A and the definitions, that proves it.
   4. **Result:** 8 of the 19 source laws now complete, all with `f`, with 1 or 2 new symbols each. They are
      the sources of 32 of the 40 open pairs with `f`. In each of the 32 pairs, both sides of B simplify to
      the same thing: **A implies B, 32 times.** No pair came out "does not imply".
   5. **Extended the checker** (`src/check_completion.py`, which does not import the search). It now
      accepts definitions, but only if the symbol is new, its inputs are distinct letters, the defining term
      uses only those letters and symbols defined before, and every symbol used anywhere is defined before
      use. It replays every chain, checks each rule shrinks in its own KBO code, recomputes every overlap,
      and recomputes the verdict of each pair. The step 17 file still passes unchanged.
   6. **Checked against everything already known.** For the 8 completed sources, the verdict on all 712
      targets each (5,696 pairs, 216 "implies") contradicts no finite counterexample (codes 1, 2) and no
      z3 implication (codes 0, 3, 4). Step 15 had already found no counterexample table of 6 or 7 elements
      for any of the 32 pairs (28 of them `unsat` at both sizes), which fits "implies".
   7. **Mutation test**: 15 broken inputs, among them 5 new ones about definitions (a definition with a
      letter not on its left side, a second definition of the same symbol, a renamed symbol, a precedence
      missing the new symbols, a derived equation passed off as a definition). All 15 rejected. A corrupted
      file makes the checker exit with 1. Running the search again gave a byte-identical file.
   8. **Tried higher limits for the rest.** The 4 sources that stopped at the size limit with `f`
      (277 `(x*y)*f(x) = y`, 408 `f(x)*(y*x) = y`, 483 `f(x*y)*x = y`, 704 `x*f(y*x) = y`, 2 open pairs
      each) were retried in a scratch run with terms up to 24 symbols and 60 rules: all stop at 60 rules.
      Their completion seems to grow without end. These 8 pairs stay open.

3. **A small example.** A = `f(f(x)*y) = x` (law 354), B = `f(f(x*y)) = x` (law 359).
   - In A put `f(x)*y` in place of `x`: `f(f(f(x)*y)*z) = f(x)*y`. Inside, `f(f(x)*y)` is `x` by A, so
     `f(x*z) = f(x)*y` for all `x`, `y`, `z`.
   - The left side does not depend on `y`, the right side not on `z`. So both are one value that depends
     only on `x`. Call it `h0(x)`; it equals `f(x*x)`.
   - Now A reads `f(h0(x)) = x`, and `f(x*y)` is `h0(x)`. So `f(f(x*y)) = f(h0(x)) = x`, which is B.
   - The search found an equivalent chain by itself and stored it; its final rules are `h0(f(x)) -> x`,
     `f(h0(x)) -> x` and `x*y -> h0(h0(x))`, and the checker replays every step. The file has
     this pair as `"353,358"` (law index = law id minus 1).

4. **What it means and what it does NOT mean.**
   - It means: 32 more open pairs are answered "implies", each by a chain of replacements that plain code
     replays step by step. All 40 pairs with `f` in queue item 1 except 8 now have an answer.
   - It does NOT mean machine-proved from first principles: the fact that a definition adds nothing new is
     used as textbook logic, not machine-checked, and the checker is by the same author as the search. That
     is why the label stays at the `z3-only` level. No Lean, no second prover.
   - It does NOT settle the 8 pairs whose sources keep growing (277, 408, 483, 704), nor the 17 pairs
     without `f` (queue item 2). "Completion did not stop" says nothing about whether those implications
     hold.
   - The stored table `results/status_matrix.npz` was not changed (still code 6; a new code is the owner's
     decision, `STATE.md`, Blocked). `src/query.py` does not read the new file.

5. **How to re-check.**

   ```
   python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_new_symbols.json
   ```

   Expected (about a second): `8 of 8 rule sets checked (derivations, KBO, critical pairs, A joins)`,
   `32 open pairs: 0 fail in T_R (not implied), 32 derived (implied)`,
   `table and ETP control: 5696 pairs, 5480 fail, 216 hold`, `ALL PASS`. Add `--selftest`:
   `selftest: 15 of 15 corrupted inputs rejected`, `ALL PASS`. To regenerate (about 5 seconds):

   ```
   python src/complete_new_symbols.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/completions_new_symbols.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json results/refutations_term_rewriting.json results/completions_open.json
   ```

   Expected: one line per source law and precedence, then `open pairs: 57; from sources with an overlap: 57`,
   `sources completed: 8 of 19`, `pairs whose source did not complete: 25`, `B holds in T_R: 32`.

## Goal

Queue item 1 (open pairs, piece 4c): the 40 open pairs with `f` whose completion stopped in step 17. Try
completion with a new symbol for equations with a letter on one side only, and higher limits for 277 and 408.

## Command(s)

The commands under "How to re-check" (with `--selftest`), every gate of `LOOP.md`, a regeneration into the
scratch directory compared byte for byte, a corrupted copy (one stored normal form changed, exit code 1), and
the scratch retry with limits 24 symbols and 60 rules for 277, 408, 483 and 704 (about 4 minutes, not kept).

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json`, `results/z3_open_retry.json`,
`results/witnesses_ffree_models.json`, `results/witnesses_etp_magmas.json`,
`results/refutations_term_rewriting.json`, `results/completions_open.json` (its 133 pairs count as decided).
Limits: 40 rules, 14 symbols per term, 4,000 equations; precedences `f > *` then `* > f`, new symbols below
both in order of creation. Python 3.12.10, Windows 10. No z3.

## Output

- `src/complete_new_symbols.py` (search). `src/check_completion.py` extended (definitions, general
  precedence, 5 new mutations); new gate lines in `LOOP.md`, `README.md` and CI.
- `results/completions_new_symbols.json`: same format as `results/completions_open.json`, with precedence
  strings such as `f > * > h0 > h1` and definition facts `{"left", "right", "chain": null, "definition": true}`.
- Completed sources (law id, new symbols, pairs): 354 `f(f(x)*y) = x` (1, 2), 455 `f(x*f(y)) = y` (1, 2),
  466 `f(x*x)*y = x` (2, 10), 485 `f(x*y)*y = x` (1, 2, with `* > f`), 489 `f(x*y)*z = x` (2, 2),
  691 `x*f(x*y) = y` (1, 2, with `* > f`), 707 `x*f(y*y) = y` (2, 10), 712 `x*f(y*z) = z` (2, 2).
  All 32 pairs: `holds`.
- Not completed: 4 sources with `f` (277, 408 at the term size limit; 483, 704 at the term size limit after
  1 new symbol), 8 open pairs; 7 sources without `f`, 17 pairs (term size limit, as in step 17).
- By step 15's z3 answers at sizes 6/7, the 32 were 28 `unsat`/`unsat`, 2 `unsat`/`unknown`,
  2 `unknown`/`unknown`; the 8 left are 6 `unknown`/`unknown`, 2 `unsat`/`unknown`.

## Checks done (and what each one can and cannot catch)

- Replay of every derivation, with definitions as the only facts without a chain. Catches an underived
  rule or a wrong step. Cannot catch an error in `parse_law` (shared, itself a gate).
- Definition checks (new symbol, distinct letters as inputs, no letter outside the left side, only symbols
  defined before; every symbol defined before use; precedence lists exactly the symbols used). Catches the 5
  definition mutations. Relies on the conservativity of explicit definitions (textbook, not machine-checked).
- KBO, critical pairs and "A joins" as in step 17 (needed only for "does not imply" verdicts, of which there
  are none here; still checked).
- Control: 5,696 verdicts against codes 0 to 4 of the table: 0 contradictions.
- Mutation test 15 of 15 on the new file, 10 of 10 on the step 17 file (unchanged output); exit code 1 on a
  corrupted file; regeneration byte-identical.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs;
  335,177 small refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table
  consistent; `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS;
  `check_term_rewriting.py` ALL PASS and selftest 8 of 8; `check_completion.py` on both files ALL PASS.

## NOT verified

- That explicit definitions are conservative is used as a textbook fact, not machine-checked, and no source
  was re-read for its exact statement in this step.
- The critical pair lemma, Newman's lemma and KBO termination (step 17) are again not machine-checked; for
  the 32 "implies" answers they are not needed (the derivations alone carry them).
- The checker was extended in the same session as the search was written, by the same author, not reviewed.
- No second prover, no Lean, no literature check for the 32 pairs. z3 was not asked to confirm them.
- The 8 pairs from 277, 408, 483, 704 and the 17 pairs without `f` are not decided. The scratch retry with
  higher limits was not kept as a file.
- One completed rule set (466, and likewise 707) keeps a redundant rule (`m(v86,v86) -> h1(v86)` is an
  instance of `m(v86,v88) -> h1(v86)`); harmless (its overlaps join), not cleaned up.
- `results/status_matrix.npz` and `src/query.py` do not use the new file.

## Surprises, errors, dead ends

- All 32 answers are "implies", although z3 with 30 seconds per pair proved none of them (steps 13, 14). The
  derivations are short once the "does not depend on this letter" values get names.
- Mutation slip caught: the old mutation "each source with only its own rule" was rejected on the new file for
  the wrong reason (precedence listing unused symbols). It now keeps only `f` and `*`, and the critical pair
  check rejects all 8 sources as intended.
- Dead end: higher limits (24 symbols, 60 rules) for 277, 408, 483, 704 do not complete; the rule sets keep
  growing.

## Next

The 8 pairs from 277, 408, 483, 704 need another idea (for example a model built by hand from the
growing rule pattern, or a derivation search aimed at the target); then the 17 pairs without `f` (queue item 2).
