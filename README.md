# Which short laws imply which? One binary and one unary operation

> Part of [math-curiosity](https://github.com/Math-Problem-Solving-Using-AI/math-curiosity): open, reproducible experiments on equational laws, one repository per problem.
> **LLMs and tools:** read [`llms.txt`](llms.txt). **Autonomous sessions:** [`LOOP.md`](LOOP.md) and [`STATE.md`](STATE.md). License: Apache-2.0.
> **Look up any pair of laws:** `python src/query.py "x*y = x" "x*(y*z) = x"`

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
| A is one of the 9 open laws | 6,399 | open, see [eq-laws-without-small-models](https://github.com/Math-Problem-Solving-Using-AI/eq-laws-without-small-models) |
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
```

ETP cross-check (needs the ETP files, see `steps/08-etp-crosscheck.md`, not run in CI):

```
python src/etp_crosscheck.py <ETP>/data/equations.txt general_outcomes.json.gz results/etp_crosscheck.json
```

## Contributing

Open an issue with a reference if you know existing results. To work on a queue item see
[`STATE.md`](STATE.md) and [`LOOP.md`](LOOP.md). Every claim keeps the label it earned.
