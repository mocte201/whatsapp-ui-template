# Diccionario de layouts — comprobantes ARCA

Traductor: fingerprint observable → anclas → contrato canónico. Cuatro layouts en `catalog.json`. Agregar entradas con corpus propio; no forzar `arca_estandar` si el fingerprint falla.

Referencia ejecutable: `parse_text.py` (stdlib). Inventario: `catalog.json`. Tests: `python test_layouts.py` (desde esta carpeta). PDFs reales: `corpus/` (gitignored; `corpus/README.md`). Extraer texto: `python extract_corpus.py` (pypdf opcional).

## Inventario (layouts que esta skill sabe procesar)

Valores: `required` = extraer o error; `candidata` = mejor aproximación documentada; `unsupported` = vacío, no adivinar.

| id | fecha_comprobante | importe_total | cuit_emisor | nro_comprobante | razon_social_emisor | fecha_vencimiento | domicilio_vendedor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `arca_estandar` | required | required | required | required | required | unsupported (no vto de pago; no usar CAE) | required |
| `cuento_hadas_fiscante` | required | required | required | required | required | unsupported | required |
| `amasuno_lauri` | required | required | required | required | required | unsupported | required |
| `sdr_resumen_cuenta` | candidata (`Hasta:`) | candidata (1er monto) | unsupported | unsupported | required | unsupported | unsupported |

### Filas de producto (`items`)

Columnas canónicas: `codigo`, `producto`, `cantidad`, `u_medida`, `precio_unitario`, `pct_bonificado`, `imp_bonif`, `subtotal`. El subtotal es cantidad × unitario **menos** `imp_bonif` (o con `%` si el layout no trae importe). No todos los layouts tienen las dos columnas de bonificación, ni en el mismo orden.

| id | codigo | producto | cantidad | u_medida | precio_unitario | pct_bonificado | imp_bonif | subtotal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `arca_estandar` | vacío (nº de renglón ≠ código) | required | nº antes de `unidades` | `unidades` entre dos importes (wrap: unir nº—unidades—nº) | nº después de `unidades` | required (`% Bonif`, a menudo 0,00) | required (`Imp. Bonif.`, a menudo 0,00) | required (qty×unit − imp_bonif) |
| `cuento_hadas_fiscante` | candidata (`PAÑALES` pegado) | required | required | unsupported | required | candidata (`% Bonif.` en el renglón pegado) | unsupported (no hay columna de importe) | required |
| `amasuno_lauri` | vacío o nº izq. | required | required | unsupported | required | candidata (`Dto(%)` solo si viene un 4º número; no usar el `IVA(%)`) | unsupported | required |
| `sdr_resumen_cuenta` | unsupported | unsupported | unsupported | unsupported | unsupported | unsupported | unsupported | unsupported |

Si el fingerprint no matchea ninguno: no hay columnas; error `layout_desconocido`. Scan sin texto: `scan_sin_texto`.

**Contrato canónico (cabecera):** `fecha_comprobante`, `importe_total`, `cuit_emisor`, `nro_comprobante`, `razon_social_emisor`, `fecha_vencimiento`, `domicilio_vendedor`. Extraer o marcar `unsupported`/`faltante`. No adivinar.

**Canónico `nro_comprobante`:** `{PV}-{NRO}` con PV a 5 dígitos y NRO a 8 (ceros a la izquierda), dígitos solo.

**Importe AR:** miles `.` decimales `,` (`1.234,56`). Amasuno en corpus usa punto decimal inglés en `TOTAL:`. No mezclar con formato de sueldos.

**`fecha_comprobante`:** anclas de abajo, verificadas en corpus de cada layout. Nunca `Fecha de Inicio de Actividades`. **`fecha_vencimiento`:** solo vencimiento de **pago**. Nunca Vto/Fecha de CAE. Corpus actual: vacío en los cuatro.

---

## Detección (orden)

Igual que `catalog.json` → `detection_order`:

1. `cuento_hadas_fiscante`
2. `amasuno_lauri`
3. `sdr_resumen_cuenta`
4. `arca_estandar` (último: es el más genérico)
5. Si ninguno matchea → `layout_desconocido`. No regex de CUIT a ciegas.

Autodetección; el operador no elige layout.

---

## `arca_estandar`

Alias histórico de fingerprints: **AFIP** / factura electrónica típica (corpus: El Picu).

### Fingerprint (todas o casi todas)

- `Fecha de Emisi` pegado o cerca de `ORIGINAL` / `DUPLICADO` / `TRIPLICADO`
- `Punto de Venta` y/o `Comp. Nro` (variantes `Comp. Nro:`, `Comp Nro`)
- `Subtotal` + `$` (importe a menudo **pegado** al label)
- CUIT etiquetado (`CUIT:`) y al menos un renglón de 11 dígitos “desnudo”

### Recorte

Texto completo → ejemplares ORIGINAL / DUPLICADO / TRIPLICADO → **quedarse con ORIGINAL**. Layouts sin esa marca: no forzar este parser.

### Mapa

| Campo | Ancla | Notas |
| --- | --- | --- |
| `fecha_comprobante` | Primer `dd/mm/yyyy` del ORIGINAL que no sea Inicio de Actividades ni Vto de CAE | Verificado (Picu). |
| `importe_total` | Wrap: montos sobre `Subtotal: $` / `Importe Total: $` | No `TRANSPORTE` ni Subtotal de página 1. |
| `cuit_emisor` | Primer CUIT de 11 dígitos **desnudo** distinto del CUIT etiquetado | El etiquetado suele ser **comprador**. |
| `nro_comprobante` | `Comp. Nro:` → PV y número | `{PV}-{NRO}` 5+8. |
| `razon_social_emisor` | Tras ORIGINAL: primer renglón MAYÚSCULAS (nombre) | No labels de formulario. |
| `fecha_vencimiento` | Vto de **pago** | Corpus Picu: no hay. No usar Vto CAE. |
| `domicilio_vendedor` | Domicilio comercial del emisor en el ORIGINAL | No domicilio del comprador. |
| `cuit_comprador` (extra) | Primer `CUIT:` etiquetado | Opcional. |

Ítems: `unidades` entre dos importes; si el wrap parte la palabra, unir nº—unidades—nº. `% Bonif` / `Imp. Bonif.` a menudo van después del subtotal en el extracto. No tratar el nombre del comprador (p. ej. un centro) como renglón de producto.

### Formato importe

AR. Parse respetando `,` decimal.

---

## `cuento_hadas_fiscante`

Factura **propia** (no layout ARCA municipal). Fingerprint dedicado; no correr `arca_estandar` sobre este texto.

### Fingerprint (algunos bastan; preferir ≥2)

- Texto: `Fiscante`, o `Subtotal General` + `Factura elect`
- Línea `ORIGINAL` suelta (no `Fecha de Emisi…ORIGINAL`)
- `N°:` / `N:` con patrón `ddddd-dddddddd` (PV-número)
- Nombre de archivo con `cuento`+`ada` **solo como pista**, no como única prueba

### Recorte

`ORIGINAL` suelto hasta `DUPLICADO` suelto; si no hay, texto completo.

### Mapa

| Campo | Ancla | Notas |
| --- | --- | --- |
| `fecha_comprobante` | `dd/mm/yyyy` del encabezado **después** de Inicio Actividades | No el año de inicio (p. ej. 2018). Verificado. |
| `importe_total` | Línea siguiente (o misma) a `Subtotal General:` — AR `N.NNN,NN` | En corpus igual al total. |
| `cuit_emisor` | CUIT con guiones del emisor, distinto del 11 dígitos del receptor | El desnudo suele ser comprador. |
| `nro_comprobante` | `N°: PPPPP-NNNNNNNN` | `{PV}-{NRO}` 5+8. |
| `razon_social_emisor` | Nombre del emisor en encabezado (texto puede ir fragmentado) | Normalizar espacios; no hardcodear en el producto destino. |
| `fecha_vencimiento` | Vto de pago | Corpus: no hay. Nunca CAE. |
| `domicilio_vendedor` | Calle + número del emisor (p. ej. GUEMES + dígitos) | Compactar letras del extracto. |

Ítems: código de rubro a menudo pegado al nombre (`PAÑALES…`). `% Bonif.` pegado; `imp_bonif` unsupported. El extracto pypdf puede romper `Ñ` (`PA�ALES`): conservar el token, no “corregir” a ciegas.

---

## `amasuno_lauri`

Factura **propia** (librería / Amasuno). No es layout ARCA.

### Fingerprint

- Razón o marca `A + 1` / `Amasuno` / `Lauri`
- `Fecha:` + `Nº` PV - número
- `TOTAL:` con montos estilo `N.NN`

### Recorte

Texto completo (sin ejemplares ORIGINAL/DUPLICADO típicos de ARCA).

### Mapa

| Campo | Ancla | Notas |
| --- | --- | --- |
| `fecha_comprobante` | `Fecha:` | Verificado. |
| `importe_total` | Último `TOTAL:` | Formato inglés `N.NN` en corpus. |
| `cuit_emisor` | CUIT del emisor (no el del comprador) | |
| `nro_comprobante` | `Nº00001 - 00002412` (forma típica) | Unificar `{PV}-{NRO}`. |
| `razon_social_emisor` | Encabezado (puede incluir alias entre comillas) | |
| `fecha_vencimiento` | Vto de pago | No `Fecha Vencimiento CAE`. Corpus: vacío. |
| `domicilio_vendedor` | Domicilio comercial del emisor | |

Ítems: primera columna numérica `N.NN` = cantidad. Código numérico a la izquierda solo a veces. No usar `IVA(%)` como `% bonificado`.

---

## `sdr_resumen_cuenta`

**No es comprobante ARCA.** Resumen de cuenta de distribuidora. Extraer lo que el layout expone; el resto `unsupported`.

### Fingerprint

- `Distribuidora SDR` y/o `Resumen de Cuenta`
- Período `Desde:` / `Hasta:`
- Sin `Comp. Nro` / `Fecha de Emisi…ORIGINAL`

### Recorte

Texto completo.

### Mapa

| Campo | Ancla | Notas |
| --- | --- | --- |
| `fecha_comprobante` | `Hasta:` del período | **Candidata** (no es fecha de factura). |
| `importe_total` | Primer monto tras `Resumen de Cuenta` | En corpus sdr 01 = Total Ventas. Candidata. |
| `cuit_emisor` | — | unsupported |
| `nro_comprobante` | — | unsupported (no hay PV+nro) |
| `razon_social_emisor` | `Distribuidora SDR` | |
| `fecha_vencimiento` | — | unsupported |
| `domicilio_vendedor` | — | unsupported |

Ítems: unsupported (el PDF lista movimientos, no renglones de factura).

---

## Cómo agregar un layout de proveedor

1. PDF en `corpus/` (o `corpus/<id>/`). Extraer texto embebido (`python extract_corpus.py` o visor). Vacío → `scan_sin_texto`.
2. Listar strings estables (título, labels, no montos variables).
3. Definir `id`, fingerprints, recorte ORIGINAL si aplica.
4. Anclar los **siete** campos + `items` con citas del corpus. `fecha_vencimiento` solo si es vto de pago.
5. Si el fingerprint de `arca_estandar` **no** matchea, **no** reutilizar ese parser.
6. Entrada aquí **y** en `catalog.json`. Implementar en `parse_text.py`. Fixture en `fixtures/` + fila en `fixtures/cases.json`. `python test_layouts.py`.

---

## Errores canónicos

| Código | Cuándo |
| --- | --- |
| `layout_desconocido` | Ningún fingerprint |
| `scan_sin_texto` | PDF sin texto extraíble |
| `faltante_<campo>` | Layout matcheó pero el ancla no dio valor |
| `cuit_emisor_es_comprador` | Emisor colisionó con comprador/comuna |
| `*_unsupported` | El layout no expone ese campo |
