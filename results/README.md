# Results

Nothing here counts as a finding until it carries a certificate anyone can re-check, and has
passed the stages in `docs/shared/VERIFICATION_PROTOCOL.md`.

## Claim types and certificates

| Claim | Certificate | How to re-check |
|-------|-------------|-----------------|
| Law A does NOT imply law B | A finite structure (tables for `*` and `f`) satisfying A and failing B | evaluate both laws on every assignment, `src/findmodel.py: check_model` (independent of z3 and numpy) |
| Law A implies law B | A derivation (chain of rewriting steps) | z3 `unsat` is a lead only. A stored derivation with an independent checker is planned |
| Law A does NOT imply law B, by an infinite structure | The structure T_A of formal terms built from A read as a rewrite rule, the witness, and B's two values there | `src/check_term_rewriting.py`: z3 checks A on all terms (`z3-only`), plain code recomputes B's values |
| Law A does NOT imply B, or A implies B, by a completed rewrite system | The rule set R (each rule with a derivation from A), and B's normal forms at distinct generators: different means B fails in the structure of normal forms, equal means B is derived | `src/check_completion.py`: replays the derivations, checks KBO and all critical pairs in plain code (relies on the critical pair lemma and Newman's lemma) |
| Law forces a one-element structure | Same as implication, a derivation of `x = y` | as above |

## Status labels (use exactly these, highest earned)

`unverified` < `z3-only` < `model-verified` (non-implications only) < `independent-prover`
< `lean-checked` < `lean-checked + fidelity-reviewed + literature-checked`

Only the last one may be called a result. `known` means already in the literature: cite it.

## Files

- `status_matrix.npz`: the outcome for every ordered pair of the 712 laws (array `codes`, row =
  law A, column = law B, index = law id minus 1 in `data/laws_3.json`). Codes:

  | Code | Meaning | Count | Label |
  |------|---------|-------|-------|
  | 0 | same law | 712 | - |
  | 1 | NOT an implication, refuted by a structure with 2 or 3 elements (regenerable) | 335,177 | `model-verified` |
  | 2 | NOT an implication, refuted by a certificate with 4 or 5 elements | 708 | `model-verified` |
  | 3 | implication proved by z3, with transitive closure | 15,877 | `z3-only` |
  | 4 | implication because A forces a one-element structure | 147,177 | `z3-only` |
  | 5 | A is one of the 9 laws with no small model, collapse unproven | 6,399 | open |
  | 6 | unresolved | 894 | open |

  Codes 3 and 4 cannot be regenerated deterministically (z3 varies between runs), which is why the
  table is stored. `src/check_status_matrix.py` checks codes 1 and 2 against what is regenerated.
- `witnesses_larger_models.json`: the 708 certificates of code 2 (plus the 894 pairs where none was
  found up to size 5). Re-check with `src/verify_witnesses.py`.
- `etp_crosscheck.json`: comparison of every pair of laws without `f` with the Equational Theories
  Project data (`steps/08-etp-crosscheck.md`). It holds the mapping of our law ids to ETP equation
  numbers, the counts (0 disagreements), and the 1,256 pairs that are open in `status_matrix.npz`
  together with the ETP's answer (label `known (ETP)`). Produced by `src/etp_crosscheck.py`.
- `witnesses_ffree_models.json`: 1,417 certificates (4 elements) for the rows of `(x*y)*(y*x) = y` and
  `(x*y)*(y*z) = y`, which are still code 5 in `status_matrix.npz` (`steps/09-ffree-models-with-f.md`).
  Re-check with `src/verify_witnesses.py results/witnesses_ffree_models.json`. `src/query.py` reads this
  file for code-5 pairs and re-checks the entry before reporting it (`steps/10-query-reads-step-09.md`).
- `witnesses_etp_magmas.json`: 2 certificates (6 elements) for pairs that are still code 6 in
  `status_matrix.npz`, built from multiplication tables published by the ETP
  (`steps/11-etp-magmas-with-f.md`, produced by `src/refute_from_etp_magmas.py`). Re-check with
  `src/verify_witnesses.py results/witnesses_etp_magmas.json`. `src/query.py` reads this file for code-6
  pairs and re-checks the entry before reporting it (`steps/12-query-reads-step-11.md`).
- `z3_open_retry.json`: z3's answers, with 10 seconds per pair and then 30 seconds for those still
  `unknown`, for each of the 892 open (code 6) pairs without a certificate (`steps/13-z3-retry-open-pairs.md`,
  `steps/14-z3-30s-open-pairs.md`, produced by `src/retry_open_z3.py`). 16 are `unsat` (`proved_ms`, the
  limit that gave the proof), label `z3-only`; with the closure they settle 20 pairs, still code 6 in
  `status_matrix.npz`. Check with `src/check_z3_retry.py` (consistency with the table and the ETP, not a
  proof check). `src/query.py` does not read this file.
- `witnesses_open_6_7.json`: the search for counterexample tables of size 6 and 7 on the 872 open pairs
  left after step 14 (`steps/15-search-size-6-7-open-pairs.md`, produced by `src/search_open_larger.py`).
  Same format as `witnesses_larger_models.json`; no table was found, so every entry has `size` null and
  only z3's answer per size in `tried` (`unsat` there is `z3-only`, `unknown` means nothing).
  `src/verify_witnesses.py` reads it (0 certificates).
- `refutations_term_rewriting.json`: 682 non-implications among the 872 open pairs left after step 15, each
  by an infinite structure T_A built from the source law read as a rewrite rule without overlap
  (`steps/16-infinite-term-structures.md`, produced by `src/refute_by_rewriting.py`). Format
  `"a,b": {A, B, rule, witness, B_left, B_right}`: B's letters sent to generators `g0, g1, ...`, and B's two
  sides computed in T_A (`F` stands for `f`, `P` for `*`), which differ. Label `z3-only`. Check with
  `src/check_term_rewriting.py` (`--selftest` for the mutation test). Still code 6 in `status_matrix.npz`;
  `src/query.py` does not read this file.
- `completions_open.json`: 133 of the 190 open pairs left after step 16, decided by Knuth-Bendix completion of
  the overlapping source rules (`steps/17-completion-overlapping-rules.md`, produced by `src/complete_open.py`).
  `sources`: for each of the 7 completed source laws, every derived equation with its derivation (a chain of
  replacement steps starting from A) and the final rule set; `pairs`: `"a,b": {A, B, verdict, B_left, B_right}`,
  132 `fails` (not implied) and 1 `holds` (implied). Terms are written `m(s,t)` for `s*t`, `f(t)`, `v0, v1, ...`.
  Label: `z3-only` level at most (no z3 used; plain-code check that relies on two textbook theorems). Check with
  `src/check_completion.py` (`--selftest` for the mutation test). Still code 6 in `status_matrix.npz`;
  `src/query.py` does not read this file.
- `completions_new_symbols.json`: 32 of the 57 open pairs left after step 17, all "implies", decided by
  completion with new symbols `h0, h1, ...` for values that do not depend on some letter
  (`steps/18-completion-new-symbols.md`, produced by `src/complete_new_symbols.py`). Same format as
  `completions_open.json`; the precedence lists every symbol (`f > * > h0 > h1`) and a definition is a fact
  `{"left": "h0(v2)", "right": "f(m(v2,v2))", "chain": null, "definition": true}`. Same label and checker
  (`src/check_completion.py`, `--selftest`). Still code 6 in `status_matrix.npz`; `src/query.py` does not read it.
- `derivations_open.json`: 4 of the 25 open pairs left after step 18, all "implies", each by a stored
  derivation (`steps/19-derivations-aimed-at-target.md`, produced by `src/derive_open.py` from a hand outline),
  and since step 21 one pair without `f`, law 153 implies law 508 (`steps/21-pairs-without-f-left.md`).
  `sources`: for laws 483, 704 and 153 (keys `"482"`, `"703"`, `"152"`), the facts with their chains of replacement steps,
  fact 0 being A; `pairs`: `"a,b": {A, B, verdict, fact}`, where `fact` is the index of the fact that is B.
  Terms as in `completions_open.json`. Label: `z3-only` level at most (no z3 used; nothing but replacing equals
  by equals). Check with `src/check_derivations.py` (`--selftest` for the mutation test). Still code 6 in
  `status_matrix.npz`; `src/query.py` does not read this file.
- `extra_laws_277.json`: the search of step 20 (`steps/20-counterexample-search-law-277.md`, produced by
  `src/scan_extra_laws.py`): `(x*y)*f(x) = y` completed together with each law E of size 1 to 4, and the targets
  `x*(y*f(x)) = y`, `x*(x*f(x)) = x` tested when a run completes. `laws`: for each E (key = its id in the list of
  `src/laws.py 4`, whose first 712 laws are `data/laws_3.json`) the outcome per symbol order: a stop reason, or
  `[order, [verdicts], rules]`. 274 complete, all `holds`; no certificates, nothing settled.
- `austin_chains.json`: for each of the 16 open pairs without `f` that the ETP calls Austin pairs (only infinite
  counterexamples), how its ETP answer is built (`steps/22-trace-austin-pairs.md`, produced by
  `src/trace_austin_pairs.py` from a local ETP clone). `pairs`: 16 rows; `chains`: 20 chains, each a base ETP
  structure (Lean file, theorem name, line; satisfies law `base_satisfies`, fails law `base_fails`, ETP numbers),
  a `mirror` flag, the laws s and r after mirroring (ETP numbers and our ids), and the link "B implies r": our table
  when `r_id` is set, else a derivation `B_implies_r` (list of terms, each one step of B from the last). No
  certificates; nothing settled; the 16 pairs are still code 6.
- `greedy_eq73.json`: the 3 finite seeds of the ETP's infinite models of `x*(x*(y*x)) = y` (law 565) and the 10
  open pairs they settle, all "does not imply" (`steps/23-seeds-eq73.md`, checked by `src/check_greedy_eq73.py`).
  Words of the free group are lists of integers (k is generator x_k, -k its inverse, [] the identity). `source`:
  ETP commit, Lean file and line numbers; `seeds`: name to list of [argument, value]; `pairs`: our pair, seed,
  `mirror` (true: operation `f(x y^-1) y` instead of `f(y x^-1) x`), law `r` that fails at `x`, and the table link
  B implies r (B = r or code 3). Label: same as `completions_open.json`; the ETP's extension theorem is not re-run.
  The 10 pairs are still code 6 in `status_matrix.npz`.
- `greedy_eq118.json`: the 2 finite seeds of the ETP's infinite models of `x*((y*x)*x) = y` (law 508) and the 4 open
  pairs they settle, all "does not imply" (`steps/24-seeds-eq118.md`, checked by `src/check_greedy_eq118.py`).
  `source`: ETP commit, Lean file and line numbers; `seeds`: name to `triples` (each [x, y, z] means x*y = z) and
  `finsupp` (the numbers the seed may use); `pairs`: our pair, seed, `mirror` (true: x*y is read as the seed's
  y*x, a model of law 143) and `env`, the values of x and y where law B fails. Label: same as `greedy_eq73.json`;
  the ETP's construction is not re-run. The 4 pairs are still code 6 in `status_matrix.npz`.
- `asterix_eq65.json`: the finite seed of the ETP's infinite "Asterix" model of `x*(y*(x*y)) = y` (law 598) and the 2
  open pairs it settles, both "does not imply" (`steps/25-asterix-eq65.md`, checked by `src/check_asterix_eq65.py`).
  `source`: ETP commit, Lean file and line numbers; `seed`: `E1`, the defined products (each [a, b, v] means
  a*b = v), and `E0`, the pairs (a, b) where a*(b*(a*b)) = b already holds; `pairs`: our pair, `mirror` (true: x*y
  is read as the seed's y*x, a model of law 88) and `env`, the value of x where law B fails. Label: same as
  `greedy_eq73.json`; the ETP's construction is not re-run. The 2 pairs are still code 6 in `status_matrix.npz`.
- `label_extension_277.json`: an infinite counterexample for `(x*y)*f(x) = y` (law 277) and its mirror (law 408): the
  4 rewrite rules of its base, the counter rule and the values where the targets fail. Settles the last 4 pairs of the
  unresolved row (277 -> 632, 574 and 408 -> 128, 122), all "does not imply" (`steps/26-label-extension-law-277.md`,
  checked by `src/check_label_extension.py`, `z3-only` level). The 4 pairs are still code 6 in `status_matrix.npz`.
- Look things up with `src/query.py`, for example
  `python src/query.py "x*y = x" "x*(y*z) = x"`.

Planned: derivations for codes 3 and 4 that an independent checker can verify.
