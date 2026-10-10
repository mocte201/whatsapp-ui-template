---
name: hermes-identidad
description: >-
  Applies Municipio de Acebal visual identity (tokens, Nunito, logos, PWA
  chrome, branded PDFs, institutional UI patterns). Use when the user says
  identidad Acebal, marca municipal, que se vea como Asistencia, kit de
  marca, or invokes this skill with hermes-arquitecto / hermes-iniciador /
  hermes-escritor on an acebal profile. Not for personal apps, Excel chrome,
  or generic UX audits.
---

# Hermes Identidad

## Goal

Leave Acebal municipal identity in every phase the repo already allows: architecture contract, file kit, then UI/PDF patterns. Refuse inventing palette/type, branding `.xlsx`, and restyling screens that do not exist yet.

## Bootstrap

1. Read `.cursor/orchestra.json` (`profile`) and `docs/architecture.md` if present. Personal profile → stop unless the user explicitly wants Acebal brand anyway.
2. On-demand (`role: null`). Iniciador does **not** copy the kit unless this skill is in the same thread.
3. Read sibling `tokens.md` and copy from this skill’s `kit/` (after sync: `.cursor/skills/hermes-identidad/kit/`). Never clone another product repo.
4. Resolve **`frontendRoot`**: `web/` if it exists; else repo root when `app/` or `src/app/` lives there; else the folder that holds `package.json` + Next/Vite app. Paths below are relative to `frontendRoot`.
5. In **one pass**, run every phase the repo allows (not only the earliest). Same thread as iniciador after it created `web/` → run kit now.
   - **Contrato** — architecture doc exists or this thread is with arquitecto, and the identity block is missing.
   - **Kit** — `frontendRoot` exists.
   - **Patrones** — real routes/screens or PDF components exist.
6. Ask once for product `name` / `short_name` if unknown. Do not assume CLI/MCP.

## Procedure

### Fase contrato

1. Add the Visual identity block from `tokens.md` to `docs/architecture.md`.
2. Ready-when items: CSS tokens present; PWA theme naranja canónico; PDF header has wordmark; xlsx unbranded.
3. If there is no `frontendRoot`, skip kit/patrones. If there is, continue — do not stop the pass.

### Fase kit (`frontendRoot` exists)

1. Copy from `kit/` (create dirs):
   - Wordmarks naranja + negro (`.svg` + `.png`) → `public/brand/`
   - `logo-iso-round.svg` → `public/brand/` and `app/icon.svg` (or `src/app/icon.svg`)
   - `logo-iso-round-180.png` → `app/apple-icon.png` (or project apple-touch equivalent)
   - `icon-192.png`, `icon-512.png`, `icon-512-maskable.png` → `public/icons/`
2. Put `:root` tokens from `tokens.md` in global CSS. Replace conflicting shadcn/default theme colors that fight the palette. Do not recolor logo SVG fills to match CSS; art may be `#f18321`.
3. Load Nunito + Nunito Sans (`next/font` or equivalent). Map `--font-nunito` / `--font-nunito-sans`.
4. PWA: `theme_color` / `themeColor` `#f6821f`, `background_color` crema. Manifest icons: 192 + 512 `any` + 512 `maskable`. Product name from the user.
5. Do **not** restyle every component yet.

### Fase patrones (MVP screens or PDF components)

1. Header/nav: wordmark naranja + title; page background crema.
2. Apply card/button/input institutional classes from `tokens.md` to existing surfaces — do not invent a new page IA.
3. If `@react-pdf/renderer` (or current PDF stack) exists: header uses `logo-wordmark-negro.png` + Municipio de Acebal; Helvetica; skip if no PDF in repo.
4. Leave Excel exporters as tables only.

### Report (always)

```markdown
## Identidad Acebal
- Profile:
- frontendRoot:
- Phases done: (list all that ran, e.g. contrato, kit)
- Product name / short_name:
- Files written:
- Skipped (and why):
- Next: a11y contrast → hermes-a11y; mobile chrome → hermes-ux-mobile
```

## Output contract

- Contrato: `docs/architecture.md` identity section matching `tokens.md`
- Kit: global CSS tokens + fonts + `public/brand/*` + `public/icons/*` + PWA theme/icons
- Patrones: header/cards/accents and PDF header when those files exist
- Chat report in the shape above (IO examples: `tokens.md`)

## Done criteria

- Every allowed phase ran this pass (no “contrato only” when `web/` already exists)
- Hex/type match `tokens.md` (`#f6821f` not `#f08322`)
- xlsx untouched for branding
- User told: sync this skill into the product repo so `kit/` is present for cloud agents

## Forbidden / handoffs

- Personal default palette / Inter / shadcn violet as “close enough”
- Copying `control_de_acceso` from disk as source of truth
- Branding Excel → refuse
- Viewport/touch/overflow → **hermes-ux-mobile**
- Login/settings completeness → **hermes-ux-surfaces**
- Contrast audit after paint → **hermes-a11y**
- Push plumbing → **hermes-pwa-push** (this skill only sets install chrome colors/icons)
- Greenfield product shape → **hermes-arquitecto**; implement slices → **hermes-escritor**
- Absolute paths, PowerShell-only steps, assuming MCP/CLI auth

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “I’ll copy Asistencia from the other repo” | Tokens live in this skill; other repos drift |
| “Arquitecto needs pretty cards now” | No screens → skip patrones; still do contrato (and kit if `frontendRoot` exists) |
| “MVP can ship Inter; brand later” | Kit lands with `frontendRoot` or the first UI slice is born off-brand |
| “theme_color #f08322 is the real naranja” | Canonical is `#f6821f` |
| “Excel should look official too” | xlsx is data; no logo |
| “PWA icons later” | Kit copies 192/512/maskable from `kit/` |
| “Iniciador always copies the kit” | Only if this skill is invoked; otherwise on-demand |
| “Architecture block missing, so I stop” | Contrato then continue into kit/patrones if the tree allows |

## Red flags

- New hex not in `tokens.md`
- Nunito missing while body uses Inter/system
- Patterns applied during architecture with no app pages
- Pass stopped after contrato while `web/` or screens already exist
- PDF without wordmark PNG when PDF components exist
- xlsx with logo or “Municipio de Acebal” banner
- `theme_color` ≠ `--color-naranja`
- Manifest missing maskable 512 when kit ran

## Verification

- [ ] `orchestra.json` profile is acebal (or user override recorded)
- [ ] Diff shows tokens/files from `tokens.md` / `kit/` (named files above), not invented colors
- [ ] Phase evidence: architecture section and/or CSS `:root` and/or a branded component path — matches **Phases done**
- [ ] Grep of xlsx/export paths: no new logo/header
- [ ] If kit ran: `theme_color` `#f6821f` and `public/icons/icon-192.png` + `icon-512.png` + `icon-512-maskable.png` exist under `frontendRoot`
