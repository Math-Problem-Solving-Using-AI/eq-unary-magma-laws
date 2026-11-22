# 01. Define the problem exactly

- Date: 2026-11-22
- Status label: definitions only (protocol stage S0). Nothing is claimed here.
- Commit(s): 010c71f

## Goal
Fix the exact meaning of every word before computing anything.

## Definitions used
- **Term:** a variable, `f(t)`, or `t * s` for terms `t`, `s`.
- **Law:** an equation `lhs = rhs` between terms, required for all values of its variables.
- **Size:** number of `*` and `f` symbols in lhs plus rhs. We do not claim this matches how
  the Equational Theories Project counts (that detail came from a search summary, not read by us).
- **Same law:** two laws are identified if one is a renaming of the variables of the other, or
  if sides are swapped. Nothing else is identified. In particular a law and its mirror image
  (arguments of `*` swapped) are counted as two laws.
- **Trivial law:** `t = t`. Dropped.
- **A implies B:** every structure (any size, finite or infinite) satisfying A satisfies B.
  Implication over finite structures only is a different relation and is NOT studied yet.
  The Equational Theories Project reported both can differ (see `docs/PRIOR_WORK.md`).

## Structures that need care
- The one-element structure satisfies every law. The empty structure satisfies every law
  vacuously. Neither can refute an implication. Our counterexample search uses sizes 2 and up.
- A law that forces every structure to have one element ("collapse") implies every other law.

## Decisions and why
- One binary plus one unary operation, short laws first: finite, split into independent
  checks, machine-checkable.
- Start at size at most 3 (712 laws): small enough to finish, large enough to be interesting.

## NOT verified
- That this family is unstudied. One search found no match, which is weak evidence.
- That our size measure is a sensible one for comparing with published work.

## Next
Step 02: enumerate the laws.
