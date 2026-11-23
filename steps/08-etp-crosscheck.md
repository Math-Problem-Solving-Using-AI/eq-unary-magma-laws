# 08. Cross-check the laws without `f` against the Equational Theories Project

- Date: 2026-11-22
- Status label: the 164,800 decided pairs among laws without `f` **agree with the ETP data**. The
  1,256 pairs that were open for us are `known (ETP)`. Neither the ETP's Lean proofs nor its closure tool
  were re-checked by us.
- Commit(s): see `git log -- steps/08-etp-crosscheck.md src/etp_crosscheck.py results/etp_crosscheck.json`

## In plain words

1. **The question.** 408 of our 712 laws do not use `f` at all. For those, an outside project has already decided
   every pair. Does our table agree with it, and can it answer the pairs that were still open for us?

   Words used here:
   - A **structure** is a set of elements with a two-input operation `*` and a one-input operation `f`. A **magma** is
     the same thing without `f`: a set with only `*`.
   - A **law** is an equation such as `x*y = x` that must hold for every choice of the letters. Law A **implies** law B
     if every structure where A holds also has B holding.
   - The **ETP** (Equational Theories Project) is a public online project that decided, for 4,694 magma laws with at
     most 4 uses of `*`, which ones imply which. Its proofs are checked in **Lean**, a program that checks
     mathematical proofs step by step. Its answers are published as one large file.
   - **Code** numbers are the answers stored in `results/status_matrix.npz` (for example 1 and 2 = "does not imply",
     shown by a table; 3 and 4 = "implies", by z3; 5 and 6 = open). **z3** is an automatic solver.
   - A law **collapses** if it forces every structure where it holds to have only one element; such a law implies
     every other law.
   - The label **`known (ETP)`** means: the answer comes from the ETP file and was not re-checked by us.

2. **What was done, in order.**
   1. Argued that the two settings ask the same question for laws without `f`: drop `f` from one of our structures
      and you get a magma; add `f(x) = x` to a magma and you get one of our structures. Neither step changes whether
      A or B holds.
   2. Downloaded two ETP files (the law list and the answer file) and recorded their versions and fingerprints
      (sha256), so the comparison can be repeated with the same data.
   3. Matched our 408 laws to ETP laws with a new reader written for this step, after renaming letters in a fixed way.
      All 408 matched, one to one.
   4. Checked which way the ETP file is read (row implies column, or the reverse) with three cases whose answer is
      known in advance, so a flipped reading would be caught.
   5. Compared all 166,056 ordered pairs of distinct laws without `f`. Result: 0 disagreements.
   6. Showed the comparison can fail: four deliberate damages (two of our codes changed, the matching shifted by one,
      the file read the wrong way round) were all detected.
   7. Took the ETP's answers for the 1,256 pairs that were open for us (412 + 17 "implies", 809 + 18 "does not
      imply") and stored them in `results/etp_crosscheck.json`, without changing our own table.

3. **A small example.** Law A = `((x*y)*z)*x = w` was "open" in our table: in step 04, z3 did not prove within 5 seconds
   that it collapses. The ETP says it collapses. A two-line check by hand: pick any two elements a and b, and put
   x = y = z = a. The law says `((a*a)*a)*a = w` for every w. With w = a and then w = b, the same left side equals both
   a and b, so a = b. Every two elements are equal: the set has one element. (Step 28 later stored this argument as a
   chain of steps that a program replays.)

4. **What it means and what it does NOT mean.**
   - It means: our 164,800 decided pairs without `f` agree with the ETP, which makes a bug in that part of our table
     unlikely. The 1,256 open pairs without `f` got an answer, labelled `known (ETP)`.
   - It does NOT mean that we checked the ETP's Lean proofs or rebuilt its answer file: we used the published file
     as it is. It says nothing about the 340,176 pairs where a law uses `f`: the ETP has no laws with `f`.
   - The 63,337 "implies" answers without `f` still rest on z3 here (`z3-only`); the ETP agreeing is extra support, not
     a proof checked by us.

5. **How to re-check.** From the repository root:
   - `python src/query.py "x*y = x" "x*y = y"`; expected, among other lines,
     `ETP: A is Equation4, B is Equation5 ... Our answer agrees with the ETP data`.
   - `python src/query.py "((x*y)*z)*x = w" "x*y = y"`; expected `code 5: OPEN` (the stored table was not changed)
     and then `the ETP data says A implies B (implicit_proof_true). Label: known (ETP; ...)`.
   - The full comparison needs the two ETP files from the internet: the commands under "Command(s)" below. The
     expected result is `"disagreements": []` in `results/etp_crosscheck.json` and the counts in the "Output" table.

## Goal

Find bugs in our table by comparing it with an independent, much more thoroughly checked source.
A law without `f` is an ordinary magma law. The Equational Theories Project (ETP) settled every
implication between its 4,694 magma laws with at most 4 operations, and our laws without `f` have at
most 3. So this part of our table must agree with the ETP.

## Why the comparison is valid (plain argument, two directions)

Let A and B be laws that do not mention `f`.
- If a structure (set, `*`, `f`) satisfies A and fails B, drop `f`: what is left is a magma that
  satisfies A and fails B.
- If a magma satisfies A and fails B, add `f(x) = x`: this gives a structure of our kind that
  satisfies A and fails B, because A and B do not mention `f`.

So "A implies B" means exactly the same thing in both settings. Both settings allow infinite
structures. Both also allow the empty structure, which satisfies every law, so it changes nothing.

## Command(s)

```
# ETP files (not stored here: they belong to the ETP and are large)
gh repo clone teorth/equational_theories -- --depth 1        # gives data/equations.txt
curl -O https://teorth.github.io/equational_theories/raw_data/general_outcomes.json.gz
python src/etp_crosscheck.py <ETP>/data/equations.txt general_outcomes.json.gz results/etp_crosscheck.json
```

## Inputs

| Input | Version | sha256 |
|-------|---------|--------|
| ETP `data/equations.txt` | repository `teorth/equational_theories`, commit `dbc9a2bf0c939e7c646841e679f0f7fb6cfe4e15` (2026-11-19) | `8351d54e8820c84f4cae94ef8a90ec5a2d5e5d472c1b3eaf23bcef34d4f07c09` |
| ETP `general_outcomes.json.gz` | project site, HTTP `last-modified: Mon, 02 Nov 2026 02:44:51 GMT`, downloaded 2026-11-22 | `48b29784b716e82d08b370321ecf531f650713fd95c31fa7e27f53697fc5bacc` |
| ours | `data/laws_3.json`, `results/status_matrix.npz` as committed before this step | |

What the ETP outcome strings mean, read in the ETP source file `equational_theories/Closure.lean`
(same commit):
- `explicit_proof_true`: "the implication has an explicit proof"
- `implicit_proof_true`: "the implication can be derived from proven theorems"
- `explicit_proof_false`: "the implication has an explicit disproof"
- `implicit_proof_false`: "the falsity of the implication can be derived from proven theorems"

The file holds only these four values (no `unknown`, no `conjecture`). It is a 4,694 x 4,694 matrix.
Entry [i][j] is about "Equation i+1 implies Equation j+1". This orientation was not assumed: the
script checks it with three forced cases (`x = y` implies everything, everything implies `x = x`,
and `x = x` does not imply `x = y`).

## How the laws were matched (not assumed: checked)

- Both law lists were parsed by a parser written for this step. It is separate from `src/laws.py`
  and `src/check_laws_text.py`. Our laws were read twice, from the stored term and from the text,
  and the two readings had to agree.
- Canonical form: name the variables in order of first appearance, try both orientations of `=`,
  keep the smaller.
- **No two ETP laws share a canonical form** (0 clashes). So, at least for our purposes, the ETP
  numbers laws up to renaming of variables and swapping the two sides. A law and its mirror image
  are **separate** ETP laws, for example Equation4 `x = x ◇ y` and Equation5 `x = y ◇ x`. Our list
  does the same.
- **All 408 of our laws without `f` matched an ETP law, one to one.** The ETP has 410 laws with at
  most 3 operations. The two unmatched are Equation1 `x = x` and Equation2 `x = y`. Both have size 0,
  and our enumeration starts at size 1 (and drops trivial laws). So the matching is complete.
- Examples: `x*x = y` is Equation6 `x = y ◇ y`; `(x*y)*(y*z) = y` is Equation168
  `x = (y ◇ x) ◇ (x ◇ z)`. The full mapping is in `results/etp_crosscheck.json`.

## Output

`results/etp_crosscheck.json`: inputs and hashes, the mapping, the counts, the (empty) list of
disagreements, the self-test results, and the 1,256 open pairs with the ETP's answer.

| Our code | Pairs | ETP says | Result |
|----------|-------|----------|--------|
| 1, refuted by a structure of size 2 or 3 | 101,025 | not an implication | agree |
| 2, refuted by a structure of size 4 or 5 | 438 | not an implication | agree |
| 3, implication by z3 | 9,613 | implication | agree |
| 4, implication because A collapses (z3) | 53,724 | implication | agree |
| 5, source is one of the 9 laws with no small model | 1,221 | 412 implications, 809 not | **settled by the ETP** |
| 6, unresolved | 35 | 17 implications, 18 not | **settled by the ETP** |
| total ordered pairs of distinct laws without `f` | 166,056 | | **0 disagreements** |

The code-5 rows come from the three laws without `f` among the nine laws with no small model:
- `((x*y)*z)*x = w` (ETP Equation303): the ETP says it implies `x = y`, so it collapses. This has a
  two-line hand proof: take any `a`, `b` and put `x = y = z = a`. The law gives
  `((a*a)*a)*a = a` (with `w = a`) and `((a*a)*a)*a = b` (with `w = b`), so `a = b`. **Our z3 run
  missed this.** Re-run on 2026-11-22: unknown at a 1 s timeout, proved at 5 s and 20 s. A likely
  reason: z3 instantiates a universally quantified law through patterns, and `w` occurs only bare,
  so no pattern contains it. This is a lead, not checked.
- `(x*y)*(y*x) = y` (ETP Equation167): the ETP says it does not collapse, and its smallest model has
  4 elements (ETP `data/smallest_magma.txt`: `167 4`). That agrees with our size-4 model.
- `(x*y)*(y*z) = y` (ETP Equation168): this is the **central groupoid law**. It is known from the
  literature. The ETP paper (`paper/intro.tex`, same commit) says it "is an order-3 law introduced by
  Evans and studied further by Knuth", and that "all finite central groupoids have order equal to
  a perfect square n^2". Our size-4 model fits that (4 = 2^2). ETP `smallest_magma.txt`: `168 4`.
  We did not read Evans' or Knuth's papers themselves.

## Checks done (and what each one can and cannot catch)

- **Mapping:** 0 canonical clashes among ETP laws, all 408 matched, distinct targets, and the
  text reading agrees with the stored term. This catches a wrong idea of the ETP normalization. It
  cannot catch a law that our enumeration and the ETP both got wrong in the same way (very unlikely:
  the two enumerations are independent, and the counts match).
- **Orientation of the matrix:** three forced cases. This catches a transposed reading.
- **Self-test (the comparison must be able to fail):** four corruptions, all detected:
  one of our codes flipped 1 to 3 (1 disagreement, expected 1); one flipped 4 to 1 (1, expected 1);
  mapping shifted by one ETP number (49,500 disagreements); ETP matrix transposed (87,269
  disagreements). The run aborts if any corruption goes unnoticed.

## What this changes for the labels

- The 63,337 implications without `f` that were `z3-only` (codes 3 and 4) now also agree with the
  ETP, whose results are proved in Lean in that project. Our own evidence for them is still z3. For
  them the claim becomes "z3-only here, agrees with ETP".
- The 101,463 non-implications without `f` were already `model-verified`, and they agree.
- The 1,256 open pairs are now `known (ETP)`. `src/query.py` prints this for any pair of laws
  without `f`. **`results/status_matrix.npz` was NOT changed**, since rule 3 says not to edit stored
  results. The new information lives in `results/etp_crosscheck.json`.

## NOT verified

- The ETP's Lean proofs and its closure tool (`implicit_*` values are derived by the ETP's tooling,
  not by a Lean proof object per pair). We trust the ETP data as published. We did not build it.
- That the published `general_outcomes.json.gz` equals what the ETP repository at commit
  `dbc9a2b` would regenerate. We did not run `lake exe extract_implications`, which needs a Lean
  build.
- Pairs where one law contains `f` (340,176 of our 506,232 pairs): the ETP says nothing about them.
- Evans' and Knuth's papers on central groupoids (cited from the ETP paper, not read by us).
- The z3 pattern explanation for the missed collapse is a guess.

## Surprises, errors, dead ends

- **Our collapse step (step 04) missed a trivial collapse.** `((x*y)*z)*x = w` has a fresh variable
  alone on one side. Any such law collapses at once, but z3 returned `unknown` at 5 s in step 04, and
  the law was set aside as "open". Rule added to `docs/shared/LESSONS.md` (hub): before calling a law
  "open", check the cheap syntactic cases by hand.
- Size 0 is not in our enumeration (`x = y` is missing). This is harmless for the table, but the
  README now says "size 1 to 3".

## Next

- Use the ETP's counterexample magmas? Not needed for laws without `f` (all settled), but a magma
  M refuting A => B also refutes A => B' for any law B' (with `f`) that fails in M under SOME `f`.
  That might settle some code-5 and code-6 pairs that involve `f`. Queue item.
- Same treatment for the `f`-containing table: no external source exists, as far as we know.
