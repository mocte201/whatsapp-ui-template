# Output templates

Loaded by **hermes-arquitecto** when writing or updating the contract and the writing plan. Section rules live in `SKILL.md`; slice-card rules live in `writer-ready-plan.md`.

## 1) Architecture — `docs/architecture.md`

```markdown
---
status: draft
profile: personal|acebal
discovery: greenfield|established|tiny
discovery_progress: G1..G7|done   # greenfield only
next_step: <one line>            # while greenfield is open
updated: YYYY-MM-DD
---

# Architecture — <name>

## Summary
## Users and goals
## MVP scope
## User journeys
- Primary happy path
- Critical alternate/error paths
## Screen and navigation map
- Per screen: role; purpose; entry/exit; visible data; actions; loading/empty/error/success/denied states
## Shape (web / GAS / hybrid / local)
## Data-system decision
- Choice; plain-language reason; alternative rejected; tradeoff; upgrade trigger
## Data model
- Entity dictionary: purpose; ID; owner; lifecycle; required/optional/sensitive data; history
- Relationships in plain language
- Mermaid erDiagram
## Record lifecycle example
- Create → read → update → archive/delete → error/recovery
## Auth and permissions
- Permission matrix per role/entity: read; create; update; delete/archive; privileged actions
(When Supabase/Postgres — fill; else N/A:)
- RLS per sensitive table (who reads/writes)
- Data API only with publishable/anon + policies
- No service_role in client; privileged ops on server/Edge only
## Glossary
| Term (as the user says it) | Meaning | Name in code (table / type / route) |
## Code map (decided conventions)
- Stack + major versions (verified via hermes-fuente or lockfile)
- Folder layout (where pages, server code, migrations, tests live)
- Naming rules (e.g. tables snake_case plural; types PascalCase singular)
- Commands: dev / lint / build / test (exact)
- Env var NAMES (never values)
## Services (from orchestra.json)
## Local DX (Windows, if web) — http://<host>.local:<port>; not production
## Identidad — on|off + signal (path | profile | asked); Acebal brand only when on
## Key decisions (table: decision | why | alternative rejected)
## Assumptions and edge cases
## Deferred capabilities
## Explicit waivers
## Implementation slices (ordered names + one-line goals; cards live in the writing plan)
## Out of scope
## Ready-when (acceptance checklist — include quality passes deferred to launch)
## Open questions (each with who decides)
```

## 2) Writing plan — `docs/implementation-plan.md`

Prefer the project’s `templates/implementation-plan.md.example` when it has the full slice card; otherwise use:

```markdown
---
status: draft
architecture: docs/architecture.md
updated: YYYY-MM-DD
branch: # optional work branch
---

# Implementation plan — <name>

## Rules
- One slice = one hermes-ship-slice.
- The writer executes the card; it does not choose. A missing decision → STOP_NEEDS_HUMAN, back to arquitecto.
- No BPs outside this plan without arquitecto.

## Slices

### S1 — <title>
- **goal:** …
- **depends_on:** []
- **status:** pending
- **gates:** [] | [seguridad] | [identidad] | [a11y] | [ux-surfaces] | [ux-mobile] | [observabilidad] | [optimizador] | [simplificador]
- **read_first:** architecture.md › <section> › <subsection>
- **paths_hint:** path/a.ts (new); path/b.ts
- **contracts:**
  - <exact name> — <shape / signature / copy>
- **bps:**
  - [ ] BP1 — <verb> <target> → <observable done condition>
- **edge_cases:**
  - <input/state> → <expected behavior>
- **acceptance:**
  - [ ] <observable behavior>
- **verify:**
  - `<exact command>` → <expected result>
  - Manual: <URL> → <steps> → <expected visible text>
- **out_of_bounds:** <files / deps / refactors not to touch>
- **stop_if:** <condition → STOP_NEEDS_HUMAN>

## Probe log
- S1 — NINGUNO | <n> huecos corregidos (<which>)
```
