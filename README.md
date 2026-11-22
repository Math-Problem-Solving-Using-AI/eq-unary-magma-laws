# Implications between short equational laws, one binary and one unary operation

Exploratory, reproducible computation in the style of Terence Tao's
[Equational Theories Project](https://teorth.github.io/equational_theories), applied to a
different family: algebras of type (2,1), meaning one binary operation `*` and one unary
operation `f`, with no assumptions.

Question: for short laws such as `f(x*y) = f(x)*y`, which laws imply which?
`A => B` means every structure satisfying law A also satisfies law B.

Keywords: equational laws, universal algebra, magma with unary operation, implication
graph, finite countermodels, automated theorem proving, z3.

## Status

**Early, experimental. No result here is verified by Lean yet.** Read `results/README.md`
for the exact status labels. Every claim is meant to ship with a certificate (a finite
counterexample table or a proof) that you can re-check without trusting this code.

Prior work is tracked in `docs/PRIOR_WORK.md`. We have not shown this family is unstudied.
If you know of existing results, please open an issue with a reference.

## Method

1. `src/laws.py` enumerates every law up to a size limit (size = number of `*` and `f`
   symbols in both sides), deduplicated up to variable renaming and side swap.
2. `src/models.py` catalogues every structure of size 2 and 3 (size 3 up to relabeling) and
   refutes implications by counterexample.
3. `src/prove.py` tries to prove the remaining candidate implications with z3.
   Proofs accumulate across runs because z3 outcomes are not stable.
4. `src/findmodel.py` searches larger finite counterexamples, and independently re-checks
   any model by direct evaluation.
5. Next: independent prover, then Lean for anything we call a finding.

## Layout

- `src/`      code
- `data/`     generated law lists (large arrays and logs are git-ignored, regenerate)
- `results/`  findings with certificates
- `docs/`     `LOG.md` (journal), `LESSONS.md` (mistakes, do not repeat), `PRIOR_WORK.md` (sources)

## Reproduce

Run from the project root (Windows paths shown, use `.venv/bin/python` elsewhere).

```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe src/laws.py 3 data/laws_3.json            # 712 laws up to size 3
.venv/Scripts/python.exe src/models.py data/laws_3.json data/o3    # small-model catalogue
.venv/Scripts/python.exe src/prove.py collapse data/laws_3.json data/o3 5000
.venv/Scripts/python.exe src/prove.py edges data/laws_3.json data/o3 1000
```
