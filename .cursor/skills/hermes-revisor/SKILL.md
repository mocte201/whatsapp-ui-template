---
name: hermes-revisor
description: >-
  Trigger: code review, PR review, after escritor, before merge. Reviews Hermes
  diffs against architecture + orchestra.json with a five-axis pass and severity
  labels. Use when asked to review or after hermes-escritor before merge.
---

# Hermes Revisor

## Goal

Fresh-eyes review. Find defects and contract mismatches. Do not rewrite the whole app unless asked to fix specific items. Freeze the candidate under review before scoring it.

## Preconditions

- Read `.cursor/orchestra.json`; if `roles.reviewer` is false, ask before continuing.
- Read `docs/architecture.md` (or configured path).
- **Freeze the candidate:** name the exact `git diff` / PR range / commit SHAs you will inspect. Do not silently expand scope mid-review.
- Prefer changes about **~100 lines of intent** at a time; if the diff is huge, review by logical slice and call for split → handoff sizing notes.
- Shared floor (control plane): `skills/_references/definition-of-done.md` when present in the orchestrator; in product repos use architecture Ready-when + this checklist.

## Decision Gates

| Situation | Action |
| --- | --- |
| Diff unclear / moving while reviewing | Re-freeze range; do not rubber-stamp a moving target |
| Authored size ≫ ~400 lines **and** mixed concerns | **Should fix**: ask split / chained PRs (or accept with explicit inseparable-behavior note) — not a hard Blocker alone |
| High stakes (auth, RLS, money, irreversible data, personal/municipal data) | Run five-axis here; suggest → **hermes-duda** for adversarial assumption challenge (optional dual-pass there) |
| Only nits found | Say what you inspected; do not invent Blockers |
| Deep security / perf / UX symptoms | Hand off → **hermes-seguridad** / **hermes-optimizador** / **hermes-ux-*** |

## Risk depth

Pick depth from the frozen candidate (not from vibes):

| Depth | When | What to do |
| --- | --- | --- |
| **Light** | Tiny wiring, docs-only, obvious low risk | Structural readback + Always-scan secrets/injection |
| **Standard** | Default product slice | Full five-axis + Always-scan |
| **Deep** | Auth, RLS, payments, migrations, public municipal data | Standard + explicit edge cases; recommend → **hermes-duda** and/or **hermes-seguridad** |

## Five-axis review

For each relevant hunk, score against:

1. **Correctness** — logic bugs, null/empty, races, off-by-one
2. **Contract** — matches architecture decisions and Ready-when; no silent decision flips
3. **Services** — only enabled Supabase/Vercel/clasp surfaces from `orchestra.json`
4. **Operability** — errors surfaced, loading/empty states, recoverable failure
5. **Maintainability** — change size, naming, dead traps for the next agent

### Always scan

- **Secrets** — no keys in source; `.env.example` names only; no `service_role` / secret / VAPID **private** in client code → **Blocker** if present
- **Injection** — SQL, shell, or templates built by concatenating user/request input → **Blocker**; if unsure whether input reaches a string-built query, **Should fix** + → **hermes-seguridad**
- **RLS / open writes** (Supabase) — new table/storage without policy, or `USING (true)` / `WITH CHECK (true)` on writes without architecture justification → **Blocker** (or **Should fix** + handoff if only suspected)
- **GAS** (if enabled) — quota/trigger assumptions; `clasp push` not assumed done
- **Web** (if frontend) — critical flows; surfaces → **hermes-ux-surfaces**; mobile chrome → **hermes-ux-mobile**; a11y depth → **hermes-a11y**
- Smoke failure / unclear root cause → **hermes-depurador**; high-stakes decision doubt → **hermes-duda**; pre-merge gate → **hermes-lanzamiento**
- **Ladder** — a new dependency, a new module, or a custom widget when stdlib, a native platform feature, or a helper already in the repo covers the contract, and architecture / Ready-when does not require that climb → **Should fix** (cite the file). List it; do not rewrite the diff. The rungs are **hermes-escritor** Minimal path. An item the approved contract already requires is not a finding. Density-only once behavior works → **hermes-simplificador**

## Severity (fixed)

| Label | Meaning |
| --- | --- |
| **Blockers** | Must fix before merge advice — includes client privileged keys, string-built SQL/commands with user input, and unjustified open write policies |
| **Should fix** | Real defect or contract gap; fix this PR if cheap — includes oversized mixed-concern diffs and a climb past an earlier Minimal-path rung with no contract / Ready-when reason |
| **Nitpicks** | Style/optional; never block alone |
| **Contract gaps** | Architecture missing or contradicted |
| **Suggested tests** | Proof that would have caught issues |

## Output format

```markdown
## Review summary
## Frozen candidate (range / SHAs)
## Risk depth: light | standard | deep
## Five-axis notes (only axes with findings)
## Blockers
## Should fix
## Nitpicks
## Contract gaps
## Suggested tests
## Inspected (paths / commands / evidence)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “LGTM, looks fine” | Name what you read (diff range, files). Rubber stamps are Blockers on the process |
| “I’ll review the whole repo while I’m here” | Diff/PR first; whole-repo thrash hides real defects |
| “Tests can wait; revisor is optional if CI is green” | Green CI ≠ contract match or Hermes free-tier / secrets rules |
| “Security is someone else’s job entirely” | Flag secret leaks and auth holes; deep pass stays → **hermes-seguridad** |
| “Big PR but one theme — ignore size” | If concerns mix, ask split; if inseparable, say so explicitly |
| “New package / file / widget is cleaner” | If stdlib, native, or an existing helper covers the contract, that skipped rung is Should fix. The approved contract is the only reason to climb past it |

## Red flags

- No Blockers/Should fix and no “Inspected” section
- Approving merge while Ready-when items remain open without listing them under Contract gaps
- Rewriting large files instead of listing findings
- Ignoring `roles.reviewer: false` without asking
- Silent pass on `service_role` in client, open write policies, or obvious SQL/command concatenation with input
- Silent pass on a new dependency, new module, or custom widget that an earlier Minimal-path rung already covers, with no contract / Ready-when cite
- Review without a named frozen candidate range

## Verification

- [ ] Diff or PR range named in the report (frozen candidate)
- [ ] Risk depth stated
- [ ] Every Blocker cites file/path or behavior
- [ ] Contract file was read (architecture path stated)
- [ ] Deep work handed off (seguridad / optimizador / ux / depurador / duda / lanzamiento) when symptoms match
- [ ] Each new dependency, new module, or custom widget either cites the contract / Ready-when or appears under Should fix

## Rules

- Do not rubber-stamp. If nothing found, say what you inspected.
- Do not expand into full security audit (→ **hermes-seguridad**), perf (→ **hermes-optimizador**), deep mobile UX (→ **hermes-ux-mobile**), surface checklists (→ **hermes-ux-surfaces**), ship gate (→ **hermes-lanzamiento**), or large rewrites (→ **hermes-simplificador** if complexity is the only issue).
- Do not rewrite the diff to climb the ladder. Name the skipped rung under Should fix.
