# Prior work (searched 2026-11-22)

Check this before starting any new direction.

## Equational Theories Project (ETP)

- Decided all 22,028,942 implications between the 4694 simplest equational laws on magmas
  (one binary operation, laws with up to 4 operations). Human plus automated proofs, all
  validated in Lean. Main goal reached 2025-04-14.
- Tools used: Prover9 (proofs), Mace4 (finite counterexamples), Vampire, SAT solvers.
- Positive implications were mostly easy for provers. Counterexamples were the hard part:
  larger finite countermodels needed well-chosen restrictions, and some implications hold
  for finite magmas but fail for infinite ones.
- Open at last report: does law E677 imply E255 for finite magmas.
- Final report: https://arxiv.org/html/2512.07087v2
- Project site and blueprint: https://teorth.github.io/equational_theories

## Follow-ups seen

- Implication semilattice of 990 quadratic quasigroup laws: https://arxiv.org/pdf/2603.29909
- Certificate-producing solver for equational implication (SAIR EQT2 Stage 2): https://arxiv.org/pdf/2609.00706
- Proof-shortening applied to ETP implications: https://arxiv.org/pdf/2605.21200

## Our variant (one binary + one unary operation)

One standard-mode web search found no work on this exact family. That is NOT proof it is
unstudied. Do a deeper search (extended mode, universal algebra literature on algebras
with type (2,1)) before claiming novelty.
