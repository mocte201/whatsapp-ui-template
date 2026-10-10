---
name: hermes-ux-surfaces
description: >-
  Audits Hermes product UI surfaces against curated checklists (auth/login,
  settings/account, empty/error/loading, onboarding, notification settings,
  and critical flows). Use when reviewing login, settings, onboarding, empty
  states, destructive flows, or “is this screen complete?”; after
  hermes-revisor flags product UX; or when the user asks for a surface
  checklist. Mobile chrome (viewport/touch) → hermes-ux-mobile. Does not own
  brand identity.
---

# Hermes UX Surfaces

## Goal

Produce a **surface-scoped** UX audit: which product screens/flows are in the diff (or named by the user), what’s missing vs the curated checklist, severity, and optional fixes. Refuse brand/palette/typography work and full-app redesigns.

## Preconditions

1. Confirm a frontend exists. If none, stop.
2. Prefer `git diff` / named routes or screens over the whole tree unless the user asks for a full pass.
3. On-demand (`role: null`) — no `orchestra.json` role flag.
4. Detect surfaces in scope (see catalog). If none match, say so and point to **hermes-ux-mobile** for chrome-only issues or **hermes-revisor** for general review.
5. Do not invent visual identity; use the project’s tokens.

## Procedure

Default mode: **audit**. Switch to **fix** only if the user says apply / implement / fix / arreglá.

1. List surfaces touched (routes, components, copy). Map each to the catalog below; skip N/A.
2. For each in-scope surface, walk its checklist. Mark pass / fail / N/A with evidence (file or UX observation).
3. Severity: **Blocker** = broken critical path or data-loss risk; **Should fix** = incomplete states users will hit; **Nit** = polish.
4. If notification subscribe/dispatch internals are missing → note and hand off to **hermes-pwa-push** (this skill only checks settings UX completeness).
5. If the only issues are viewport/touch/overflow → **hermes-ux-mobile**.
6. Apply fixes only in fix mode; keep changes scoped to the audited surfaces.

### Catalog (curated — not a design-system encyclopedia)

#### Auth / Login / 2FA
- Email/user + password (or project auth method) with correct `autocomplete` / `type`
- Submit pending + disable; inline error for invalid credentials (no silent fail)
- Forgot / reset password path reachable when the product has passwords
- Session expired → clear return to login with a readable message
- 2FA (if enabled): code entry, resend/cooldown, error for invalid/expired codes

#### Settings / Account
- Grouped sections; save affordance clear (explicit Save or reliable autosave + feedback)
- Unsaved changes: warn before navigate/close when edits can be lost
- Account fields validate; server errors shown on the field or section
- Sign-out reachable; destructive account actions → confirm (see Flows)

#### Empty / Error / Loading
- First-use empty: explanation + primary next action
- Filtered/search empty ≠ first-use empty (copy differs)
- Load failure ≠ empty; retry (or equivalent) on critical lists
- Loading: skeleton/spinner; no blank flash of “empty” while fetching

#### Onboarding
- Skippable unless the contract forbids it; progress or step count if multi-step
- Permissions (push, camera, etc.) asked with context, not as the first unexplained screen
- End state lands in a useful home screen; can re-enter help later if needed

#### Notification settings
- Visible control to enable/disable; permission denied explained with OS/path hint
- Reflects real subscription state (subscribed / blocked / unsupported)
- Deep push pipeline (VAPID, SW, cron) → **hermes-pwa-push**

#### Flows (when the diff touches them)
- **Submit form:** client validation → pending → success feedback or stay with errors; no double submit
- **Save changes:** success confirmation; failure recoverable without losing input
- **Delete account / irreversible:** typed confirm or equivalent; pending disable; post-success sign-out or redirect

## Output contract

```markdown
## UX surfaces summary
## Surfaces in scope
## Blockers
## Should fix
## Nits
## Per-surface checklist
### <Surface>
- [ ] … (pass | fail | N/A — evidence)
## Fixes applied
(none | list — only if user asked to fix)
## Handoffs
(none | hermes-ux-mobile / hermes-pwa-push / hermes-seguridad / …)
```

## Done criteria

- Every in-scope surface has a filled checklist (or explicit N/A)
- Mode clear (audit vs fixes)
- Blockers listed with next step; no claim of full a11y/security/perf audit

## Forbidden / handoffs

- Brand tokens, palette, typography → **hermes-identidad** (Acebal) or project CSS tokens (refuse)
- Mobile chrome only (zoom, scroll-x, touch size) → **hermes-ux-mobile**
- Web Push implementation / schema / cron → **hermes-pwa-push**
- RLS, authz, secrets → **hermes-seguridad**
- PR/contract review → **hermes-revisor**
- Perf / free-tier → **hermes-optimizador**
- Greenfield IA or new product surfaces not in contract → **hermes-arquitecto**
- Cloning external checklist libraries wholesale; stick to this curated catalog
- Absolute paths, PowerShell-only commands, assuming CLI/MCP auth
