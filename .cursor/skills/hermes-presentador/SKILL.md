---
name: hermes-presentador
description: >-
  Creates self-contained HTML slide decks from an idea, outline, document, or
  transcript. Use when the user asks for a presentation, slides, deck,
  diapositivas, or wants existing content converted into a visual presentation.
---

# Hermes Presentador

## Goal

Crear presentaciones HTML autocontenidas, claras y listas para abrir en navegador. Priorizar narrativa, jerarquía visual y uso real por encima de adornos.

## Bootstrap

1. Leé el contenido fuente o la idea y detectá objetivo, audiencia y uso previsto.
2. Si faltan datos críticos (audiencia, objetivo o duración aproximada), preguntá antes de generar.
3. No chequear flag de rol en `orchestra.json` — skill on-demand (`role: null`).
4. Si el usuario dio marca, colores o tono, respetalos por encima de cualquier estilo por defecto.
5. Artefacto: entregá el HTML en el chat; si el usuario da una ruta de archivo en el repo, escribí ahí.

## Procedure

1. Definí una estructura narrativa breve: apertura, contexto, desarrollo, evidencia y cierre.
2. Elegí un estilo visual coherente con el tema y el público; explicá la elección en una línea.
3. Reducí el contenido a ideas por slide; no conviertas párrafos largos en diapositivas.
4. Variá layouts con criterio, pero mantené una gramática visual consistente.
5. Generá un único HTML con CSS en `<style>`, sin assets remotos críticos; tipografía del sistema o embebida.
6. Incluí navegación entre slides (teclado y/o controles) y responsive básico.
7. Si es para video/pantalla: texto corto y elementos grandes. Si es reunión/formación: claridad y numeración visible.

## Output contract

Respondé siempre en este orden:

1. **Resumen de enfoque** — objetivo, público asumido, estilo elegido (1–3 frases).
2. **Estructura de slides** — lista numerada de títulos.
3. **Presentación HTML** — el documento completo, autocontenido, en un bloque de código marcado como HTML (o escrito en la ruta pedida).

Opcional al final: recomendaciones de marca/logo/imágenes que el usuario podría sumar después. Si el deck quedó en un archivo del repo y el usuario quiere retocar copy o dejar comentarios en el HTML, → `hermes-editor` (no reescribas el deck entero por un polish menor).

## Done criteria

- Hay un arco narrativo claro
- El HTML es autocontenido y abrible en navegador (o archivo escrito en la ruta pedida)
- La salida incluye resumen de enfoque, estructura y código completo

## Forbidden

- Pegar párrafos largos sin jerarquía
- Depender de imágenes o assets remotos críticos
- Inventar cifras o datos faltantes
- Documentación de producto / README → `hermes-documentador`
- Pulir solo el copy de las slides sin generar el deck → `hermes-humanizador`
- Edición fina con comentarios / `*_editado` / PDF del retocado → `hermes-editor`
