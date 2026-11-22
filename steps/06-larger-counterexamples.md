# 06. Larger counterexamples for the unresolved pairs

- Date: 2026-11-22
- Status label: `model-verified` for the 708 pairs settled here
- Commit(s): 04f0409 (script), certificates in a later commit

## Goal
For each of the 1,602 pairs left unresolved by step 05, look for a finite structure of size 4 or
5 that satisfies A and fails B. A structure found and re-checked is a certificate that A does not
imply B, with no prover to trust.

## Command(s)
```
P=problems/unary-magma-laws
.venv/Scripts/python.exe $P/src/resolve_open.py $P/data/laws_3.json $P/data/o3 5 5000 $P/results/witnesses_larger_models.json
.venv/Scripts/python.exe $P/src/verify_witnesses.py $P/results/witnesses_larger_models.json
```

## Inputs
z3 as a finite model finder (enumeration sort, laws instantiated on every assignment), timeout 5 s
per size and pair. Sizes 4 and 5.

## Output
`results/witnesses_larger_models.json` (certificates, tracked in git).

| Outcome | Pairs |
|---------|-------|
| certificate found, size 4 | 566 |
| certificate found, size 5 | 142 |
| none found up to size 5 | 894 (from 71 source laws) |

All 28 pairs that z3 had answered `sat` in step 05 are among the 708 certificates, so z3's `sat`
answers were right.

## Checks done
- During the run, each structure was re-checked by `findmodel.check_model` (plain evaluation).
  0 of 708 failed.
- `verify_witnesses.py` re-checks the stored file afterwards using its own parser and evaluator,
  no z3 and no numpy: 708 checked, 0 failed. The law texts in the file are parsed (not the stored
  terms), so a text that did not match its law would fail here.

## NOT verified
- The 894 open pairs: no structure up to size 5 within 5 s, and no proof within 1 s. This says
  nothing about truth. They may be implications, or have only larger or infinite counterexamples.
- That the verifier is correct. It is short (read it), and `verify_witnesses.py` shares the law
  text parser with `check_laws_text.py`.

## Next
Longer proof attempts on the 894, larger structures (6 and up), and a hand analysis of the
source laws that occur most (`f(x)*f(y) = x` and `f(x)*f(y) = y` have 38 open targets each).
