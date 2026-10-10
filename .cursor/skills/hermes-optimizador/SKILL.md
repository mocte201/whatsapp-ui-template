---
name: hermes-optimizador
description: >-
  Performance and cost pass for Hermes projects with measure-first discipline:
  React re-renders, Supabase query shape, Vercel/Supabase free-tier, GAS quotas,
  Core Web Vitals when UI is in scope. Use when the user asks to optimize,
  reduce costs, speed up, or after hermes-escritor for a dedicated perf session.
---

# Hermes Optimizador

## Goal

Improve performance and reduce free-tier waste. One focused pass; **measure first**. Recommendations must fit the **actual** free-tier limits of each service — never propose a “cheap” setup that free plans reject or silently throttle.

## Preconditions

- Read `.cursor/orchestra.json`; honor `roles.optimizer`.
- Ask which surface to optimize if unclear (UI, queries, GAS, build size, scheduled work).
- Assume Hobby / free unless the user or account evidence says Pro/paid.
- Establish a before signal: timing, query count, bundle size, Lighthouse/CWV estimate, or reasoned bottleneck with evidence — never optimize by vibe alone.

## Free-tier hard limits (always honor)

When proposing schedules, background work, or hosting patterns, treat these as hard constraints. If the need exceeds them, name the constraint and pick an alternative — do not invent hourly/near-real-time **Vercel Cron** on free.

### Vercel (Hobby / free)

| Cap | Rule |
| --- | --- |
| Cron frequency | **Once per day max** per cron expression. Anything more frequent fails deploy (`Hobby accounts are limited to daily cron jobs`). |
| Precision | Invocation may land **anywhere in the target hour** — not minute-accurate. |
| Environment | Built-in crons run on **production** only. |

**Do not** recommend Vercel Cron for hourly, every-N-minutes, dual daily slots (`0 9,21 * * *`), or near-real-time jobs on free.

If the job must run more than once per day on free-tier, choose one and state the tradeoff:

1. **External free scheduler → HTTP** — hit the same Route Handler / API with a secret header (GitHub Actions `schedule`, cron-job.org, etc.). Still counts as function invocations.
2. **Supabase `pg_cron` / DB-side job** — only if Supabase is enabled and the work is data-centric.
3. **GAS time-driven trigger** — only if clasp/GAS is enabled and the work fits Apps Script.
4. **Upgrade path** — Pro allows sub-daily Vercel Cron; say so only if the user prefers that over free alternatives.

One daily Vercel Cron (e.g. nightly cleanup, daily digest) is fine on Hobby.

### Supabase (free)

- Prefer lean selects/indexes over “poll every minute from serverless”.
- Note project pause on inactive free projects; long silence between cron-like pings can leave the project cold.
- Do not propose unlimited Realtime fans or unbounded storage as free-safe.

### GAS (if enabled)

- Batch Sheet I/O; avoid per-row `getValue` loops.
- Trigger frequency vs Apps Script daily quotas; prefer fewer, thicker runs.

## Checklist by service

### Frontend (and CWV when UI is in scope)

- Unnecessary re-renders; list virtualization only if needed
- Fetch waterfalls; duplicate requests
- Bundle: heavy imports that can be lazy-loaded
- If user-facing web: consider LCP / INP / CLS drivers (large images, blocking JS, layout shift) — measure or state what you could not measure

### Supabase

- Select only needed columns
- Missing indexes for hot filters (propose migration; don't invent blindly)
- N+1 patterns; over-fetching relations
- Realtime subscriptions left open

### Vercel

- ISR/SSR vs static choice vs architecture
- Large serverless payloads / cold paths
- Image/font weight
- Scheduled work: apply **Free-tier hard limits** above before adding or keeping crons in `vercel.json`

### GAS

- Batch Spreadsheet reads/writes
- Avoid per-row `getValue` in loops
- Trigger frequency vs quota
- CacheService where appropriate

## Output contract

```markdown
## Perf summary
## Before signal (what was measured or why measure failed)
## Wins (applied or proposed)
## Metrics / before-after (if available)
## Free-tier risk
## Scheduling (if any): cadence | provider (Vercel Cron / external / GAS / none) | why it fits free-tier
## Do-not-touch (premature optimization)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “I’ll optimize everything that looks slow” | Measure/rank first; micro-wins drown high-impact fixes |
| “Cron every hour on Hobby is fine” | Deploy fails; use external scheduler / pg_cron / GAS / Pro |
| “Bundle size doesn’t matter on Vercel” | Cold starts, TTI, and CWV still do |
| “Skip before metrics; change and retest later” | Without a before signal you cannot claim a win |

## Red flags

- Optimizations applied with no before signal and no free-tier section
- Recommend rewriting architecture for a micro-gain without → **hermes-arquitecto**
- Security work disguised as perf (→ **hermes-seguridad**)

## Verification

- [ ] Surface in scope stated
- [ ] Before signal documented
- [ ] Any cron/schedule fits free-tier table or is labeled paid/external
- [ ] Smoke (build/lint) after applied code changes when applicable

## Done criteria

- High-impact items listed; applied changes smoke-tested when code changed (build/lint if applicable)
- Any schedule/cron suggestion fits free-tier hard limits above or is labeled as paid/external with an alternative
- Free-tier risk section filled (even if “none”)
- Architecture rewrites deferred to **hermes-arquitecto**; security depth to **hermes-seguridad**

## Forbidden

- Hourly / sub-daily / multi-fire-per-day **Vercel Cron** while assuming free/Hobby
- “Just add a Vercel cron” as the default background pattern without checking cadence vs Hobby
- Full product rewrite or feature thrash for micro-gains
- Security audit masquerading as perf (→ **hermes-seguridad**)
