# 16. Infinite term structures settle 682 of the 872 open pairs: "does not imply"

- Date: 2026-11-23
- Status label: each of the 682 non-implications is `z3-only`. That the structure satisfies law A is
  shown by z3 on all elements (plus a short hand argument, below); that law B fails in it is checked by
  plain Python. Not `model-verified` (that label is for finite tables), not Lean, not reviewed, no
  literature check for these pairs.
- Commit(s): see `git log -- src/refute_by_rewriting.py src/check_term_rewriting.py results/refutations_term_rewriting.json steps/16-infinite-term-structures.md`

## In plain words

1. **The question.** 872 pairs of laws were still open: for each pair (A, B) we did not know whether
   law A forces law B. No finite counterexample table was found (up to 5 elements in earlier steps,
   and none of 6 or 7 elements in step 15). Can an *infinite* structure show that A does not force B?

   Words used here:
   - A **structure** is a set of elements with a two-input operation `*` and a one-input operation `f`.
     It may be finite or infinite. (With no other assumptions it is sometimes called a magma with a
     unary operation.)
   - A **law** is an equation such as `f(x)*y = x` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding. Infinite structures
     count: the question in `README.md` is about all structures.
   - A **counterexample** (or **witness**) for "A implies B" is a structure where A holds and B fails.
     One is enough to show that A does NOT imply B.
   - A **term** is a formal expression written with letters and the two operations, such as
     `f(x*y)`. Two different terms are different texts; nothing is calculated.
   - **z3** is an automatic solver. Asked "is there a choice of elements where A fails?", it answers
     `sat` (yes), `unsat` (it claims there is none) or `unknown` (it gave up).
   - **`z3-only`** labels an answer that rests on z3, with nothing else confirming that part.
   - **Code 6** in the stored table `results/status_matrix.npz` means "open".
   - A **mutation test** feeds a checker deliberately broken input to make sure it can say "no".

2. **What was done, in order.**
   1. **Noticed a common shape.** Every one of the 872 open pairs has a source law A of the form
      "a term = one letter that occurs in it", for example `f(x)*y = x` or `f((x*y)*z) = z`. Read such a
      law as a **rewrite rule**: wherever the pattern on the left appears, it may be replaced by the
      letter's value. Each replacement makes the expression shorter, so replacing always stops.
   2. **Built a structure from the rule**, called T_A. Its elements are formal terms over infinitely
      many starting elements `g0, g1, g2, ...`, written with `F(...)` (stands for `f`) and `P(...,...)`
      (stands for `*`). To apply `f` to an element `e`, write `F(e)`; to multiply `d*e`, write `P(d,e)`.
      If the new term matches the left side of the rule, replace it by what the rule says; otherwise
      keep it. T_A is infinite.
   3. **Found when T_A satisfies A.** If no smaller piece of the rule's left side can match the rule's
      left side itself (no **overlap**), then T_A satisfies A. Hand argument (a lead, see "NOT verified"):
      put any elements into A's letters and compute the left side from the inside out. Every inner
      piece stays a plain formal term, because a replacement there would need exactly such an overlap.
      At the top the whole left side matches the rule and is replaced by the value of the letter, which
      is the right side of A. For 36 of the source laws (682 open pairs) the rule has no overlap; for
      the other 26 source laws (190 pairs) it has one, and those were not tried.
   4. **Searched** (`src/refute_by_rewriting.py`): for each of the 682 pairs, compute both sides of B in
      T_A with B's letters sent to `g0, g1, ...`. In all 682 the two sides came out as different terms,
      so B fails in T_A, and A does not imply B. Running the search again gave a byte-identical file.
   5. **Wrote a separate checker** (`src/check_term_rewriting.py`, it does not import the search). For
      each certificate it reads A and B from their texts, re-derives the rule, re-checks that it has no
      overlap (with its own unification code), recomputes both sides of B and compares with the stored
      values, which must differ. For each of the 36 source laws it asks z3 whether A fails anywhere in
      T_A, with the terms given to z3 as a datatype, so this covers every element, not just small ones:
      z3 says `unsat` (A never fails) for all 36. It also evaluates A on all assignments of the 38 terms
      with at most 2 operations over `g0, g1` in plain Python.
   6. **Checked against the rest of the table.** For all 81 laws of the list whose rule has no overlap
      (not only the 36 sources of open pairs), the checker compares T_A's verdict on each of the 712
      targets with the stored table: never "fails in T_A" where z3 proved an implication (codes 3 and 4),
      never "holds" where a finite table refutes it (codes 1 and 2). 0 contradictions in 57,672 pairs.
   7. **Mutation test**: 8 broken inputs (changed values, swapped laws, shifted key, a non-distinct
      witness, an entry for a rule with an overlap, a checker whose T_A never rewrites, and the z3
      encoding on overlapping rules); all 8 rejected. A corrupted file makes the checker exit with 1.
   8. Ran every gate of `LOOP.md` and added the checker to the gates and to CI.

3. **A small example.** A = `f(x)*y = x`, B = `f(x*x) = x` (open pair 33,36 in law ids).
   - The rule is `f(x)*y -> x`. In T_A, `f(c)` is `F(c)`, and the product `F(c)*e` would be the term
     `P(F(c),e)`, which matches the rule and is replaced by `c`. So `f(c)*e = c` for every `c` and `e`:
     A holds.
   - B with `x = g0`: `x*x = P(g0,g0)` (its left part `g0` is not of the form `F(...)`, so no replacement),
     and `f(x*x) = F(P(g0,g0))`. That is not `g0`, so B fails.
   - Why finite tables could not show this (step 15): A makes `f` one-to-one, which in a finite set forces
     `f` to reach every element, and then B follows. In T_A, `f` never reaches `g0`, which is only
     possible because T_A is infinite.

4. **What it means and what it does NOT mean.**
   - It means: for 682 of the 872 open pairs, A does NOT imply B, with an explicit infinite
     counterexample that anyone can recompute. Label `z3-only`: that T_A satisfies A rests on z3 (all
     elements) and the hand argument above; B's failure is plain arithmetic on terms.
   - It does NOT mean these laws are independent in finite structures. For many of these pairs every
     finite structure satisfying A may satisfy B (as in the example); "implies" here is about all
     structures, as the README asks.
   - It does NOT settle the other 190 open pairs: their source laws have overlaps, so T_A need not
     satisfy A (the checker's mutation test shows one where it fails). 18 of them have no `f` and the ETP
     answers them; 172 pairs with `f` have no answer.
   - The stored table `results/status_matrix.npz` was not changed: the 682 pairs stay code 6 there
     (a new code changes a published format, which is the owner's decision, see `STATE.md`, Blocked).
     `src/query.py` does not read the new file yet.

5. **How to re-check.**

   ```
   python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_term_rewriting.json
   ```

   Expected (a few seconds): `682 certificates checked, from 36 source laws; ...`, then
   `table control: 81 overlap-free source laws, 57126 targets fail in T_A, 546 hold; 0 contradictions with the table`,
   then `ALL PASS`. The mutation test adds `--selftest` at the end; expected
   `selftest: 8 of 8 corrupted inputs rejected` and `ALL PASS`.
   To regenerate the certificates:

   ```
   python src/refute_by_rewriting.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/refutations_term_rewriting.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
   ```

   Expected: `open pairs: 872`, `refuted: 682`, `source rule has an overlap (not tried): 190`.

## Goal

Open-pairs item, piece 4 ("finite yes, infinite no"): infinite counterexamples with a certificate that
code can check. Done here for every open pair whose source law gives a rule without overlap.

## Command(s)

```
python src/refute_by_rewriting.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/refutations_term_rewriting.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_term_rewriting.json
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_term_rewriting.json --selftest
```

plus every gate of `LOOP.md`, a regeneration into the scratch directory compared byte for byte, and a
corrupted copy of the certificate file (one stored value changed) to check the exit code (1).

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json`, `results/z3_open_retry.json`,
`results/witnesses_ffree_models.json`, `results/witnesses_etp_magmas.json` (the open-pair list is computed
as in step 15). Python 3.12.10, z3 `5.4.1` (version string as recorded in step 15), Windows 10.
z3 time limit 60 s per source law (each answered in under a second).

## Output

- `src/refute_by_rewriting.py` (search), `src/check_term_rewriting.py` (checker, with `--selftest`).
- `results/refutations_term_rewriting.json`: 682 certificates `"a,b": {A, B, rule, witness, B_left, B_right}`
  (law index = id minus 1). All 682 have `f` in A.
- By step 15's z3 answers at sizes 6/7, the 682 were: 336 `unsat`/`unsat`, 208 `unsat`/`unknown`,
  138 `unknown`/`unknown`.
- Still open: 190 pairs from 26 source laws whose rules overlap: 172 with `f` (no answer; largest rows
  `(x*y)*f(z) = z`, `f(f(x)*y) = y`, `f(x)*(y*z) = x`, `f(x*f(y)) = x` with 31 each, `f(x*x)*y = x`,
  `x*f(y*y) = y` with 10 each), 18 without `f` (ETP answer, step 08).

## Checks done (and what each one can and cannot catch)

- Recomputation of B's two sides at the witness, against the stored values. Catches a wrong value or a
  search bug. Cannot catch an error in the idea that T_A satisfies A; that is the next two checks.
- z3 on the datatype of all terms: "A fails somewhere in T_A" is `unsat` for each of the 36 source laws.
  Covers every element. It is z3's answer only. The mutation "never rewrite" makes z3 say `sat`, and for
  the overlapping law `(x*x)*y = x` z3 finds that A fails in T_A, so the encoding can say "fails".
- Plain evaluation of A on all assignments of the 38 terms with at most 2 operations over `g0, g1`. A
  sample, not all elements; catches a gross error independently of z3.
- Overlap check with the checker's own unification code (different code from the search). The search and
  the checker agree on all 62 source laws of open pairs (36 without, 26 with overlap).
- Table control: 81 overlap-free laws, 57,672 pairs, 0 contradictions with the finite counterexamples
  (codes 1, 2) and the z3 implications (codes 0, 3, 4). Catches a T_A that refutes a z3-proved implication.
  Cannot catch anything on the open pairs themselves, where the table has no answer.
- Every certificate's pair is code 6 and its texts are those of `data/laws_3.json` at its key.
- Mutation test 8 of 8 rejected; exit code 1 on a corrupted file.
- Regeneration byte-identical.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177
  small refutations re-verified, 0 failed; 708, 1,417, 2 and 0 certificates, 0 failed; status table
  consistent (counts unchanged); `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and
  selftest ALL PASS.

## NOT verified

- The hand argument that T_A satisfies A when the rule has no overlap is not machine-checked as an
  argument. Each of the 36 instances is checked by z3 (`z3-only`) and on a finite sample in plain Python.
- z3's datatype answers were not confirmed by a second prover.
- That z3's datatype with generators `G(Int)` is exactly the structure T_A (free terms, distinct terms
  distinct) is how z3 documents datatypes as we understand it; we did not re-read z3's documentation in
  this step.
- The checker was written in the same session as the search, by the same author, and is not reviewed.
  It shares the law parser `src/check_laws_text.py` with `src/verify_witnesses.py`.
- The checker's branch "both sides of B are equal in T_A" is not reached by any mutation (every mutation
  that could reach it is stopped earlier by another guard).
- The 190 pairs whose source rules overlap were not tried. The 546 "holds in T_A" verdicts of the table
  control (implications obtained by rewriting) were not stored as derivations.
- No literature check for any of the 682 pairs.
- `results/status_matrix.npz` and `src/query.py` do not use the new file.

## Surprises, errors, dead ends

- z3 asked for an infinite model directly (integers as elements, `f` and `*` unknown functions) answered
  `unknown` in 10 s for `f(x)*y = x` => `f(x*x) = x`. Building the structure from the law itself was the
  way through, and it took seconds for all 682 pairs.
- The first version of the search matched the rule (written with `f` and `m`) against element terms
  written with `F` and `P`, which can never match; caught while writing it, before any run. Elements are
  now kept in the law's own encoding and only printed with `F` and `P`.
- The first mutation "send all witness letters to g0" was accepted: it was applied to a certificate whose
  B has one letter, so it changed nothing. Same lesson as before: check that a mutation changes something.
  It now picks a certificate with two or more letters and is rejected.

## Next

The 190 open pairs whose source rules overlap: complete those rules (add the equations their overlaps
produce, Knuth-Bendix style) and, where this ends in a rule set without unresolved overlaps, build T_A from
it the same way. Start with the four rows of 31 pairs each.
