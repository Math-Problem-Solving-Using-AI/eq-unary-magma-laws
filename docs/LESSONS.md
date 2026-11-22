# Lessons: do not repeat these

Add an entry whenever something fails or surprises us. Format: what happened, why, rule.

## Environment

- **numpy missing in venv** (2026-11-22). `models.py` crashed with ModuleNotFoundError.
  Venv only had z3. Rule: install from `requirements.txt` first, and refreeze after adding packages.
- **`rmdir` failed with "Device or resource busy"** (2026-11-22). Shell working directory was
  inside the folder being removed, and a `&&` chain then skipped later steps silently.
  Rule: never remove the current directory, and check output of chained commands.
- Windows: call the venv Python directly (`.venv/Scripts/python.exe`), not `python`.

## Method

- A web search result summary is not a literature review. Mark claims of novelty only after
  a deeper search. See `PRIOR_WORK.md`.
- Counterexample-by-small-model leaves candidates that may still be false, because some
  non-implications need models larger than 3 elements (ETP found the same).
- "No model of size 2 or 3" does NOT mean "forces a one-element structure". Two laws,
  `(x*y)*(y*x) = y` and `(x*y)*(y*z) = y`, have models of size 4. Headline candidate counts
  also mislead: 153,576 of 171,055 candidates came from such zero-model source laws.

## z3

- `CheckSatResult` is unhashable. Use `str(result)` as the dict key.
- `EnumSort` names must be unique per call, or z3 raises "enumeration sort name is already declared".
- **z3 outcomes are not stable between runs.** Proving collapse for 216 laws gave 207 proofs
  at a 5s timeout and 205 at a 60s timeout (8 parallel workers). `unsat` (a proof) can be
  trusted, `unknown` carries no information. Rule: accumulate proofs across runs, never
  overwrite, never read a missing proof as evidence of non-implication.
