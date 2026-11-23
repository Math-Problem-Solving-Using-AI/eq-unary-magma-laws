# 27. Rows of the four laws with only infinite models: 2,828 "does not imply", 16 "implies"

- Date: 2026-11-23
- Status label: the 2,828 non-implications are `z3-only` (as in step 16: that the structure satisfies law A is
  shown by z3 on all elements; that law B fails is checked by plain Python). The 16 implications are stored chains
  of replacement steps replayed by plain code (same level as step 19: `z3-only` level at most, no z3 used). Not
  Lean, not reviewed by a person. Same verdicts as the sibling repository eq-laws-without-small-models, which
  reached them with a different structure and different code.
- Commit(s): see `git log -- src/refute_nine_laws.py src/selftest_nine_laws.py src/compare_nine_laws_sibling.py results/refutations_nine_laws.json results/derivations_nine_laws.json steps/27-rows-of-four-infinite-laws.md`

## In plain words

1. **The question.** Nine laws have no small example: no table with 2 or 3 elements obeys them. In the stored table
   their rows (9 laws times 711 other laws = 6,399 pairs) say "open" (code 5). The sibling repository
   eq-laws-without-small-models answered all nine laws. This step brings in the answer for four of them, with a
   check of our own: for each of the four laws A, and each of the 711 other laws B, does A force B?

   Words used here:
   - A **structure** (also called a magma with a unary operation) is a set of elements with a two-input operation
     `*` and a one-input operation `f`. It may be finite or infinite.
   - A **law** is an equation such as `f(x*(y*z)) = y` that must hold for every choice of the letters.
   - Law A **implies** law B if every structure where A holds also has B holding. Infinite structures count.
   - A **model** of A is a structure where A holds. A **counterexample** (or **witness**) for "A implies B" is a
     model of A where B fails.
   - A law **collapses** if its only models have one element. The four laws here do not collapse: they have an
     infinite model (sibling repository). By a hand argument there, they have no finite model with 2 or more
     elements, so only an infinite structure can tell them apart from collapsing laws.
   - A **term** is a formal expression such as `F(g0)` or `P(g0,g1)`; different texts are different elements.
   - A **derivation** is a chain of steps, each replacing one piece of an expression by an equal one according to
     law A. If the chain leads from B's left side to B's right side, B holds wherever A holds.
   - **z3** is an automatic solver. `unsat` means it claims there is no case where the statement fails. **`z3-only`**
     labels an answer that rests on z3 with nothing else confirming that part.
   - **Code 5** in `results/status_matrix.npz` means "A is one of the 9 laws with no small model"; it is an open code.
   - A **mutation test** feeds a checker deliberately broken input to make sure it can say "no".

2. **What was done, in order.**
   1. **Looked at the nine laws.** Four of them, `(f(x)*y)*z = y` (law 135), `f((x*y)*z) = y` (law 336),
      `f(x*(y*z)) = y` (law 450) and `x*(y*f(z)) = y` (law 639), have the shape "a term = one of its letters", and
      the term cannot overlap with itself. That is exactly the case of step 16, where such a law read as a rewrite
      rule gives an infinite model T_A of formal terms. The other five laws do not have this shape (they are left
      for later queue items).
   2. **Ran the step 16 construction on the four rows** (`src/refute_nine_laws.py`). For each target B, both sides
      of B were computed in T_A with B's letters sent to different starting elements `g0, g1, ...`.
      - In 2,828 cases the two sides differ: B fails in T_A, so A does not imply B. These are stored as
        certificates in the format of step 16 (`results/refutations_nine_laws.json`).
      - In 16 cases (4 per law) the two sides are equal. Each B is law A with some letters made equal. The script
        stored the rewriting steps that made them equal as a derivation in the format of step 19
        (`results/derivations_nine_laws.json`). Each derivation has one step.
      Running the script again gave byte-identical files.
   3. **Checked with the existing checkers.** `src/check_term_rewriting.py` (step 16) and `src/check_derivations.py`
      (step 19) do not import the search. They required each pair to be in the "open" code 6; they now accept the
      two open codes, 5 and 6 (two-line change in each). For the four laws, z3 says `unsat` to "A fails somewhere in
      T_A" (all elements), and a plain Python sample agrees. All 2,828 certificates and all 16 derivations pass.
   4. **Mutation tests.** The step 16 selftest runs on the new file: 8 of 8 broken inputs rejected. The step 19
      selftest needs a chain of 3 steps or more, which the new file does not have, so a new script
      `src/selftest_nine_laws.py` corrupts the new derivations (changed substitution, position, direction, emptied
      chain, a refuted pair claimed as implied) and claims a pair that is not open (code 0) through both checkers:
      7 of 7 rejected. The step 19 selftest on its own file still passes (14 of 14).
   5. **Compared with the sibling repository** (`src/compare_nine_laws_sibling.py`, reads the sibling's
      `results/refutations_term_models.json`, last changed there on 2026-11-22). The sibling uses different
      structures (one starting element; for laws 336 and 450 its `f` leaves non-matching elements unchanged where
      ours keeps a formal `F(...)`). Same split: 2,828 refuted there and here, the same 16 not refuted there and
      derived here, 0 differences. The comparison script was tested on two corrupted copies of the sibling file
      (one certificate moved to "not refuted", one target number shifted): both reported problems.
   6. Ran every gate of `LOOP.md` and added the new checks to the gates and to CI.

3. **A small example.** A = `f(x*(y*z)) = y` (law 450), B = `f(x) = x` (law 1).
   - In T_A, a product `a*b` is always the formal term `P(a,b)`. `f(e)` is `F(e)`, except when `e` has the form
     `P(a,P(b,c))`: then `f(e)` is `b`.
   - A holds: for any elements a, b, c, `a*(b*c)` is `P(a,P(b,c))`, so `f(a*(b*c)) = b`.
   - B fails: `f(g0)` is `F(g0)`, because `g0` is not a product. `F(g0)` is not `g0`.
   - An implied target: B = `f(x*(x*x)) = x` is A with x, y, z all equal to x. The derivation is one step: replace
     `f(x*(x*x))` by `x` using A with x, y, z := x.
   - No finite table shows this: by the sibling's counting argument (a hand argument), a finite model of A has one
     element, and there every law holds.

4. **What it means and what it does NOT mean.**
   - It means: for the four laws 135, 336, 450 and 639, every one of their 2,844 pairs now has an answer with a
     machine check in this repository: 2,828 "does not imply" (`z3-only`) and 16 "implies" (replayed derivation).
     The answers agree with the sibling repository, reached by different code and slightly different structures.
   - It does NOT mean: Lean-checked, or reviewed by a person. That T_A satisfies A for every element rests on z3
     plus the step 16 hand argument. The "does not imply" answers are about all structures; over finite structures
     these laws (by the sibling's hand argument, not checked here) imply every law.
   - It does NOT change `results/status_matrix.npz`: those 2,844 pairs still say code 5 there. New codes would
     change a published format, which the owner decides (STATE.md, "Blocked").
   - The other 5 laws with no small model are not covered by this step: 3 collapse laws (2,133 pairs) and the 2
     laws with 4-element models (1,422 pairs, mostly settled by step 09) are the next queue items.

5. **How to re-check it.** From the repository root:
   - `python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json`
     prints `2828 certificates checked, from 4 source laws; ...`, `table control: ... 0 contradictions with the table`
     and `ALL PASS`.
   - `python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_nine_laws.json`
     prints `4 of 4 sources checked (16 replacement steps replayed)`, `16 open pairs derived (implied)` and `ALL PASS`.
   - `python src/selftest_nine_laws.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json results/derivations_nine_laws.json`
     prints `selftest: 7 of 7 corrupted inputs rejected` and `ALL PASS`.
   - With the sibling repository next to this one:
     `python src/compare_nine_laws_sibling.py data/laws_3.json results/refutations_nine_laws.json results/derivations_nine_laws.json ../eq-laws-without-small-models/results/refutations_term_models.json`
     prints four lines ending in `: 0` and `SAME VERDICTS`.

## Goal

Queue item 1 of `STATE.md`, first piece: give the rows of the four code 5 laws with an infinite term model an
answer with a machine check here, without changing `results/status_matrix.npz`.

## Command(s)

```
python src/refute_nine_laws.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json results/derivations_nine_laws.json
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json --selftest
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_nine_laws.json
python src/selftest_nine_laws.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json results/derivations_nine_laws.json
python src/compare_nine_laws_sibling.py data/laws_3.json results/refutations_nine_laws.json results/derivations_nine_laws.json ../eq-laws-without-small-models/results/refutations_term_models.json
```
plus every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz` (unchanged), the step 16 functions in `src/refute_by_rewriting.py`
(imported by the search, not by the checkers). For the comparison only: the sibling's
`results/refutations_term_models.json` (sibling commit `1119265`, 2026-11-22), read, not changed. z3 as in
`requirements.txt`.

## Output

- `results/refutations_nine_laws.json`: 2,828 certificates (707 per law), format of step 16.
- `results/derivations_nine_laws.json`: 4 sources, 16 pairs, one replacement step each, format of step 19.
- Rows skipped by the search (no overlap-free rule "term -> letter"): laws 110, 250, 257, 284, 415.
- `src/check_term_rewriting.py`, `src/check_derivations.py`: the open-pair check accepts codes 5 and 6.
- New: `src/refute_nine_laws.py` (search), `src/selftest_nine_laws.py` (mutation test, gate and CI),
  `src/compare_nine_laws_sibling.py` (comparison, needs the sibling, not in CI).

## Checks done (and what each one can and cannot catch)

- `check_term_rewriting.py` on the new file: re-derives each rule, re-checks "no overlap" with its own unification,
  recomputes both sides of B, and asks z3 whether A fails anywhere in T_A (`unsat` for all 4). Catches a wrong value,
  a wrong rule, a pair that is not open. Cannot catch an error shared by the hand argument and the z3 encoding.
- Its table control (all 81 overlap-free laws against the whole table): 0 contradictions. It ignores codes 5 and 6
  by design, so it says nothing about the new pairs.
- `check_derivations.py` on the new file: replays all 16 steps. Its small-model control is empty here (these laws have
  no model with 2 or 3 elements), so only the replay counts.
- Mutation tests: 8 of 8 (step 16 selftest on the new file), 7 of 7 (`selftest_nine_laws.py`), 14 of 14 (step 19
  selftest, unchanged file). The code check that was widened is exercised by two of the 7 (a code 0 pair).
- Comparison with the sibling: same split of all 2,844 pairs. Catches a disagreement in verdicts; does not re-check the
  sibling's certificates, and both repositories use the same 712 law texts (sibling step 12 checked that).
- Byte-identical rerun of the search.

## NOT verified

- That T_A satisfies A for every element rests on z3 (`unsat`) and the step 16 hand argument; no Lean, no person.
- The sibling's hand argument that these four laws have no finite model with 2 or more elements was not re-checked
  here; nothing in this step depends on it except the remark about finite structures.
- The sibling's own certificates were not re-run here; only their verdicts were compared.
- The rows of the other 5 code 5 laws (laws 110, 250, 257, 284, 415) are not covered by this step.
- `results/status_matrix.npz` and `src/query.py` do not report these answers (published format, owner's decision).
- No literature check for these 2,844 pairs in this step (the sibling's step 20 searched, shallowly, and found none of
  the non-implications stated anywhere).

## Surprises, errors, dead ends

- The step 19 selftest picks a pair whose chain has 3 steps or more and fails with an error when none exists; the
  one-step chains here needed their own mutation script instead of a change to that selftest.
- My first draft of the mutation script tested the widened code check with a made-up source whose fact 0 was not A;
  the checker rejected it earlier for that reason, so the code check was never reached ("ACCEPTED" by the filter I
  used). Rewritten to claim the pair (A, A), which reaches the code check; recorded in `docs/LOG.md`.

## Next

Queue: the 3 collapse laws (2,133 pairs) by the sibling's stored collapse derivations replayed here; then the 2 laws
with 4-element models (5 implications that rest on the ETP only).
