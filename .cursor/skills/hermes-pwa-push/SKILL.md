---
name: hermes-pwa-push
description: >-
  Implements or audits Web Push for Hermes PWAs (Next.js + Supabase): service
  worker push/click, VAPID subscribe UX, subscription APIs, queued
  notification_events, dispatch with web-push, and secured cron. Use when the
  user asks for notificaciones push, PWA notifications, Web Push, VAPID,
  activar notificaciones, service worker push, push queue/dispatch, or to
  port a proven push pattern to another Hermes project.
---

# Hermes PWA Push

## Goal

Leave Web Push working end-to-end: permission → stored subscription → domain events enqueued → secured dispatch delivers → SW shows and deep-links. Refuse inventing product event types without contract, multi-channel (email/WhatsApp), and SQL that performs outbound HTTP.

## Bootstrap

1. Confirm a web frontend that can host a service worker at origin scope `/`. No UI → stop.
2. Read `docs/architecture.md` and `.cursor/orchestra.json` if present. Permanent schema with push out of contract → stop → **hermes-arquitecto**.
3. On-demand (`role: null`); no orchestra role flag required.
4. Inventory (Fase A) before writing; adapt, do not duplicate.
5. Read sibling `reference.md` for schema shapes, traps, and the queue-then-dispatch canon. Secrets = **names only**. Do not assume CLI/MCP authenticated.

## Procedure

Modes: **audit** (mapear/revisar) · **implement** (wire/activá) · **document** (spec/runbook). Default: audit then implement gaps.

### Fase A — Inventory

| Piece | Look for |
| --- | --- |
| Manifest | installable PWA (`standalone`, icons) |
| SW register | client `register("/sw.js")` early |
| SW push/click | `push` + `notificationclick`; payload `title`/`body`/`url` |
| Subscribe UX | permission → SW ready **with timeout** → VAPID key → `subscribe` → POST |
| Unsubscribe | DELETE + browser `unsubscribe`; soft `is_active=false` |
| APIs | GET public key; POST/DELETE subscriptions (**session auth**); POST dispatch (**cron secret**) |
| Tables | `push_subscriptions`, `notification_events` (+ RLS + service_role for dispatch) |
| Enqueue | insert `delivery_status=queued` only (trigger or server) |
| Dispatch | service role + `web-push` + VAPID private; 404/410 deactivate sub |
| Retries | `attempt_count` / max attempts; stay `queued` until max then `failed` |
| Cron | GH Actions or equivalent; `PUSH_CRON_SECRET`; **`PUSH_DISPATCH_URL` var** (no hardcoded foreign host) |
| Env | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`, `PUSH_CRON_SECRET` |

### Fase B — Wire missing pieces (order)

1. Env names in project docs / `orchestra.json`; generate VAPID if needed; never commit keys.
2. Schema + RLS (own subs; own event read; service path for send).
3. Enqueue only (no HTTP from Postgres).
4. Lib: env helpers, web-push config, `dispatchQueuedNotifications` (sent / failed / expired / requeued).
5. Routes for key, subscriptions, dispatch.
6. SW: required push + click; offline cache optional.
7. Client: register SW; timeout on `ready` (iOS); `userVisibleOnly: true`; base64url → `Uint8Array`.
8. Cron with secret + configurable base URL.
9. Product `type` → `{ title, body, url }` in dispatch lib; keep SW domain-dumb.

### Fase C — Verify

Subscribe persists → domain event queued → dispatch → notification + correct URL → unsubscribe deactivates. Failures: list blockers instead of claiming green.

### Hard rules

- **Queue then dispatch** — never send from SQL.
- Deep links must exist in the real router (do not invent paths).
- Prefer repo var for dispatch origin over hardcoded product URLs.
- Traps (ready hang, 410, no retries, free-tier cron limits): see `reference.md`.

## Output contract

Update `docs/api/web-push-spec.md` (or project equivalent). Always leave:

```markdown
## PWA Push summary
(mode: audit | implement | document; e2e: yes/no/partial)

## Inventory
| Piece | Path | Status |

## Flow
(mermaid or 5–8 bullets)

## Changes applied
(none | list)

## Env checklist (names only)
- [ ] VAPID_PUBLIC_KEY
- [ ] VAPID_PRIVATE_KEY
- [ ] VAPID_SUBJECT
- [ ] PUSH_CRON_SECRET
- [ ] PUSH_DISPATCH_URL (repo variable for cron)

## Verify
- [ ] subscribe persists
- [ ] queued → sent | requeued | failed | expired
- [ ] notification + click URL
- [ ] unsubscribe / 410 deactivates

## Gaps / risks
## Next step
(one concrete user action)
```

## Done criteria

- Inventory complete before and after writes
- Queue-then-dispatch respected; secrets by name only
- Spec lists endpoints, statuses, retry rule, env **names**
- Verify checked or blockers explicit

## Forbidden / handoffs

- Brand / mobile chrome UX only → **hermes-ux-mobile**; Acebal `theme_color` / icons → **hermes-identidad**
- Notification settings screen completeness (copy/states) without push plumbing → **hermes-ux-surfaces**
- Full RLS beyond push tables → **hermes-seguridad**
- Free-tier cost deep dive → **hermes-optimizador**
- WhatsApp / email → **hermes-baileys** / product skills
- Greenfield product contract → **hermes-arquitecto**
- Absolute paths, PowerShell-only steps, assuming CLI/MCP auth
- Committing VAPID private keys or cron secrets
- Inventing domain event types not in architecture or explicit user list
