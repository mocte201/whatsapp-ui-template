# Greenfield workshop — block detail

Loaded by **hermes-arquitecto** in greenfield mode. Complete the blocks in order. All are mandatory unless the user explicitly waives one; apply the teaching protocol from `SKILL.md` inside every block.

## G1 — Problem, actors, and success

- Identify who has the problem, who operates the system, who receives the result, and what they do today.
- Obtain one primary real-world example from trigger to desired outcome.
- Define measurable success and the smallest useful MVP. Separate later functions (for example notifications or WhatsApp) into `Deferred capabilities`; they do not block the contract.

## G2 — Product shape and journeys

- Recommend web, GAS, hybrid, CLI, or script from the actual users and operating context; explain why.
- Describe the main happy path step by step, then the critical alternate/error paths.
- Name the actor, entry point, decisions, handoffs, and end state for each journey.
- Confirm the journeys before deriving screens. Features are not screens.

## G3 — Screen and navigation map

- Derive the minimum MVP screens from confirmed journeys; do not ask the user to invent UI structure alone.
- For every screen specify: actor/role, purpose, entry/exit, visible data, primary and secondary actions, and loading/empty/error/success/permission-denied states.
- Record navigation between screens and explain why each screen exists. Merge screens that have no independent job; flag post-MVP screens separately.
- Stay at behavior and information architecture level. Pixel styling and brand tokens belong to later UI work / **hermes-identidad**.

## G4 — Data-system decision

- Compare only realistic candidates: spreadsheet/Sheet, relational database/Postgres (possibly Supabase), local storage, or another justified system.
- Base the recommendation on relationships, simultaneous users, permissions, audit/history, expected volume, offline needs, maintenance, and cost limits.
- Explain the difference between the **data model** (how information is organized), **database engine** (how it is stored), and **provider** (who hosts it).
- Treat services in orchestra as available capabilities, not proof that they are the right choice. Record the chosen system, why it fits, rejected alternative, tradeoff, and upgrade trigger.

## G5 — Conceptual data model

- Derive entities from journeys and screen data. Explain each entity as a real-world “thing”; avoid premature SQL details.
- For every entity define purpose, stable identifier, owner, lifecycle/status, required vs optional fields, sensitive fields, and audit/history needs.
- Define relationships and cardinality in plain language, then add a Mermaid `erDiagram`.
- Walk one representative record through create, read, update, archive/delete, and error/recovery. Remove fields/entities with no journey or rule supporting them.

## G6 — Authentication and permissions

- Decide who may enter and how: anonymous, magic link, Google, or another justified method.
- Build a permission matrix per role and sensitive entity: read, create, update, delete/archive, and privileged actions.
- If Supabase/Postgres is selected: state RLS per sensitive table; Data API uses publishable/anon + policies; privileged key never reaches the browser; privileged operations stay server/Edge only.

## G7 — Synthesis and boundary

- Confirm identity aloud once (`identidad on/off porque …`), integrations, constraints, explicit waivers, assumptions, edge cases, deferred capabilities, and out of scope.
- Re-read journeys → screens → data model → permissions in both directions. Every screen datum must have a source; every entity must support a journey or rule.
- Present a short decision recap and ask for corrections before finalizing the draft contract.
