---
name: hermes-kill-switch
description: >-
  Wires or audits remote entitlement (kill switch) clients: at-run check against
  Percy's personal control plane, opaque fail when suspended, grace-day fail-open
  when the server is down. Use when the user asks for kill switch, entitlement,
  apagar scripts a distancia, licencia remota, grace_days, or to port the Hermes
  kill-switch standard into a GAS, web, or local Node project.
---

# Hermes Kill Switch

## Goal

Leave a project **gateable remotely** under the Hermes entitlement contract: each run checks the control plane; `suspended` aborts with an opaque error; unreachable server + fresh cache allows work up to `grace_days` (default 30). Refuse inventing DRM, billing UIs, or co-admin municipal toggles. Refuse putting service-role / table reads of the license DB in the product repo.

## Bootstrap

1. Read sibling `reference.md` (HTTP contract, client policy, env **names**, schema of the personal control plane).
2. Read `docs/architecture-kill-switch.md` if present (canonical full contract in Orchestrator); if product only has a short note, follow `reference.md`.
3. Inventory runtime(s): GAS, server web (Next/API), Node/local batch. No runnable entrypoint → stop and ask.
4. On-demand (`role: null`); no orchestra role flag. Do not assume CLI/MCP authenticated.
5. Modes: **audit** · **implement** · **document**. Default: audit then implement gaps. **Control plane** (Supabase personal table + Edge Function) is built only if the user is working on the control plane / Orchestrator and explicitly asks; default product work = **client kit only**.

## Procedure

### Fase A — Inventory

| Piece | Look for |
| --- | --- |
| Entry points | Menú GAS, time-driven triggers, `main`/CLI, server routes that do real work |
| Entitlement call | HTTP client to control plane before useful work |
| Cache | `last_ok_at` + `grace_days` (PropertiesService, local file, server memory) |
| Opaque errors | Generic network/service failure; no "license"/"kill switch" copy in UI |
| Env / secrets | `ENTITLEMENT_URL`, `ENTITLEMENT_PROJECT_ID`, `ENTITLEMENT_INSTANCE_SECRET` (names only in git) |
| Server-only gate (web) | Check not only in client React |
| Row registered | Operator has `project_id` + secret hash in personal control plane (ask user; cannot invent) |

### Fase B — Wire missing pieces (order)

1. Confirm or ask for **stable `project_id`** (e.g. `acebal-<system>`) and that the operator will insert the row + hash in the personal table (skill does not invent secrets).
2. Copy/adapt kit from Orchestrator `templates/kill-switch/` when available; otherwise implement from `reference.md`.
3. Place client module + invoke at **start of each execution** (every job/run/serious mutating request).
4. Persist cache only after explicit `active`. On `suspended`, abort opaque (**grace does not apply**). On network/5xx, apply grace if `last_ok_at` within `grace_days`.
5. Env **names** in `.env.example` / `orchestra.json` → `secrets` / runbook; values only in Script Properties, host env, or local gitignored files.
6. Web: gate in **server** path. GAS: `UrlFetchApp`. Local: `fetch` + file/cache.

### Fase C — Verify (or list blockers)

- [ ] `active` → trabajo útil sigue
- [ ] `suspended` (o mock) → abort opaco en el próximo run
- [ ] server down + cache fresca → sigue dentro de grace
- [ ] server down + sin cache / grace vencido → abort opaco
- [ ] secrets not in git

## Client policy (normative — do not weaken)

1. Check entitlement at **start of each execution**.
2. `suspended` → opaque abort; ignore remaining grace.
3. `active` → store `last_ok_at` + returned `grace_days`; continue.
4. Timeout/5xx → continue only if `now - last_ok_at ≤ grace_days`; else opaque abort.
5. User-facing errors stay generic (network/service). Never surface control-plane URL as a "license" message.

## Output contract

Always leave:

```markdown
## Kill switch summary
(mode: audit | implement | document; runtimes: GAS | web | local)

## Inventory
| Piece | Path | Status |

## project_id
(value or TBD — operator must register control plane row)

## Changes applied
(none | list)

## Env checklist (names only)
- [ ] ENTITLEMENT_URL
- [ ] ENTITLEMENT_PROJECT_ID
- [ ] ENTITLEMENT_INSTANCE_SECRET

## Verify
- [ ] active → ok
- [ ] suspended → opaque abort
- [ ] down + grace → ok
- [ ] down + no/expired grace → abort
- [ ] no secrets in git

## Gaps / risks
## Next step
(one concrete operator action — e.g. insert row, set Script Property)
```

Optional: short project note under `docs/` only if the repo already documents ops patterns — do not invent a marketing doc.

## Done criteria

- Inventory before and after writes
- Client policy above respected (opaque suspend; grace only on unreachable + prior active)
- Env **names** listed; no secret values committed
- Verify checked or blockers explicit
- User told: operator still must toggle rows on **personal** Supabase Table Editor; product deploy alone is not enough

## Forbidden / handoffs

- Greenfield product domain design → **hermes-arquitecto**
- Full product feature implementation beyond the gate → **hermes-escritor**
- Broad RLS / secret audit of the product → **hermes-seguridad**
- Free-tier deep cost → **hermes-optimizador**
- Changing the global kill-switch contract → edit Orchestrator `docs/architecture-kill-switch.md` (then this skill / `reference.md`); do not fork policy per repo
- Reading license table from product with service role / anon open select
- Co-admin municipal reactivation UX; billing UI; DRM/obfuscation
- Message like "licencia vencida / contactar al autor" when suspended
- Absolute paths, PowerShell-only steps, assuming CLI/MCP auth
- Committing `ENTITLEMENT_INSTANCE_SECRET` or control-plane service keys
