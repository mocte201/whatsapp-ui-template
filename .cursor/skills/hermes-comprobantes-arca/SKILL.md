---
name: hermes-comprobantes-arca
description: >-
  Canonical map of Argentine electronic voucher (ARCA, historically AFIP)
  fields and a layout dictionary that translates distinct PDF layouts onto
  that contract. Use when the user asks for hermes-comprobantes-arca, extraer
  datos de facturas/comprobantes electrónicos AR, or a product must extract
  fecha, importe, cuit_emisor and nro_comprobante on voucher upload.
---

# Hermes Comprobantes ARCA

## Goal

Give the agent a **canonical field map** plus a **layout dictionary** so a product can extract voucher data without rediscovering the PDF from scratch. Produce fingerprint → parser → canonical contract. Refuse treasury/CBU/TRM, payroll receipts, generic OCR of scans, and shipping a full app.

## Bootstrap

1. Read this file, `layouts.md`, and `catalog.json` (seven canonical fields + layout ids). Behavior of the four known layouts lives in `parse_text.py` (stdlib reference). Port **those** rules into the destination; do not copy another product’s Python (tesorería / TRM). Real sample PDFs go in `corpus/` (gitignored).
2. In the destination repo: find the upload path; check how PDF text is extracted (library already in the repo). None → document a text-extract fallback; **do not** pretend OCR.
3. If a sample PDF exists, extract **embedded text** first. Empty text → explicit fail (`scan_sin_texto`), not a guessed layout.
4. Stop and hand off if the ask is architecture/UI of a new product → **hermes-arquitecto** / **hermes-escritor**; storage/RLS → **hermes-seguridad**.

On-demand (`role: null`). Naming: **ARCA**; mention AFIP only as historical alias of existing fingerprints.

## Procedure

1. **Scope the caller.** Header fields: `fecha_comprobante`, `importe_total`, `cuit_emisor`, `nro_comprobante`, `razon_social_emisor`, `fecha_vencimiento`, `domicilio_vendedor`. Line items (`items`): `codigo`, `producto`, `cantidad`, `u_medida`, `precio_unitario`, `pct_bonificado`, `imp_bonif`, `subtotal`. Bonus columns are layout-specific; empty if unsupported. `subtotal_ok` = qty × unit − `imp_bonif` (or % if there is no importe).
2. **Extract text** (embedded). One PDF → one voucher unless the corpus of *this* layout proves otherwise.
3. **Detect layout** by fingerprint order in `layouts.md` (special layouts before ARCA estándar). Operator does not pick layout. No match → `layout_desconocido` — **no** blind CUIT regex.
4. **Slice ORIGINAL** per that layout (ARCA: ORIGINAL vs DUPLICADO/TRIPLICADO; stay on ORIGINAL).
5. **Map anchors** from the dictionary. Do not swap importe anchors (Subtotal vs Total vs Subtotal General). Do not treat the buyer/municipality CUIT as `cuit_emisor`.
6. **Unify `nro_comprobante`** as documented for that layout (PV + number joined).
7. **`fecha_comprobante`:** anchors in `layouts.md`. Never `Fecha de Inicio de Actividades`. **`fecha_vencimiento`:** vencimiento de **pago** only — never Vto/Fecha de CAE. If the layout has no payment due date, leave empty (`unsupported`). SDR `Hasta:` is candidata for fecha_comprobante only.
8. **Wire** extraction into the destination upload flow. Adapt `parse_text.py` + `catalog.json`; do not vendor tesorería/TRM code.
9. **New vendor layout:** corpus text → fingerprint → anchors → `layouts.md` + `catalog.json` + parser + fixture. Never force the ARCA parser if fingerprint fails.

## Output contract

Leave this report (chat and/or `docs/` if the user asked to document):

```markdown
## Comprobantes ARCA
(mode: map | extract | wire)

## PDF text
(source: library | none → fallback listed | empty=scan)

## Layout
id | match | unknown

## Fields
| Campo | Valor | Ancla | Status |
| fecha_comprobante | | | extraido | candidata | faltante |
| importe_total | | | |
| cuit_emisor | | | |
| nro_comprobante | | | |
| razon_social_emisor | | | |
| fecha_vencimiento | | | |
| domicilio_vendedor | | | |

## Items
| codigo | producto | cantidad | u_medida | precio_unitario | pct_bonificado | imp_bonif | subtotal | subtotal_ok |

## Gaps
(layout to add / missing anchors / scan)

## Wiring
(upload path touched or “map only”)
```

Anonymize CUITs in examples (`20-XXXXXXXX-X`). Secrets = names only.

## Done criteria

- Layout id or explicit `layout_desconocido`
- Table for the seven header fields (plus `items`) with anchors
- Missing fields are errors, not guesses
- Destination code (if wiring) follows `parse_text.py` / `catalog.json`, not a cloned TRM parser
- Seven fields reported; SDR gaps explicit (no CUIT / nro / vto / domicilio vendedor)

## Forbidden / handoffs

- Tesorería, CBU, bank export, TRM grid
- Recibos de sueldo / Sueldos PP → not this job
- OCR of scans; empty extract = fail
- Blind CUIT / amount regex when fingerprint fails
- Copying reference-app Python or service-account files
- Full product/UI → **hermes-escritor** / **hermes-arquitecto**
- Uploads/RLS → **hermes-seguridad**
- New canonical skill → **hermes-forjador**
- Absolute paths, PowerShell-only, assuming CLI/MCP auth

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “All ARCA invoices are the same; skip the dictionary.” | Wrap, glued Subtotal, ORIGINAL copies, and vendor PDFs differ. Match `layouts.md` or fail. |
| “Fingerprint failed; I’ll regex any CUIT.” | Buyer CUIT and municipality CUIT pollute. Unknown layout = error. |
| “I’ll copy the Python from transferencias-masivas.” | Port **rules from `parse_text.py`**. That app also does CBU/TRM/sueldos — out of scope. |
| “Sueldos PP is almost a voucher.” | Different fingerprints, English amounts, employer CUIT. Refuse. |
| “No sample PDF; I’ll invent fecha anchors.” | Use anclas already verified in `layouts.md`. New layout: empty until corpus text shows the token. |

## Red flags

- Parser runs without a layout id
- `cuit_emisor` equals labeled buyer/municipality CUIT
- Importe taken from TOTAL when the layout anchor is Subtotal (or the reverse)
- `nro_comprobante` missing PV when the layout splits PV + number
- Scan/OCR “success” with no embedded text
- Fecha filled from `Fecha de Inicio de Actividades` or from `Fecha de Emisión:ORIGINAL` without a date token
- `fecha_vencimiento` filled from Vto/Fecha de CAE
- Buyer / municipality name parsed as an `items` row

## Verification

- [ ] Report has layout id or `layout_desconocido` (quoted)
- [ ] Seven fields table with anchors; empties labeled faltante / unsupported / error
- [ ] Importe format matches layout (AR `1.234,56` vs English payroll — payroll not used)
- [ ] Upload wiring points at destination files, or mode is map-only
- [ ] Seven canonical fields present in the report; `unsupported` fields empty
- [ ] From this skill folder, `python test_layouts.py` passes (or quote the failure)
- [ ] Report / `catalog.json` lists every known layout id and its columns (`required` / `candidata` / `unsupported` / `optional`)
