# Acebal municipal identity — canonical tokens

Source of truth for **hermes-identidad**. Do not invent hex or type. Do not copy from another product repo.

## Palette (lock)

| Token | Hex | Use |
| --- | --- | --- |
| `--color-naranja` | `#f6821f` | Accent hover, PWA `theme_color` / viewport `themeColor`, logo chrome |
| `--color-teal` | `#0892a5` | Primary accent, focus rings, institutional buttons |
| `--color-crema` | `#f6f1ed` | Page background (`--bg-base`) |
| `--color-gris` | `#464646` | Primary text |

Mapped:

```css
:root {
  --color-naranja: #f6821f;
  --color-teal: #0892a5;
  --color-crema: #f6f1ed;
  --color-gris: #464646;
  --bg-base: #f6f1ed;
  --bg-surface: #ffffff;
  --text-primary: #464646;
  --text-secondary: #515151;
  --text-muted: #636363;
  --accent: var(--color-teal);
  --accent-hover: var(--color-naranja);
  --success: #0d9488;
  --warning: #f59e0b;
  --danger: #ef4444;
}
```

Never use `#f08322` (old PWA drift). One naranja only in CSS/PWA: `#f6821f`. Wordmark SVG art may use `#f18321` — leave it.

## Type

- Headings / brand UI: **Nunito** (`next/font/google` → `--font-nunito`)
- Body: **Nunito Sans** (`--font-nunito-sans`)
- PDF (`@react-pdf/renderer`): **Helvetica** / Helvetica-Bold (do not embed Nunito in PDF unless the stack already does)

## Assets (this skill’s `kit/`)

Destinations are under **`frontendRoot`** (see SKILL.md).

| File | Product destination |
| --- | --- |
| `logo-wordmark-naranja.svg` + `.png` | `public/brand/` (web header / login) |
| `logo-wordmark-negro.svg` + `.png` | `public/brand/` — PDF header uses the **PNG** |
| `logo-iso-round.svg` | `public/brand/` and `app/icon.svg` |
| `logo-iso-round-180.png` | `app/apple-icon.png` (or apple-touch equivalent) |
| `icon-192.png` | `public/icons/` — manifest `any` 192 |
| `icon-512.png` | `public/icons/` — manifest `any` 512 |
| `icon-512-maskable.png` | `public/icons/` — manifest `maskable` 512 |

Ask the user for **product `name` / `short_name`** (never copy “Asistencia Acebal”).

## PWA

- `display: standalone`
- `background_color`: `#f6f1ed` (crema)
- `theme_color` and viewport `themeColor`: `#f6821f`
- Icons: copy the three PNGs above; plus iso SVG as App Router `icon.svg`. Do not invent a new mark.

## PDF

- Header: `logo-wordmark-negro.png` + product title + “Municipio de Acebal”
- Footer: generated-by line, no marketing
- Do not brand **Excel / xlsx** (data grid only)

## Architecture block (fase contrato)

Paste into `docs/architecture.md` (adapt names):

```markdown
## Visual identity (Acebal)

- Profile: acebal. Palette/type/assets: hermes-identidad tokens (naranja #f6821f, teal #0892a5, crema, gris; Nunito / Nunito Sans).
- Web: CSS variables + kit logos in public/brand; PWA PNGs in public/icons.
- PWA: theme_color #f6821f, background crema, iso icon + 192/512/maskable.
- PDF: wordmark negro PNG in header; Helvetica; not a clone of the web cards.
- Excel/xlsx: no logo, no municipal chrome.
- Patterns (cards, header, accents): after real screens exist — not during architecture-only.
```

## Patterns (fase patrones — only if UI exists)

- Page bg `--color-crema` / `--bg-base`
- Header/nav: wordmark naranja + product title; logout/hover naranja
- `.card-institucional`: white, radius 16px, light border/shadow
- `.btn-institucional`: teal border; hover fill naranja/white text
- `.input-institucional`: focus teal ring
- Accents: teal primary, naranja emphasis — do not rainbow the palette

## Example input / output

**Input:** acebal repo with `web/`, login + list pages, no identity section, user says “identidad Acebal”; product name “Turnos”.

**Output:** architecture identity block + kit under `web/` (tokens, Nunito, `public/brand/*`, `public/icons/*`, theme `#f6821f`) + patrones on existing header/cards. Report `Phases done: contrato, kit, patrones`. No xlsx chrome.

**Input:** arquitecto thread, no `web/` yet.

**Output:** identity block only. Report `Phases done: contrato`. Skip kit/patrones.
