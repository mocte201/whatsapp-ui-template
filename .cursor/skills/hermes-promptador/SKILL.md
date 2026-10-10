---
name: hermes-promptador
description: >-
  Turns rough ideas, incomplete instructions, or messy notes into clear prompts
  ready for an AI tool. Use when the user asks to improve a prompt, structure
  an idea for Claude/ChatGPT/Gemini, write a prompt for coding/image/video
  tools, or optimize instructions before using an AI.
---

# Hermes Promptador

## Goal

Convertir ideas desordenadas en prompts claros, específicos y listos para copiar. Optimizar la instrucción sin cambiar el objetivo real del usuario.

## Bootstrap

1. Identificá para qué herramienta va el prompt: texto, código, imagen, video o automatización.
2. Si la herramienta objetivo no está clara y cambia mucho el formato, preguntá antes de seguir.
3. No chequear flag de rol en `orchestra.json` — skill on-demand (`role: null`).
4. Si el objetivo es crear o auditar una skill Hermes canónica → `hermes-forjador` (no reescribas playbooks del control plane como “prompts genéricos”).
5. Si faltan detalles menores, asumí lo razonable y marcá las dudas opcionales al final.

## Procedure

1. Extraé objetivo, contexto, tarea concreta, restricciones, formato de salida y cosas a evitar.
2. Detectá huecos críticos: herramienta, idioma, tono, formato esperado, límites técnicos.
3. Ordená el prompt con secciones útiles para la herramienta objetivo; no agregues relleno.
4. Para texto/código, explicitá rol, tarea, criterios de calidad y formato de respuesta.
5. Para imagen/video, priorizá sujeto, composición, estilo, restricciones y elementos a evitar.
6. Para automatizaciones, detallá trigger, pasos, inputs, outputs y manejo de errores.
7. Revisá que el prompt sea inmediatamente usable y más corto que una explicación innecesaria.

## Output contract

Respondé siempre en este orden. Omití **Dudas opcionales** si no hay ninguna útil.

```markdown
**Prompt optimizado:**
<prompt final>

**Cambios principales realizados:**
- <mejora 1>
- <mejora 2>
- <mejora 3>

**Dudas opcionales:**
- <solo si faltan datos que mejorarían mucho el resultado; máx. 2–3>
```

## Done criteria

- La herramienta objetivo quedó clara o fue preguntada
- El prompt final es copiable y accionable
- La respuesta incluye cambios principales; dudas solo si aportan valor real

## Forbidden

- Cambiar el objetivo original del usuario
- Inventar detalles críticos no dados
- Explicar teoría de prompting si no la pidieron
- Performance / free-tier de apps Hermes → `hermes-optimizador`
- Crear o editar skills canónicas → `hermes-forjador`
