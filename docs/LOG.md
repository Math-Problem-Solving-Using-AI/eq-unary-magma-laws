# Project log

Newest entries at the bottom.

## 2026-11-22

- Goal: start a new ETP-style project. Chose family: one binary op `*` plus one unary op `f`,
  short laws first. Reason: finite, splits into small independent checks, machine-checkable.
- Prior work search done, see `PRIOR_WORK.md`. No exact match found (weak evidence only).
- Law counts by size (total `*` and `f` symbols, up to renaming and side swap):
  size 1: 7, size 2: 62, size 3: 643 (cumulative 712), size 4: 8093 (cumulative 8805).
- Chose to start with size <= 3 (712 laws, about 506k ordered pairs).
- `src/laws.py` and `src/models.py` written. First run of `models.py` failed on missing numpy.
  Fixed, see `LESSONS.md`.
- Repo created, folders match pipeline stages.

### Model catalogue, size <= 3 (sizes 2 and 3 models, 88,786 total)

- 335,177 of the ordered pairs refuted by a small model. 171,055 candidates left.
- 216 laws have no model of size 2 or 3. z3 proved 207 of them force `x = y` (collapse), which
  makes them imply every law. Nine unresolved. Of those nine, `(x*y)*(y*x) = y` and
  `(x*y)*(y*z) = y` have size 4 models. The other seven have no model up to size 6 and z3
  has not proved collapse yet. They could collapse with a harder proof, or have only infinite
  models. Open, details in `results/zero_model_laws.json`.
- Repo made public-ready: README states status honestly, `results/README.md` defines
  certificate types and status labels. Publishing to a remote is not done, user decides.
- Edge prover run started on the remaining candidates (1s timeout per pair, 8 workers).

### Rigor pass (same day, later)

- Owner asked for: granular steps in the repo, no skipped unknowns, Lean caveats from real cases,
  one folder and README per problem.
- Read primary pages (via subagents) on Lean soundness, `native_decide`, misformalization, junk
  values. Results in `LEAN_CAVEATS.md`, with several search-summary claims downgraded to UNCONFIRMED.
- Added `VERIFICATION_PROTOCOL.md` and independent checks: law text round trip (712 ok), brute
  force recount of laws (exact match up to size 4), plain-Python spot-check of the model
  catalogue (0 disagreements).
- Restructured the (then private) monorepo into one folder per problem. The second problem is now its own repository.
- First edge-prover run lost (results only saved at the end). Prover rewritten to save and resume.
- Hand proof that `f(x)*(y*z) = y` collapses, checked step by step by z3 (`z3-only`).

### Results pass (same day, evening)

- Edge prover rerun (259 s): every one of the 506,232 ordered pairs is now in exactly one group,
  see `README.md`.
- 708 pairs settled by certified structures of size 4 and 5 (`resolve_open.py`), all re-checked by
  an independent verifier. The 28 earlier z3 `sat` answers were all confirmed.
- All 335,177 small-structure refutations re-verified, 0 failed. Verifiers mutation-tested.
- Two of the six open laws look like finite-versus-general cases (hand argument plus sample-checked
  infinite models). Not machine-proven, labeled as leads.

## Where things stand

Nothing has passed the full protocol. Strongest evidence: 335,885 certified non-implications
(`model-verified`). Weakest: 163,054 implications that rest on z3 alone.

## Next

1. 894 open pairs from 71 source laws: longer proofs, structures of size 6 and up, hand analysis.
2. The six open laws, then use the two infinite models to refute more of their 711 targets each
   with explicit counterexample elements (needs a careful certificate format).
3. Store derivations for implications, with a tiny independent checker, instead of trusting z3.
4. Lean for anything that survives, following `docs/shared/LEAN_CAVEATS.md`.
5. Deeper literature search (extended search, universal algebra of type (2,1)) before any
   novelty claim.
6. Owner decisions: publish or not, license, author identity in commits.

### Literature and ETP pass (2026-11-22, research branch)

- Cross-checked every pair of laws without `f` against the Equational Theories Project data
  (step 08): 408 laws map one-to-one to ETP laws 3-410. 164,800 decided pairs, 0 disagreements.
  1,256 pairs open for us are settled by the ETP.
- Found that `((x*y)*z)*x = w` collapses trivially. It had sat on the "open" list because z3 timed
  out at 5 s. Lesson added to the hub.
- Step 09: all 256 choices of `f` on the known 4-element tables of `(x*y)*(y*x) = y` and
  `(x*y)*(y*z) = y` refute 1,417 of their 1,422 open targets. The 5 left are exactly the ETP's proved
  implications.
- Literature check (`PRIOR_WORK.md`): no table of type (2,1) laws found. The two `f`-free laws are
  known (Stein's third law / centrist groupoids, OEIS A128934; central groupoids, Evans and Knuth).
  The finite-versus-general leads are "candidate Austin laws".

## 2026-11-23

### Decisions taken by the loop

- Queue item 0 (make the table and `query.py` reflect steps 08 and 09) offered two options: teach
  `query.py` to read `results/witnesses_ffree_models.json`, or add new codes to `export_status.py` and
  regenerate `results/status_matrix.npz`. The loop took the first: it changes no published format,
  publishes nothing and costs nothing. A new code in the stored table stays an owner decision
  (`STATE.md`, Blocked). Step 10.
- Queue item 0b (ETP magmas plus a chosen `f`, for open pairs whose source has no `f`) turned out to
  apply to no open pair: all 35 such pairs have targets without `f` too. The loop widened it to every open
  pair (ETP tables of size 4 and 5, every `f`) and to every ETP table for the 35 `f`-free pairs. This
  changes no format, publishes nothing and costs seconds. Step 11.
- Queue item 0c (`query.py` reads the step 11 certificates) had one way to do it and it changes no
  format, publishes nothing and costs nothing, so the loop did it without an owner decision. Step 12.

### Loop run 1 (step 10)

- `query.py` now reports the 1,417 step 09 certificates for code-5 pairs, after re-checking each entry
  with the independent verifier's code. Stored table unchanged.
- Dead end avoided: the mutation "replace `f` by the identity" does not have to break a witness
  (1,397 of 1,417 stay valid). Confirmed with a second evaluator instead of counting it as a failure.
  Rule: a mutation test needs changes that are sure to break the claim, or a second evaluator.

### Loop run 2 (step 11)

- ETP tables of size 4 and 5 with every `f` (769,287 structures) settle none of the 894 open pairs.
  Every ETP table with `f` the identity gives 6-element certificates for 2 of the 35 open `f`-free pairs
  (both ETP non-implications). Positive control: the same search on the code-5 rows reproduces the
  1,417 certificates of step 09 exactly.
- Bug caught: a helper "does this law mention `f`?" walked the stored pair (left, right) as if it were
  one term and skipped the left side. It crashed on the first law with `f` only on the left.

### Loop run 3 (step 12)

- `query.py` now reports the 2 step 11 certificates for code-6 pairs, after re-checking each entry. The
  step 09 reader became one table (`CERTIFICATE_FILES`, code to file); 6 of 9 saved outputs are
  byte-identical, the other 3 only gained lines. Mutation test: 0 broken entries accepted in either file.
- Slip caught: a scripted text replacement silently did nothing (escaped newline in the search text).
  Found by searching for the old function name afterwards.

### Loop run 4 (step 13)

- Queue item 1 (894 open pairs) is too big for one run; split into four pieces (z3 at 10 s, z3 at 30 s,
  structure search of size 6 and 7, "finite yes, infinite no" analysis). This run did the first.
- z3 with 10 s per pair on the 892 open pairs without a certificate: 13 `unsat`, 879 `unknown`, 0 `sat`.
  Chaining with codes 3 and 4 settles 5 more: 18 pairs `z3-only`. All 15 `f`-free ones are "implies" in
  the ETP; the closure contradicts no refutation. New checker `src/check_z3_retry.py` (mutation test
  5 of 5) is a gate and runs in CI.
- Surprise: asked again in one process, z3 repeated only 6 of the 13 proofs; a fresh pool repeated 4 more
  within a second each. z3's success depends on the process's history. 3 proofs (75,209 77,94 142,491,
  all `f`-free and ETP "implies") were not repeated.
- Dead end recorded: a mutation "open pair whose closure contradicts a refutation" cannot exist (a
  structure refuting A => C, with B => C, also refutes A => B).
- Not done: `status_matrix.npz` keeps code 6 for the 18 (the z3 proof arrays `export_status.py` needs are
  git-ignored and not present); `query.py` does not read the new file (Optional later).

### Loop run 5 (step 14)

- Open pairs, piece 2: z3 with 30 s per pair on the 879 pairs that were `unknown` at 10 s. Seven resumable
  runs of about 500 s each. 3 `unsat` (239,209 497,564 567,603, all `f`-free, all ETP "implies"),
  876 `unknown`, 0 `sat`. With chaining, 20 pairs `z3-only` (239,209 was already settled by chaining).
  872 pairs still open: 18 `f`-free (ETP answer), 854 with `f` (no answer).
- `--rerun` repeated 8 of the 16 proofs; 202,485 and 709,57, repeated in step 13, were not repeated now.
- Dead end recorded: more z3 time did nothing for the pairs with `f` (3 proofs at 10 s in step 13, none
  added at 30 s). Next pieces: structure search of size 6 and 7, then infinite counterexamples.

### Loop run 6 (step 15)

- Open pairs, piece 3: z3 looked for counterexample tables of size 6 and 7 (10 s per size) on the 872 open
  pairs, new resumable script `src/search_open_larger.py`, three runs. 0 found. Size 6: 718 `unsat`,
  154 `unknown`; size 7: 395 `unsat`, 477 `unknown`. Positive control: the same search finds the two known
  6-element certificates of step 11 in 0.1 s each.
- Dead end recorded: whole rows (`f(x)*y = x`, `x*f(y) = y`, `f(f(x))*y = x`, `x*f(f(y)) = y`,
  `f(x*x)*y = x`, `x*f(y*y) = y`) are `unsat` at both sizes for every target. Hand lead (not machine
  checked): these laws make `f` one-to-one, hence onto in a finite table, which forces the targets; an
  infinite structure (numbers, `f(n) = n+1`) refutes `f(x)*y = x` => `f(x*x) = x`. Larger finite searches
  will not settle such pairs; piece 4 (infinite counterexamples with a checkable format) is next.

### Loop run 7 (step 16)

- Open pairs, piece 4 (infinite counterexamples), first part. Every open source law is "term = letter". Read
  as a rule term -> letter, it defines an infinite structure T_A of formal terms (apply the rule once at the
  top of each new term). If the rule's left side has no overlap with itself, T_A satisfies A (hand argument,
  z3 on the term datatype for each law). 682 of 872 open pairs refuted, all source laws with `f`; 190 left
  (26 source laws with overlaps). New search `src/refute_by_rewriting.py`, new checker
  `src/check_term_rewriting.py` (mutation test 8 of 8), gate and CI.
- Control against the table: for all 81 overlap-free laws, T_A's verdicts on all 712 targets contradict no
  finite counterexample and no z3 implication (57,672 pairs).
- Dead end: z3 with integers as elements and unknown functions gave `unknown` in 10 s on the example pair.
- Slip caught: first mutation "witness letters all g0" was applied to a one-letter certificate and changed
  nothing (accepted). Now picks a certificate with two letters.
- Split recorded: piece 4 continues as piece 4b (overlapping rules, completion), queue item 1.

### Loop run 8 (step 17)

- Open pairs, piece 4b: Knuth-Bendix completion (KBO, weight 1, both precedences, limits 40 rules, 14 symbols,
  4,000 equations) of the 26 overlapping source rules. 7 complete in under a second; 133 of 190 open pairs
  decided (132 not implied, 1 implied: `(x*(y*y))*y = x` => `(x*y)*(y*y) = x`, ETP agrees). Every derived
  equation is stored with a replayable derivation from A. New search `src/complete_open.py`, new checker
  `src/check_completion.py` (own KBO, unification and innermost simplifier; mutation test 10 of 10), gate and CI.
- Control: 4,984 verdicts of the 7 rule sets against the table and the ETP, 0 contradictions.
- Dead end recorded: 10 sources stop at `cannot orient` (equations with a letter on one side only, like
  `f(x)*z = f(x*x)`, or `x*(y*x) = z*(y*z)`), 9 at the term size limit (7 of them without `f`). 57 pairs left,
  split into queue items 4c (40 with `f`) and 4d (17 without `f`).
- Decision taken by the loop: label of the step 17 answers (see "Decisions taken by the loop" below).

### Loop run 9 (step 18)

- Open pairs, piece 4c (40 pairs with `f` whose completion stopped). An equation with a letter on one side only,
  `s = t`, gets a new symbol `h(V)` (V the shared letters) with the conservative definition `h(V) = s[other
  letters := first letter of V]` and the rules `s -> h(V)`, `t -> h(V)`, both derived. New search
  `src/complete_new_symbols.py`; `src/check_completion.py` extended (definitions, general precedence, 5 new
  mutations, 15 of 15; step 17 file still 10 of 10). 8 of 19 sources complete; 32 open pairs, all "implies".
  Control: 5,696 verdicts of the 8 rule sets against the table, 0 contradictions.
- Dead end recorded: 277, 408, 483, 704 (8 pairs) do not complete at 24 symbols and 60 rules either (scratch run,
  about 4 minutes). Item split: these 8 pairs are the new first queue item.
- Mutation slip caught: "each source with only its own rule" was rejected on the new file for the wrong reason
  (precedence listed unused symbols); fixed so the critical pair check is what rejects it.

### Loop run 10 (step 19)

- Open pairs, piece 4e (8 pairs with `f` whose completion keeps growing). Law 483 `f(x*y)*x = y`: by hand,
  E1 `f(y)*f(x*y) = x`, E2 `f(x)*f(y) = f(x*y)`, E3 `f(x*(f(y)*x)) = f(y)`, and then the target
  `x*(f(y)*x) = y` in 5 steps (every value z equals `f(w)*(f(z)*f(w))`). `src/derive_open.py` turns the outline
  into stored steps (it stops when two neighbouring terms are not one step apart), mirrored for law 704. New
  checker `src/check_derivations.py` (replay, pair checks, control on the 16 models with 2 or 3 elements,
  mutation test 14 of 14), gate and CI. 4 pairs "implies"; 21 left (4 with `f`, from 277 and 408).
- Slip caught by the step finder: an outline term `f(f(y))` should have been `f(y)`.
- Dead ends (paper, not kept): for 277 `(x*y)*f(x) = y`, affine models on groups and translation-invariant
  models force `f` one-to-one, and then the target holds. A layered construction over a model Q of 277 needs
  `f` not onto in Q; z3 found no such Q with 2 to 5 elements (for 277 and 483). Item split: the 4 pairs of 277
  and 408 are the new first queue item.

### Loop run 11 (step 20)

- Open pairs, piece 4f (277 `(x*y)*f(x) = y` to 632 and 574; mirror 408 to 128 and 122). No answer.
- Tried: z3 with three derived facts as hints, 120 s: `unknown`. Completion of 277 alone at 30 rules, size 16:
  grows; the rules treat `x*(y*f(x))` like `y` everywhere but never reduce it to `y`. New `src/scan_extra_laws.py`:
  277 plus one extra law E of size 1 to 4 (8,804 laws), completed with step 18's code and limits: 274 complete,
  law 632 holds in all of them (`results/extra_laws_277.json`). Positive control: a step 17 "fails" pair is
  reported "fails". ETP (local clone, outcome file 2024-11-10): `f(x)` replaced by `x`, `x*x`, `x*(x*x)`,
  `(x*x)*x` gives magma implications the ETP lists as true.
- Hand notes (leads): in a counterexample, the set F of values of `f` is a model of 277 and 632, `f` is
  one-to-one on F and not onto F (endless chain F, f(F), ...), and values with equal `f` lie outside F. The free
  model of 277 and 632 (4 rules) has such an `f`.
- Mistake caught on paper: one argument used one-to-one-ness of `z -> z*c` on F for a value outside F; dropped.

### Loop run 12 (step 21)

- Open pairs, piece 4d (17 pairs without `f`, sources 86, 88, 143, 153, 508, 565, 598). Split: this run did the
  first piece.
- Completion with 20 and 45 symbols per formula, 80 rules: all 7 sources keep growing (dead end, scratch only).
- ETP (local clone, read only): the 1 "implies" (153 to 508 = ETP 222 to 118) has a 3-step Vampire proof; it is
  now a 4-step derivation in `results/derivations_open.json`, replayed by `src/check_derivations.py`. The 16
  "does not imply" are all in the ETP's `data/Austin_implications.txt` (finite models always satisfy B); the ETP's
  base refutations are greedy infinite constructions (`Generated/Greedy/Eq118.lean`, `ManuallyProved/Equation73.lean`,
  `Asterix.lean`), the rest follow by chaining.
- Bug fixed in `src/derive_open.py` (`one_step` crashed when the target position ran through a letter); the 4 step 19
  derivations are unchanged.
- Mistake: the first outline had a wrong middle formula; the script stopped with "no step", as designed.
- 20 pairs open (4 with `f`, 16 without).

### Loop run 13 (step 22)

- Open pairs, piece 4d-2: traced the 16 Austin pairs (`src/trace_austin_pairs.py`, `results/austin_chains.json`).
- All 16 rest on 6 proven infinite "facts" entries of the ETP from 3 constructions: ETP 73 (`Eq73.not_99_4380`,
  `not_203`, `not_255`, one construction with 3 seeds; 10 pairs, 5 through the mirror), ETP 118 greedy (2 entries,
  4 pairs, 2 through the mirror), Asterix for ETP 65 (1 entry, 2 pairs, 1 through the mirror).
- Links used: 7 code-3 implications of our table (`z3-only`) and 2 two-step derivations from B to a 4-product law
  that the Asterix model fails (ETP 4065 from law 224, ETP 3253 from law 579), replayed by the script.
- Mirrors recomputed from the law text agree with the ETP's `duals.json` for every chain.
- Selftest 12 of 12 corruptions rejected. Not a gate and not in CI: it needs the ETP clone.
- Mistakes: first run counted the 2 step 11 pairs (still code 6) as well; crash on ETP numbers above 4,694
  (metatheorem entries). Both fixed before any output was kept.
- 20 pairs still open (4 with `f`, 16 without).

### Loop run 14 (step 23)

- Open pairs, piece 4d-3, split: the ETP 73 construction only. Read `ManuallyProved/Equation73.lean` in full. Its
  models are the free group with `x*y = f(y x^-1) x`; a seed (finite partial f) passing 4 finite conditions extends
  to a total f by the Lean theorem `exists_extension`.
- New checker `src/check_greedy_eq73.py` with its own free group code: the 3 seeds pass the 4 conditions, the
  target law (or r with B implies r, code 3) fails at x = 1 from seed values only, normal and mirrored; bounded run
  of the extension rule, 20,000 steps per seed, conditions checked, laws 565 and 86 evaluated directly at 4,225 pairs
  each, 0 failures. Selftest 13 of 13. Gate and CI.
- 10 open pairs (from 565 and 86) "does not imply", step 17 level (`z3-only` at most): the general theorem is the
  ETP's Lean proof, read and not re-run. 10 pairs still open (4 with `f`, 6 without).
- Mistake: two first mutations of the selftest (`x4` replaced by `x5` in a seed; an added value whose `f(a) a^-1`
  was new) were accepted, correctly: they did not make the certificate wrong. Replaced by mutations that break a
  condition.
- Mistake: a README patch script wrote with the Windows default encoding, failed on `⁻¹` and left README.md empty.
  Restored from the last commit (which held only this run's committed version) and redone with UTF-8.

### Loop run 15 (step 24)

- Open pairs, piece 4d-3, rest, split: the ETP 118 greedy construction only; the Asterix model goes back to the top
  of the queue as its own item. Read `Generated/Greedy/Eq118.lean` lines 2441 to 2791 (partial solutions as triples
  x*y = z with 11 rules, the extension step `adjoin`, the greedy chain, the seeds `counter222` and `counter274`).
- New checker `src/check_greedy_eq118.py`: the 2 seeds meet the 11 rules (copied verbatim, `--etp` compares them with
  the Lean file: identical); law B fails from seed products only, normal and mirrored; bounded run of the extension
  step (20,000 steps in the Lean chain order, 5,000 random, then on demand), rules checked, laws 508 and 143
  evaluated at 1,600 pairs each, 0 failures. Selftest 14 of 14. Gate and CI.
- 4 open pairs (508 -> 86, 508 -> 153, 143 -> 498, 143 -> 565) "does not imply", same label as step 23. 6 pairs
  still open (4 with `f`, 2 without).
- Mistake: the first selftest ran its mutations without the bounded test and accepted "rule 1 misread" (the
  misread rule holds on both seeds). All mutations now run the full check, which rejects it.
- Found: the derived triples of kind sP6 never occur in the bounded test, in any order tried. Recorded as not tested.

### Loop run 16 (step 25)

- Open pairs, piece 4d-3, last: the ETP's Asterix model of ETP 65 (`equational_theories/Asterix.lean`, read in full).
  A partial solution there is a set E1 of defined products and a subset E0 of closed pairs, with 6 conditions; one
  seed (`initial`, 18 products, 6 closed pairs).
- New checker `src/check_asterix_eq65.py`: the seed meets the 6 conditions (copied verbatim; `--etp` compares the
  conditions, the ETP 65 text and the seed with the Lean file: identical); law B fails at x = 0 from seed products
  only, normal and mirrored; bounded run of the Lean extension step (`add_e0`: 20,000 in `closureSeq` order, 5,000
  random, then on demand; 49,426 single steps, 8 of the "bad" kind), conditions and seed products checked, laws 598
  and 88 evaluated at 1,600 pairs each, 0 failures. Selftest 16 of 16. Gate and CI.
- 2 open pairs (598 -> 224, 88 -> 579) "does not imply", same label as steps 23 and 24. All 16 ETP Austin pairs
  now have a check here. 4 pairs still open, all with `f`.
- Mistake: the first run took 66 s (fresh number searched from 0 each step); fixed by keeping the smallest unused
  number, same output in 1 s.
- Mistake: the first selftest's "seed product removed" took out `0*3 = 4`, which the certificate does not need; it was
  accepted, correctly. Replaced by removing products the certificate needs.

### Loop run 17 (step 26)

- Open pairs, piece 4f: `(x*y)*f(x) = y` (277) and its mirror (408). Read the rules of completion of law 277 alone
  (40 rules): `x*(y*f(x))` behaves like `y` in all of them, never equal. Idea: pairs (m, k) over the free model M of
  laws 277 and 632 (the 4 rules of step 20), with a counter k (k = 0 on values of `f`): multiplying by a non-value
  of `f` adds 1, by a value of `f` takes 1 away (not below 0), product inside F gives 0. Law 277 holds (label lemma,
  uses only law 277 in M and "m*n in F implies n in F", which is rules 1 and 4); law 632 and 574 fail at (g, 0).
- New checker `src/check_label_extension.py`: rules shrink, 13 critical pairs join, rule 1 = law 277, rule 4
  present, no rule starts with `f`; lemma over 210 cases; law 277 directly on 175 elements (30,625 pairs, 0
  failures); 4 failures computed. Selftest 18 of 18 (each reason read). Optional `--z3`: z3 proves
  `f(x)*f(y) = f(x*y)` from 277 and then the lemma for every model of 277 (both `unsat`). Gate and CI.
- 4 pairs (277 -> 632, 574; 408 -> 128, 122) "does not imply", `z3-only` level. All 894 code-6 pairs now have an
  answer with a check. Not finished: the 6,399 code-5 pairs (rows of the 9 laws) still rest on the sibling repository.
- Dead end: z3 on the lemma without the fact `f(x)*f(y) = f(x*y)`: `unknown` after 60 s, with two encodings of "in F".
- Mistake: one z3 command ran without the 10-minute foreground limit, went to the background and was stopped; rerun
  in the foreground. Rule kept: give every computation `timeout 600000`.
- Queue item "pairs where z3 gave up at size 6 or 7" has no pairs left (the 4 pairs of 4f are answered); removed.

### Loop run 18 (step 27)

- Queue item "the nine laws with no small model", first piece. Four of the nine (135, 336, 450, 639) are "term =
  letter" with no overlap, exactly the case of step 16, which had only been run on code 6 pairs. New search
  `src/refute_nine_laws.py` runs it on their code 5 rows: 2,828 refuted, 16 equal in T_A, the equal ones stored as
  one-step derivations. Checked by the step 16 and step 19 checkers, whose "pair is open" test now accepts codes 5
  and 6. Mutation tests: step 16 selftest 8 of 8 on the new file, new `src/selftest_nine_laws.py` 7 of 7.
- Same split as the sibling's `results/refutations_term_models.json` (different structures, different code), 0
  differences (`src/compare_nine_laws_sibling.py`, tested on 2 corrupted copies of the sibling file).
- Mistake: the first mutation for the widened code check used a source whose fact 0 was not A; the checker rejected
  the source first and never reached the code check, and my filter on the message showed "ACCEPTED". Rewritten to
  claim the pair (A, A). Rule kept: a mutation must reach the check it targets; read why it is rejected.
- Not finished: the rows of laws 110, 284, 415 (collapse) and 250, 257 (4-element models; 5 implications rest on the
  ETP only) have no check here yet. Item split; the two pieces are back at the top of the queue.

### Loop run 19 (step 28)

- Queue item "rows of the 3 collapse laws". `src/collapse_derivations.py` writes, for laws 110, 284 and 415, a chain
  deriving `x = y` (2 steps for 110; helper equation plus 4 steps for 284 and 415) and then each of the 711 targets in
  one step from `x = y`: 2,133 pairs, all "implies" (`results/derivations_collapse_laws.json`). Replayed by the
  unchanged `src/check_derivations.py` (2,147 steps). New mutation test `src/selftest_collapse_laws.py`, 14 of 14.
  The sibling's checker also passes on its own two collapse proofs (run with `python -B`, sibling left clean).
- Rows of 7 of the 9 code 5 laws now have a check here. Left: the 5 ETP-only implications of laws 250 and 257.

### Loop run 20 (step 29)

- Queue item "rows of laws 250 and 257". The 5 pairs without a step 09 certificate (250 -> 204; 257 -> 204, 206, 250,
  253) are each the source law with letters made equal: one replacement step. `src/ffree_derivations.py` writes them
  (`results/derivations_ffree_laws.json`), the unchanged `src/check_derivations.py` replays them. New
  `src/selftest_ffree_laws.py`: coverage of both rows (1,417 + 5 = 1,422), control on the 4-element tables, mutation
  test 10 of 10. Gates 35 of 35.
- Finish line checked: conditions 1 and 2 hold; condition 3 does not (steps 01 to 09 have no "In plain words"; README
  has no short plain-words answer). Queue items added for those; `finished` stays `no`.
- Lesson: these 5 "ETP-only" pairs had been open since step 09 although each is a direct instance of the source law. Before
  calling a pair open or "known elsewhere", run the cheap syntactic test "is B an instance of A (letters made equal)?".
- Slip: Python `write_text` on Windows wrote LOOP.md, README.md and the CI file with CRLF; restored to LF before commit.

### Decisions taken by the loop (run 19)

- The item said to write the sibling's collapse derivations in our format. The sibling's proofs use rules our checker
  does not have (symmetry, transitivity, instantiation of a derived equation). Rather than widen the checker, the
  same argument was rewritten as plain replacement chains (a helper equation, then `x = y`), which the unchanged
  checker replays. Nothing published, no cost, no format change.

### Decisions taken by the loop (run 18)

- The queue item said "update codes 5 from its results and re-export the table". That changes the published table
  (new meaning for codes or new codes), which the owner decides (Blocked). The loop took the option that changes no
  published format: certificates and derivations in two new result files with their own checks, table unchanged.
  Nothing published, no cost.
- The two checkers of steps 16 and 19 were widened (codes 5 and 6 instead of 6) rather than copied, so the same
  code checks both files; their selftests still pass on their old files.

### Decisions taken by the loop (run 17)

- Label for the 4 pairs: `z3-only` level, as for steps 17 and 23 to 25 (infinite structure, rules and lemma checked
  by plain code, lemma also by z3, Newman's lemma not re-proved). No published format change, nothing published, no
  cost. The stored table keeps code 6 for them (Blocked item unchanged).
- Finish line not declared: `README.md` still lists the 6,399 pairs of the 9 laws as open here.

### Decisions taken by the loop (run 16)

- Label for the 2 pairs: same reasoning as run 14 (finite part re-checked here, the extension theorem is the ETP's
  Lean proof, not re-run). No published format change, nothing published, no cost.

### Decisions taken by the loop (run 15)

- Queue item "piece 4d-3, rest" had two constructions; the loop did the ETP 118 one and put the Asterix model back
  at the top of the queue as a separate item (LOOP.md: split an item too big for one session). Label for the 4
  pairs: same reasoning as run 14. No published format change, nothing published, no cost.

### Decisions taken by the loop (run 14)

- Label for the 10 pairs: the certificate's finite part is re-checked by plain code here, the general extension
  theorem is the ETP's Lean proof (not re-run). Same treatment as step 17 (a re-checked certificate resting on a
  theorem not machine-checked here): recorded at the `z3-only` level, never higher, and the pairs count as answered.
  Re-running the ETP's Lean file would raise the label, so it goes to "Optional later". No published format change,
  nothing published, no cost.

### Decisions taken by the loop (run 11)

- Queue order: the 4 pairs of 277 and 408 resisted steps 18, 19 and 20 and need a new idea. The 17 pairs without
  `f` (next item) have ETP answers that may be reachable by reading the ETP's proofs and counterexamples. The loop
  put the 17 pairs first and the 4 pairs second, so the next run starts on work with a known way in. No published
  format changes, nothing published, no cost.

### Decisions taken by the loop (run 8)

- The status ladder has no rung for a rewrite-system certificate re-checked by plain code (no z3 involved, but
  resting on the critical pair lemma and Newman's lemma, which are not machine-checked). The loop recorded these
  answers at the `z3-only` level, never higher, and wrote "no z3 used" next to the label everywhere. It changes no
  published format and stays on the safe side of the labels. Whether to add a rung is for the owner and the hub.

### Lessons for the hub

- Before calling a pair open, or leaving it to outside data, test whether B is an instance of A (some letters made
  equal). Here 5 pairs waited 20 steps for a check that is one replacement step each.

- When completion of a law grows without end and some value `u` behaves like `v` in every rule found but is never
  made equal to it, try a structure whose elements carry an extra counter that tells `u` from `v` (here: pairs over
  the free model of the law plus the target, with a counter that products add to and values of `f` take from). It
  settled 4 pairs that finite searches, extra laws and z3 had not.
- When z3 cannot prove a lemma about all models of a law, give it a short consequence of the law that it proves
  separately in its own call (here `f(x)*f(y) = f(x*y)`): `unknown` after 60 s became `unsat` in 0.3 s.

- Before building an infinite counterexample by hand, add one extra law and complete: if the pair fails in the
  completed system, that system is a counterexample with a certificate. It is cheap (8,804 extra laws in about 25
  minutes here). It found nothing for law 277, but it rules out the easy constructions quickly.

- When completion keeps growing, aim at the target before raising limits: here a 5-step proof existed for 4
  pairs whose completion did not finish at 60 rules. Writing the hand proof as a list of terms and letting a
  script find each single step makes slips visible at once and gives a chain any replay checker can verify.

- When completion stops at an equation with a letter on one side only (`f(x)*z = f(x*x)`), name the value that
  ignores that letter with a new defined symbol and continue. Here it turned 8 stuck completions into
  convergent systems and 32 open implications, which z3 with 30 s per pair had not proved, into short
  replayable derivations.

- When a law "term = letter" overlaps itself, run Knuth-Bendix completion before anything heavier: here 4 laws with
  31 open targets each completed to one rule in one round (the overlap shows one letter does not matter, e.g.
  `(x*y)*f(z) = z` gives `x*f(y) = y`), and 133 pairs were settled in under a second.
- The verification ladder has no rung for an infinite structure whose certificate (rule set, derivations, critical
  pairs) is re-checked by plain code. This repository records such answers at the `z3-only` level; the hub may want
  a rung for it.

- Before searching for an infinite counterexample, look at the source law as a rewrite rule. A law
  "term = letter" whose term cannot overlap itself has an infinite model of formal terms that decides every
  target at once; here it settled 682 pairs in seconds after finite searches up to size 7 found nothing.

- z3 results depend on the process state, not only on the time limit: a proof found in a pool worker
  was not found again in a single process with the same limit, but was found at once in a fresh pool.
  When re-checking z3 claims, try more than one process layout before calling a proof unrepeatable.

- A selftest must run the same checks as a normal run. Skipping the slow part (here a bounded run of an extension
  rule) to save time let a misread rule through, because the seeds alone happened to satisfy it.
- A mutation test must make the claim false, not only change the input. Replacing one fresh generator in a seed by
  another gives an equally valid certificate, and a checker that accepts it is right. Pick mutations that break a
  stated condition, and look at each "ACCEPTED" before calling the checker weak.
- On Windows, Python's `open()` defaults to the ANSI code page: a script that reads and rewrites a Markdown file with
  `⁻¹` in it fails at write time and leaves the file empty. Always pass `encoding="utf-8"`, and keep the file's line
  endings (`newline=`).

- Count the cases an idea applies to before writing code for it. Queue item 0b had zero cases.
- A search that returns nothing in seconds needs a positive control: point it at cases with known
  answers and check it finds them, before reporting "nothing found".
