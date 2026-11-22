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

## Next

- Run `models.py` on size <= 3, record how many implications small models refute.
- Write `src/prove.py`: z3 proof attempts on remaining candidates, with transitive closure
  to cut work. Consider installing Vampire if z3 is too weak.
- Add model finder for size 4 and 5 counterexamples.
