# Output templates

Loaded by **hermes-arquitecto** when writing or updating the contract and the writing plan. Section rules (greenfield fill, draft status, plan quality) live in `SKILL.md`.

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
## Services (from orchestra.json)
## Local DX (Windows, if web) — http://<host>.local:<port>; not production
## Identidad — on|off + signal (path | profile | asked); Acebal brand only when on
## Key decisions (table: decision | why | alternative rejected)
## Assumptions and edge cases
## Deferred capabilities
## Explicit waivers
## Implementation slices (ordered names + one-line goals; BPs live in the writing plan)
## Out of scope
## Ready-when (acceptance checklist — include quality passes you deferred to launch)
## Open questions
```

## 2) Writing plan — `docs/implementation-plan.md`

Prefer `templates/implementation-plan.md.example` when the project has it; otherwise use:

```markdown
---
status: draft
architecture: docs/architecture.md
updated: YYYY-MM-DD
---

# Implementation plan — <name>

## Rules
- One slice = one hermes-ship-slice.
- No BPs outside this plan without arquitecto.

## Slices

### S1 — <title>
- **goal:** …
- **depends_on:** []
- **status:** pending
- **gates:** [] | [seguridad] | [identidad] | [a11y] | [ux-surfaces] | [ux-mobile] | [observabilidad] | [optimizador] | [simplificador]
- **paths_hint:**
- **acceptance:** checklist (smoke + behavior) or `wiring-only` + how it will be proven later
- **bps:**
  - [ ] BP1 — …
```
