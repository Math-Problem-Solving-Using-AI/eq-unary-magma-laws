# 01. Define the problem exactly

- Date: 2026-11-22
- Status label: definitions only (protocol stage S0). Nothing is claimed here.
- Commit(s): 010c71f

## In plain words

1. **The question.** Take a set of things with two ways of combining them: a two-input operation written `*` and a
   one-input operation written `f`. Some short rules (equations) may hold in such a set. If one rule holds, does
   another rule have to hold too? This repository asks that for every ordered pair of short rules. This step only fixes
   what each word means, before anything is computed.

   Words used here:
   - A **structure** is a set of elements with a two-input operation `*` and a one-input operation `f`. A **magma** is
     the same thing without `f`. A finite structure can be written as two tables: one for `*` (row = left input,
     column = right input) and one for `f`.
   - A **term** is an expression built from letters (x, y, z, ...) with `*` and `f`, such as `f(x)*y`.
   - A **law** is an equation between two terms that must hold for every choice of the letters, such as `x*y = y*x`.
   - The **size** of a law is how many `*` and `f` symbols it has on both sides together: `x*y = y*x` has size 2.
   - Law A **implies** law B if every structure where A holds (of any size, finite or infinite) also has B holding.
   - A **model** of a law is a structure where it holds.
   - A law **collapses** if its only models have one element (it forces any two elements to be equal). Such a law
     implies every other law, because every law holds in a one-element structure.

2. **What was done, in order.**
   1. Wrote down what a term, a law and the size of a law are, so that the list of laws in step 02 is well defined.
   2. Decided when two laws count as the same: when one is the other with the letters renamed (`x*y = x` and
      `y*z = y`), or with the two sides swapped (`x = x*y`). Nothing else is merged. A law and its **mirror** (the two
      inputs of `*` swapped everywhere, for example `x*y = x` and `y*x = x`) stay two different laws. This was needed
      so that counts can be compared and re-computed.
   3. Dropped laws whose two sides are identical (`x = x`): they say nothing.
   4. Fixed the meaning of "implies" to include infinite structures. Implication among finite structures only is a
      different question and is not studied here.
   5. Noted two structures that can never show "A does not imply B": the one-element structure (every law holds in
      it) and the empty one. So searches for counterexamples start at 2 elements.
   6. Chose the scope: laws of size at most 3, which gives 712 laws (counted in step 02).

3. **A small example.** Take the set {0, 1} with `x*y = x` (the result is always the left input) and `f(x) = 0`:

   ```
   *  | 0 1        f(0) = 0
   ---+----        f(1) = 0
   0  | 0 0
   1  | 1 1
   ```
   The law `x*y = x` (size 1) holds: every entry in row x is x. The law `x*y = y*x` (size 2) fails: `0*1 = 0` but
   `1*0 = 1`. So this structure shows that `x*y = x` does NOT imply `x*y = y*x`.

4. **What it means and what it does NOT mean.**
   - It means: later steps use exactly these definitions.
   - It does NOT mean: any result. Nothing is claimed in this step. It also does not mean that our way of measuring
     size matches the Equational Theories Project (ETP, an outside project that studied laws of magmas): that was not
     checked.

5. **How to re-check.** There is nothing to compute here. The example above can be checked from the repository root
   with `python src/query.py "x*y = x" "x*y = y*x" --witness`; the expected output includes
   `code 1: NOT an implication: refuted by a structure with 2 or 3 elements` and
   `structure satisfying A and failing B: {"size": 2, "mul": [[0, 0], [1, 1]], "f": [0, 0]}`.

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
