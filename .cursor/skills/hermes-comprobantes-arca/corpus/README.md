# Corpus de PDFs (trabajo local)

Acá van los **PDFs reales** para descubrir layouts nuevos o ajustar los que ya están en `catalog.json`.

Los PDF y cualquier extracto **no se commitean** (CUIT, razón social, montos). Lo que sí va a git son fixtures anonimizados en `../fixtures/`.

## Dónde poner cada archivo

| Qué estás haciendo | Dónde |
| --- | --- |
| Layout todavía desconocido | esta carpeta (raíz) o `inbox/` |
| Ajustar un layout ya listado | subcarpeta con el **id** (`arca_estandar/`, `cuento_hadas_fiscante/`, …) |

Un PDF = un comprobante, salvo evidencia en el texto.

## Flujo

1. Copiá el PDF acá.
2. Extraé **texto embebido** (no OCR). Si el extracto sale vacío → `scan_sin_texto`; no adivinar anclas.
3. Si el fingerprint no matchea → layout nuevo (no forzar `arca_estandar`).
4. Anclas de los cuatro campos canónicos + extras solo si están claros.
5. Anonimizá y copiá el texto a `../fixtures/<id>_….txt` + fila en `../fixtures/cases.json`.
6. Actualizá `../catalog.json` y `../layouts.md`. Corré `python ../test_layouts.py`.

Extraer texto (si hay `pypdf` en el entorno):

```text
python extract_corpus.py
```

Eso escribe `.txt` al lado de cada PDF (también ignorados por git). Sin `pypdf`: el agente o un visor que copie el texto.

## Naming

Preferí nombres de archivo **sin** CUIT ni razón social (`proveedor-x-2026-08.pdf`). El contenido igual queda fuera de git.
