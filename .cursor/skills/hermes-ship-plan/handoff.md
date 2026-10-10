# Ship phase evidence

`hermes-ship-plan` and `hermes-ship-slice` read this file. The subagent prompt already requires the block; do not paste this file into the parent chat.

## Block

```markdown
## Phase evidence
phase: escritor | smoke | gate | docs | commit
slice_id: S<n>
status: pass | fail | skip | STOP_NEEDS_HUMAN
commands:
  - cmd: <exact command>
    exit: <integer | pending | skipped>
bp_evidence:
  - bp: <id or text>
    path: <repo-relative path>
files:
  - <repo-relative path>
why_stop: <one sentence or n/a>
gate: <name or n/a>
```

Review keeps its own block (`## Review handoff` in the revisor-fix template). Do not invent a second review format.

## Parent rules

- Smoke `pass` needs at least one `commands` entry with an integer `exit`. Missing exit → STOP. Do not re-run the suite.
- Smoke `skip` only when `commands` is empty and `why_stop` says why nothing ran (docs-only / wiring-only).
- Smoke `fail` or `STOP_NEEDS_HUMAN` → STOP the loop. The smoke agent never writes slice `status: done`.
- Tick a BP only when `bp_evidence` lists it and `git diff --stat` contains that path. Do not re-open the full diff.
- Gate `fail` or missing block → STOP. Gate `skip` is recorded (identidad off, or gate not listed). Unknown gate string → ask once; do not invent a skill.
- Stage only `files` from escritor and docs evidence. Never stage `.env`, doctor dumps, or secret-bearing files.
