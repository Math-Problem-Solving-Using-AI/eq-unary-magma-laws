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
with type (2,1)) before claiming novelty. (Done on 2026-11-22, see below.)

---

# Literature check of 2026-11-22 (Part A of the research prompt)

How to read this section:
- **[read, re-checked]**: a research subagent read the page, and the main session then fetched the
  same primary page itself (curl, or the local clone of the ETP repository) and found the quote.
- **[read by subagent]**: a research subagent read the page and gave a verbatim quote. The main
  session did not re-fetch it. Treat it as reliable but single-checked.
- **[not read]**: only seen in search results, or blocked. A lead, not a fact.

Blocked for Claude agents by robots.txt, so not read: ams.org, link.springer.com,
erdosproblems.com. Queries were run with extended web search. Exact query strings are listed per item.

## A1. Has the ETP idea been extended to a unary operation (type (2,1))?

Queries (2026-11-22): "equational theories project unary operation"; "implications between equational
laws unary operation binary operation"; "type (2,1) algebras equational implications enumeration";
"groupoid with unary operation identities implication"; "Equational Theories Project extension
signatures"; "magma laws with inverse operation implication graph"; "\"Equational Theories Project\"
semigroups OR quasigroups OR involution OR \"unary\" follow-up arXiv 2026"; "\"unary operation\" magma
equational laws implication graph classification"; "leanprover zulip Equational stream \"unary\"".
GitHub searches in teorth/equational_theories: issues "unary" 0 hits, "signature" 0, "type (2,1)" 0,
"other signatures" 0, "multiple operations" 0. Pull requests "unary" 0. Discussions are disabled.

Sources:
- ETP final report, https://arxiv.org/html/2512.07087v2 **[read, re-checked]**. §10.1: "The ETP is
  focused exclusively on magmas, which only feature a single (binary) operation." The only use of a
  unary operation is to repackage group inverse: "The binary operation ∗, unary operation (⋅)^{-1},
  and nullary operation e (identity element) can be repackaged into a single division operation".
  Future directions (§14) mention semigroups ("This includes the question of implications between
  equational laws in semigroups (associative magmas)") and non-equational properties. They do not
  mention unary operations.
- ETP repository README **[read by subagent]**: "we shall focus only on theories of a single equation,
  and specifically on the 4694 equational laws involving at most four magma operations".
- Tao's 2024 blog post announcing the ETP, comment section **[read by subagent]**: a reader asked
  "is there a similar kind of Hasse Diagram one could make for unary functions?". The reply is about
  one unary operation alone, not about type (2,1).
- arXiv 2603.29909, B. Le Floch, "Implication semilattice of 990 quadratic quasigroup equational
  laws" (v1 2026-03-31) **[read, re-checked, abstract]**: "I determine all 114 equivalence classes of
  their conjunctions, and all implications between them." This is ETP-style work in another
  signature (multiplication and two division operations). No unary operation.
- arXiv 2609.00706 (Ma, Zhang, Cázares, 2026-09-01), solver for the SAIR equational challenge
  **[read by subagent, abstract]**: "classify whether one magma identity implies another". Magmas only.
- arXiv 2605.21200 (Kondylidou, Blanchette, Heule, 2026-05-20), proof shortening for an ETP proof
  **[read by subagent, abstract]**. Magmas only.
- arXiv 2609.39872 (Le Floch, 2026-09-30) **[read by subagent]**: "a semigroup analogue of the
  Equational Theories Project, but extended to conjunctions of equations." Same signature as the ETP.
- arXiv 2610.02500 (SemiBase, finite identity bases for small semigroups) and arXiv 2610.26467
  (magmas) **[read by subagent, abstracts]**. Not type (2,1).

**Verdict A1: NOT-FOUND.** No source we read builds an implication graph for laws with one binary
and one unary operation. RELATED: Le Floch's quasigroup work (another signature) and the ETP itself.
"Not found" is not proof that nobody did it.

## A2. Cross-check with the ETP data

Done, see `steps/08-etp-crosscheck.md` and `steps/09-ffree-models-with-f.md`. 0 disagreements in
164,800 pairs. 1,256 open pairs are settled by the ETP (`known (ETP)`), and 1,417 certificates settle
the rows of the two `f`-free laws with 4-element models.

## A3. The nine laws with no small model

(a) **`f(x)*(y*z) = y` (collapse).** Query: "identity implies trivial algebra \"singleton law\" OR
\"trivializing identity\" universal algebra one-element variety criterion". Nothing specific.
ETP blueprint, `constant.tex` **[read, re-checked in the local clone]**: "815 laws" were shown to be
equivalent to the singleton law. Observation by the subagent, re-checked: putting `f(x) = x` gives
`x*(y*z) = y`, which is ETP Equation15 `x = y ◇ (x ◇ z)` after renaming. ETP `smallest_magma.txt` has
no entry for 15. The subagent inferred that the file omits laws with only trivial models, from the count
4694 − 3198 = 1496, which equals the report's number of laws equivalent to E2. This is consistent with
our collapse claim, but proves nothing about the law with general `f`.
**Verdict: NOT-FOUND for the law itself. RELATED: its `f = identity` case is trivial in the ETP.**

(b) **`(x*y)*(y*x) = y` and `(x*y)*(y*z) = y`.** **[read, re-checked]**:
- ETP `commentary/Equation167.md`: "This law is Stein's third law, as named by Sade. It was also
  called the bookend property. ... Also called centrist groupoid by the OEIS entry counting them".
- OEIS A128934 **[read, re-checked]**: "Number of centrist groupoids with n elements.", data
  "1,0,0,58,6634,0", comment "Systems with a binary operation that satisfies AB.BA=B. ... Any central
  groupoid is centrist." So 58 such structures with 4 elements, none with 2 or 3: this matches our
  finding exactly.
- ETP `commentary/Equation168.md`: "This law defines central groupoids ... all finite central
  groupoids have a cardinality that is necessarily a square number." ETP report: "introduced by Evans
  and studied further by Knuth".
- ETP `smallest_magma.txt`: "167 4", "168 4".
**Verdict: KNOWN-EXACT.** Both laws, and the fact that their smallest nontrivial models have 4
elements, are known. README rows are relabeled `known`.

(c) **No nontrivial finite model, but an infinite one** (our leads `f(x*(y*z)) = y`, `x*(y*f(z)) = y`).
Queries: "Austin \"A note on models of identities\" Proceedings of the American Mathematical Society
1965"; "Kisielewicz \"Varieties of algebras with no nontrivial finite members\""; "identity with unary
operation \"no nontrivial finite models\" infinite model algebra binary and unary operation".
- The phenomenon has a name: **Austin law**. ETP blueprint, `infinite_models.tex` **[read,
  re-checked]**: "An Austin law is a law which admits infinite models, but no nontrivial finite
  models". In the same file: "a computer search was also used to show that no law of order four or
  less is an Austin law." ETP report **[read, re-checked]**: "as observed by Austin [6], the converse
  is not true in general", plus open questions on E5093 and on surjunctive models.
- ETP blueprint, `order_5.tex` **[read, re-checked]**: among order-5 magma laws, "106 allow only
  trivial finite models. Of these, 10 are Austin laws".
- arXiv 2609.05690 (Zhao, Wu, Yang, Miao, 2026-09) **[read by subagent, abstract]**: "Finite model
  finders cannot witness an Austin law".
- Z. Ernst, slides (2008), https://www.cs.unm.edu/~veroff/ADAM/2008/ernst08.pdf **[read by
  subagent]**: "Dudek's algebra D has the identity: (ex)y = x. Although this system has non-trivial
  models, they are all infinite." Here `e` is a constant: binary plus nullary, a very short Austin-type
  identity.
- **[not read]**: Austin 1965 (AMS, blocked), Kisielewicz 1990/1997 (no full text available).

**Verdict: RELATED.** The phenomenon is known and named, so our two leads should be described as
"candidate Austin laws in type (2,1)". For magmas, Austin laws need order at least 5 (ETP blueprint).
Our two laws have size 3 but use a unary operation, much like Dudek's short identity uses a constant.
That makes them unsurprising in kind. We found no source on these two specific laws.

**Is our argument right? Independent re-check (2026-11-22, main session, by reading each step; not
a human, not Lean):**
- `f(x*(y*z)) = y`, finite part: if `y*z = y'*z'` then `y = f(x*(y*z)) = f(x*(y'*z')) = y'`. So the n
  sets `{y*z : z}` are pairwise disjoint and non-empty inside n elements, hence singletons:
  `y*z = p(y)` with `p` a bijection. Then `f(x*(y*z)) = f(p(x))` does not depend on `y`, yet equals `y`:
  so n = 1. Each step holds.
- Infinite part: elements are terms in a free magma on at least one generator. `x*y` is the formal
  pair. `f` sends a term of the form `(a, (c, d))` to `c`, and every other term to itself. Unique
  decomposition of free-magma terms makes `f` well defined, and `f(x*(y*z)) = f((x,(y,z))) = y`. The
  structure has more than one element. Each step holds.
- `x*(y*f(z)) = y`, finite part: if `y*f(z) = y'*f(z')` then `y = y'`, so as before `y*f(z) = p(y)`
  with `p` a bijection. Then `x*p(y) = y` gives `x*w = p^{-1}(w)` for all `x, w`, so
  `p(y) = y*f(z) = p^{-1}(f(z))` does not depend on `y`. That contradicts `p` being a bijection when
  n ≥ 2. Each step holds.
- Infinite part: elements are formal terms built from generators with formal pairs `(a, b)` and a
  formal `F(a)`. Put `f = F`. Put `x*w = y` if `w` is a formal pair `(y, F(z))`, otherwise
  `x*w = (x, w)`. Then `y*f(z) = (y, F(z))`, because `F(z)` is not itself a pair of that shape, so
  `x*(y*f(z)) = y`. Each step holds.
Label stays `hand-argument`, now re-read twice. A Lean proof (finite part: a statement about all
finite structures) and a human reviewer are still needed.

## A4. Is the whole family tabulated anywhere?

Queries: "single axiom groups product inverse McCune"; "enumeration of all identities binary operation
and unary operation small size implication catalogue automated theorem prover Mace4", plus the A1
queries.
- McCune and Kinyon, https://www.cs.unm.edu/~mccune/projects/gtsax/ **[read, re-checked]**: work
  "toward showing that the there are no single axioms shorter or simpler than those previously known
  for group theory in terms of {product,inverse}". "1,981,980 equations were generated, and 20,568
  of those are group identites." This is a systematic computer enumeration of product and inverse
  identities, but aimed only at group axioms, and at much larger sizes than ours.
- arXiv 1004.0007 (Araújo, Kinyon), unary semigroups; arXiv 0902.1155 (Auinger, Dolinka, Volkov),
  matrix identities with transposition **[read by subagent, abstracts]**. RELATED, not catalogues.
- [not read]: McCune 1993 and Kunen 1992 (Springer, blocked).

**Verdict A4: NOT-FOUND** for a table of all type (2,1) laws up to size 3. RELATED work as listed. Our
open pairs (code 6) are not discussed anywhere we looked.

## What this changes

- The two `f`-free laws with 4-element models are `known` (Stein's third law / centrist groupoids,
  and central groupoids).
- The two finite-versus-general leads should be called **candidate Austin laws**.
- No novelty claim is made for the family. The search found nothing that covers it, and that is the
  only claim.
