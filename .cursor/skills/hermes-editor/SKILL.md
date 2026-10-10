---
name: hermes-editor
description: >-
  Runs the human+agent loop on editable HTML documents: open shell with a mini
  rich-text toolbar, inline edit, selection comments, save as sibling *_editado
  via local server (Guardar = disk write; Descargar = separate), re-read and
  apply comments, export PDF from the edited HTML. Use when the user asks
  hermes-editor, “editar el informe/carta/deck a mano”, “abrir el editor”,
  “comenté el HTML”, “generá el PDF del editado”, or after generating HTML they
  want lightweight manual corrections without long prompt rounds.
---

# Hermes Editor

## Goal

Bajar fricción en retoches: el humano edita y comenta en el navegador; el agente relee el archivo, resuelve comentarios y exporta. Aplica a **cualquier HTML Hermes** (informes, cartas, textos, presentaciones). No rediseña el producto ni inventa números.

## Bootstrap

1. Read `.cursor/orchestra.json` if present (profile, local-only notes). Skill is on-demand (`role: null`).
2. Locate the document:
   - User path if given
   - Else last generated HTML for the job in progress
   - Prefer working copy if it already exists (see Naming)
3. Discover editor infra in the **current repo only** (do not invent commands):
   - README / `docs/` for “editor”, “editado”, “hermes-editor”, local server, PDF
   - `package.json` scripts (e.g. `editor`, `editor:*`, `edit`)
   - scripts under `scripts/` matching `*editor*`, `*hermes*save*`
   - If cwd is **informes-contables** (or the user names that pilot), use its shell/docs there
   - Elsewhere: **do not** assume that pilot’s paths exist
4. If no shell + local save endpoint: do **not** invent a stack in silent mode. Draft/update a short contract → **hermes-arquitecto** if open → **hermes-escritor**. When implementing the shell, honor **Shell UX contract** below.
5. Cloud VMs without local browser/server: still manage files and comments on disk; say one-click Guardar/PDF needs a **local** run on the user’s machine.

## Conventions (stable)

| Concept | Rule |
| --- | --- |
| Original | Generator output (script may overwrite) |
| Working copy | Sibling named by **Naming**; **never** silent overwrite of original on Guardar |
| Edit mode | **Both**: free text in the document **and** selection comments for the agent |
| Mini text editor | Shell includes a small **rich-text format bar** so the human can fix typography without only using raw keystrokes or external apps (see Shell UX) |
| **Guardar** | Writes the working copy **on disk** via the project’s local save endpoint. Must **not** download a file. |
| **Descargar** | Separate control. Download / blob fallback only. Never label download as “Guardar”. |
| Export v1 | PDF from the **edited** HTML; other formats optional |
| PDF chrome | Do **not** print comment UI / format bar (`@media print` hide chrome) |
| Comments panel | Must **not** cover document text — reflow layout so content and panel share space (see Shell UX) |

### Naming

- Original `path/name.ext` → working copy `path/name_editado.ext` (same directory, same extension).
- If the path already ends with `_editado` before the extension, **work in-place** (do not create `…_editado_editado`).
- Seed: if working copy missing, copy original → working copy, then open that.

### Comment model (v1)

Store comments **inside** the HTML (portable). Default when the project has no own format:

```html
<script type="application/json" id="hermes-comments">
{
  "version": 1,
  "items": [
    {
      "id": "c1",
      "quote": "selected span text",
      "body": "agent instruction",
      "status": "abierto",
      "author": "optional",
      "createdAt": "optional ISO-8601"
    }
  ]
}
</script>
```

- `status`: `abierto` | `resuelto` only.
- Prefer `quote` (exact selected text). Shell range/selector attrs are fine alongside `quote`.
- If the project shell already uses another in-HTML schema, **follow it**; never rewrite storage to v1 unprompted.
- Do not invent comments the human did not leave.

### Shell UX contract (when implementing or auditing the shell)

1. **Chrome toolbar** (actions; Spanish OK):
   - **Guardar** → `POST` (or project-equivalent) to the local save API → write `*_editado` on disk → status “guardado en disco”. On failure: explain need for server; **do not** silently download.
   - **Descargar** → download the HTML. Optional; never the primary save path.
   - Comentar selección / Comentarios / Imprimir·PDF as the product already does.
2. **Mini text editor** (format bar on the editable body — required for new shells; add when improving an existing bare `contenteditable`):
   - Scope: **lightweight** inline formatting inside the document region (`contenteditable` is enough; no full CMS, no multi-user collab, no cloud editor deps unless the repo already has one).
   - Minimum actions (apply to current selection / caret in the doc):
     - **Negrita**, **Cursiva**, **Subrayado** (optional)
     - **Lista con viñetas**, **Lista numerada**
     - **Párrafo** vs **Título** (h2/h3 is enough; do not force h1 over the product title)
     - **Enlace** (prompt URL or unlink) if the document type uses links
     - **Quitar formato** / clear markup on selection
   - UX: format controls live on or next to the chrome toolbar (or a compact second row); only affect the document body, never the comments JSON / toolbar itself (`contentEditable=false` on chrome).
   - Implementation default: `document.execCommand` / `beforeinput` on a known `#doc` (or project root) is fine for v1. Prefer semantic tags (`strong`, `em`, `ul`/`ol`, `h2`/`h3`, `a`) that match the surrounding HTML; avoid dumping unrestricted paste from Word with huge `<span style>…` when a simple paste-as-plain option is easy.
   - Keyboard: keep browser defaults (Ctrl/Cmd+B, I where available); do not fight them.
   - Do **not** ship TipTap/ProseMirror/Quill “full suite” for this skill unless the product already depends on them — mini bar only.
3. **Comments panel layout**: fixed overlay that **covers** the document is **wrong**. Open panel must:
   - push / shrink the document (`body.comments-open` + `margin-right` / grid / flex side-by-side), **or**
   - otherwise guarantee every line of body text remains readable without scrolling under a drawer.
   - Provide a clear close control on the panel.
4. **Save endpoint safety**: only allow write of names matching `*_editado.html` (or project doc-root siblings); never overwrite generator originals via Guardar.
5. **Print/PDF**: hide chrome toolbar, format bar, and comments panel; never bake editor chrome into the PDF body.

## Local server & access (explicit)

**Problem:** browsers opened via `file://` cannot write the real file on disk. “Guardar” that only downloads is a broken UX for this skill.

**Expected loop for the human:**

1. Agent starts the repo’s documented editor server (if present).
2. Agent opens / tells the user the **http://** URL of the **working copy** (not a bare disk path, unless the shell is disk-only).
3. Human edits and comments in that page.
4. Human clicks **Guardar** → file updates under the repo on disk.
5. Human tells the agent; agent **re-reads the path on disk**.

**What the agent must do when running procedure A:**

| Step | Agent action |
| --- | --- |
| Find command | From package scripts / README / `scripts/*editor*` (example shape: `npm run editor:…` or `python scripts/…_server.py`). If none → Bootstrap §4. |
| Start server | Run the documented command in the repo root; wait until it listens (or report failure). |
| Give access | Paste the **exact open URL** for the working copy (e.g. `http://127.0.0.1:<port>/…_editado.html`). Prefer host `127.0.0.1` over vague “localhost only” text without port/path. |
| State limits | In one line: **Guardar** needs this server; double-click / `file://` only allows **Descargar** (or read-only browse). |
| Stay available | Keep the server process instruction visible in **Next** if the user will keep editing. |

**If the user already has the page open as `file://`:** tell them to switch to the http URL after starting the server; do not pretend Guardar worked without a disk write.

**Cloud:** cannot provide one-click Guardar on the user’s laptop; apply comments from the saved HTML if they used Descargar and re-uploaded/pasted path, or wait until they save locally.

## Procedure

### A — Open for human editing

1. Ensure a current HTML exists (project script / prior skill); seed working copy per Naming.
2. Resolve and start the local editor server if the repo has one (see **Local server & access**). If none → Bootstrap §4; disk-only agent edits still OK.
3. Tell the user, in this order:
   - **URL exacta** (or path if no server yet)
   - What **Guardar** vs **Descargar** do
   - Use the **mini format bar** for negrita/listas/títulos; comments for agent instructions (tone/structure larger than a keystroke)
   - **Guardar** after edits/comments; then ask the agent to apply remaining comments / PDF
4. Do **not** say “Guardá = descargá el HTML” unless the project still lacks a server and you are explicitly in Descargar-only fallback.
5. If the shell is still bare `contenteditable` without a format bar: when implementing/improving the shell, add the mini editor (Shell UX §2); do not tell the user to “paste into Word” for simple bold/list fixes.

### B — After human Save / “leé el editado”

1. Read working copy **from disk** (not only chat paste).
2. List **open** comments (id + quote + body). Restate intent in 1–3 bullets.
3. Apply: rewrite prose per comments; keep facts honest; leave human text edits unless asked to reverse.
4. Mark applied items `resuelto` (or project-equivalent); write the working copy again.
5. Ask once: promote shared boilerplate into the **generator script**? Only after user yes → **hermes-escritor**; never invent monto/cifra.

### C — Export

1. PDF from **edited** HTML only via a command the **repo documents** (shell button or CLI). Verify first; do not assume Playwright/Chrome/global tools.
2. If no export path: state the gap + exact command needed; do not invent tooling.
3. Confirm output path. Never replace the working copy with a data regen without asking.

### D — Regen from source data

1. Regenerating original is allowed; **do not delete** the working copy unless the user discards manual work.
2. If original and edited diverge: offer keep editado · rebase comments · start fresh from new original.

## Output contract

Closing message always includes:

1. **Working file** — full path of the working copy (or “still only original”).
2. **Open URL / server** — exact http URL if the shell is running, else the start command + gap, or “disk-only / file://”.
3. **Open comments** — count + one-line each, or “ninguno”.
4. **Actions taken** — edits / resolved / none.
5. **Export** — PDF path, or exact documented command / gap.
6. **Next** — only if relevant (how to open editor; promote to generator; arquitecto/escritor for missing shell).

## Done criteria

- Naming + no silent original overwrite
- **Guardar** = disk write; **Descargar** separate
- Mini format bar present (or gap called out when only auditing an old shell)
- Comments panel does not cover body text
- User received exact access URL or explicit server failure path
- Agent can list open comments, apply, mark resolved (Comment model v1 or project schema)
- PDF (if requested) from edited HTML without editor chrome
- Regen never wipes manual work without ask

## Forbidden

- Calling “Guardar” any flow that only downloads the file
- Shipping bare `contenteditable` as a *new* shell without a mini format bar
- Pulling in a full page-builder / CMS / multi-user collab stack for this job
- Building a comments drawer that hides document text without reflow
- Overwriting the generator original as the only Save target
- Inventing financial or factual figures to “improve” wording
- Embedding secrets or real sensitive amounts into git without project rules
- Assuming CLI/browser/PDF/server tools without repo docs or verify-first
- Leaving the user with “open the HTML somehow” without URL or start command when a server exists
- Building a multi-user SaaS editor or cloud auth stack for this job
- Redesigning the whole document system → **hermes-arquitecto**
- Implementing missing shell without contract when choices are open → **hermes-arquitecto** then **hermes-escritor**
- README product docs only → **hermes-documentador**
- Tone-only rewrite with no file/comments workflow → **hermes-humanizador**
- Full slide redesign → **hermes-presentador** (then re-enter editor for polish)
