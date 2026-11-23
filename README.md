# Which short laws imply which? One binary and one unary operation

> Part of [math-curiosity](https://github.com/Math-Problem-Solving-Using-AI/math-curiosity): open, reproducible experiments on equational laws, one repository per problem.
> **LLMs and tools:** read [`llms.txt`](llms.txt). **Autonomous sessions:** [`LOOP.md`](LOOP.md) and [`STATE.md`](STATE.md). License: Apache-2.0.
> **Look up any pair of laws:** `python src/query.py "x*y = x" "x*(y*z) = x"`

## The answer in plain words

1. **The question.** Take a set with two operations: `*`, which combines two elements into one, and `f`, which turns
   one element into one element. Nothing else is assumed. Such a set is called a **structure**. A **law** is an
   equation, such as `x*y = x`, that must hold for every choice of the letters. Law A **implies** law B when every
   structure where A holds also has B holding. The question: for every ordered pair of different laws with at most 3
   symbols `*` and `f` (712 laws, 712 x 711 = 506,232 pairs), does A imply B?

2. **The answer.** Every one of the 506,232 pairs has an answer, and each answer has a machine check that the
   independent checks below re-run:

   | Answer | Pairs | How it was checked | Label |
   |--------|------:|--------------------|-------|
   | does not imply | 337,304 | a small table (2 to 6 elements) where A holds and B fails, re-checked by plain code that tries every choice of the letters | `model-verified` |
   | does not imply | 3,662 | an infinite structure where A holds and B fails; plain code checks most of it, but parts rest on z3 or on Lean proofs of the outside Equational Theories Project that were read, not re-run | `z3-only` level |
   | implies | 163,074 | the solver z3 found a proof (147,177 of them because A forces a one-element structure, where every law holds) | `z3-only` |
   | implies | 2,192 | a stored chain of replacement steps from A to B, replayed by plain code | `z3-only` level at most |
   | **total** | **506,232** | 340,966 "does not imply", 165,266 "implies" | |

   Words used in the table: **z3** is a computer program (an SMT solver) that searches for proofs and
   counterexamples. **`model-verified`** and **`z3-only`** are labels from `docs/shared/VERIFICATION_PROTOCOL.md`:
   the first means an explicit counterexample checked by plain code; the second means we trust z3, or a check of
   about the same strength, without an independent proof.

3. **A small example.** A = `x*y = x`, B = `x*y = y`. Take the 2 elements {0, 1} with `x*y = x` for all x, y (and
   `f` sending both to 0). A holds by definition. B fails: `0*1 = 0`, not 1. So A does not imply B. In the other
   direction, A = `x*y = x` does imply B = `x*(y*z) = x`: put `y*z` in place of `y` in A.

4. **What it does NOT mean.**
   - Nothing here is checked in Lean (a proof assistant), and nothing has passed the full protocol of
     `docs/shared/VERIFICATION_PROTOCOL.md`. `z3-only` is not "proved": it rests on z3 being right.
   - The 3,662 infinite counterexamples say nothing about finite structures: for some of these pairs every finite
     structure where A holds also has B holding.
   - Only laws up to 3 symbols are covered. Larger laws are a new question.
   - "We found no earlier table of these laws" (`docs/PRIOR_WORK.md`, 2026-11-22) is not "nobody did it".

5. **How to re-check.** Run the independent checks listed under "Reproduce" (CI runs them on every push). The counts
   above come from

   ```
   python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results
   ```

   which ends with `total: 506,232 ordered pairs of different laws (712 x 711 = 506,232)` and `tally: OK`. It checks
   that every pair left open by the stored table gets an answer from a result file and that no two answers disagree;
   the other checks re-check the answers themselves. `src/query.py` answers one pair, but it reads only the stored
   table and steps 08 to 12: for the 5,874 pairs answered in steps 13 to 29 it still says "open" (sometimes with the
   ETP's verdict). The answers are in the result files those steps name; changing the stored table's format is the
   owner's decision (see `STATE.md`).

## The problem

A structure has a set, one binary operation `*`, and one unary (single-input) operation `f`,
with no assumptions. A **law** is an equation such as `f(x*y) = f(x)*y`, required to hold for
all values of its variables. Law A **implies** law B if every structure satisfying A also
satisfies B.

Question: for all laws up to a size limit, decide every implication. This is the same kind of
question the Equational Theories Project answered for one binary operation, applied to a family
we have not found studied (literature check of 2026-11-22 in `docs/PRIOR_WORK.md`: nothing found
that tabulates laws with one binary and one unary operation; "not found" is not proof). The part
without `f` is ordinary magma laws and is covered by the ETP (see the cross-check below).

Size of a law = number of `*` and `f` symbols on both sides. Laws are counted up to renaming
variables and swapping sides. Current scope: size 1 to 3 (712 laws, 506,944 ordered pairs including
each law with itself). Size 0 (`x = y`, which collapses everything) is not in the list.

## Status

**Early. No result is Lean-checked or has passed the full protocol.** Status labels are defined
in `docs/shared/VERIFICATION_PROTOCOL.md`. What we hold so far:

| Item | Status |
|------|--------|
| 712 laws up to size 3 (8,805 up to size 4) enumerated | independently recounted by a different algorithm, exact match. Law texts round-trip to stored terms. |
| 207 of the 216 laws with no model of size 2 or 3 force a one-element structure | `z3-only` |
| 9 laws with no small model, collapse unproven | open, own problem: [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models) |

All 506,232 ordered pairs (A different from B) are accounted for, in exactly one row
(details in `steps/05-edge-proofs.md`):

| Group | Pairs | Status |
|-------|-------|--------|
| A does not imply B, refuted by a structure of size 2 or 3 | 335,177 | `model-verified`: every pair re-checked by `src/verify_small_refutations.py` (step 07), verifier mutation-tested |
| A does not imply B, refuted by a structure of size 4 or 5 | 708 | `model-verified`: certificates in `results/witnesses_larger_models.json`, re-checked by `src/verify_witnesses.py` |
| A collapses every structure, so it implies B | 147,177 | `z3-only` |
| A implies B, proved by z3 (with transitive closure) | 15,877 | `z3-only` |
| A is one of the 9 open laws | 6,399 | open in the table; all 9 answered in [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models); the rows of 7 of them also checked here (step 27: 2,844 pairs, `z3-only`; step 28: 2,133 pairs, replayed derivations) |
| unresolved (no structure up to size 5, no proof in 1 s) | 894 | open, from 71 source laws |

**Cross-check with the Equational Theories Project (step 08).** Our 408 laws without `f` are ordinary
magma laws, and they are exactly ETP laws 3 to 410. Of the 166,056 ordered pairs among them, the
164,800 that our table decides **all agree with the ETP data (0 disagreements)**. The remaining
1,256 pairs, open for us (code 5 or 6), are settled by the ETP data and are labeled `known (ETP)`.
`src/query.py` prints the ETP equation numbers and the ETP verdict for such pairs. The ETP's results
are proved in Lean in that project. We did not re-check them. `results/status_matrix.npz` is
unchanged, and the ETP information is in `results/etp_crosscheck.json`.

**The two `f`-free laws with 4-element models (step 09).** For `(x*y)*(y*x) = y` and `(x*y)*(y*z) = y`,
trying all 256 choices of `f` on the known 4-element table refutes 1,417 of their 1,422 open
targets (608 of them contain `f`; certificates in `results/witnesses_ffree_models.json`, re-checked
by `src/verify_witnesses.py`). The 5 left are exactly the implications the ETP proves, so both rows
are fully decided. `src/query.py` prints these certificates (step 10); `results/status_matrix.npz` still
says code 5 for them.

**ETP tables with every `f` (step 11).** Every finite multiplication table published by the ETP of size
4 or 5, with every possible `f`, was tried against the 894 open pairs, and every ETP table of any size
against the 35 open pairs without `f`. Result: 2 new certificates (both 6 elements, both pairs without
`f`, both agreeing with the ETP), in `results/witnesses_etp_magmas.json`, re-checked by
`src/verify_witnesses.py`. No pair that involves `f` was settled this way, which says nothing about
whether those implications hold. `src/query.py` prints these 2 certificates after re-checking them
(step 12); `results/status_matrix.npz` still says code 6 for the 2 pairs.

**z3 with 10 seconds per pair (step 13).** z3 was asked again about the 892 open pairs without a
certificate, with 10 seconds each instead of 1. It proved 13 of them, and chaining those with the older
proofs settles 5 more: 18 open pairs are now "implies", label `z3-only`. The 15 of them without `f` agree
with the ETP; 3 of the 13 direct proofs were not repeated when z3 was asked again. The answers are in
`results/z3_open_retry.json`, checked against the table and the ETP by `src/check_z3_retry.py`.
`results/status_matrix.npz` still says code 6 for them.

**z3 with 30 seconds per pair (step 14).** The 879 pairs z3 could not decide in 10 seconds got 30 seconds
each. 3 more proofs, all for laws without `f` (the ETP agrees), 0 counterexamples. With chaining, 20 open
pairs are now "implies", label `z3-only` (same file and checker). **Still open after step 14: 872 pairs**
(18 without `f`, which have an ETP answer; 854 with `f`, with no answer).

**Tables of size 6 and 7 (step 15).** z3 looked for a counterexample table of 6, then 7 elements for each
of the 872 open pairs (10 seconds per size). It found none. For 395 pairs it says no table of either size
exists (`z3-only`); for the other 477 it gave up. This settles nothing: a counterexample may be larger or
infinite. For laws such as `f(x)*y = x`, which make `f` one-to-one, a hand argument (not checked by
machine) suggests every finite table satisfies the targets, so only infinite structures can refute them.
The search outcome is in `results/witnesses_open_6_7.json` (no certificates).

**Infinite structures built from the law itself (step 16).** Each open source law has the form "a term =
one of its letters", for example `f(x)*y = x`. Read as a rule "replace the pattern by the letter", it
defines an infinite structure whose elements are formal terms. When the rule cannot overlap with itself,
that structure satisfies the law, and computing the target law in it decides the pair. Result: **682 of the
872 open pairs are "does not imply"**, each with a certificate in `results/refutations_term_rewriting.json`,
checked by `src/check_term_rewriting.py`. Label `z3-only`: that the structure satisfies the source law is
checked by z3 on all elements (plus a hand argument); that the target fails is checked by plain code. These
say nothing about finite structures. `results/status_matrix.npz` still says code 6 for them. **Still open
after step 16: 190 pairs** (172 with `f`, no answer; 18 without `f`, which have an ETP answer), all from
source laws whose rule overlaps itself.

**Repairing the overlaps (step 17).** For each of those 26 source laws, the overlaps were turned into new
rules (Knuth-Bendix completion), each stored with a derivation from A. For 7 of them this ends with a rule
set where every overlap gives the same result, and the structure of simplified terms satisfies A. It settles
**133 of the 190 open pairs: 132 "does not imply", 1 "implies"** (`(x*(y*y))*y = x` implies
`(x*y)*(y*y) = x`, which the ETP also says). Certificates in `results/completions_open.json`, re-checked in
full by plain code (`src/check_completion.py`), which relies on two textbook theorems of rewriting; label at
the `z3-only` level, no higher (no z3 is used). `results/status_matrix.npz` still says code 6 for them.
**Still open after step 17: 57 pairs** (40 with `f`, no answer; 17 without `f`, which have an ETP answer),
from 19 source laws whose completion stopped.

**New names for values that ignore a letter (step 18).** Most of those 19 completions stopped at an equation
with a letter on one side only, such as `f(x)*z = f(x*x)`: it says `f(x)*z` does not depend on `z`. Giving
that value a new name (a symbol `h0(x)` defined as `f(x*x)`) and completing again finishes for 8 source laws,
all with `f`. It settles **32 of the 40 open pairs with `f`: all 32 "implies"**, each with a chain of
replacement steps from A that plain code replays (`results/completions_new_symbols.json`, checked by
`src/check_completion.py`; same label as step 17). `results/status_matrix.npz` still says code 6 for them.
**Still open after step 18: 25 pairs** (8 with `f`, from `(x*y)*f(x) = y`, `f(x)*(y*x) = y`, `f(x*y)*x = y` and
`x*f(y*x) = y`, whose completion keeps growing; 17 without `f`, which have an ETP answer).

**Derivations aimed at the target (step 19).** For `f(x*y)*x = y` and its mirror `x*f(y*x) = y`, a short proof
found by hand (`f` turns products into products, and every value is fixed by its `f`) was turned into chains of
replacement steps that plain code replays. It settles **4 of the 8 open pairs with `f`: all 4 "implies"**
(`f(x*y)*x = y` implies `x*(f(y)*x) = y` and `x*(f(x)*x) = x`; the mirror implies the mirrored targets).
Derivations in `results/derivations_open.json`, checked by `src/check_derivations.py`; same label as step 17.
`results/status_matrix.npz` still says code 6 for them. **Still open after step 19: 21 pairs** (4 with `f`, from
`(x*y)*f(x) = y` and its mirror `f(x)*(y*x) = y`; 17 without `f`, which have an ETP answer).

**Looking for a counterexample to `(x*y)*f(x) = y` (step 20).** Any counterexample must be infinite. Adding one
extra law of size 1 to 4 to `(x*y)*f(x) = y` and completing (8,804 tries) never gave a model where
`x*(y*f(x)) = y` fails: 274 runs completed and in all of them it holds. Replacing `f(x)` by `x`, `x*x`,
`x*(x*x)` or `(x*x)*x` gives laws without `f` for which the ETP says the implication holds. z3 with hints said
`unknown` after 120 s. **Nothing was settled; still 21 open pairs.** The search outcome is in
`results/extra_laws_277.json` (no certificates).

**The 17 open pairs without `f` (step 21).** Completion with larger limits still grows for all 7 source laws. The
ETP answers all 17. The one "implies", `(x*(y*x))*x = y` implies `x*((y*x)*x) = y`, now has a 4-step derivation
built from the ETP's Vampire proof and replayed by plain code (added to `results/derivations_open.json`, checked by
`src/check_derivations.py`; same label as step 17). The 16 "does not imply" are all ETP "Austin pairs": B holds in
every finite model of A, so any counterexample is infinite; the ETP builds them step by step (greedy constructions,
in Lean). This repository has no check of its own for those 16 yet. `results/status_matrix.npz` still says code 6.
**Still open after step 21: 20 pairs** (4 with `f`; 16 without `f`, which have an ETP answer).

**Where the 16 ETP answers come from (step 22).** Each of the 16 "does not imply" answers rests on one infinite
structure that the ETP proves in Lean, read as stored or in the mirror, plus implications that are already in this
repository (7 from the table, code 3, `z3-only`; 2 short derivations replayed by plain code). Only **3 ETP
constructions** carry all 16: the one for `x*(x*(y*x)) = y` (10 pairs), the one for `x*((y*x)*x) = y` (4 pairs)
and the "Asterix" model for `x*(y*(x*y)) = y` (2 pairs). The chains are in `results/austin_chains.json`
(`src/trace_austin_pairs.py`, needs a local copy of the ETP). **Nothing new is settled; still 20 open pairs.**

**The construction for `x*(x*(y*x)) = y`, checked here (step 23).** The ETP builds its infinite models of this law
on the free group (words in x1, x2, ... where `x x⁻¹` cancels), with `x*y = f(y x⁻¹) x`, starting from one of 3
short lists of values of `f` ("seeds") and extending them by a fixed rule. `src/check_greedy_eq73.py` checks with
its own code that each seed meets the 4 conditions the ETP's extension theorem needs, that the target law (or a law
the target implies, code 3 in our table) fails using seed values only, and runs the extension rule for 20,000 steps
per seed with law 565 evaluated directly (0 failures). **10 open pairs, all from law 565 or its mirror law 86: "does
not imply"** (`results/greedy_eq73.json`, gate and CI). Same label as step 17: the ETP's general extension theorem
is a Lean proof that was read, not re-run here. `results/status_matrix.npz` still says code 6 for them. **Still
open after step 23: 10 pairs** (4 with `f`; 6 without `f`, which rest on the ETP 118 and Asterix constructions).

**The construction for `x*((y*x)*x) = y`, checked here (step 24).** The ETP builds its infinite models of this law
on the numbers 0, 1, 2, ... from a short starting table of products ("seed", 2 or 4 entries) that meets 11 rules,
and fills the table one product at a time with a new number each time. `src/check_greedy_eq118.py` checks with its
own code that both seeds meet the 11 rules (copied verbatim from the Lean file, compared with it), that the target
law fails using seed products only, and runs the extension step about 26,000 times per seed with laws 508 and 143
evaluated directly (0 failures). **4 open pairs, from law 508 or its mirror law 143: "does not imply"**
(`results/greedy_eq118.json`, gate and CI). Same label as step 23: the ETP's construction is a Lean proof that was
read, not re-run here. `results/status_matrix.npz` still says code 6 for them. **Still open after step 24: 6 pairs**
(4 with `f`; 2 without `f`, which rest on the ETP's "Asterix" model).

**The "Asterix" construction for `x*(y*(x*y)) = y`, checked here (step 25).** The ETP builds an infinite model of this
law on the numbers 0, 1, 2, ... from a starting table of 18 products, 6 of them marked "closed" (the law already holds
there), that meets 6 conditions, and adds products one at a time with a new number each time.
`src/check_asterix_eq65.py` checks with its own code that the starting table meets the 6 conditions (copied verbatim
from the Lean file and compared with it, as is the table itself), that the target law fails using its products only,
and runs the extension step about 49,000 times with laws 598 and 88 evaluated directly (0 failures). **2 open pairs,
598 -> 224 and its mirror 88 -> 579: "does not imply"** (`results/asterix_eq65.json`, gate and CI). Same label as
step 23: the ETP's construction is a Lean proof that was read, not re-run here. `results/status_matrix.npz` still says
code 6 for them. **Still open after step 25: 4 pairs, all with `f`** (`(x*y)*f(x) = y` and its mirror; no answer
here, and the ETP has no laws with `f`). All 16 ETP Austin pairs now have a check here.

**The last 4 pairs of the unresolved row (step 26).** `(x*y)*f(x) = y` (law 277) does **not** imply
`x*(y*f(x)) = y` (law 632) or `x*(x*f(x)) = x` (law 574), and its mirror `f(x)*(y*x) = y` (law 408) does not imply
the mirrors, laws 128 and 122. The counterexample is infinite. Its elements are pairs (m, k): m is a formula over one
letter `g` that 4 rewrite rules cannot shorten (the free model of laws 277 and 632), and k is a counter. Multiplying
by an ordinary element adds 1 to the counter, multiplying by a value of `f` takes 1 away. Law 277 always ends with
"times `f(x)`", which undoes the 1 just added, so it holds; law 632 does not, so at x = y = (g, 0) it gives (g, 1)
instead of (g, 0). `src/check_label_extension.py` checks the rules (all shrink formulas, all 13 critical pairs join),
the counter rule over all cases, law 277 directly on 175 small elements (30,625 pairs, 0 failures) and the 4
failures (`results/label_extension_277.json`, gate and CI, selftest 18 of 18). With `--z3`, z3 also proves the
counter rule for every model of law 277. Label `z3-only` level, like steps 17 and 23 to 25; not Lean.
`results/status_matrix.npz` still says code 6 for them. **All 894 pairs of the "unresolved" row now have an answer
with a machine check here.** The 6,399 pairs of the row "A is one of the 9 open laws" rested at this point on the other repository
(eq-laws-without-small-models); steps 27, 28 and 29 below give each of them a check here.

**Rows of the four laws with only infinite models (step 27).** Four of the 9 laws with no small model,
`(f(x)*y)*z = y` (law 135), `f((x*y)*z) = y` (law 336), `f(x*(y*z)) = y` (law 450) and `x*(y*f(z)) = y` (law 639),
have the shape of step 16 ("a term = one of its letters", no overlap), so the infinite structure of formal terms
built from the law decides their rows. Of their 2,844 pairs, **2,828 are "does not imply"** (certificates in
`results/refutations_nine_laws.json`, checked by `src/check_term_rewriting.py`, `z3-only`) and **16 are "implies"**
(each target is the law with letters made equal; one-step derivations in `results/derivations_nine_laws.json`,
replayed by `src/check_derivations.py`, `z3-only` level at most). Mutation test `src/selftest_nine_laws.py`, gates and
CI. Same verdicts as the sibling repository, which used different structures and code
(`src/compare_nine_laws_sibling.py`, 0 differences). These say nothing about finite structures, where (by the
sibling's hand argument) these laws have only one-element models. `results/status_matrix.npz` still says code 5.

**Rows of the three collapse laws (step 28).** Three of the 9 laws, `((x*y)*z)*x = w` (law 110), `(x*y)*f(z) = y`
(law 284) and `f(x)*(y*z) = y` (law 415), force every structure to have one element: each forces `x = y`. A stored
chain of replacement steps derives `x = y` from each (2 steps for law 110; a helper equation and 4 steps for the other
two, following the sibling repository's hand proofs), and every other law then follows in one step. So **all 2,133
pairs of their rows are "implies"** (`results/derivations_collapse_laws.json`, replayed by `src/check_derivations.py`,
`z3-only` level at most, no z3 used; mutation test `src/selftest_collapse_laws.py` 14 of 14; gates and CI).
`results/status_matrix.npz` still says code 5.

**Rows of the two laws with 4-element models (step 29).** For `(x*y)*(y*x) = y` (law 250) and `(x*y)*(y*z) = y`
(law 257), 1,417 of their 1,422 pairs have 4-element certificates since step 09. The other 5 targets are the source
law itself with some letters made equal (for example z := x in law 257 gives law 250), so **all 5 are "implies"** by a
one-step derivation (`results/derivations_ffree_laws.json`, replayed by `src/check_derivations.py`, `z3-only` level at
most, no z3 used; `src/selftest_ffree_laws.py` checks that both rows are fully covered, that every derived equation
holds in the 4-element tables, and rejects 10 of 10 corrupted copies). Agrees with the ETP. `results/status_matrix.npz`
still says code 5. **Every pair of the 9 code 5 laws (6,399) and of the unresolved row (894) now has an answer with a
machine check here.**

## Steps (granular record)

Read in order, `steps/`:

1. `01-define-the-problem.md`
2. `02-enumerate-laws.md`
3. `03-small-model-catalogue.md`
4. `04-collapse-laws.md`
5. `05-edge-proofs.md`
6. `06-larger-counterexamples.md`
7. `07-full-recheck-of-small-refutations.md`
8. `08-etp-crosscheck.md`
9. `09-ffree-models-with-f.md`
10. `10-query-reads-step-09.md`
11. `11-etp-magmas-with-f.md`
12. `12-query-reads-step-11.md`
13. `13-z3-retry-open-pairs.md`
14. `14-z3-30s-open-pairs.md`
15. `15-search-size-6-7-open-pairs.md`
16. `16-infinite-term-structures.md`
17. `17-completion-overlapping-rules.md`
18. `18-completion-new-symbols.md`
19. `19-derivations-aimed-at-target.md`
20. `20-counterexample-search-law-277.md`
21. `21-pairs-without-f-left.md`
22. `22-trace-austin-pairs.md`
23. `23-seeds-eq73.md`
24. `24-seeds-eq118.md`
25. `25-asterix-eq65.md`
26. `26-label-extension-law-277.md`
27. `27-rows-of-four-infinite-laws.md`
28. `28-rows-of-three-collapse-laws.md`
29. `29-last-five-pairs-laws-250-257.md`
30. `30-plain-words-answer.md`

## Layout

- `src/` code. `data/` generated data (large arrays and logs are git-ignored, regenerate).
- `results/` claims with certificates. `steps/` the step records.
- Related problem: [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models).

## Reproduce

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt            # Windows: .venv\Scripts\pip
python src/laws.py 3 data/laws_3.json                # the 712 laws
python src/models.py data/laws_3.json data/o3        # catalogue of structures with 2 and 3 elements
python src/prove.py collapse data/laws_3.json data/o3 5000
python src/prove.py edges data/laws_3.json data/o3 1000
python src/resolve_open.py data/laws_3.json data/o3 5 5000 results/witnesses_larger_models.json
python src/export_status.py data/laws_3.json data/o3 results/witnesses_larger_models.json results/status_matrix.npz
```

The two `prove.py` steps use z3, whose outcomes differ between runs (proofs accumulate across runs).
That is why the outcome is stored in `results/status_matrix.npz` instead of being expected to
regenerate exactly. Everything else is deterministic.

Independent checks (CI runs them on every push, `.github/workflows/verify.yml`):

```
python src/check_laws_text.py data/laws_3.json
python src/check_laws_count.py 3
python src/check_catalogue.py data/laws_3.json data/o3 1000
python src/verify_small_refutations.py data/laws_3.json data/o3
python src/verify_witnesses.py results/witnesses_larger_models.json
python src/verify_witnesses.py results/witnesses_ffree_models.json
python src/verify_witnesses.py results/witnesses_etp_magmas.json
python src/check_status_matrix.py data/laws_3.json data/o3 results/witnesses_larger_models.json results/status_matrix.npz
python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_larger_models.json
python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json
python src/check_z3_retry.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/z3_open_retry.json results/witnesses_ffree_models.json results/witnesses_etp_magmas.json --selftest
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_term_rewriting.json
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_term_rewriting.json --selftest
python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_open.json
python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_open.json --selftest
python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_new_symbols.json
python src/check_completion.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/completions_new_symbols.json --selftest
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_open.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_open.json --selftest
python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json
python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json --selftest
python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json
python src/check_greedy_eq118.py data/laws_3.json results/status_matrix.npz results/greedy_eq118.json --selftest
python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json
python src/check_asterix_eq65.py data/laws_3.json results/status_matrix.npz results/asterix_eq65.json --selftest
python src/check_label_extension.py data/laws_3.json results/status_matrix.npz results/label_extension_277.json
python src/check_label_extension.py data/laws_3.json results/status_matrix.npz results/label_extension_277.json --selftest
python src/check_term_rewriting.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_nine_laws.json
python src/selftest_nine_laws.py data/laws_3.json results/status_matrix.npz results/refutations_nine_laws.json results/derivations_nine_laws.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json
python src/selftest_collapse_laws.py data/laws_3.json results/status_matrix.npz results/derivations_collapse_laws.json
python src/check_derivations.py data/laws_3.json results/status_matrix.npz results/derivations_ffree_laws.json
python src/selftest_ffree_laws.py data/laws_3.json results/status_matrix.npz results/witnesses_ffree_models.json results/derivations_ffree_laws.json
python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results
python src/tally_answers.py data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results --selftest
```

ETP cross-check (needs the ETP files, see `steps/08-etp-crosscheck.md`, not run in CI):

```
python src/etp_crosscheck.py <ETP>/data/equations.txt general_outcomes.json.gz results/etp_crosscheck.json
```

## Contributing

Open an issue with a reference if you know existing results. To work on a queue item see
[`STATE.md`](STATE.md) and [`LOOP.md`](LOOP.md). Every claim keeps the label it earned.
