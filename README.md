# Math curiosity

Exploratory, reproducible computer experiments in the style of Terence Tao's
[Equational Theories Project](https://teorth.github.io/equational_theories): decide which
simple algebraic laws imply which, with every claim carrying a certificate that a reader can
re-check without trusting this code.

**Status: early and experimental. No result has passed the full verification protocol.**
Lean acceptance alone is not treated as proof, see `docs/LEAN_CAVEATS.md`.

## Problems

One folder per problem under `problems/`, each with its own README and a `steps/` record.

| Problem | Question | State |
|---------|----------|-------|
| [unary-magma-laws](problems/unary-magma-laws) | Which short laws over one binary and one unary operation imply which? | in progress, 712 laws up to size 3 |
| [laws-without-small-models](problems/laws-without-small-models) | Nine of those laws have no model of size 2 or 3. Do they collapse every structure to one element? | 1 collapse shown (`z3-only`), 2 have a size 4 model, 6 open |

## Shared documents (`docs/`)

- `VERIFICATION_PROTOCOL.md`: the stages a claim must pass, and the status ladder.
- `LEAN_CAVEATS.md`: documented cases where a Lean-accepted proof is not enough, each labeled by
  how well we could confirm it.
- `LESSONS.md`: mistakes and surprises, so they are not repeated.
- `PRIOR_WORK.md`: related published work and what we did and did not find.
- `LOG.md`: journal. `STEP_TEMPLATE.md`: format of the step records.

## Adding a problem

Create `problems/<short-name>/` with a `README.md` (question, status table, steps list, how to
reproduce), a `steps/` folder with one record per step (`docs/STEP_TEMPLATE.md`), and its own
code, data and results. Add it to the table above. Problem folders may depend on another
problem's code, say so in the README.

## Reproduce

Run from the repo root (Windows paths, use `.venv/bin/python` elsewhere):

```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

then follow the "Reproduce" section of the problem's README.

## Using this work

If you know of existing results that cover any of this, please say so (an issue with a
reference is ideal). We have not shown any of these families is unstudied.
