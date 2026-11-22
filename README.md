# Math curiosity: equational laws with one binary and one unary operation

Small Equational-Theories-Project-style experiment. Question: for simple laws over
a structure with one binary operation `*` and one unary operation `f`, which laws
imply which?

An implication `A => B` means: every structure satisfying law A also satisfies law B.

## Method

1. `src/laws.py` enumerates every law up to a size limit (size = number of `*` and `f`
   symbols in both sides), deduplicated up to variable renaming and side swap.
2. `src/models.py` builds a catalogue of all small structures (sizes 2 and 3) and refutes
   implications by counterexample: a structure satisfying A but not B.
3. Pairs not refuted are candidates. A prover tries to prove them; harder non-implications
   need larger counterexamples from a model finder.
4. Final proofs should be checked in Lean before anything is called a result.

## Layout

- `src/`      code
- `data/`     generated law lists (large arrays are git-ignored, regenerate with the scripts)
- `results/`  findings worth keeping
- `docs/`     `LOG.md` (journal), `LESSONS.md` (mistakes, do not repeat), `PRIOR_WORK.md` (sources)

## Run

```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt     # Windows
.venv/Scripts/python.exe src/laws.py 3 data/laws_3.json         # laws up to size 3
.venv/Scripts/python.exe src/models.py data/laws_3.json data/o3 # model catalogue
```

Run from the project root.
