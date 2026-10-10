---
name: hermes-lanzamiento
description: >-
  Pre-merge / pre-production ship gate for Hermes apps: unifies smoke, secrets,
  free-tier, security residual risk (incl. hardening axes), critical UX, and
  optional kill-switch or push surfaces into go/no-go. Use before merging
  preview to main, before a production deploy, or when the user asks if it is
  safe to ship / lanzar.
---

# Hermes Lanzamiento

## Goal

Answer **go / no-go** for merge or production with evidence. Consolidate findings; do not re-architect. Run deep passes by invoking other skills’ checklists (or reading recent reports), not by rubber-stamping.

## Bootstrap

1. Read `.cursor/orchestra.json` and `docs/architecture.md` (status should be `approved` for real ship; if draft, no-go until **hermes-arquitecto** + human approval).
2. Read writing plan (`orchestra.paths.implementationPlan` or `docs/implementation-plan.md`) for §H queue/gates.
3. Identify target: PR → `main`, preview URL, or production domain. **Freeze the candidate:** record the exact head SHA the verdict covers; every check below must run against that SHA.
4. Skim latest review/security/gate notes if present; re-run only what is stale or missing.
5. Shared floor when available: orchestrator `skills/_references/definition-of-done.md`; else architecture Ready-when + this skill’s checklist.

## Ship checklist

Complete what applies (skip disabled services):

### A. Smoke & correctness

- [ ] Install/build/lint/tests (or project equivalent) — report commands
- [ ] Any failure called “pre-existing” reproduced with the same command on a clean `main` checkout; otherwise report it as `baseline unverified` (counts as a failure for GO)
- [ ] Ready-when items from architecture met or waived by human in writing
- [ ] Open Blockers from **hermes-revisor** resolved

### B. Secrets & config

- [ ] No secret values in git; `.env.example` has **names** only
- [ ] Runtime secrets present in the right place (local `.env`, Vercel/Cursor dashboard — do not print values)
- [ ] `orchestra.json` secrets list matches what production needs (names)

### C. Security residual

- [ ] RLS / authz / GAS scopes pass or residual risk accepted explicitly (→ **hermes-seguridad** if not done)
- [ ] No service-role / private keys in client bundles
- [ ] Hardening residual from **hermes-seguridad** addressed or accepted: prod HTTPS (not local `*.local`), security headers, auth abuse/rate-limit on login surfaces, upload caps if Storage used, no over-broad API fields, field-tampering allowlists on privileged writes — each ok / residual / N/A with evidence

### D. Free-tier & ops

- [ ] No Hobby **Vercel Cron** denser than once/day (→ **hermes-optimizador**)
- [ ] Cron/background jobs have a known owner and secret header pattern if external
- [ ] GAS quotas/triggers sane if clasp enabled

### E. Product surfaces (if UI)

- [ ] Critical path: load / empty / error not blank
- [ ] Mobile/chrome risks flagged or cleared → **hermes-ux-mobile** / **hermes-ux-surfaces** when symptoms **or** when Ready-when / plan gates required them
- [ ] Public UI a11y blockers known → **hermes-a11y** if in scope (Ready-when, gate, or public multi-user UI)

### F. Hermes extras (if enabled in project)

- [ ] Kill-switch / entitlement path OK when skill used → **hermes-kill-switch**
- [ ] Web Push VAPID: public in client, **private** never in git → **hermes-pwa-push**
- [ ] Baileys/worker: session/secrets not committed → **hermes-baileys**
- [ ] Minimal operability/logs for prod path → **hermes-observabilidad** if shipping long-lived service **or** Ready-when/gate required it

### G. Human gates

- [ ] Pipeline: no auto-merge; human merge still required
- [ ] Preview URL or deploy target stated
- [ ] Required CI checks identified (branch protection / rulesets) and green on the frozen SHA; requiredness unknown → not merge-ready, say so
- [ ] **Rollback path** stated: how to revert (hosting instant rollback, revert commit, feature flag / kill switch) **and** what it does not undo — DB migrations, sent push/WhatsApp/email, cron or webhook side effects, external writes. Destructive migration (drop/rename column or table, data rewrite) with no backup or down path → Blocker unless human accepts it in writing

### H. Plan & promised passes

- [ ] Writing plan: every slice `done`, **or** human waiver in writing for any `pending`/`blocked`/`in_progress`
- [ ] Every typed `gates` value that appeared on any slice has evidence (skill report / checklist) or an explicit residual acceptance: `seguridad`, `identidad`, `a11y`, `ux-surfaces`, `ux-mobile`, `observabilidad`, `optimizador`, `simplificador`
- [ ] Architecture **Identidad**: if `on` → brand pass evidenced or waived; if `off` / Hermes tree → **N/A** (do not demand hermes-identidad)
- [ ] Ready-when items from architecture: each checked or waived — this is where deferred quality passes close

## Output contract

```markdown
## Ship verdict: GO | NO-GO
## Target (branch / URL / env)
## Candidate SHA (verdict void after any new commit)
## Plan queue: complete | waived | incomplete (NO-GO)
## Identidad: on | off | N/A — evidence or waiver
## Evidence (commands / checks)
## Open Blockers (must be empty for GO)
## Rollback (how + what it does not undo)
## Residual risk (accepted?)
## Follow-ups (post-merge ok)
```

Verdict **GO** only if no open Blockers, smoke evidence exists on the frozen SHA, a rollback path is stated, and §H plan/gates are satisfied or waived. Otherwise **NO-GO**. A GO is evidence, not authorization: merge/deploy stays a separate human order.

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Review looked fine last week” | Re-check smoke + secrets for *this* revision |
| “Preview works on my machine” | Name the environment; dashboard secrets may differ |
| “We’ll fix RLS after launch” | Data exposure is not a post-merge nice-to-have |
| “Cron hourly is temporary” | Temporary still fails deploy or burns free-tier |
| “Supabase nos cubre de SQLi” | Typed client helps; still need **hermes-seguridad** evidence (or clear residual) on injection paths, RLS, and no privileged keys in client — do not GO on brand alone |
| “RLS ok = hardening ok” | Headers, auth abuse, uploads, and response trim still need ok / residual / N/A before GO |
| “Plan still has pending slices but preview looks good” | Incomplete queue = NO-GO unless human waived those slices |
| “Always run identidad before GO” | Only when architecture identidad is **on** (Acebal sistemas); Hermes tree = N/A |
| “That test was already failing on main” | Prove it on a clean `main` with the same command, or report `baseline unverified` |
| “GO was given this morning; one small fix since” | The verdict covers one SHA; a new commit needs a re-check of what it touches |
| “We can always roll back” | Hosting rollback does not undo migrations or messages already sent; name what is irreversible |

## Red flags

- GO with failed smoke
- GO while architecture `draft`
- Secret values pasted into the report
- Skipping security section on auth-bearing apps
- GO with blank hardening axes on apps that have login, uploads, or public APIs
- GO with pending plan slices and no waiver
- Demanding Acebal brand evidence on a Hermes (identidad off) repo
- Verdict with no SHA, or evidence gathered on a different SHA than the one to merge
- Failure waved as “pre-existing” without clean-base proof
- GO on a destructive migration with no backup/down path and no written acceptance

## Verification

- [ ] Verdict is GO or NO-GO (not “probably”)
- [ ] Candidate SHA recorded; smoke/CI evidence refers to that SHA
- [ ] Rollback section names the revert mechanism and the irreversible parts (or “none: reason”)
- [ ] Evidence section lists real commands or explicit “not runnable: reason”
- [ ] Security §C includes hardening axes (or explicit N/A per axis) when login/uploads/public API exist
- [ ] §H plan queue + gates/Ready-when addressed
- [ ] Every NO-GO has at least one Blocker with owner skill or human action

## Done criteria

- Human has a binary verdict and residual risk list
- NO-GO items point to **hermes-depurador** / **hermes-seguridad** / **hermes-escritor** / **hermes-arquitecto** (re-plan) / human secret config as needed

## Forbidden

- Merging or deploying without human request
- Self-approving architecture
- Marking GO while inventing missing live checks as green
- Requiring **hermes-identidad** when identidad is off
