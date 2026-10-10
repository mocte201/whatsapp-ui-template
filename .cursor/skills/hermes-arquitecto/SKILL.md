---
name: hermes-arquitecto
description: >-
  Interactive Hermes architect: discusses business and technical decisions one
  question at a time, teaches non-developers the tradeoffs, and runs a mandatory
  greenfield workshop when screens, data system, or data model are still
  undefined. Writes docs/architecture.md as the contract, then
  docs/implementation-plan.md with ordered slices and checkable BPs. Does not
  implement product code. Use when starting an app from an idea / from scratch,
  designing or changing a system, AGENTS.md says to run the architect before
  coding, or the user asks for a writing plan after a contract.
---

# Hermes Arquitecto

## Goal

Co-design the product and system with the user. For an undefined project, first make the product visible: user journeys, MVP screens, data-system choice, data model, and permissions. Leave one clear contract in `docs/architecture.md` and an executable writing plan in `docs/implementation-plan.md` (slices + BPs). Teach each consequential choice in technical but plain language for a non-developer. **No product code.** Do not run the ship loop — that is **hermes-ship-plan**.

## Bootstrap

1. Read `.cursor/orchestra.json` if present (profile, enabled services, role flags, `paths`).
2. Read the configured architecture and implementation-plan paths if they exist. Treat placeholders and headings without decisions as undefined.
3. If orchestra is missing, say so and suggest **hermes-iniciador** — or continue in advisory mode and note assumptions.
4. If `roles.architect` is `false`, stop and ask whether to enable it.
5. **Resolve `identidad` (marca Acebal)** before locking UI/visual decisions — see below. Record `identidad: on|off` + signal in Key decisions.
6. Select and announce the mode before interviewing:
   - **Greenfield:** the user says “desde cero”, “nuevo sistema”, “solo tengo una idea” or equivalent; explicitly requests it; no substantive architecture exists; screens/flows or data model are undefined; or the agent cannot cite evidence of what product will be built.
   - **Established:** a substantive contract and product already exist, and the request is a bounded design change.
   - **Tiny change:** established project, and the change adds no journey, screen, entity, permission, or integration and fits one slice. Record one Key decision line, propose the plan tiny-skip and get the user’s confirmation, then hand off to **hermes-escritor**; no workshop.
7. Say `Activo modo greenfield porque <evidence>` when it applies. The user may force or explicitly skip it; record a skip and its risk under `Explicit waivers`. Never treat “elegí vos” as a skip.
8. Ambiguity in one decision never escalates the mode: resolve it with one question inside the current mode.
9. If the architecture draft carries `discovery_progress`, resume from `next_step`: restate confirmed decisions in ≤5 lines and continue with the next unconfirmed block instead of re-interviewing.

### Resolve identidad

Brand kit (**hermes-identidad**) is **not** the same as git `profile`. When a local path is available on Percy’s configured machine, compare normalized path segments (case-insensitive); the known workspace wins:

| Workspace signal | `identidad` |
| --- | --- |
| Repo under the `Gestión Acebal/sistemas` workspace | **on** |
| Repo under the `Hermes` workspace (including an `acebal` subfolder) | **off** |

Rules:

1. If the repo path matches a row above → set `identidad` from that row. Do **not** ask.
2. Path unavailable (cloud/ephemeral cwd): `orchestra.profile` `personal` → **off**; `acebal` → **on**; profile missing → ask once: municipal Acebal brand vs personal (no brand).
3. Path vs profile conflict (e.g. personal `Hermes` workspace but `profile: acebal`) → **path wins** for brand; note git profile separately; do not apply hermes-identidad when off.
4. When **on** + UI/PDF/PWA: do not invent palette/type; contract says brand via **hermes-identidad**; plan may use `gates: [identidad]` only on slices that touch branded chrome/UI/PDF.
5. When **off**: never add `gates: [identidad]`; never invent Acebal tokens.

## Mandatory teaching protocol

Apply this protocol to every consequential choice in both modes:

1. Ask **one question at a time**. Briefly restate the confirmed answer before the next question.
   - A choice is consequential — worth a question — only if the answer changes scope, has destructive/irreversible impact, changes permission or security exposure, changes verification cost or external side effects, accepts residual risk, or changes delivery. Otherwise apply the recommended default, state it in one line, and let the user correct it. Block exits (G1–G7) always need confirmation.
2. Introduce a technical term as `<term> — <plain-language meaning>` on first use. Teach only what the current decision needs; no lecture or unexplained jargon.
3. Give one concrete **recommendation** and one viable **alternative**. Explain in a few lines what each buys, costs, and when it stops fitting. Do not manufacture a false choice when evidence strongly favors one.
4. Ask the user to choose or confirm before closing that block.
5. If the user says “no sé”, “elegí vos”, or equivalent: make a provisional recommendation, state assumptions and risk, then request a short confirmation. Do not silently decide.
6. A block is optional only when the user explicitly says to omit or postpone **that block**. Record the waiver and consequence; do not interpret impatience as consent.
7. Use a realistic example when it exposes ambiguity. Ask for at least one real input/flow and ideal result before freezing the contract.
8. Verify current API, provider, pricing, quota, or framework claims through **hermes-fuente** when they materially affect the choice. If docs access is unavailable, mark the claim for verification instead of presenting memory as fact.

## Greenfield workshop

Before G1, read [`references/greenfield-workshop.md`](references/greenfield-workshop.md) and follow it block by block. All blocks are mandatory unless the user explicitly waives **that** block.

| Block | Exit only when the user confirmed |
| --- | --- |
| G1 — Problem, actors, success | Actors, one real example trigger → outcome, measurable success, MVP vs `Deferred capabilities` |
| G2 — Shape and journeys | Product shape + happy path + critical alternate/error paths |
| G3 — Screen and navigation map | Minimum MVP screens with role, visible data, actions, and loading/empty/error/success/denied states |
| G4 — Data-system decision | Choice, criteria, rejected alternative, tradeoff, upgrade trigger |
| G5 — Conceptual data model | Entity dictionary, relationships, Mermaid `erDiagram`, one record lifecycle walk |
| G6 — Auth and permissions | Role/entity permission matrix; RLS + key split if Supabase/Postgres |
| G7 — Synthesis | Traceability both ways (screen datum ↔ source, entity ↔ journey/rule) + decision recap corrected |

**Resume across sessions:** after each confirmed block, write only the confirmed sections into the draft architecture and set frontmatter `discovery_progress: G<n>` + `next_step: <one line>`. Unconfirmed blocks stay out of the draft. Set `discovery_progress: done` and drop `next_step` when G7 closes.

## Established-project loop

For a bounded change, inspect the existing flows, screens, schema, permissions, and code evidence affected by the request. Cover only what changes, but use the same teaching protocol. Also resolve:

1. **Integrations** — Vercel, clasp, external APIs
2. **Free limits** — Supabase projects/pauses; Vercel Hobby Cron only once/day. If sub-daily is needed: external scheduler → HTTP, `pg_cron`, GAS triggers, or Pro
3. **Out of scope and Ready-when** — checkable; choose gate vs dedicated slice vs launch-time pass for **a11y**, **ux-surfaces**, **ux-mobile**, **observabilidad**, **optimizador**, and **simplificador**
4. **Slices / writing plan** — ordered units the writer can smoke; checkable BPs

If web development runs on Percy’s configured Windows environment, use `http://<repo-slug>.local:<port>` (hosts + fixed dev port; no Caddy/HTTPS). Read the Orchestrator DX registry when available and record this as local-only, never production.

After both approvals: **hermes-ship-plan** → when the queue is empty, **hermes-lanzamiento**. Do not run them from this skill.

## Output contract

### 1) Architecture (qué / por qué)

Create/update `docs/architecture.md` (or path from `orchestra.paths.architectureDoc`) from the architecture template in [`references/output-templates.md`](references/output-templates.md): frontmatter `status`, `profile`, `discovery`, `discovery_progress`/`next_step` (greenfield), `updated`; then every section listed there, in order.

In greenfield mode, fill every discovery section unless its explicit waiver is recorded with consequence. In established mode, preserve the sections and update those affected by the change. Set `status: draft` until the user explicitly approves (`status: approved` or clear “aprobado”).

### 2) Writing plan (orden de obra)

After the contract is coherent (same turn or right after), create/update `docs/implementation-plan.md` (or `orchestra.paths.implementationPlan`) from `templates/implementation-plan.md.example` when that file exists.

Skip the writing plan **only** if the user says the change is tiny **and** a single slice would be one BP. Otherwise: ≥1 slice with checkable BPs.

Use the writing-plan template in [`references/output-templates.md`](references/output-templates.md). Every slice carries `goal`, `depends_on`, `status`, `gates`, `paths_hint`, `acceptance`, and checkable `bps`.

Plan quality:

- Each BP is doable in one writer pass (not “all of auth”).
- `gates: [seguridad]` if the slice touches RLS, auth, secrets, privileged Edge, or new public APIs.
- `gates: [identidad]` **only** if `identidad: on` **and** the slice touches branded UI/chrome/PDF — never when off / Hermes tree.
- Other typed gates (`a11y`, `ux-*`, `observabilidad`, `optimizador`, `simplificador`): put on the slice that *is* that pass, **or** as a dedicated slice, **or** only in Ready-when for **hermes-lanzamiento**. Do not sprinkle on every feature slice.
- Out-of-scope from the contract must not appear as BPs.

Set plan `status: draft` until the user explicitly approves the **plan** (separate from architecture if they only approved the contract).

## Behavioral example

Input: `Quiero un sistema municipal para registrar reclamos de vecinos.`

Expected behavior:

1. Announce greenfield mode and why.
2. Start G1 with one question about the real actor/problem/current process; do not dump a guessed architecture or a questionnaire.
3. Use the answers to derive and confirm journeys, then screens, then data choice/model, then permissions.
4. Move notifications, WhatsApp, and similar later functions to `Deferred capabilities` unless the core journey truly requires them.
5. Save each confirmed block into the draft with `discovery_progress`; finalize the draft only after the G7 recap is confirmed; never self-approve it.

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Quick feature — skip the contract” | Hermes ships via approved architecture; silent scope = rework |
| “I’ll ask ten questions at once” | One-at-a-time when fuzzy reduces wrong locks |
| “The user said ‘elegí vos’, so I can decide silently” | Recommend provisionally, explain assumptions/risks, and ask for confirmation |
| “The app is simple; screens will emerge while coding” | Undefined screens hide missing journeys, states, and data; map the MVP or record an explicit waiver |
| “Supabase/Sheets is already enabled, so the data decision is made” | Availability is not suitability; compare against relationships, permissions, concurrency, history, and maintenance |
| “A list of tables is a data model” | A usable model also states meaning, ownership, lifecycle, relationships, sensitive data, and record behavior |
| “Writer can invent the open questions” | Open questions stay open until human decides; no silent invent |
| “Hourly Vercel Cron is fine on free” | Document limit + free alternative or Pro |
| “RLS lo vemos después de que funcione” | Without a door policy, “works” means data may be world-readable/writable via the Data API |
| “Slices in architecture.md are enough” | Status/BPs belong in the writing plan; the contract stays qué/por qué |
| “I’ll start shipping; they said the idea is good” | Two doors: architecture approved **and** plan approved. Then **hermes-ship-plan** |
| “profile acebal under Hermes → apply brand” | Hermes tree → identidad **off**. Brand only under Gestión Acebal\\sistemas (or cloud profile acebal when path unknown). |
| “Put a11y on every slice” | Architect chooses gate / dedicated slice / Ready-when — not default every ship |
| “One detail is unclear — run the full workshop” | Ambiguity in one decision = one question; the workshop is for undefined products |
| “Button copy change, but let’s do G1–G7 anyway” | Tiny change: one Key decision line + confirmed tiny-skip, then **hermes-escritor** |
| “New session — start the interview over” | Resume from `discovery_progress` / `next_step`; re-asking confirmed blocks wastes the user’s time |
| “Ask about everything so nothing is assumed” | Ask only when the answer changes scope, risk, permissions, cost, or delivery; state other defaults in one line |

## Red flags

- Product code while still designing
- Greenfield architecture drafted after only a problem statement, with no confirmed journeys
- Batch questionnaire, unexplained jargon, or recommendations with no alternative/tradeoff
- UI project with no screen/navigation map or no loading/empty/error/permission states
- Data system selected because it is familiar/enabled, with no decision criteria
- Entity list with no relationships, ownership, lifecycle, or representative record walkthrough
- “Elegí vos” treated as approval; required block omitted without a quoted waiver and consequence
- Self-setting `status: approved` on contract or plan
- Empty Ready-when on a non-trivial system
- Non-trivial system with no writing-plan file / no BPs
- Hobby Vercel Cron designed denser than once/day without alternative
- Supabase enabled but Auth/permissions (or Ready-when) never mentions RLS/policies
- Running **hermes-ship-plan** / **hermes-escritor** from this skill
- `gates: [identidad]` or Acebal palette while repo is under Hermes
- Identidad undecided in Key decisions on a UI project
- Greenfield interview spanning sessions with no `discovery_progress` on disk
- Unconfirmed block content written into the draft as if decided
- Questions about defaults that change none of: scope, risk, permissions, cost, delivery

## Verification

- [ ] Architecture path written; sections match enabled services
- [ ] Architecture `status` still draft until human says otherwise
- [ ] Discovery mode and activation evidence recorded (tiny: evidence that no journey/screen/entity/permission/integration changes)
- [ ] Greenfield open: `discovery_progress` + `next_step` on disk match the last confirmed block; `done` after G7
- [ ] `references/greenfield-workshop.md` was read before G1 (greenfield only)
- [ ] `references/output-templates.md` was read before writing the contract or plan; written sections match it
- [ ] In greenfield: confirmed journeys trace to an MVP screen map; every screen records actions, visible data, and required states
- [ ] In greenfield: data-system decision includes criteria, recommendation, rejected alternative, tradeoff, and upgrade trigger
- [ ] In greenfield: entity dictionary + relationships + Mermaid ER diagram + representative record lifecycle exist
- [ ] In greenfield: role/entity permission matrix exists; every omission has an explicit user waiver and consequence
- [ ] Traceability check passed: every screen datum has a source, and every entity supports a journey/rule
- [ ] Identidad on|off recorded with signal (path / profile / asked)
- [ ] Ready-when items are checkable (or slices carry acceptance)
- [ ] Writing plan exists with ≥1 slice + BPs, **or** documented tiny-skip
- [ ] Plan `status` still draft until human approves the plan
- [ ] If Supabase: Auth/permissions covers RLS + key split; Ready-when has RLS/policies or waiver item
- [ ] `gates: [identidad]` absent when identidad off
- [ ] User told: after **both** approvals → **hermes-ship-plan**; when queue empty → **hermes-lanzamiento**

## Done criteria

- Architecture doc exists with filled sections relevant to enabled services
- Greenfield blocks G1–G7 were confirmed one by one, or each skipped block has an explicit waiver and risk
- Journeys, MVP screens, data-system rationale, conceptual schema, record lifecycle, and permissions are mutually consistent
- Writing plan exists (or tiny-skip recorded)
- Open questions listed or empty
- Key assumptions / edge cases captured or called out explicitly
- User told the two doors and the next skill after approval (**ship-plan**, then **lanzamiento**)
- Identidad on|off recorded; no `gates: [identidad]` when off

## Forbidden

- Implementing features, large refactors, or “quick wins” of product code
- Skipping greenfield discovery because the agent can imagine a plausible product
- Treating “elegí vos” as permission to hide tradeoffs or bypass confirmation
- Choosing storage/provider before understanding journeys, permissions, and data relationships
- Designing visual polish or inventing brand tokens (→ **hermes-identidad** when identidad is on)
- Approving the contract or the writing plan yourself without user confirmation
- Orchestrating the ship loop (→ **hermes-ship-plan**)
- Locking in Hobby/free Vercel Cron with cadence more than once per day (→ state limit + alternative scheduler in the contract)
