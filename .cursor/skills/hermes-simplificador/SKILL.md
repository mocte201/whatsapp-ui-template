---
name: hermes-simplificador
description: >-
  Reduces code complexity while preserving exact behavior (Chesterton's Fence):
  deletes dead paths, flattens nesting, removes speculative abstraction. Use when
  code works but is hard to maintain, after a review flags complexity, or when
  the user asks to simplify / limpiar sin cambiar comportamiento.
---

# Hermes Simplificador

## Goal

Make the code easier to read and change **without** changing user-visible or API behavior. Prefer deletion and inlining over new frameworks.

## Bootstrap

1. Confirm the scope (paths or PR diff). Prefer small slices.
2. Ensure there is a way to prove behavior: existing tests or agree a short smoke before editing.
3. If the request is really “fix bugs” or “ship?” → **hermes-depurador** / **hermes-lanzamiento**.
4. If the design is wrong, not just dense → **hermes-arquitecto**.
5. If the ask is “while implementing, stay minimal” → that bias lives in **hermes-escritor** (minimal path ladder); this skill only cleans after behavior works.

## Procedure

1. **Fence** — for each non-obvious construct, state why it might exist (comment, history, API constraint). Do not delete until the reason is known or proven obsolete.
2. **Inventory** — list candidates: dead code, duplicate helpers, needless indirection, gold-plating, speculative config.
3. **Risk tag** — Low / Med / High per candidate (public API, auth, data migrations = High). Code that **reads persisted data or formats** (stored rows, files, cache, localStorage, old payload/webhook shapes) is High even if no current writer produces them: existing data still needs the read path.
4. **Deletion proof** — before removing anything, record why it is dead: grep of callers/imports/string references (incl. dynamic keys, routes, cron/webhook entrypoints, GAS triggers), tests that cover it, and config that could reach it. No proof → keep it or tag High.
5. **Apply Low/Med** only in-scope; leave High as proposals unless user accepts risk.
6. **Prove** — re-run tests/smoke for the slice.

## Output contract

```markdown
## Simplify scope
## Applied (with risk)
## Deleted (proof: grep / tests / entrypoints checked)
## Proposed only (High / needs decision)
## Behavior proof (commands)
## Intentionally kept (fence reasons)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “This abstraction will help later” | YAGNI; delete until a second use appears |
| “Rewrite cleaner in a new style” | Preserve behavior; style-only mass rewrite is out of scope |
| “No tests, but it’s obvious” | Define smoke first; silent simplify is sabotage |
| “Same as review” | Revisor finds defects; you only reduce complexity |
| “No callers in the IDE, so it’s dead” | Routes, cron, webhooks, GAS triggers, and dynamic keys don’t show as callers; grep strings and entrypoints |
| “Nobody writes the old format anymore; drop the parser” | Rows/files already stored still need it; High unless data is migrated first |

## Red flags

- Behavior or API change packaged as “cleanup”
- Deleting auth/RLS/security checks as “dead”
- Huge multi-file rewrite without proof plan
- Deleted item with no grep/entrypoint evidence in the report
- Reader of stored data removed as “unused”

## Verification

- [ ] Before smoke or tests identified
- [ ] After proof re-run recorded
- [ ] High-risk items not silently applied
- [ ] Every deletion listed under `Deleted` with its proof

## Done criteria

- Net complexity down or residual proposals listed
- Behavior proof green (or honest block)

## Forbidden

- Feature work or product redesign → **hermes-escritor** / **hermes-arquitecto**
- Security policy weakening → **hermes-seguridad**
