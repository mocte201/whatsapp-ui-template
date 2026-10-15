---
name: hermes-escritor
description: >-
  Trigger: implement plan, writer, composer, slice_id, aprobado. Implements an
  approved Hermes architecture contract in thin vertical slices with smoke
  verification. Use when architecture is approved, ship-plan names a slice_id,
  or the user asks to implement the plan.
---

# Hermes Escritor

## Goal

Turn `docs/architecture.md` into working code via thin vertical slices. Smoke-test each slice path that changes behavior. Leave deep review to **hermes-revisor** / **hermes-seguridad**. Leave green-path failures to **hermes-depurador** when triage is non-trivial.

## Preconditions

1. Read `.cursor/orchestra.json` — respect enabled services and `roles.writer`.
2. Read architecture doc (`orchestra.paths.architectureDoc` or `docs/architecture.md`).
3. Require `status: approved` (frontmatter) **or** explicit user message approving the plan. If still `draft`, stop and send them to **hermes-arquitecto**.
4. If a writing plan exists (`orchestra.paths.implementationPlan` or `docs/implementation-plan.md`) and this turn names a `slice_id`, implement **only** that slice’s pending BPs. Do not invent extra BPs. When the card has them: read only the `read_first` contract sections, use `contracts` names and copy exactly, handle every `edge_cases` line, list `verify` commands as the smoke commands, and respect `out_of_bounds`. A `stop_if` condition, or a BP that needs a behavior/data/security choice the card and contract do not make → return `STOP_NEEDS_HUMAN` (subagent) or ask once (direct) instead of choosing.

## Minimal path (before writing)

After reading the slice and tracing the real flow end to end — not instead of understanding — stop at the first rung that holds:

1. Does the approved contract already forbid this work / mark it out of scope? Stop.
2. Does a helper, util, or pattern already exist in this repo? Reuse it.
3. Does the language/stdlib cover it? Use it.
4. Does a native platform / framework feature already enabled in the contract cover it? Use it.
5. Does an **already-installed** dependency cover it? Use it — do not add a package to save a few lines.
6. Can this be a few lines in an existing file? Prefer that over a new module.
7. Only then: write the minimum new code that satisfies the slice.

**Contract beats YAGNI.** Ready-when items (RLS, kill-switch, channels, identity, cron shape) are not optional rungs — do not “simplify away” what `docs/architecture.md` already approved. If the user’s ask is broader than the slice/contract, ask once: “¿necesitás X, o alcanza Y del plan?”

**Not minimal about:** trust-boundary validation, error paths that prevent data loss, security/RLS, a11y on UI you touch, anything explicitly in the contract or Ready-when.

**Deliberate ceilings:** if you knowingly ship a coarse approach with a known limit (global lock, O(n²), naive heuristic), leave one short comment `// hermes:ceiling <limit> → <upgrade path>` at the site. No essay.

## Decision Gates

| Situation | Action |
| --- | --- |
| Architecture still `draft` | Stop → **hermes-arquitecto** |
| Ask broader than current slice / contract | Ask once what to keep in scope |
| Forecast authored diff ≫ ~400 lines **and** multiple concerns mixed | Split into smaller vertical slices / chained PRs before coding; do **not** hard-stop a single inseparable behavior |
| Non-trivial logic without a runnable check | Add test-with / behavioral check, or cite existing smoke that covers it |
| Caller delegated smoke (**hermes-ship-slice** / `hermes-escritor-run`) | Return the command list with `exit: pending`. Do not execute. Do not mark the slice done |
| Smoke fails mid-slice | Stop-the-line → **hermes-depurador** or honest fail report |

## Work units (when committing)

If the user (or **hermes-ship-slice**) asks to commit:

- One commit = one deliverable behavior, fix, migration, or docs unit — **not** “models then services then tests”.
- Keep tests (and user-visible docs) in the **same** commit as the behavior they verify/explain.
- Record evidence in the smoke/finish note: focused test command + result; runtime/smoke command + result **or** explicit `N/A` with reason; rollback boundary (what can revert without dragging unrelated work).
- Prefer Conventional Commit-style messages that state the **outcome**, not the file list.

## Implementation rules

- Follow the contract; if a decision is missing, ask once — do not invent silently.
- Before large work, restate the plan in ordered **vertical slices** (each slice: one user-visible or API-complete cut). Call out highest-risk edge cases.
- For non-trivial business logic: leave **one** runnable check that fails if the logic breaks (failing/behavioral test, assert-based self-check, or the project smoke path). Prefer test-first or test-with. Pure wiring covered by existing smoke needs no extra file. Trivial one-liners need no new test.
- No speculative abstractions, boilerplate, or new files nobody asked for. Fewest files; boring over clever; deletion over addition when behavior stays correct.
- Prefer existing project patterns; do not add unrelated libs.
- Ambiguous framework APIs → **hermes-fuente** (cite official docs) before inventing.
- Use MCP/CLI already linked (Supabase, gh, etc.). Verify first: on a cloud agent VM they may be absent or unauthenticated. If so, do the file work and list the commands the user must run locally instead of guessing.
- Secrets only in `.env` (gitignored); update `.env.example` with placeholders. Client/public bundles: publishable/anon only — **never** `service_role` / secret keys (those stay server/Edge).
- **Supabase data access:** prefer the typed client (`.from().select().eq()` / filters). Do **not** build SQL, shell, or templates by concatenating user/request input. Raw SQL or RPC must use bound parameters / typed args; if you cannot, stop and ask (or → **hermes-arquitecto** / **hermes-seguridad**).
- **New user-data tables/paths:** ship RLS policy (migration) in the same slice **or** leave an explicit Ready-when remainder / human waiver — never “RLS later”.
- If clasp enabled: keep GAS under configured `services.clasp.rootDir`.
- Free-tier: never add Vercel Cron schedules denser than once/day unless the approved architecture and plan are explicitly Pro/paid or use an external scheduler. On Hobby, sub-daily Vercel Cron fails deploy (→ **hermes-optimizador** / **hermes-arquitecto** if the need is real).
- Small commits only if the user asks to commit. Do **not** auto-commit by default.
- **Stop-the-line:** if smoke fails, do not claim Ready-when complete — fix or switch to **hermes-depurador** / report failed smoke honestly.
- Before finishing, self-check against architecture `Ready-when`: completed / deferred / assumptions that could break the contract. Floor bar: smoke truthfulness, no secrets in git, no privileged keys in client, no string-built SQL/commands, free-tier cron rules (see orchestrator `skills/_references/definition-of-done.md` when available).

## Smoke test (required)

If the caller delegated smoke (ship-slice or `hermes-escritor-run`): do not run the suite. List the commands below with `exit: pending` in the phase evidence and stop. Direct escritor (no delegating caller) runs them here.

Run what applies after each meaningful slice and before declaring done:

1. Install deps if needed (`npm install` / equivalent)
2. Lint if configured
3. Build if configured
4. Unit/integration tests if present
5. For GAS: note that full Apps Script runtime may need `clasp push` + manual run — say so

Report a short **Smoke report**: passed / failed / skipped (with reason) + which commands ran. If the slice touched schema/API/data paths: add one line `RLS/policies: done | deferred (cite Ready-when) | N/A`.

## Out of scope for this skill

- Full security audit (→ **hermes-seguridad**)
- Long-form docs rewrite (→ **hermes-documentador**) except minimal comments needed for the change
- Performance pass (→ **hermes-optimizador**)
- Pre-merge ship checklist (→ **hermes-lanzamiento**)
- Pure complexity cleanup without feature work (→ **hermes-simplificador**)
- Approving your own PR as “clean” without **hermes-revisor** when `roles.reviewer` is true — suggest reviewer next
- Inventing Acebal palette/type/logos → **hermes-identidad**

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Still draft but user is in a hurry — I’ll code” | No product code until approved; → **hermes-arquitecto** |
| “I’ll smoke at the end of everything” | Slice smoke catches breaks early; end-only smoke often arrives with multi-cause failures |
| “Ship-slice delegated smoke, but I’ll run it here” | The cheap phase runs the suite. Running it here bills the capable model and duplicates evidence |
| “Tests later” | Behavior without proof fails Ready-when; at least one automated or documented manual smoke path |
| “Cloud has no MCP so I can’t implement” | Write files; list live verify steps for the human; don’t invent success |
| “Commit each slice automatically” | Commit only if the user asks |
| “Es un MVP, sin RLS” | Open Data API without policies exposes rows now; ship policy or explicit Ready-when remainder |
| “Concateno el filtro, es más fácil” | String-built SQL/commands turn user input into executable instructions — use typed filters or bound params |
| “Smallest diff — skip reading callers/flow” | A tiny patch in the wrong place is a second bug; trace first, then climb the ladder |
| “New util/layer for cleanliness” | No abstraction until a second real use or the contract names it; → **hermes-simplificador** only after behavior works |
| “YAGNI the RLS / channel / Ready-when item” | Approved contract is not speculative gold-plating; ship or explicit remainder |
| “Commit by file type is cleaner” | Reviewers need a behavior story; tests/docs travel with the unit |
| “400 lines is a hard stop” | Soft sizing signal: split when concerns mix; one inseparable behavior may stay larger with an explicit note |

## Red flags

- Implementing while `status: draft`
- Silent inventions of open questions
- Declaring done with failed/skipped smoke and no honest report
- Delegated smoke executed inside escritor-run
- Sub-daily Vercel Cron on free/Hobby without architecture Pro/external path
- `service_role` / secret key imported or bundled in client components
- SQL/command/template strings built with request or user input
- New dependency or framework when stdlib/existing helper would do
- Coarse algorithm shipped with no `hermes:ceiling` and no Ready-when note
- Commits split as models/services/tests with none independently meaningful
- Huge mixed-concern diff with no split note and no justification

## Verification

- [ ] Architecture status approved or explicit human approval quoted
- [ ] Smoke report with commands and pass/fail/skip, or a delegated command list with `exit: pending` and the suite not run
- [ ] Ready-when items mapped to done / remaining
- [ ] No privileged secrets in client; new data paths have RLS posture declared (done / deferred / N/A)
- [ ] Non-trivial logic has one runnable check (or explicit “covered by smoke X”)
- [ ] If commits were made: each is a work unit with tests/docs alongside (or N/A noted)
- [ ] Next roles suggested (revisor / seguridad / documentador / lanzamiento as fit)

## Done criteria

- Acceptance items in architecture “Ready-when” addressed or listed as remaining
- Smoke report posted
- User pointed to next role(s) enabled in orchestra.json
