# 23. The ETP construction for `x*(x*(y*x)) = y`: its 3 finite seeds checked here, 10 open pairs not implied

- Date: 2026-11-23
- Status label: same level as step 17, never higher than `z3-only`. The finite part of each certificate (the seed,
  the failure of the target law, the link B implies r) is re-checked in full by plain Python here, no z3 used. One
  general theorem it relies on, the ETP's `Eq73.Greedy.exists_extension` ("every seed passing the finite
  conditions extends to a whole model"), is proved in Lean by the ETP and was **not** re-run here; it was read, and
  its extension rule was tested by plain code on a bounded range. 4 of the 10 pairs also use an implication of our
  table with code 3 (`z3-only`). Not `model-verified` (that label is for finite tables), not Lean here, not
  reviewed, no literature check for these pairs.
- Commit(s): see `git log -- src/check_greedy_eq73.py results/greedy_eq73.json steps/23-seeds-eq73.md`

## In plain words

1. **The question.** 20 pairs of laws were still open after step 22. For 10 of them the source law is
   `x*(x*(y*x)) = y` (law 565) or its mirror `((x*y)*x)*x = y` (law 86). The Equational Theories Project (ETP) says
   law 565 does not imply the 10 target laws, but only infinite examples show it. Can this repository check those
   infinite examples with its own code?

   Words used here:
   - A **magma** (or **structure**) is a set with an operation `*` that takes two elements and gives one.
   - A **law** is an equation that must hold for every choice of its letters. A **model** of a law is a structure
     where it holds. A **implies** B if every model of A is a model of B. A **counterexample** (or **witness**)
     is a model of A where B fails.
   - The **mirror** of a law reads every product the other way round (`x*(y*z)` becomes `(z*y)*x`). Reading a
     structure's operation the other way round turns a model of a law into a model of its mirror.
   - The **free group** on generators x1, x2, x3, ... is the set of all **words** such as `x3 x1` or `x2⁻¹ x4`,
     where `x x⁻¹` cancels and nothing else does. The empty word is written `1`.
   - A **seed** is a short list of values of a function `f` on a few words, for example `f(1) = x1`, `f(x1) = x2`.
   - **z3** is an automatic solver. **Labels:** `z3-only` means nothing stronger than a solver (or a hand theorem
     not checked here) backs the answer; `known (ETP)` means the ETP has a Lean proof that was not re-run here;
     `open` means no answer here.
   - **Lean** is a proof checker. The ETP stores its proofs as Lean files.

2. **What was done, in order.**
   1. **Read the ETP file** `ManuallyProved/Equation73.lean` in full (331 lines, ETP commit `dbc9a2bf`). Its
      models live on the free group, with `x*y = f(y x⁻¹) x`. Law 565 then holds exactly when
      `f(f(f(a) a⁻¹)) = a⁻¹` for every word a. The file proves (theorem `exists_extension`) that any seed passing
      four finite conditions can be extended, one word at a time, to a function `f` defined on all words with that
      property. Each new value is a brand-new generator, and when the rule needs it, one extra value is added.
   2. **Copied the 3 seeds** of the file (theorems `not_99_4380`, `not_203`, `not_255`) into
      `results/greedy_eq73.json`, word by word.
   3. **Wrote a checker** (`src/check_greedy_eq73.py`) with its own free group code. For each seed it checks the
      four finite conditions of the Lean file. Why: those conditions are all the general theorem needs.
   4. **For each of the 10 pairs**, the checker computes the target law (or a law r that the target implies) at
      `x = 1`, using only values that are in the seed, and finds two different words. Since every extension keeps
      the seed's values, r fails in every model built from that seed. For the 5 pairs from law 86 it uses the
      mirrored operation `x*y = f(x y⁻¹) y`. When r is not the target B, it checks that our table says B implies r
      (code 3). Why: a model of 565 where r fails, and B implies r, means B fails too.
   5. **A bounded test of the extension rule.** The checker runs the rule itself from each seed for 20,000 steps
      (about 36,800 values), checks the four conditions every 200 steps and at the end, and then evaluates law 565
      and law 86 (mirrored) directly at all 4,225 pairs of words up to length 2 over x1 to x4. 0 failures. Why: it
      tests both the rule and the step from `f(f(f(a) a⁻¹)) = a⁻¹` to law 565 with code that does not follow the
      Lean proof. It is not a proof for all words.
   6. **A check of the checker** (`--selftest`): 13 corrupted inputs (a changed seed value, a removed seed entry, a
      conflicting value, a broken one-to-one condition, a flipped mirror flag, a wrong seed, a wrong law r, a link
      not in the table, a pair that is not open, an unreduced word, the rule without its extra value, the wrong
      operation `f(x y⁻¹) x`). All 13 rejected.

3. **A small example.** Pair "does law 565 imply law 137, `(x*(x*x))*x = x`?", seed `not_203`:
   `f(1) = x1`, `f(x1) = x2`, `f(x2) = 1`, `f(x2⁻¹) = x3`, `f(x3) = x2⁻¹`. Put `x = 1` and use `x*y = f(y x⁻¹) x`:
   - `1*1 = f(1) = x1`;
   - `1*(1*1) = 1*x1 = f(x1) = x2`;
   - `(1*(1*1))*1 = x2*1 = f(1 x2⁻¹) x2 = f(x2⁻¹) x2 = x3 x2`.

   So the left side is `x3 x2`, the right side is `1`: law 137 fails. Every model built from this seed satisfies
   law 565 (by the ETP theorem) and fails law 137. No finite table can do this: every finite model of law 565
   satisfies law 137 (the pair is an ETP "Austin pair").

4. **What it means and what it does NOT mean.**
   - It means: the 10 pairs from law 565 and law 86 now have an answer here, "does not imply", with a certificate
     whose finite part this repository re-checks on every run (a gate of `LOOP.md` and CI). Open pairs: 20 before,
     **10 after** (4 with `f`; 6 without `f`, which rest on the ETP 118 and Asterix constructions).
   - It does NOT mean the pairs are proved here. The general extension theorem is the ETP's Lean proof, not re-run
     and not re-proved here; the bounded test only shows that the rule behaves on the first 20,000 steps.
   - The 4 links "B implies r" used for pairs 565 -> 143, 565 -> 498, 86 -> 153 and 86 -> 508 are code 3 in the
     table: z3 said so, nothing else checked it.
   - `results/status_matrix.npz` still says code 6 (open) for the 10 pairs: new codes are a published format
     change left to the owner (Blocked in `STATE.md`).

5. **How to re-check.** From the repository root:

   ```
   python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json
   python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json --selftest
   ```

   Expected: `3 seeds pass the finite conditions of the Lean file`, one line per pair (for example
   `pair 565 -> 137: seed not_203, law 137 fails at x = 1: [3, 2] != []`), six `bounded test` lines each with
   `4225 instances evaluated, 0 failures`, `10 open pairs with a seed certificate` and `ALL PASS` (about 20 s).
   The selftest prints 13 `rejected` lines, `selftest: 13 of 13 corrupted inputs rejected` and `ALL PASS` (about
   35 s). No ETP files are needed.

## Goal

Queue item 1 (open pairs, piece 4d-3), first piece: see whether the ETP 73 construction (3 seeds, 10 of the 16
Austin pairs) can be checked by plain code here, and with what label.

## Command(s)

- `python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json`
- `python src/check_greedy_eq73.py data/laws_3.json results/status_matrix.npz results/greedy_eq73.json --selftest`
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`. Local ETP clone at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), read only: `equational_theories/ManuallyProved/Equation73.lean`
(all 331 lines), `equational_theories/FreshGenerator.lean` (definitions of `freshGenerator` and `forgetOld`),
`data/equations.txt` (lines 47, 73, 99, 203, 255, 274). The Zulip note the Lean file links (a PDF) was **not** read.
No web access. Python 3.12.10, Windows 10.

## Output

- `results/greedy_eq73.json` (new): the source (repository, commit, file, line numbers of the definitions and
  theorems used), the operation, E0 and the 3 seeds as lists of words, and the 10 pairs (seed, mirror flag, law r,
  value of x).
- `src/check_greedy_eq73.py` (new): the checker and its `--selftest`; a new gate in `LOOP.md`, in CI and in the
  README command list.
- The 10 pairs, all "does not imply":

  | Our pair | Seed | Mirror | Law r that fails at x = 1 | Value of r's left side | Link B implies r |
  |---|---|---|---|---|---|
  | 565 -> 70 | `not_255` | no | 70 | `x4 x3 x1` | B = r |
  | 565 -> 137 | `not_203` | no | 137 | `x3 x2` | B = r |
  | 565 -> 143 | `not_203` | no | 137 | `x3 x2` | code 3 |
  | 565 -> 492 | `not_99_4380` | no | 492 | `x4` | B = r |
  | 565 -> 498 | `not_255` | no | 70 | `x4 x3 x1` | code 3 |
  | 86 -> 137 | `not_99_4380` | yes | 137 | `x4` | B = r |
  | 86 -> 153 | `not_255` | yes | 559 | `x4 x3 x1` | code 3 |
  | 86 -> 492 | `not_203` | yes | 492 | `x3 x2` | B = r |
  | 86 -> 508 | `not_203` | yes | 492 | `x3 x2` | code 3 |
  | 86 -> 559 | `not_255` | yes | 559 | `x4 x3 x1` | B = r |

  The right side is `1` in every row. The laws r found to fail agree with the ETP's own facts (`not_255` fails ETP
  255 = our 70, `not_203` fails ETP 203 = our 137, `not_99_4380` fails ETP 99 = our 492; mirrors 47 = our 559,
  203 = our 137, 99 = our 492), and with the chains of step 22.
- Open pairs: 10 (4 with `f`, 6 without). `results/status_matrix.npz` unchanged.

## Hand reading of the general theorem (a lead, not a check)

The extension step (`Extension1.Next` and `next`, lines 116 to 121) adds `f(d) = c` for an argument d without a value, with c a
generator that appears in no word used so far, and, if some old a has `f(a) a⁻¹ = d` (at most one, by the
one-to-one condition), also `f(c) = a⁻¹`. The proofs `next_func`, `next_eq73` and `next_aux` (lines 123 to 167) go
through every combination of old, new and extra values; each impossible case is closed by the map `forgetOld`, which
sends every old generator to 1 and keeps c, so an equation between an old word and a word containing c gives a
contradiction. `exists_extension` (line 196) then takes a greedy chain over all words and its limit. This was read,
not re-proved; the bounded test of step 5 runs the same rule.

## Checks done (and what each one can and cannot catch)

- Seed conditions (func, base, eq73, aux) on the 3 seeds: catch a wrongly copied seed or one that the theorem does
  not apply to. Cannot catch an error in the theorem itself.
- Failure of r from seed values only, normal and mirrored: catches a wrong seed, mirror flag or law. It relies on
  the theorem's promise that extensions keep the seed's values (`f_base`, line 227), which was read, not checked.
- Link B implies r: code 3 or 4 in our table, or B = r. Cannot catch a wrong code 3 (`z3-only`).
- Bounded test: 20,000 extension steps per seed, the four conditions checked every 200 steps and at the end, laws
  565 and 86 evaluated directly at 4,225 pairs each (all values defined), 0 failures. Catches a misread rule or a
  misread operation (the selftest shows it rejects both). Cannot prove anything about words never reached.
- Selftest: 13 of 13 corrupted inputs rejected.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS; `check_term_rewriting.py`
  ALL PASS and selftest ALL PASS; `check_completion.py` on both files ALL PASS, both selftests ALL PASS;
  `check_derivations.py` ALL PASS, selftest 14 of 14; `check_greedy_eq73.py` ALL PASS, selftest 13 of 13.

## NOT verified

- The ETP's general theorem `exists_extension` and the theorem `eq73` (law 565 holds in every such model): Lean
  proofs not re-run here; read only. The ETP's Lean build was not run.
- That an extension keeps the seed's values (`f_base`): read, not checked.
- The Zulip PDF note the Lean file follows was not read.
- The 4 links B implies r are code 3 (`z3-only`).
- The bounded test covers 20,000 steps from a fixed order of arguments; other orders and longer runs were not tried.
- The other 6 Austin pairs (ETP 118 greedy, Asterix for ETP 65) are not touched here.

## Surprises, errors, dead ends

- The first version of the selftest changed seed `not_255`'s value `x4` to `x5`, and the checker accepted it.
  That was right: any unused generator works as well as x4, so the changed seed is a valid certificate too. The
  mutation was replaced by one that really breaks a condition (`f(x3) = x2` instead of `x2⁻¹` in `not_203`). Its
  second version of "aux broken" added a value that broke nothing either; replaced by one whose `f(a) a⁻¹` repeats
  an existing one. Lesson (`docs/LOG.md`): a mutation must make the claim false, not just change the input.
- The bounded test hits its 20,000-step cap: each new generator creates a new argument to fill, so the rule never
  runs out of work. Expected for an infinite model.

## Next

Queue item "piece 4d-3, rest": the same for the ETP 118 greedy construction (`Generated/Greedy/Eq118.lean`, 4
pairs) and then the Asterix model of ETP 65 (`Asterix.lean`, 2 pairs).
