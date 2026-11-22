# State

push: ask   (commit locally only; the owner pushes. Change to `allowed` to let loop sessions push.)

## Focus

Settle the 894 open pairs and make the implication claims independently checkable.

## Queue (take the first item)

1. **894 open pairs (code 6 in `results/status_matrix.npz`), 71 source laws.** Retry z3 with longer
   timeouts (10 s, 30 s, accumulate proofs, save state), search structures of size 6 and 7
   (`src/resolve_open.py` with larger MAXN), then analyze by hand the most frequent sources:
   `f(x)*f(y) = x` and `f(x)*f(y) = y` (38 open targets each). Every counterexample goes through
   `src/verify_witnesses.py`.
2. **Derivations for implications (codes 3 and 4).** Replace "z3 said unsat" by a stored chain of
   rewriting steps and write a tiny independent checker with mutation tests. Start with the
   collapse laws (207), then the 15,877 others.
3. **The nine laws with no small model**: see https://github.com/MauroBCardoso/eq-laws-without-small-models. When it is settled, update codes 5 and
   re-export the table.
4. **Literature check.** Extended search on algebras of type (2,1) / identities / varieties. Record
   queries and dates in `docs/PRIOR_WORK.md`. Until then make no novelty claim.
5. **Scale up to size 4** (8,805 laws, 8,093 new): generate laws, catalogue, prove. Needs saving and
   resuming everywhere (see lessons). Check memory and time first.
6. **Lean** for anything that survives, following `docs/shared/LEAN_CAVEATS.md`.

## Done

- 2026-11-22: steps 01 to 07, see `steps/`. All 506,232 pairs accounted for.

## Last iteration

(none yet)

## Blocked

(nothing)
