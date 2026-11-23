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

### Lessons for the hub

- z3 results depend on the process state, not only on the time limit: a proof found in a pool worker
  was not found again in a single process with the same limit, but was found at once in a fresh pool.
  When re-checking z3 claims, try more than one process layout before calling a proof unrepeatable.

- Count the cases an idea applies to before writing code for it. Queue item 0b had zero cases.
- A search that returns nothing in seconds needs a positive control: point it at cases with known
  answers and check it finds them, before reporting "nothing found".
