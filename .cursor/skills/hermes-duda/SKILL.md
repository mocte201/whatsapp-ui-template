---
name: hermes-duda
description: >-
  Trigger: doubt, challenge, adversarial review, high stakes before APROBADO.
  Adversarial in-flight review: CLAIM → EXTRACT → DOUBT → RECONCILE → STOP.
  Use when stakes are high (prod/auth/personal data/irreversible) or the user
  asks to doubt a plan before approval.
---

# Hermes Duda

## Goal

Stress-test a decision, plan, or patch **before** APROBADO or merge. Produce doubts with severity — not a full five-axis revisor pass (→ **hermes-revisor** for diffs).

## Bootstrap

1. Confirm stakes are real: prod data, security, money, irreversible migration, public municipality data, or user requested doubt.
2. Identify the **claim** under review (architecture choice, PR summary, algorithm).
3. If the task is a normal bug hunt → **hermes-depurador**; normal PR review → **hermes-revisor**.

## Decision Gates

| Situation | Action |
| --- | --- |
| Low stakes / style nits | Refuse theater; send to revisor or skip |
| High stakes + Task/subagent available + user wants stronger challenge | Optional **dual-pass**: two short independent doubt passes on the same frozen claim; merge only overlapping Blockers as auto-escalations |
| One pass finds Blocker, the other does not | Record as suspect; do not auto-treat as confirmed Blocker |
| After two reconcile rounds Blockers remain | Verdict **stop**; do not invent more rounds |

## Procedure

1. **CLAIM** — restates the decision in one paragraph (what / why / alternative rejected). Freeze that text as the target.
2. **EXTRACT** — list load-bearing assumptions (explicit and hidden).
3. **DOUBT** — attack each assumption: what if false? worst case? free-tier? multi-tenant? cloud agent limits?
4. **RECONCILE** — for each doubt: dismiss with evidence, accept residual risk, or change the plan. At most **two** reconcile rounds if the user iterates.
5. **STOP** — if a Blocker-level doubt remains, recommend not approving / not merging until addressed.

### Optional dual-pass (high stakes only)

When enabled: launch two brief independent passes (or two subagents) against the **same frozen claim**. Parent merges findings. Confirmed Blockers = reported by both. Single-sided findings stay “suspect”. Dual-pass does **not** authorize merge, push, or release — it only strengthens the verdict. Missing subagent tooling → single pass + note `doubt_mode: single`.

## Output contract

```markdown
## Claim under review
## Assumptions
## Doubts (severity: Blocker | Should address | FYI)
## Reconciliations
## doubt_mode: single | dual
## Verdict: proceed | proceed-with-risk | stop
## Suggested next skill (arquitecto / seguridad / fuente / revisor)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “We’re sure — skip doubt” | High stakes make confidence cheap and wrong expensive |
| “This replaces revisor” | Different job: decisions/assumptions, not every line |
| “All doubts are Blockers” | Prioritize; FYI noise trains humans to ignore |
| “No evidence, so dismiss” | Unverified load-bearing claims stay open → **hermes-fuente** |
| “Dual-pass forever until green” | Two rounds max; then escalate to the human |

## Red flags

- Verdict proceed with an open Blocker doubt
- Doubting unrelated style nits instead of assumptions
- Running on trivial copy tweaks without user request
- Treating a single-sided dual-pass finding as confirmed Blocker

## Verification

- [ ] Claim restated and acknowledged (frozen)
- [ ] At least one non-trivial assumption extracted (or explicit “none; low stakes”)
- [ ] `doubt_mode` stated
- [ ] Verdict matches residual Blockers

## Done criteria

- Human has proceed / proceed-with-risk / stop with named doubts
- Handoffs set for unresolved items

## Forbidden

- Rewriting the app during doubt
- Approving architecture on the user’s behalf
- Using doubt theater to delay trivial work
- Claiming dual-pass delivery authority (merge/push/release)
