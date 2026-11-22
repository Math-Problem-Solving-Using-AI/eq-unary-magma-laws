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
- Restructured into `problems/unary-magma-laws` and `problems/laws-without-small-models`.
- First edge-prover run lost (results only saved at the end). Prover rewritten to save and resume.
- Hand proof that `f(x)*(y*z) = y` collapses, checked step by step by z3 (`z3-only`).

## Next

- Run `models.py` on size <= 3, record how many implications small models refute.
- Write `src/prove.py`: z3 proof attempts on remaining candidates, with transitive closure
  to cut work. Consider installing Vampire if z3 is too weak.
- Add model finder for size 4 and 5 counterexamples.
