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
