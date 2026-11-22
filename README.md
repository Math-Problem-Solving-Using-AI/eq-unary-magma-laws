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
we have not found studied (see `docs/PRIOR_WORK.md`, and note that "not found" is not proof).

Size of a law = number of `*` and `f` symbols on both sides. Laws are counted up to renaming
variables and swapping sides. Current scope: size at most 3 (712 laws, 506,944 ordered pairs).

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

## Steps (granular record)

Read in order, `steps/`:

1. `01-define-the-problem.md`
2. `02-enumerate-laws.md`
3. `03-small-model-catalogue.md`
4. `04-collapse-laws.md`
5. `05-edge-proofs.md`
6. `06-larger-counterexamples.md`
7. `07-full-recheck-of-small-refutations.md`

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
python src/check_status_matrix.py data/laws_3.json data/o3 results/witnesses_larger_models.json results/status_matrix.npz
python src/selftest_verifiers.py data/laws_3.json data/o3 results/witnesses_larger_models.json
```

## Contributing

Open an issue with a reference if you know existing results. To work on a queue item see
[`STATE.md`](STATE.md) and [`LOOP.md`](LOOP.md). Every claim keeps the label it earned.
