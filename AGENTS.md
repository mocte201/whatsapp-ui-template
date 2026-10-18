# Agents — whatsapp-ui-template

## Work order

1. **hermes-arquitecto** — `docs/architecture.md` + `docs/implementation-plan.md` with `status: approved` (ready)
2. **hermes-ship-plan** — next slice (or **hermes-escritor** for a one-off change) + smoke
3. On demand: **hermes-revisor**, **hermes-documentador**, **hermes-seguridad**, **hermes-optimizador**, **hermes-depurador**, **hermes-lanzamiento**, **hermes-ux-mobile**, **hermes-ux-surfaces**, **hermes-a11y**, **hermes-simplificador**, **hermes-fuente**, **hermes-duda**, **hermes-observabilidad**, **hermes-baileys** (WhatsApp channel, slice S4)

## Skills

The `hermes-*` skills are **not** in this repo. They come from Percy's personal store:

- On Percy's machine, Cursor loads them automatically.
- In a cloud agent they are at `/cursor/stores/user/skills/<skill>/SKILL.md` (delivered by *Sync Skills for Cloud Agents*). Before a Hermes role, read the matching skill from that folder. If it is missing, say so instead of improvising the role.

They are updated from the Orchestrator with `hermes-sync-skills.ps1 -Target local`, not from this repo. `hermes-doctor`, `hermes-iniciador` and `hermes-forjador` belong to Percy's machine and are not used here.

## Hermes Pipeline

Pipeline templates (APROBADO/REHACER comments, Automation prompts, Issue body) live in `.cursor/pipeline/`, and subagents in `.cursor/agents/`. The source of truth is the `hermes-orchestrator` repo. To update them:

```powershell
powershell -NoProfile -File <orchestrator-path>\scripts\hermes-sync-skills.ps1 -Target repo -Path <this-repo-path>
```

Then commit `.cursor/pipeline` and `.cursor/agents`. If an Automation prompt changed, paste it again in cursor.com/automations.

## Profile

- **personal** → GitHub `YOUR_OWNER`, remote `git@github.com:YOUR_OWNER/whatsapp-ui-template.git`
- Folder: your local path

## Secrets

`orchestra.json` lists **names** of variables. Values: local `.env` (gitignored) and Cursor dashboard for cloud agents. Never in the repo.

Supabase projectRef: your projectRef.

Worker VM: GCP `e2-micro` per sector — configure in `orchestra.json` and `docs/runbook-whatsapp-vm.md` (Always Free: `pd-standard`, no snapshots).

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->