---
name: hermes-observabilidad
description: >-
  Lightweight observability for Hermes free-tier apps: structured logs, user-visible
  errors, minimal metrics mindset — without heavy APM. Use when shipping a
  long-lived service, debugging production blindness, before hermes-lanzamiento
  on non-trivial apps, or when the user asks for logging / métricas / telemetry.
---

# Hermes Observabilidad

## Goal

Make production failures diagnosable without expensive stacks. Prefer structured logs + clear error boundaries over full OpenTelemetry unless the project already has it.

## Bootstrap

1. Read `.cursor/orchestra.json` and architecture runtime shape.
2. Identify critical paths (auth, writes, payments, workers, crons, WhatsApp).
3. Assume free/Hobby: no mandatory paid APM; do not propose multi-vendor observability as default.
4. Secrets never logged (tokens, PII beyond need). Prefer ids over raw personal data.

## Procedure

1. **On-call questions** — for each critical path: “How do we know it failed? How do we find the request?”
2. **Logs** — structured fields: `level`, `event`, `request_id`/`correlation` if available, `user_id` only if needed, `error_code`. Avoid `console.log` dumps of whole objects with secrets.
3. **User-visible errors** — map failures to safe messages; keep detail in logs.
4. **Metrics (minimal)** — if easy: count of hard failures on critical path; else document what dashboard (Vercel/Supabase logs) the human uses.
5. **Alerts** — only if there is a free path the user will actually watch; otherwise list manual log checks in runbook → **hermes-documentador**.
6. **Workers / crons / Baileys** — ensure job start/end/fail logs; never mute crash loops.

## Output contract

```markdown
## Observability summary
## Critical paths covered
## Changes applied or proposed
## What we still cannot see
## Free-tier / cost notes
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Logs later after launch” | First prod incident needs yesterday’s logs |
| “Need full Datadog now” | Start with platform logs + structured app logs on free |
| “Log the whole request body” | PII/secrets risk → **hermes-seguridad** |
| “Metrics without a question” | Each metric must answer a fail/success question |

## Red flags

- Tokens or passwords in log lines
- Silent `catch` with empty handler on critical paths
- Recommending paid APM as the only solution on Hobby without a free baseline

## Verification

- [ ] Each critical path has a “how we know it failed” answer
- [ ] No secret values in sample log lines
- [ ] User-facing errors do not leak internals

## Done criteria

- Gap list clear for **hermes-lanzamiento**
- Optional runbook note if ops needed

## Forbidden

- Full product rewrite for telemetry
- Replacing error fixing with dashboards → **hermes-depurador** for the bug
- Security policy design beyond log hygiene → **hermes-seguridad**
