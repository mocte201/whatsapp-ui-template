---
name: hermes-depurador
description: >-
  Trigger: debug, depurar, smoke fail, build fail, root cause, blocked agent.
  Five-step failure triage: reproduce, localize, reduce, fix, guard — by root
  class, not symptom patches. Use when runtime/smoke/tests fail or after
  hermes-revisor finds a defect that needs root-cause work.
---

# Hermes Depurador

## Goal

Recover from a concrete failure with the smallest safe fix and a regression guard. Do not feature thrash or “rewrite to see if it helps.” Prefer one root fix that closes a cluster of symptoms over N caller patches.

## Bootstrap

1. Read `.cursor/orchestra.json` if present (enabled services constrain where to look).
2. Capture the failure **exactly**: command, exit code, stack, UI symptom, or agent log snippet.
3. If the “bug” is actually an unverified architecture decision or missing approval → **hermes-arquitecto** / stop implementing.
4. If pure security misconfig without a reproduce path → **hermes-seguridad**.

## Decision Gates

| Situation | Action |
| --- | --- |
| Unreproducible | Say so; stop guessing |
| Ticket mechanism passes on unmodified main | Trust the **symptom**; the stated line/diagnosis is wrong — strengthen repro until it hits the real surface |
| 2+ failures share a root | One cluster fix + named guard; do not ship N symptom patches |
| Fix wants a new state / flag / verb / parallel “truth” | Redesign: can you delete or relax something instead? |
| Broken in prod, green in tests | Suspect the test/fixture was taught to agree; remove or rewrite the pinning assertion |
| Only the named caller is patched | Grep siblings; fix the shared path once |

## Procedure (stop-the-line)

1. **Reproduce** — one minimal command or steps that fail consistently. If unreproducible, say so and stop guessing. Treat the ticket’s **mechanism** as a hypothesis; only the symptom is evidence.
2. **Classify** — bucket before coding: (A) superseded by in-flight design, (B) duplicate of a known class, (C) real bug → root-cause **cluster**, (D) feature request → **hermes-escritor** / arquitecto, (E) unclear → ask once.
3. **Localize** — which package/file/service boundary (frontend, API route, Supabase, GAS, worker). Prefer binary search over full rewrites.
4. **Reduce** — smallest failing case; strip unrelated changes from the working set.
5. **Fix** — one causal fix aligned with architecture; no drive-by refactors. Find the shared function/path, grep every caller, fix the root once. One guard there beats a patch per caller.
6. **Guard** — test, assert, or documented manual check that would catch this again. Re-run the failing smoke. Prefer guards that close the **cluster**, not only the reported path.
7. **Cloud humility** — if CLI/MCP missing on a cloud VM, do file-level fixes if safe and list the exact local commands the human must run; for pipeline Issues mark blocked language (`hermes/blocked`) with the missing secret/tool — never invent credentials.

## Output contract

```markdown
## Failure (repro)
## Bucket / cluster
## Root cause
## Fix (paths)
## Guard added
## Smoke re-run (pass/fail + commands)
## Still blocked (if any)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “I’ll rewrite the module” | Localize first; rewrites hide root cause |
| “Flaky once — ignore” | Treat as failure until proven flaky with evidence |
| “Can’t repro on cloud so ship it” | List blocked checks; do not claim green |
| “Add a try/catch and swallow” | Fix cause or surface error; silent catch is not a guard |
| “Only patch the caller in the ticket” | Symptom ≠ root; grep callers and fix the shared function once |
| “N issues need N PRs” | Shared root → one fix + evidence that closes the cluster |
| “New flag will gate the bad path” | Prefer delete/relax; new machinery often hides the real exit |

## Red flags

- Fix without reproduce steps
- Multiple unrelated changes in the same “debug” pass
- Declaring success without re-running the original failing command
- Inventing env secret values to “make smoke pass”
- Same bug class left open in an ungrepped sibling caller
- “Fixed” while a test still asserts the defective behavior as intended

## Verification

- [ ] Original failure command/steps recorded
- [ ] Bucket/cluster named (or explicit single-issue)
- [ ] Root cause stated in one or two lines
- [ ] Shared path callers considered (grep evidence or “single caller”)
- [ ] Guard present (test or manual check)
- [ ] Same smoke re-run reported pass (or honest fail + next step)

## Done criteria

- Failure fixed or explicitly blocked with reason and handoff
- Smoke path that failed now passes, or residual block is documented for the human

## Forbidden

- Broad feature work under the guise of debugging → **hermes-escritor**
- Security-only audit theater → **hermes-seguridad**
- Approving merge while still red → **hermes-lanzamiento** must stay fail
