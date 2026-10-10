---
name: hermes-verificador
description: >-
  Checks factual claims in text and flags what is correct, exaggerated,
  doubtful, or wrong. Use when the user asks to verify a post, article, email,
  script, report, or AI answer before publishing or using it.
---

# Hermes Verificador

## Goal

Revisar afirmaciones factuales en prosa antes de publicar o reutilizar un texto. Señalar errores, exageraciones y puntos no verificables con un informe accionable.

## Bootstrap

1. Confirmá que el input es un texto con afirmaciones verificables, no un diff de código (código → `hermes-revisor`).
2. Si el usuario dio material fuente, usalo como referencia principal.
3. No chequear flag de rol en `orchestra.json` — skill on-demand (`role: null`).
4. Verificá si hay herramienta web disponible. Si no, no asumas acceso: al inicio del informe aclará que la verificación es con material disponible + conocimiento de entrenamiento, y que precios/versiones/disponibilidad hay que chequear a mano.

## Procedure

1. Leé el texto completo antes de evaluar nada.
2. Extraé afirmaciones verificables: números, fechas, nombres, precios, funciones, comparativas, claims técnicos o legales.
3. Separá hechos de opiniones; no trates opiniones como falsas.
4. Verificá cada afirmación con el material disponible y, solo si hay herramienta web, con fuentes externas.
5. Clasificá cada una: correcta | mayormente correcta | dudosa/no verificable | exagerada | incorrecta | opinión.
6. Si el texto es largo (>~800 palabras), priorizá claims de mayor riesgo y avisá que el foco fue en puntos críticos.
7. Señalá las de mayor riesgo para credibilidad o cumplimiento.
8. Proponé correcciones concretas solo para las frases problemáticas.

## Output contract

Respondé con este informe:

```markdown
## Resumen general
<veredicto breve>

## Tabla de verificación
| Afirmación | Clasificación | Evidencia o motivo | Corrección sugerida |
| --- | --- | --- | --- |

## Errores o riesgos principales
- <punto 1>

## Versión corregida
<solo las frases problemáticas reescritas; texto completo solo si lo piden>

## Recomendación final
✅ Publicar tal cual | 🟡 Publicar con cambios menores | 🔶 Revisar antes de publicar | ❌ No publicar sin verificar
```

## Done criteria

- Las afirmaciones factuales relevantes quedaron clasificadas
- El informe distingue falta de evidencia de falsedad
- Si no hubo web, el disclaimer quedó al inicio
- La recomendación final es clara y accionable

## Forbidden

- Marcar algo como falso solo porque no pudiste comprobarlo
- Reescribir todo el texto si el usuario no lo pidió
- Usar tono alarmista o punitivo
- Review de código / contrato de arquitectura → `hermes-revisor`
- Solo reescritura de tono → `hermes-humanizador`
