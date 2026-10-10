---
name: hermes-a11y
description: >-
  Practical accessibility pass for Hermes web UIs against WCAG 2.1 AA oriented
  checks: keyboard, names, contrast, forms, focus, semantics. Use when shipping
  public or multi-user UI, after hermes-revisor flags a11y risk, or when the user
  asks for accessibility / accesibilidad review.
---

# Hermes A11y

## Goal

Find accessibility defects that block or humiliate real users. Focus on actionable issues in the touched surfaces — not a legal certification.

## Bootstrap

1. Confirm UI exists (web). Pure API/GAS-only without HTML UI → stop (N/A).
2. Identify pages/flows in scope (auth, forms, tables, dialogs).
3. Prefer keyboard + semantic review; use automated tooling only if already in the project — do not invent CI.
4. Mobile chrome/PWA feel stays → **hermes-ux-mobile**; product empty/error surfaces → **hermes-ux-surfaces**.

## Checklist (WCAG-oriented, practical)

### Keyboard & focus

- All interactive controls reachable and operable without a pointer
- Focus order sensible; no keyboard traps in modals
- Visible focus styles not removed

### Names & semantics

- Buttons/links/icon-only controls have accessible names
- Headings / landmarks not purely for style
- Images with meaning have alt; decorative empty/hidden

### Forms

- Labels tied to inputs; errors associated and announced in plain language
- Required fields programmatically indicated

### Contrast & motion

- Text/icon contrast reasonable on brand surfaces (flag gross failures)
- No essential info only via color
- Respect reduced motion when animations carry meaning (if project animates)

### Dynamic UI

- Dialogs: focus move + escape/return
- Live updates not silent if critical (errors, auth)

## Output contract

```markdown
## A11y summary
## Blockers
## Should fix
## Nits
## Out of scope / not tested
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Mobile pass already covered a11y” | Touch UX ≠ keyboard/SR/name/contrast |
| “Only internal tool” | Municipality/staff UIs still need operable UI |
| “We’ll add aria later” | Wrong aria is worse; fix names/labels first |
| “Lighthouse 100 required” | Practical defects first; score optional |

## Red flags

- Icon-only controls with no name
- Modals without keyboard exit
- Form errors only as red borders
- Declaring “AA compliant” as legal fact

## Verification

- [ ] Surfaces in scope listed
- [ ] Each Blocker has component/path
- [ ] Not tested called out (e.g. no screen reader available)

## Done criteria

- Report filed with severities
- Handoff to **hermes-escritor** for fixes if user wants implementation

## Forbidden

- Full brand/visual redesign under a11y → **hermes-identidad** (Acebal)
- Claiming certification or legal compliance
- Deep security RLS work → **hermes-seguridad**
