---
name: hermes-ship-plan
description: >-
  Walks an approved docs/implementation-plan.md queue: next pending slice,
  then hermes-ship-slice (writer → revisor-fix → typed gates from the plan →
  docs → commit/push). Updates slice/BP status on disk. Stops on smoke fail or
  STOP_NEEDS_HUMAN. Use when the user says ship-plan, /hermes-ship-plan,
  próximo slice, hasta terminar, or asks to loop slices from the writing plan.
disable-model-invocation: true
---

# Hermes Ship-plan

## Goal

Consume the **writing plan** one slice at a time by running **hermes-ship-slice**. Update plan status on disk. Refuse draft plans, failed smoke, silent `main` push, and continuing after `STOP_NEEDS_HUMAN`. Do not design the product (→ **hermes-arquitecto**). Do not merge to `main`.

## Preconditions

1. Read `.cursor/orchestra.json` — honor writer/reviewer/documenter/security flags; if a needed role is `false`, ask once.
2. Read architecture **frontmatter** `status` only (`orchestra.paths.architectureDoc` or `docs/architecture.md`). Require `status: approved` **or** an explicit approval phrase this turn. Else → **hermes-arquitecto**. Do not load the architecture body in this loop.
3. Read writing plan (`orchestra.paths.implementationPlan` or `docs/implementation-plan.md`). Require `status: approved` **or** an explicit plan-approval phrase this turn. Else stop and ask for approval (or → **hermes-arquitecto** to write the plan).
4. Resolve `SHIP_BRANCH` as in **hermes-ship-slice**. Never default-push `main`/`master`.
5. User asked to run the plan / next slice / N slices / until empty (see modes). If they only said “implement everything” with no plan file → stop → arquitecto.
6. Evidence rules: [handoff.md](handoff.md). Do not paste that file into phase prompts.

## Modes

Parse the user message:

| Cue | `max_slices` |
| --- | --- |
| “próximo” / “siguiente” / default | **1** |
| “próximos N” / “hasta N” | **N** |
| “hasta terminar” / “vaciar la cola” | `min(pending_runnable, 5)` |

Hard cap: **5 slices per invocation** even on “hasta terminar”. If more remain, say so and give the next command.

## Procedure

Re-read **slice status, `depends_on`, and BPs** from the plan file before every slice (disk is source of truth, not chat memory). Do not re-read the architecture body.

For `i = 1 .. max_slices`:

1. Pick the first slice whose `status` is `pending` (or `in_progress` if resuming a STOP) and whose `depends_on` slices are `done`. If none: report empty or blocked queue and stop.
2. Set that slice to `in_progress` on disk.
3. Run **hermes-ship-slice** for **that slice only**. Pass the full slice card verbatim (`slice_id`, title, and every field under that slice heading: goal, pending BPs, `contracts`, `edge_cases`, acceptance, `verify`, `gates`, `read_first`, `paths_hint`, `out_of_bounds`, `stop_if` when present). Do not follow **hermes-escritor**, **hermes-revisor**, or **hermes-documentador** in this chat.
4. After ship-slice, trust evidence blocks, not a prose “done”:
   - Smoke `fail`, or `pass` without an integer exit → slice `blocked` or leave `in_progress`; **STOP** (optionally → **hermes-depurador**). Do not re-run the suite.
   - Review `STOP_NEEDS_HUMAN`, or missing `## Review handoff` → **STOP**. Do not mark `done`.
   - `PASS` / `FIXED`: launch **one foreground subagent per typed gate** (order below). Do not read the gate skill here. Do not pass a model override. Any `fail`, `STOP_NEEDS_HUMAN`, or missing block → **STOP**.
     1. `seguridad` if listed **or** evidence `files` touch RLS/auth/secrets/privileged Edge / new public APIs → `hermes-ship-gate` (`gate: seguridad`)
     2. `identidad` if listed → `hermes-ship-gate` (`gate: identidad`). `skip` means arquitectura off; record the mismatch
     3. `a11y`, `ux-surfaces`, `ux-mobile`, `observabilidad`, `optimizador`, `simplificador` → `hermes-ship-gate-medio` for that one name
     4. Unknown gate string → ask once; do not invent a skill
   - No subagent tooling → run that one mapped skill in-process and mark `gates_mode: degraded`.
   - Do **not** invent gates the plan omitted (no automatic a11y/optimizador/etc.).
   - If `bp_evidence` does not cover acceptance or unchecked BPs → **STOP** (do not mark `done`).
   - Findings outside this slice do **not** become new BPs or extra edits: list them as `Follow-ups → hermes-arquitecto`.
5. **Verify before closing:** cite smoke command + integer exit (or justified skip), review handoff, each gate block, and commit evidence. Tick a BP only when `bp_evidence` names it and `git diff --stat` lists that path. Do not re-open the full diff and do not re-run smoke. Then set slice `status: done` and write the progress report. The smoke agent never does this step.
6. If STOP: `Waiting on human: yes`; stop. Do not start the next slice.
7. If success and `i < max_slices`: continue from step 1 (re-read disk).

If the queue is empty after a success: tell the user the plan is complete → **hermes-lanzamiento** when they want a go/no-go. Do not merge.

## Output contract

After each slice and at loop end:

```markdown
## Ship-plan progress
- State: Trabajando | Verificando | Listo | Necesita tu decisión (+ one line why)
- Plan: docs/implementation-plan.md (approved)
- Branch: <SHIP_BRANCH>
- Mode: next | until N | until empty (capped 5)
- This run: S<k> <title> → done | blocked | stopped
- BPs closed: … / still open: …
- Review: PASS | FIXED | STOP_NEEDS_HUMAN
- Smoke evidence: command + exit | missing
- Gates run: … (gate → pass|skip|STOP) …
- gates_mode: subagent | degraded
- Commit/push: …
- Follow-ups → hermes-arquitecto: … | none
- Queue remaining: S… (pending)
- Waiting on human: yes | no
- Next command: "…"
```

`State` is the first line a non-developer reads: **Trabajando** = a slice is still changing; **Verificando** = smoke/review/gates running; **Listo** = slice(s) closed with evidence; **Necesita tu decisión** = STOP — state the cause, the impact, and the concrete options. `Necesita tu decisión` ⇔ `Waiting on human: yes`.

## Done criteria

- Preconditions met or honest stop naming the blocking skill
- Plan file on disk matches claimed slice statuses
- Ship-slice gates honored (no docs/commit after STOP)
- Smoke evidence cited (command + exit, or justified skip); slice `done` was not set by the smoke agent
- Progress report posted
- Cap 5 respected; remaining queue listed

## Forbidden

- Approving architecture or plan yourself
- Implementing BPs that are not in the plan (→ **hermes-arquitecto**)
- Skipping **hermes-ship-slice** and “just writing the slice”
- Reading **hermes-escritor**, **hermes-revisor**, **hermes-documentador**, or a gate skill body in this loop when the subagent ran
- Passing a model override (the template pins the class; a fast variant is STOP)
- Push to `main`/`master` as default
- Continuing after failed smoke or `STOP_NEEDS_HUMAN`
- Parallel slices
- Pre-merge theater → **hermes-lanzamiento**
- GitHub label automations (out of scope v1)
- Committing secrets or doctor output

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Plan is in my head; skip the file” | Disk is the queue. No file → arquitecto. |
| “Hasta terminar means all 20 slices” | Cap 5 per invocation. |
| “Review PASS but BPs still open; close the slice” | Unmet acceptance = STOP. |
| “UI slice but I added RLS; skip seguridad” | Heuristic fires even if `gates` forgot it. |
| “Same as ship-slice; I’ll invent extra steps” | Reuse ship-slice. This skill is the loop + status. |
| “Always run identidad / a11y” | Only if the slice `gates` list them (architect’s job). |
| “Gate not in the map; I’ll skip quietly” | Ask once or STOP — do not drop typed gates. |
| “Ship-slice said PASS, mark it done” | A report is a claim; require smoke command + exit, commit, and BP ↔ `git diff --stat` before ticking |
| “I’ll re-run smoke to be sure” | Re-running bills this chat for a phase that already returned exits. Missing exit = STOP |
| “I’ll open the gate skill so I can judge it” | Launch the gate subagent. Reading the skill here pulls that job into the loop |
| “Revisor found a bug in another module; I’ll fix it here” | Out-of-slice finding = follow-up → arquitecto; silent scope growth breaks the plan |

## Red flags

- Slice marked `done` while BPs unchecked
- Next slice started after STOP
- More than 5 slices in one invocation
- `seguridad` skipped on auth/RLS/secrets diff
- Typed gate listed but no Phase evidence for it (or `gates_mode: degraded` without an in-process result)
- Plan or architecture still `draft` but shipping claimed
- Push destination is `main`/`master` without a second explicit order
- `identidad` gate run against architecture `identidad: off` without calling out the mismatch
- BP ticked with no `bp_evidence` path in `git diff --stat`
- Slice `done` while smoke evidence has no integer exit
- Parent read a sibling or gate `SKILL.md` during the loop
- Gate launch passed a model override or a fast variant
- Diff touches paths outside the slice’s `paths_hint` / goal with no follow-up note
- STOP reported without cause, impact, and options

## Verification

- [ ] Architecture + plan approval quoted (`status: approved` or user phrase) or stop evidenced
- [ ] Chosen slice id + `depends_on` satisfied (or blocked queue reported)
- [ ] Ship-slice report cited per slice that ran, including smoke command + exit (or justified skip)
- [ ] Each listed typed gate has a Phase evidence pass/skip/STOP (or `gates_mode: degraded`)
- [ ] Plan file diff shows status/BP updates matching the progress report
- [ ] Every ticked BP is in `bp_evidence` and in `git diff --stat`; commit visible in `git log`
- [ ] No sibling or gate skill body was read in this chat when its subagent ran
- [ ] `State` line present and consistent with `Waiting on human`
- [ ] Out-of-slice findings listed as follow-ups, not implemented
- [ ] If Waiting on human = no and more slices remain: next command given; if queue empty: lanzamiento named
