# Greenfield workshop — block detail

Loaded by **hermes-arquitecto** in greenfield mode. Complete the blocks in order with the interview protocol from `SKILL.md` (rounds of ≤3 questions, recommendation + alternative, `Asumí` list). G1 is mostly questions; from G2 on, **propose a draft from the answers so far and ask for corrections**.

## G1 — Problem, actors, and success

- Ask: who has the problem, who operates the system, who receives the result, what they do today. Offer a recommended guess for each.
- Obtain one primary **real** example from trigger to desired outcome (a recent case, with names/data anonymized).
- Define measurable success and the smallest useful MVP. Propose moving later functions (notifications, WhatsApp, reports) to `Deferred capabilities`; they do not block the contract.

## G2 — Product shape and journeys

- Recommend web, GAS, hybrid, CLI, or script from the real users and operating context (devices, connectivity, who maintains it); say why.
- Draft the happy path step by step, then the critical alternate/error paths. For each journey: actor, entry point, decisions, handoffs, end state.
- Ask for corrections. Confirm journeys before deriving screens — features are not screens.

## G3 — Screen and navigation map

- Derive the minimum MVP screens from the confirmed journeys yourself; present them as a list or a Mermaid flowchart.
- Per screen: actor/role, purpose, entry/exit, visible data, primary/secondary actions, and loading/empty/error/success/permission-denied states.
- Merge screens with no independent job; flag post-MVP screens. Stay at behavior and information level — styling and brand belong to later UI work / **hermes-identidad**.

## G4 — Data-system decision

- Compare only realistic candidates: spreadsheet/Sheet, relational database/Postgres (e.g. Supabase), local storage, or another justified system.
- Criteria: relationships, simultaneous users, permissions, audit/history, volume, offline needs, maintenance, cost limits.
- Explain once: **data model** (how information is organized) vs **database engine** (how it is stored) vs **provider** (who hosts it).
- Services in orchestra are available capabilities, not proof of fit. Record choice, reason, rejected alternative, tradeoff, upgrade trigger.

## G5 — Conceptual data model

- Derive entities from journeys and screen data; explain each as a real-world “thing”.
- Per entity: purpose, stable identifier, owner, lifecycle/status, required vs optional fields, sensitive fields, history needs.
- Relationships and cardinality in plain language, then a Mermaid `erDiagram`.
- Walk one representative record through create → read → update → archive/delete → error/recovery. Remove fields/entities no journey or rule needs.

## G6 — Authentication and permissions

- Recommend how people enter: anonymous, magic link, Google, or another justified method.
- Permission matrix per role × sensitive entity: read, create, update, delete/archive, privileged actions.
- Supabase/Postgres: RLS per sensitive table; Data API with publishable/anon + policies; privileged key never in the browser; privileged operations server/Edge only.

G4–G6 usually close together: present them as one **data package** for correction when no consequential question remains open.

## G7 — Synthesis and boundary

- State identity once (`identidad on/off porque …`), integrations, constraints, waivers, assumptions, edge cases, deferred capabilities, out of scope.
- Re-read journeys → screens → data model → permissions both ways: every screen datum has a source; every entity supports a journey or rule.
- Draft the **Glossary** (user term → meaning → code name) and the **Code map** (stack, folders, naming, commands, env var names). These freeze the names every slice will use.
- Present a short decision recap and ask for corrections before finalizing the draft contract.
