<!-- Canonical copy: https://github.com/Math-Problem-Solving-Using-AI/math-curiosity (docs/). Synced by tools/sync_shared_docs.sh.
     Do not edit this copy, change the hub and sync. -->

# Step record template

Copy into `steps/NN-short-title.md`. One file per step. Commit the step with
the code change that produced it. Fill every field, write "none" or "not done" instead of
leaving blanks. A step that failed is still a step: record it.

```markdown
# NN. Title

- Date:
- Status label: (see docs/shared/VERIFICATION_PROTOCOL.md status ladder)
- Commit(s):

## Goal
One or two sentences.

## Command(s)
Exact commands, run from the repo root.

## Inputs
Files, parameters, tool versions.

## Output
Files produced, key numbers.

## Checks done (and what each one can and cannot catch)
- ...

## NOT verified
Everything we did not check. This list must not be empty.

## Surprises, errors, dead ends
What went wrong, and the entry added to docs/shared/LESSONS.md.

## Next
```
