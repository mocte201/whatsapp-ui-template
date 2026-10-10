---
name: hermes-baileys
description: >-
  Ships the WhatsApp channel via Baileys for a Hermes project end to end:
  audits what the repo already has (tables + grants, connect/disconnect/status/
  send-test APIs, QR settings UI, Node worker), writes only the missing pieces,
  then deploys the worker as a persistent PM2 process on the project's Oracle
  VM. Use when the user asks for WhatsApp, Baileys, QR de WhatsApp, avisos o
  recordatorios por WhatsApp al paciente/cliente; when an existing worker is
  down, the QR never appears, or messages stay queued in the outbox; or when
  the phone shows "Esperando el mensaje" / waiting for this message and never
  decrypts.
---

# Hermes Baileys

## Goal

Leave WhatsApp actually sending **and decryptable on the recipient phone**: repo code complete, worker alive on the VM, verified `connected` session, and a test message that the user confirms readable (not stuck on “Esperando el mensaje”). Refuse Meta Cloud API migrations, sharing one session between products, and any attempt to run Baileys on serverless (Vercel) — it needs a long-lived socket.

## Bootstrap

1. Read `.cursor/orchestra.json`: Supabase `projectRef`, `secrets`, and the `whatsappVm` block (`host`, `user`, `appsPath`, `sshKeyName`, `pm2Name`). If `whatsappVm` is absent, ask the user for those values and offer to write the block; never store key material, only the key file name.
2. Read `docs/architecture.md`. If the WhatsApp channel is not in the approved contract, stop → **hermes-arquitecto**.
3. Probe the environment before promising anything: try a non-interactive SSH to the VM. No key or no route (typical for a cloud agent) means **repo-only mode** — do Fase A/B and emit the Fase C runbook for the user to run locally.
4. Confirm the product gets its **own** WhatsApp number, auth dir and PM2 process. Reusing another product's session is a hard stop.

## Procedure

### Fase A — Inventory

Report which of the five pieces exist, before writing anything:

| Piece | Look for |
| --- | --- |
| Tables | migration creating `whatsapp_connections` + `whatsapp_outbox` |
| Grants | `grant ... to service_role` on WA tables **and** every table the worker SELECTs (e.g. `appointments`, `patients` for reminders) — not only `authenticated` |
| APIs | `connect`, `disconnect`, `connection`, `send-test` routes |
| UI | settings screen polling status and rendering the QR |
| Worker | `workers/whatsapp-baileys/` with `package.json` + `src/`; dependency must be **Baileys ≥ 7** (LID) — package name `baileys` **or** `@whiskeysockets/baileys`, never 6.x / dist-tag `legacy` |

### Fase B — Write only what is missing

- **Tables:** `business_id` keyed to the tenant entity; `whatsapp_connections` (status, `qr_payload`, phone, `last_error`) and `whatsapp_outbox` (`to_e164` with E.164 check, body, status, attempts). Enable RLS, add tenant policies, and grant table privileges to **both** `authenticated` and `service_role`.
- **APIs:** connect flips status to `qr_pending`; disconnect to `disconnected`; connection returns status + QR for polling; send-test enqueues one row. Restrict connect/disconnect to the owner role.
- **UI:** poll status while `qr_pending`, render the QR, show `last_error`, and state that the worker runs on the VM.
- **Worker (required socket shape):**
  - **Version axis (not package name):** pin a concrete **≥ 7.0.0-rc** release (as of 2026-08, npm `latest` is still RC, e.g. `7.0.0-rc14`). Accept `baileys` **or** `@whiskeysockets/baileys` at that pin. Reject any `6.x` / `legacy` (no PN↔LID; phone stuck on “Esperando el mensaje”). Upstream README may still show the scoped name — that is fine if the version is 7+.
  - **Runtime:** Node **≥ 20**; worker package is **ESM** (`"type": "module"`), or load Baileys via `await import(...)` from CJS. Confirm `node -v` on the VM before blaming Baileys.
  - Auth: `useMultiFileAuthState` (must persist `lid-mapping`, `device-list`, `tctoken` keys — wipe auth dir + re-scan QR when upgrading 6→7; 6.x creds are not reusable). Wrap keys in `makeCacheableSignalKeyStore`.
  - Do **not** call `fetchLatestBaileysVersion()` for the socket (**Hermes hard rule** — upstream `example.ts` still calls it; WA may advertise a protocol the pinned library cannot speak). Use the version bundled by the pin.
  - `getMessage` for retry receipts: cache sent payloads keyed by **message id only** (retry `key.remoteJid` is often `…:device@s.whatsapp.net` or `<lid>@lid`, not the JID you sent to). Store `sent.message` (real protobuf), not a reconstructed `{ conversation }`. Leave `enableRecentMessageCache` at its default (true) unless there is a measured reason to disable it.
  - Resolve destination with `onWhatsApp` **on phone numbers / PN JIDs only** before send (AR mobile `9` / non-canonical JIDs). Do **not** pass `@lid` into `onWhatsApp` (library rejects LIDs). Prefer JID helpers (`isLidUser`, `isPnUser`, `jidNormalizedUser`, `areJidsSameUser`) over string splits. For triage, `sock.signalRepository.lidMapping` and `lid-mapping-*` under the auth dir matter.
  - Optional `BAILEYS_LOG_LEVEL` (default silent) so Baileys' own `recv retry` / `message not available` lines can be turned on without drowning production logs. Own log on `getMessage` with `hit: true|false` helps triage.
  - Poll connections, one socket per tenant with `useMultiFileAuthState`, publish QR, drain `pending` outbox when `connected`, mark `sent`/`failed`. Guard against double-start (tick + soft reconnect).
  - **Outbox hardening:** tick mutex (no overlapping polls); atomic outbox claim (`update … eq status=pending` + `.select()` / skip if null); reclaim orphan `sending` rows not in this process's in-flight set back to `pending` (outbox often has no `updated_at`); soft disconnect must **not** flip `connected` → `qr_pending` while auth is still valid (only `last_error`); reminder appointment-read failures return to `pending` with **backoff** (~60s) so missing grants do not hot-loop.

Keep the enqueue helper separate from product flows so cancel/reschedule/reminder callers only pass phone + body.

### Fase C — Deploy on the VM

1. **Repo access.** Private repo means the VM needs a read-only deploy key: generate a dedicated key on the VM, add it to the repo's deploy keys, pin it in the VM SSH config with `IdentitiesOnly yes`, verify with a GitHub auth test.
2. **Code.** Clone into `<appsPath>/<repo>` (or `git pull`), then `npm install` inside `workers/whatsapp-baileys`. Confirm worker `package.json` / `node_modules/<pkg>/package.json` shows **≥ 7** (scoped or unscoped) and `node -v` is ≥ 20.
3. **Env.** Write the worker env file with `SUPABASE_URL` **identical** to the app's public Supabase URL, the `service_role` key of that same project, a `WHATSAPP_AUTH_DIR` unique to this product, and a log level. Transfer it as a file (`scp`), never as a command-line argument that lands in shell history. `chmod 600`.
4. **Process.** Source the env in the shell, then start PM2 with the product-specific name and the worker directory as cwd. Run `pm2 save`, and confirm PM2 resurrects on boot (`systemctl is-enabled pm2-<user>`).
5. **Neighbours.** List existing PM2 processes first and leave them untouched. Report — do not silently fix — any unrelated process found crash-looping.
6. **Remote shells.** Prefer `scp` a small script and run it on the VM over nested quoting (PowerShell/`ssh` quoting breaks heredocs and inline `node -e`).

### Fase D — Verify

1. Tail worker logs: a healthy start logs the auth dir and Supabase URL and then goes quiet. Any `42501` means missing grants, not a Baileys problem. Startup crash citing ESM/`ERR_REQUIRE_ESM` or Node engine → fix runtime before touching outbox.
2. Ask the user to hit Conectar in the app, scan the QR from the phone (WhatsApp → Dispositivos vinculados), and confirm the status turns `connected`.
3. Send a test message and confirm **delivery on the phone** (readable text). Outbox `sent` alone is not enough.
4. Triage signal: after a good send with Baileys 7 + LID mapping, **no** (or rare) `getMessage` / retry-receipt storms. Immediate multi-retry with `hit: true` still stuck on the phone → still encrypting against the wrong addressing layer (check package **version** ≥ 7 and `lid-mapping-*` under the auth dir).

## Known traps

| Symptom | Cause | Fix |
| --- | --- | --- |
| `permission denied for table whatsapp_*` (42501) | RLS policies exist but table privileges were granted only to `authenticated` | Grant to `service_role` too |
| Reminder/job logic treats live appointments as cancelled | Worker SELECTs `appointments`/`patients` without `service_role` grant; error misread as missing row | Grant SELECT to `service_role`; on read failure return job to `pending` with backoff, do not mark cancelled |
| QR never appears in the UI | Worker points at a different Supabase project than the app | Make both URLs identical; verify the key belongs to that project |
| Soft reconnect flashes QR in the UI | Close handler set status to `qr_pending` while multi-file auth is still valid | Keep `connected`; only patch `last_error` (“Reconectando…”) and `scheduleReconnect` |
| Outbox row stuck in `sending` | Crash mid-send; no drain path | Reclaim orphan `sending` (not in-process in-flight) → `pending` each tick / on boot |
| Duplicate WhatsApp sends | Overlapping `setInterval` ticks or non-atomic claim | Tick mutex + claim with `.eq(status,'pending').select()` |
| Worker starts then exits or ignores config | Worker reads `process.env` and does not load a `.env` by itself | Source the env file before `pm2 start` so PM2 captures it |
| Session lost on every restart | Auth dir inside a path that gets wiped, or shared with another product | Dedicated persistent `WHATSAPP_AUTH_DIR` per product |
| Messages queue but never send | No socket for that tenant, or status is not `connected` | Check connection row and logs before touching the outbox |
| Phone shows “Esperando el mensaje” forever | Recipient cannot decrypt; missing `getMessage`, **or** Baileys **6.x** (no PN↔LID) even with retries/`hit: true` | `getMessage` cache by **id**; pin Baileys **≥ 7** (either package name); wipe auth; re-scan QR |
| Retries logged but lookup always misses | Cache keyed by `remoteJid\|id`; receipt uses device JID or LID | Index cache by message id only; store `sent.message` |
| Protocol / Bad MAC / Stream Errored (ack) noise | Soft reconnects and inbound decrypt failures are common; outbound can still work | Reconnect on non-logout; do not chase every Bad MAC until outbound decrypt fails |
| `ERR_REQUIRE_ESM` / import failures | Baileys 7 is ESM-only; worker still CommonJS `require` | `"type": "module"` or dynamic `import()`; Node ≥ 20 |
| Worker dies on old Node | `engines.node` is `>=20` | Upgrade Node on the VM; do not pin 6.x to “make it run” |
| Installed `@whiskeysockets/baileys@6` while “using WhiskeySockets” | Package **name** is not the axis — **version** is | Move to `@whiskeysockets/baileys@≥7` or `baileys@≥7`; wipe auth + re-QR |
| Supabase CLI rejects the migration file | It refuses multiple statements per call | Send one statement per call, or push the migration file |
| Migration history drift blocks `db push` | Remote versions absent from the local directory | Apply the statements directly and report the drift; do not repair history unasked |

## Output contract

Write `docs/whatsapp-baileys.md`:

```markdown
# WhatsApp (Baileys) — <project>

## Estado
Worker `<pm2Name>` en la VM `<host>` · sesión: <connected | pendiente de QR>
Librería: <baileys | @whiskeysockets/baileys> <pinned-version> (must be ≥ 7; not 6.x)

## Piezas
| Pieza | Ubicación |

## Operación
- Ver estado / logs / reiniciar (comandos PM2)
- Reconectar: desconectar en la app, Conectar, escanear QR
- Ruta de la sesión guardada
- Tras major de Baileys (p. ej. 6→7): wipe auth + re-QR
- Runtime: Node ≥ 20, worker ESM

## Problemas conocidos
| Síntoma | Causa | Solución |

## No verificable desde el repo
<lo que depende del server o del teléfono>
```

Report separately, in chat: pieces written, deploy result, and the exact manual steps left for the user.

## Done criteria

- Inventory reported before any file was written
- Missing pieces implemented, including `service_role` grants on WA tables and any extra tables the worker reads
- Worker depends on Baileys **≥ 7** (either package name) with `getMessage` (id-keyed), `makeCacheableSignalKeyStore`, Node ≥ 20 / ESM, and no blind `fetchLatestBaileysVersion` for the socket
- Worker tick is serialized; outbox claim is atomic; orphan `sending` rows are reclaimed
- Worker online under its own PM2 name, saved, with its own auth dir and number
- Logs clean of permission / engine / ESM errors; QR scanned and status `connected`; test message **confirmed readable on the phone**
- `docs/whatsapp-baileys.md` written with real package name + pin; unverifiable facts (server state, phone) labelled as such
- In repo-only mode: runbook emitted and the user told to run it locally

## Forbidden / handoffs

- Inventing host, IP, key names or server state — read `orchestra.json` or ask
- Printing secret values into logs, commands or docs; secret **names** only
- Touching another product's PM2 process, auth dir or WhatsApp number
- Shipping or “fixing” with Baileys **6.x** / `legacy` when LID/decrypt symptoms are present — upgrade to **≥ 7** (either package name) instead of stacking 6.x workarounds
- Rejecting `@whiskeysockets/baileys@7+` solely because the skill once preferred the unscoped name — version is the gate
- Calling `fetchLatestBaileysVersion` “because the official example does” — Hermes pin wins
- Repairing Supabase migration history or applying unrelated pending migrations without approval
- Running Baileys on Vercel or switching to Meta Cloud API — that is a contract change → **hermes-arquitecto**
- Broader RLS/secrets audit → **hermes-seguridad**; free-tier and memory/cost tuning → **hermes-optimizador**; API claim refresh → **hermes-fuente**

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “README says `@whiskeysockets/baileys`, so 6.x is fine” | README install line is not a version pin; LID needs **≥ 7** |
| “Unscoped `baileys` is mandatory; scoped 7 is wrong” | Either package name at ≥ 7 is OK; reject 6.x only |
| “Official example uses `fetchLatestBaileysVersion`” | Hermes hard rule: use the bundled version of the pin |
| “Phone stuck waiting — add more 6.x retries” | Upgrade to ≥ 7, wipe auth, re-QR; then verify `getMessage` hits |
| “Node 18 is close enough” | Baileys 7 declares `engines.node >= 20`; fix the runtime |
| “Outbox says `sent`, so we are done” | Done only when the user confirms readable text on the phone |
| “Cloud agent cannot SSH — skip the worker” | Repo-only mode: finish Fase A/B and emit Fase C runbook; do not pretend deploy happened |

## Red flags

- `package.json` / lockfile shows `@whiskeysockets/baileys@6` or any `6.x` while decrypt fails
- Worker uses `require('baileys')` without dynamic import on an ESM package
- Socket created with `version: await fetchLatestBaileysVersion()`
- `getMessage` keyed by `remoteJid|id` or returns `{ conversation: body }` instead of stored `sent.message`
- Soft-close path writes `qr_pending` while multi-file auth still exists
- Docs claim “baileys 7” without recording the concrete pin and package name

## Verification

After the procedure, confirm with **evidence** (command output, file path, log line — not “seems fine”):

- [ ] Inventory table was reported **before** any write (chat evidence)
- [ ] Worker dependency shows Baileys **≥ 7** (`npm ls` or `node_modules/.../package.json` version)
- [ ] VM or local runtime: `node -v` ≥ 20 (or repo-only runbook states the requirement)
- [ ] Socket code has `getMessage` (id-keyed) + `makeCacheableSignalKeyStore` and **no** `fetchLatestBaileysVersion` for the socket
- [ ] No `42501` on WA / reminder tables in worker logs (or grants added with migration/SQL evidence)
- [ ] User confirmed QR → `connected` **and** a test message readable on the phone (or labelled unverifiable + runbook left)
- [ ] `docs/whatsapp-baileys.md` exists with package name, pin, PM2 name, auth path
