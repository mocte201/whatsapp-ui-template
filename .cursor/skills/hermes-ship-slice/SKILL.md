---
name: hermes-ship-slice
description: >-
  Trigger: ship-slice, /hermes-ship-slice, aprobado e implementar, slice_id.
  Delegates escritor, smoke, revisor-fix, and docs to subagents, then commits
  on a work branch. Use when shipping one small approved slice end-to-end.
disable-model-invocation: true
---

# Hermes Ship-slice

## Goal

Ship one **small** approved slice end-to-end with hard stop gates. Refuse draft contracts, failed smoke, silent push to `main`/`master`, and continuing after `STOP_NEEDS_HUMAN`.

## Preconditions

1. Read `.cursor/orchestra.json` — honor `roles.writer` / `reviewer` / `documenter` if present; if a needed role is `false`, ask once before continuing.
2. Read architecture frontmatter `status` (`orchestra.paths.architectureDoc` or `docs/architecture.md`). Do not load the body here; the writer and reviewer subagents do.
3. Require `status: approved` **or** an explicit user approval phrase in this turn. If `draft` → stop → **hermes-arquitecto**.
4. Resolve `SHIP_BRANCH`: user-named branch, else current branch if not `main`/`master`. If on `main`/`master` with no name → create or ask for a work branch; **do not** push to main.
5. Evidence contract: [handoff.md](../hermes-ship-plan/handoff.md). Launch named subagents and **do not pass a model override** — the platform template pins the class (cheap smoke/docs, capable writer/reviewer). If the launch reports a fast variant, **STOP** (`model_pin: fast`). If the platform cannot pin, mark `model_pin: unpinned` and continue. No subagent tooling → degraded path in the phase that needs it.

## Procedure

### Fase 0 — Scope

If the parent passed a writing-plan `slice_id` (from **hermes-ship-plan** / `docs/implementation-plan.md`): that slice’s goal + pending BPs **are** the scope. Do not add BPs.

Otherwise restate the slice in one sentence from the user message. If unbounded (“fix everything”) → ask to narrow once.

If the planned authored diff (additions + deletions, excluding obvious generated goldens) looks ≫ ~400 lines **and** mixes unrelated concerns → ask once to split or chain PRs. Do **not** hard-stop a single inseparable behavior; note the exception in the ship report.

### Fase 1 — Escritor (subagent)

Launch foreground `hermes-escritor-run`. Pass only the slice card verbatim: `slice_id`, title, goal, pending BPs, acceptance, `gates`, `paths_hint`, plus `read_first`, `contracts`, `edge_cases`, `verify`, `out_of_bounds`, `stop_if` when the plan has them. Do not follow **hermes-escritor** in this chat.

Require `## Phase evidence` with `phase: escritor`. Missing block → **STOP**.

No subagent tooling → follow **hermes-escritor** in-process (that path owns smoke), mark `writer_mode: degraded`, and skip Fase 1b.

### Fase 1b — Smoke (subagent)

Skip if Fase 1 was degraded (smoke already ran there).

Launch foreground `hermes-ship-smoke` with the escritor `commands`. Do not run the suite in this chat.

`fail`, or `pass` without an integer `exit` → **STOP**. `skip` only when the command list is empty and `why_stop` says why. The smoke agent must not mark the slice done.

No smoke subagent → run the listed commands here, record exits, mark `smoke_mode: degraded`.

### Fase 2 — Revisor-fix (subagent)

Launch foreground `hermes-revisor-fix`. Pass slice summary, touched paths, smoke evidence, and the contract bits that constrain this slice. Do not follow **hermes-revisor** here and do not paste a review playbook.

Read `## Review handoff`. Missing or malformed → **STOP**.

No subagent tooling → run the revisor-fix rules in-process and mark `review_mode: degraded`.

### Fase 3 — Human gate (parent)

| status | Action |
| --- | --- |
| `STOP_NEEDS_HUMAN` | Show `why_stop` + remaining. **STOP.** Wait for explicit user go-ahead. |
| `PASS` or `FIXED` | Continue. |
| Missing/malformed handoff | Treat as `STOP_NEEDS_HUMAN`. |

### Fase 4 — Documentador (subagent)

Launch foreground `hermes-ship-docs` with the slice card and `files`. Do not follow **hermes-documentador** here.

No subagent tooling → follow it minimally in-process, `docs_mode: degraded`.

### Fase 5 — Commit + push (parent)

This skill **includes** commit+push (overrides escritor’s default no-commit).

1. Stage only paths listed in escritor and docs evidence. Never stage `.env`, doctor dumps, or secret-bearing files.
2. Prefer **work-unit commits**: one deliverable behavior per commit; tests/docs with the code they cover; message states the outcome. If multiple units landed in one working tree, split commits when cheap; otherwise one commit with an honest scope note.
3. Commit with a repo-style message focused on why.
4. Push to `SHIP_BRANCH` (`git push -u origin HEAD` or equivalent). **Never** push to `main`/`master` unless the user repeats that order in this turn after seeing the ship report.
5. If git/remote unavailable: leave commit instructions; do not invent success.
6. Emit `## Phase evidence` with `phase: commit` (hash or the commands the user must run).

## Output contract

```markdown
## Ship-slice report
- Branch: <SHIP_BRANCH>
- Slice: <one line>
- Size note: ok | split-asked | exception (<why inseparable>)
- Escritor: done | stopped (<reason>)
- Smoke: pass | fail | skipped (<reason>) — command + exit, or stop
- Review status: PASS | FIXED | STOP_NEEDS_HUMAN
- review_mode: subagent | degraded
- writer_mode / smoke_mode / docs_mode: subagent | degraded
- model_pin: pinned | unpinned | fast
- Docs: done | skipped (<reason>)
- Commit/push: done | skipped (<reason>)
- Waiting on human: yes | no
```

## Done criteria

- Preconditions satisfied or honest stop with handoff skill named
- Smoke evidence has command + integer exit, a justified skip, or a stop before review
- Review handoff status honored (no docs/commit after STOP)
- Ship-slice report posted
- On full success: commit exists on `SHIP_BRANCH` and push attempted or commands listed

## Forbidden

- Push to `main`/`master` as default
- Continuing after failed smoke or `STOP_NEEDS_HUMAN`
- Following **hermes-escritor** / **hermes-revisor** / **hermes-documentador** in this chat when that phase’s subagent ran
- Passing a model override, or selecting a fast variant of the cheap model
- Replacing those skills with a paraphrased mini-playbook
- Deep security/perf/UX audits here → gates in **hermes-ship-plan** / **hermes-seguridad** / **hermes-optimizador** / **hermes-ux-***
- Pre-merge go/no-go theater → **hermes-lanzamiento**
- Committing secrets or doctor output

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Same chat is fine for review” | Fresh context is the point; launch the subagent (or mark degraded). |
| “I’ll read escritor to supervise the subagent” | The evidence block is the check. Reading the skill pulls that job into this context. |
| “Should fix is large but I’ll just finish” | Large = `STOP_NEEDS_HUMAN`. Do not stretch the cheap-fix budget. |
| “User said ship so push main” | Default is work branch; main needs a second explicit order after the report. |
| “Smoke flaky; continue anyway” | Failed/unknown smoke stops the line. |
| “Smoke said pass; no need for the exit code” | Pass without an integer exit is STOP. |
| “Handoff missing; I’ll assume PASS” | Missing handoff = STOP. |
| “A fast cheap model is fine for smoke” | Do not pass a model override. A reported fast variant is STOP. |
| “Huge mixed PR is fine; ship-slice means finish” | Soft size signal: ask to split when concerns mix; note exceptions. |

## Red flags

- Docs/commit/push without a `PASS`/`FIXED` handoff
- Subagent never launched and the phase not marked `degraded`
- Parent loaded a sibling `SKILL.md` while that phase’s subagent also ran
- Smoke `pass` with no integer exit
- Launch used a fast-variant model
- Push destination is `main`/`master` without a second explicit user order
- Applied “fixes” that change architecture, auth, RLS, or add migrations inside Fase 2
- Ship-slice report omitted

## Verification

- [ ] Architecture approval quoted (`status: approved` or user phrase) or stop → arquitecto evidenced
- [ ] Escritor evidence block cited, or `writer_mode: degraded` with in-process evidence
- [ ] Smoke command + integer exit, justified skip, or stop before review
- [ ] Review handoff block cited (`PASS` / `FIXED` / `STOP_NEEDS_HUMAN`)
- [ ] `model_pin` reported; fast variant caused STOP
- [ ] If Waiting on human = no and success claimed: branch name + commit/push evidence (hash or command output)
