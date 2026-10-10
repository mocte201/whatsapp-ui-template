---
name: hermes-ux-mobile
description: >-
  Audits mobile UX for Hermes UIs: viewport/PWA zoom lock, overflow, touch
  targets, loading/spinners, empty/error states, mobile forms, destructive
  confirms, and focus/keyboard basics. Does not own brand tokens or visual
  identity. Use when reviewing mobile UX, scroll-x, zoom, touch targets,
  loading states, empty states, PWA feel, or after hermes-revisor flags
  frontend interaction issues. For product-surface checklists (login, settings,
  onboarding) → hermes-ux-surfaces.
---

# Hermes UX Mobile

## Goal

Produce a mobile-UX audit (checklist + severity report). Fix code only when the user asks. Refuse brand/palette/typography identity work.

## Preconditions

1. Confirm the repo has a frontend (web UI, Next/React, or equivalent). If none, stop and say so.
2. Prefer `git diff` / changed UI files over the whole tree unless the user asks for a full pass.
3. Do not check an `orchestra.json` role flag — this skill is on-demand (`role: null`).
4. Do not invent or enforce palette/typography. Identity lives in the project's own tokens (e.g. CSS variables); refuse that work here.

## Procedure

Default mode: **audit**. Switch to **fix** only if the user says apply / implement / fix / arreglá.

Walk these checks (principles first; Tailwind/Next class names are examples only):

1. **Viewport / PWA feel** — If the product is meant to feel native: `device-width`, `maximumScale: 1`, `userScalable: false`, `viewportFit: cover` (intentional a11y tradeoff) → missing zoom lock is a Blocker. If not PWA-native, mark zoom lock N/A; still require inputs `font-size` ≥ 16px on mobile.
2. **Overflow** — no unintentional horizontal scroll; find the cause before root `overflow-x: hidden`; avoid `overflow-x: auto` on wrappers unless justified.
3. **Safe area / touch** — safe-area padding where needed; targets ~44×44; immediate `active`/pressed feedback; critical CTAs full-width on small screens; sticky CTAs must not cover content or errors (pad scroll area).
4. **Layout** — mobile-first breakpoints; fluid type/spacing; no hover-only discovery of actions.
5. **Tables / forms** — tables → stacked cards below ~768px; labels visible; inputs full-width + touch height; correct `type` / `inputMode`; scroll to first error; don’t hide errors behind the keyboard; submit shows pending + disables to prevent double submit; inline field errors stay visible after failed submit.
6. **Loading** — every async action shows visible feedback; buttons disable + spinner/“cargando…”; lists/pages: skeleton or centered spinner (no blank screen); prefer skeleton for structure, spinner for one-shot actions.
7. **Empty / error** — empty state with next action (not only an illustration); recoverable errors with retry on critical flows (not only a fleeting toast); distinguish empty vs failed-to-load when the data source can fail.
8. **Gestures / density** — adequate gap between tappable controls; `touch-manipulation` where it helps.
9. **Destructive** — irreversible actions (delete account, cancel plan, wipe data) require an explicit confirm step; confirm CTA stays disabled while the request is pending.
10. **Focus / keyboard** — interactive controls show a visible focus state; modals/drawers trap focus and restore it on close; Esc (or equivalent) dismisses when that pattern exists on desktop widths.

## Output contract

```markdown
## UX mobile summary
## Blockers
## Should fix
## Nits
## Checklist
- [ ] viewport / zoom lock if PWA-native (else N/A) + inputs ≥16px
- [ ] no unintentional scroll-x
- [ ] safe-area padding where needed
- [ ] touch targets ~44×44 + active feedback
- [ ] critical CTAs full-width on small screens; sticky CTAs don’t cover content
- [ ] tables → cards on small screens
- [ ] forms: labels, full-width, inputMode/type, errors visible, pending submit
- [ ] loading on async (button + page/list)
- [ ] empty (with next action) + recoverable error; empty ≠ load failure
- [ ] no hover-only actions
- [ ] gaps / touch-manipulation between controls
- [ ] destructive actions need confirm + pending disable
- [ ] focus visible; modal focus trap / restore when modals exist
## Fixes applied
(none | list — only if user asked to fix)
```

Severity: Blockers block merge advice for mobile-critical flows.

## Done criteria

- Report filled for the inspected surface
- Mode clear (audit vs fixes applied)
- User told next steps if Blockers remain; deep security/perf not claimed here

## Forbidden / handoffs

- Brand tokens, palette, typography, institutional color semantics → **hermes-identidad** (Acebal) or the project’s CSS tokens (refuse; do not invent).
- Product-surface completeness (login, settings, onboarding, billing copy/states) → **hermes-ux-surfaces**
- Full PR correctness / contract review → hermes-revisor. Revisor defers deep mobile UX → this skill.
- RLS / secrets / GAS scopes → hermes-seguridad
- Perf / free-tier → hermes-optimizador
- PWA packaging (manifest icons, service worker strategy) — out of scope unless it blocks viewport/install feel already in checklist
- Absolute paths, PowerShell-only commands, assuming CLI/MCP auth
