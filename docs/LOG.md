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

- Count the cases an idea applies to before writing code for it. Queue item 0b had zero cases.
- A search that returns nothing in seconds needs a positive control: point it at cases with known
  answers and check it finds them, before reporting "nothing found".
