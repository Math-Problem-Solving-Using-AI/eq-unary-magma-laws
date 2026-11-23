# 22. The 16 Austin pairs: which ETP infinite structure each one rests on

- Date: 2026-11-23
- Status label: none new. The 16 pairs stay `open` in this repository (ETP answer "does not imply", label
  `known (ETP)`, not re-checked here). This step only records how each answer is built, and checks with plain
  code that every link except the base ETP structure is already in this repository.
- Commit(s): see `git log -- src/trace_austin_pairs.py results/austin_chains.json steps/22-trace-austin-pairs.md`

## In plain words

1. **The question.** After step 21, 16 pairs of laws without `f` are still open here. For each pair (A, B) the
   Equational Theories Project (ETP) says: A does **not** imply B, but every example showing it is infinite. Before
   trying to check those infinite examples ourselves, this step asks: how many different infinite examples are
   really needed, and is every other piece of the ETP's argument already in this repository?

   Words used here:
   - A **magma** (or **structure**) is a set with an operation `*` that takes two elements and gives one.
   - A **law** is an equation such as `x*(x*(y*x)) = y` that must hold for every choice of the letters. A
     **model** of a law is a structure where it holds.
   - A **implies** B if every model of A is a model of B. A **counterexample** (or **witness**) is a model of A
     where B fails.
   - An **Austin pair** is a pair (A, B) where B holds in every **finite** model of A, but some **infinite** model
     of A breaks B. The ETP keeps a list of them (`data/Austin_implications.txt`).
   - A **base structure** is one infinite structure that the ETP proves (in the proof checker Lean) satisfies one
     law s and fails another law r. The ETP stores these as "facts" in `data/full_entries.json`.
   - The **mirror** of a law swaps the two sides of every product: the mirror of `x*(y*z)` is `(z*y)*x`. Reading a
     structure's table the other way round (using `y*x` where it had `x*y`) turns a model of a law into a model of
     its mirror, and a structure that fails a law into one that fails its mirror.
   - **z3** is an automatic solver. **Labels:** `z3-only` means only a solver backs the answer; `known (ETP)` means
     the ETP has a Lean proof that this repository did not re-run; `open` means no answer here.

2. **What was done, in order.**
   1. **The logic of a chain.** Suppose a base structure M satisfies s and fails r. If s implies A, M satisfies A.
      If B implies r, then M cannot satisfy B (it would satisfy r). So M is a counterexample for (A, B). The same
      works with the mirror of M. So each pair needs: one base structure, and two implications.
   2. **A script** (`src/trace_austin_pairs.py`) takes every base structure the ETP proves infinite (511 entries),
      both as stored and mirrored, and keeps a chain only when the two implications are already in this
      repository's own table (or are trivial because s = A or r = B). Why: then the only thing still taken from the
      ETP is the base structure itself. The mirror is computed from the law text and must agree with the ETP's
      list of mirror pairs (`data/duals.json`).
   3. **Two pairs needed one more link.** For the pairs from `x*(y*(x*y)) = y` and its mirror, the base structure
      (the ETP's "Asterix" model) fails only laws with 4 products, which are outside this repository's laws (at
      most 3). The script then searches a short chain of replacement steps from B to that law and replays it.
      Example: from B, `(x*x)*x = x*x`, it gets `((x*x)*x)*x = (x*x)*x = x*x`, which is the 4-product law the
      Asterix model fails.
   4. **A check of the checks.** The chain check was run on 12 corrupted chains and inputs (wrong base entry, wrong
      mirror flag, wrong pair, a broken derivation, a removed implication in the table, a wrong mirror list). It
      rejected all 12.
   5. **A look at the base files.** The 3 ETP constructions for `x*(x*(y*x)) = y` are one step-by-step construction
      started from 3 different small seeds (`ManuallyProved/Equation73.lean`, lines 268, 295, 312, built on a free
      group, following a note linked from the file).

3. **A small example.** Take the pair "does `x*(x*(y*x)) = y` (law 565) imply `x*((x*y)*x) = y` (law 498)?".
   The ETP proves there is an infinite structure M where law 565 holds and `((x*x)*x)*x = x` (law 70) fails (base
   entry `Eq73.not_255`). This repository's table says law 498 implies law 70 (code 3: z3 found a proof, nothing
   else checked it). So if M satisfied law 498, it would satisfy
   law 70, which it does not. Hence M satisfies 565 and fails 498: "does not imply". No finite table can do this,
   because every finite model of 565 does satisfy 498 (that is what "Austin pair" means).

4. **What it means and what it does NOT mean.**
   - It means: all 16 answers rest on just **6 base entries from 3 ETP constructions**: the greedy construction for
     `x*((y*x)*x) = y` (ETP 118; 2 entries, 4 pairs), the step-by-step construction for `x*(x*(y*x)) = y` (ETP 73;
     3 entries, 10 pairs, 5 of them through the mirror) and the Asterix model for `x*(y*(x*y)) = y` (ETP 65; 1
     entry, 2 pairs, 1 through the mirror). Every other link is in this repository: 7 implications of the table
     (code 3, `z3-only`), 2 short derivations replayed by plain code, and mirrors recomputed from the text.
   - It does NOT settle any pair here. The 16 pairs stay open in this repository until the base structures
     themselves get a check of our own (next queue item).
   - The 7 table implications are `z3-only`, not proved. The base structures are proved in Lean by the ETP; that
     proof was not re-run or read in full here.
   - The script is not a gate of `LOOP.md` and not in CI: it needs a local copy of the ETP, which is not stored here.

5. **How to re-check.** With a clone of https://github.com/teorth/equational_theories (commit `dbc9a2bf`) next to
   this repository as `../_external/equational_theories`:

   ```
   python src/trace_austin_pairs.py ../_external/equational_theories data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/austin_chains.json --selftest
   ```

   Expected: `Austin pairs among them: 16; not Austin: [(145, 652), (501, 230)]`, one line per pair, `pairs with at
   least one chain: 16 of 16; without: []`, two derivation lines, `base ETP structures used: 6`, `selftest: 12 of 12
   corrupted inputs rejected` and `ALL PASS`. `results/austin_chains.json` is rewritten byte for byte.

## Goal

Queue item 1 (open pairs, piece 4d-2): for each of the 16 Austin pairs, find the base ETP refutation and the
implications that carry it over, and check that this repository has those implications. No new certificates.

## Command(s)

- `python src/trace_austin_pairs.py ../_external/equational_theories data/laws_3.json results/status_matrix.npz results/etp_crosscheck.json results/austin_chains.json --selftest`
- Every gate of `LOOP.md`.

## Inputs

`data/laws_3.json`, `results/status_matrix.npz`, `results/etp_crosscheck.json`. Local ETP clone at commit
`dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19), read only: `data/equations.txt`, `data/full_entries.json`,
`data/duals.json`, `data/Austin_implications.txt`; `equational_theories/ManuallyProved/Equation73.lean` (lines 1 to 40
and 255 to 320 read). No web access. Python 3.12.10, Windows 10.

## Output

- `src/trace_austin_pairs.py` (new): finds and re-checks the chains; `--selftest` mutation test.
- `results/austin_chains.json` (new): `pairs` (16 rows: ids, texts, ETP numbers, number of chains) and `chains`
  (20 chains: pair, base file, name and line, the base laws s0 and r0, mirror flag, s and r after mirroring with
  ETP numbers and our ids, and for r outside our laws its text and the derivation as a list of terms).
- The chains, one per pair (where a pair has two, both are listed):

  | Our pair | ETP | Base entry (ETP file) | Mirror | Extra link |
  |---|---|---|---|---|
  | 86 -> 137 | 274 -> 203 | `Eq73.not_99_4380` (Equation73.lean) | yes | none |
  | 86 -> 153 | 274 -> 222 | `Eq73.not_255`; `Eq73.not_99_4380` | yes | 153 implies 559; 153 implies 137 (code 3) |
  | 86 -> 492 | 274 -> 99 | `Eq73.not_203` | yes | none |
  | 86 -> 508 | 274 -> 118 | `Eq73.not_203`; `Eq73.not_255` | yes | 508 implies 492; 508 implies 559 (code 3) |
  | 86 -> 559 | 274 -> 47 | `Eq73.not_255` | yes | none |
  | 88 -> 579 | 261 -> 307 | `Asterix.Equation65_facts` (Asterix.lean) | yes | derivation of ETP 3253 from 579 (2 steps) |
  | 143 -> 498 | 229 -> 125 | `Equation118_not_implies_Equation222` (Greedy/Eq118.lean) | yes | none |
  | 143 -> 565 | 229 -> 73 | `Equation118_not_implies_Equation274` | yes | none |
  | 508 -> 86 | 118 -> 274 | `Equation118_not_implies_Equation274` | no | none |
  | 508 -> 153 | 118 -> 222 | `Equation118_not_implies_Equation222` | no | none |
  | 565 -> 70 | 73 -> 255 | `Eq73.not_255` | no | none |
  | 565 -> 137 | 73 -> 203 | `Eq73.not_203` | no | none |
  | 565 -> 143 | 73 -> 229 | `Eq73.not_203`; `Eq73.not_255` | no | 143 implies 137; 143 implies 70 (code 3) |
  | 565 -> 492 | 73 -> 99 | `Eq73.not_99_4380` | no | none |
  | 565 -> 498 | 73 -> 125 | `Eq73.not_255`; `Eq73.not_99_4380` | no | 498 implies 70; 498 implies 492 (code 3) |
  | 598 -> 224 | 65 -> 359 | `Asterix.Equation65_facts` | no | derivation of ETP 4065 from 224 (2 steps) |

- The 2 open pairs without `f` that the ETP refutes but are not Austin pairs, (145, 652) and (501, 230), are the 2
  pairs with 6-element certificates of step 11; they are not part of this step.
- Open pairs: still 20 (4 with `f`, 16 without). `results/status_matrix.npz` unchanged.

## Checks done (and what each one can and cannot catch)

- `check_chain` re-checks each chain from the input files: the pair is open and an Austin pair, the base entry
  exists, is proven and infinite and lists s0 and r0, the mirror recomputed from the text agrees with `duals.json`,
  ids match, both implications are in our table, a derivation replays step by step. It cannot catch an error in
  the ETP's Lean proof of the base structure, nor a wrong code 3 in our table (those are `z3-only`).
- Selftest: 12 of 12 corrupted chains and inputs rejected.
- All gates of `LOOP.md`: law texts 712, 0 mismatches; count MATCH; catalogue 335,177 refuted pairs; 335,177 small
  refutations re-verified, 0 failed; 708, 1,417 and 2 certificates, 0 failed; status table consistent;
  `selftest_verifiers.py` ALL PASS; `check_z3_retry.py` ALL PASS and selftest ALL PASS; `check_term_rewriting.py`
  ALL PASS and selftest ALL PASS; `check_completion.py` on both files ALL PASS, both selftests ALL PASS;
  `check_derivations.py` ALL PASS, selftest 14 of 14.

## NOT verified

- The 6 base structures: their Lean proofs were not re-run, and only the start of `Equation73.lean` and its three
  theorems were read. `Eq118.lean` and `Asterix.lean` were not read in this step.
- `full_entries.json` was taken as an honest index of the ETP's Lean theorems (name, file, line, `proven`,
  `finite`); that each entry matches its Lean statement was not checked.
- The 7 table implications used are code 3 (`z3-only`), not derived here.
- The Austin list was read, not re-derived; a pair being on it only explains why no finite search found anything.
- Whether other chains exist that use base structures with laws of size 4 on the `s` side was not explored (the
  script only allows s to be one of our laws).

## Surprises, errors, dead ends

- Surprise: only 3 ETP constructions carry all 16 pairs; one of them (ETP 73) carries 10, half through the mirror.
- First run counted 18 pairs, not 16: the 2 pairs with step 11 certificates are still code 6 in the table. Fixed by
  keeping only pairs on the Austin list and printing the other 2.
- First run crashed on ETP equation numbers beyond the 4,694 of `equations.txt` (entries such as
  `Equation26302` from a metatheorem file). Fixed by skipping them.
- The 2 Asterix pairs had no chain inside our laws: the Asterix model fails only 4-product laws. A 2-step
  derivation from B fixed it; no ETP implication was needed.
- A first attempt to patch the script through a shell heredoc failed on quoting; the file was rewritten whole.

## Next

Queue item "piece 4d-3": see whether the 3 base constructions (ETP 73 with 3 seeds, ETP 118 greedy, Asterix for
ETP 65) can be checked by plain code here: the starting finite piece plus the extension rule, and with what label.
Start with ETP 73 (10 pairs): read `ManuallyProved/Equation73.lean` in full and the note it links.
