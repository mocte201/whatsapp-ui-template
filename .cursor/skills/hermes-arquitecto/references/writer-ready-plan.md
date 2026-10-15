# Writer-ready plan

Loaded by **hermes-arquitecto** before writing or updating `docs/implementation-plan.md`.

**Who reads the plan:** a cheaper writer subagent. It receives one slice card, reads the contract sections in `read_first`, and has no chat history. It cannot ask mid-run: every ambiguity becomes a guess (a review failure later) or a `STOP_NEEDS_HUMAN`. The card therefore carries every decision; the writer only executes.

## Slicing

- **Vertical tracer bullets:** each slice completes one narrow path through every layer it needs (data → server → UI → check) and is demoable or verifiable alone. Never “all tables”, then “all APIs”, then “all screens”.
- **Fits one fresh context:** ≤ ~5 BPs, ≤ ~8 files touched, authored diff ≲ 400 lines. Bigger → split.
- **Order by real dependency:** schema/migration before the UI that reads it; prefactor first (“make the change easy, then make the easy change”).
- **Greenfield S1 = walking skeleton:** scaffold with the chosen stack, folder layout from the Code map, `lint` / `build` / `test` scripts that run green, one trivial passing test, `.env.example` with variable **names**, local DX URL if web. Every later `verify` relies on it.
- **Wide mechanical refactor** (rename across the codebase): expand (new beside old) → migrate in batches (one slice each) → contract (delete old).
- **Quality passes** (a11y, ux-*, observabilidad, optimizador, simplificador): their own slice or Ready-when, per the gate rules in `SKILL.md`.

## Slice card

| Field | Content | Bar |
| --- | --- | --- |
| `goal` | One sentence, user-visible outcome | A non-dev understands what changes |
| `depends_on` | Slice ids | Only real blockers |
| `status` | `pending` | ship-plan owns later states |
| `gates` | Typed gates | Per `SKILL.md` rules |
| `read_first` | Contract sections by heading, e.g. `architecture.md › Data model › Reclamo` | ≤ ~4; the writer reads only these |
| `paths_hint` | Exact repo-relative paths to create `(new)` or modify | Existing paths verified on disk |
| `contracts` | Exact names and shapes created or consumed: tables, columns, types, constraints; RLS policy in words; route/function signatures with input → output; component props; env var **names**; user-facing copy and error texts | Matches Glossary/Code map character by character |
| `bps` | Ordered steps: verb + target (path/symbol) + observable done condition | Passes the decision-free test |
| `edge_cases` | Relevant inputs/states with expected behavior (empty, duplicate, denied, offline, invalid input) | Each has an expected result |
| `acceptance` | Behaviors a reviewer can check | Observable, not “works well” |
| `verify` | Exact commands + expected result; for UI, URL + steps + expected visible text | Commands exist (created by S1 or earlier) |
| `out_of_bounds` | What not to touch or add: files, dependencies, refactors, deferred capabilities | Specific to this slice |
| `stop_if` | Conditions where the writer returns `STOP_NEEDS_HUMAN` instead of improvising | At least one when the slice touches existing data or auth |

Inline a short code **shape** in `contracts` when prose would be ambiguous: a table definition, a type, a signature, a state machine. Never a full implementation: that is the writer’s job, costs capable-model tokens, and goes stale.

## Decision-free test (every BP)

A BP fails when two reasonable implementations exist and the choice changes behavior, data, security, cost, or another slice. Make that choice in the card. Purely local style (internal variable names, loop form) stays with the writer.

| Fails | Passes |
| --- | --- |
| `BP1 — Implementar login` | `BP1 — Crear app/login/page.tsx: campo email → enviar magic link con el cliente Supabase (redirect a /auth/callback). Éxito: texto "Te enviamos un link a tu correo". Error: mensaje en un elemento role="alert".` |
| `BP2 — Manejar errores` | `BP2 — Si el insert en reclamos falla, mantener el formulario con los datos cargados y mostrar "No pudimos guardar el reclamo. Probá de nuevo."; no redirigir.` |
| `BP3 — Formatear fechas` | `BP3 — Mostrar creado_en con Intl.DateTimeFormat('es-AR', { dateStyle: 'short', timeStyle: 'short' }); no agregar dependencias.` |
| `BP4 — Tabla de reclamos` | `BP4 — Migración supabase/migrations/<ts>_reclamos.sql: tabla reclamos según contracts; RLS on; vecino lee/crea solo los suyos; operador lee todos.` |

## Blind-writer probe

Run before asking for plan approval: at least on S1, on every slice with `gates`, and on every slice with ≥3 BPs.

1. **Subagent available:** launch `hermes-plan-probe` once per probed slice (parallel when the platform allows), passing only the slice card and the text of its `read_first` sections. Do not pass a model override: the platform template pins the writer’s model class. Require its `## Probe result` block; missing → treat as not probed.
2. **No `hermes-plan-probe` (agents not synced) but generic subagents exist:** launch a readonly one with the same inputs and this prompt:
   > Sos el escritor de este slice. No implementes nada. Listá cada punto donde tendrías que elegir o adivinar algo, cada nombre que no está definido, y cada comando de `verify` que no sabés si existe. Si no hay ninguno, respondé NINGUNO.
3. **No subagent tooling:** do the same pass in-process, reading the card as if you knew nothing else, and mark the log line `(in-process)`.
4. Fix every finding in the card or contract. If a finding is a consequential decision, ask the user in the next round.
5. Record in the plan under `## Probe log`: `S2 — 3 huecos corregidos (nombre de columna, copy de error, comando test)` or `S1 — NINGUNO`.

## Plan-level checks

- Every confirmed journey, screen, entity, and permission is covered by a slice, or listed in Deferred / Out of scope.
- No BP outside the contract’s scope.
- Every name in any `contracts` field appears in Glossary/Code map, spelled identically across slices.
- Every Ready-when item maps to a slice `acceptance` or to a launch-time pass for **hermes-lanzamiento**.
- `depends_on` has no cycles; the first `pending` slice is runnable now.
