---
name: hermes-seguridad
description: >-
  Security pass for Hermes apps: Supabase RLS, API routes, secrets, and GAS
  permission surfaces according to orchestra.json, plus a short OWASP-oriented
  sweep (auth abuse, uploads, headers, response trim). Use when auditing
  security, RLS, before production, hermes-lanzamiento, or when the user asks
  for a security review.
---

# Hermes Seguridad

## Goal

Find authz/authn and secret-handling issues. Adapt checklist to enabled services. Report findings and residual risk — never claim “secure”.

## Preconditions

- Read `.cursor/orchestra.json`. If `roles.security` is false, ask first.
- Read architecture auth section.
- **State the threat model** before auditing: which actors are in scope (anonymous internet, authenticated user of another tenant/role, leaked anon key holder) and which are out (e.g. an attacker with the owner’s machine, dashboard, or cloud account). Findings and residual risk refer to that scope.
- **Never read secret values** while auditing: check presence, names, gitignore, and where they are referenced. Do not open `.env*`, `~/.ssh`, key files, or credential stores to inspect contents; do not print values in the report.
- Use Supabase MCP (`list_tables`, advisors, SQL read-only) when Supabase enabled — prefer advisors over guesswork. If MCP is unavailable (common on a cloud agent VM), audit migrations and policy files in the repo and say which checks could not be run live.

## Checklist by service

### Always (do first)

- Secrets not in git; `.env` gitignored; no values in docs/commits
- If secrets were ever pushed: rotate; deleting the file alone is not enough
- No service-role keys or privileged tokens in frontend / public bundles
- Dangerous defaults called out (open buckets, `USING (true)` writes, public web apps)
- Authn vs authz: prove who the caller is **and** what they may do (server/Edge for privileged ops)
- **Fail closed:** when an auth, role, entitlement, or signature check errors, times out, or gets malformed input, the code denies. Any `catch` / fallback that grants access or skips the check is **High**. Only exception: a time-boxed grace written in the architecture (e.g. **hermes-kill-switch** `grace_days`, which applies only on unreachable server after a prior `active`, never on `suspended` or malformed responses) — audit that the code matches those limits
- Obscurity is not auth: an unguessable URL, a hash, or a token in the query string does not replace a server-side check (webhooks need signature verification, not just a secret path)

### Supabase enabled

- RLS enabled on user data tables
- Policies: least privilege; no open writes on sensitive tables
- Financial / attendance / personal data: explicit deny for anon where required
- Storage bucket policies if used
- Edge functions: auth verification on privileged paths
- Passwords: if Supabase Auth owns them → **N/A** (do not invent custom hashing). Custom credential stores → hash + never log plaintext
- App-level encryption of columns: only if architecture stores secrets beyond Auth/Vault; else residual or N/A

### Vercel / frontend enabled

- Server/client key split (publishable/anon only in client)
- CORS and OAuth callback URLs match environments
- Preview deploy env assumptions (weaker secrets?) called out
- Production / public host: HTTPS (Vercel default). Do **not** require local HTTPS — Hermes DX is `http://*.local:<port>`
- Security headers present or residual noted (at least frame/XSS/content-type basics via Next/Vercel config or middleware)
- Custom session cookies (if any beyond Supabase SSR): HttpOnly, Secure on HTTPS, SameSite appropriate

### clasp / GAS enabled

- OAuth scopes minimal
- `ScriptApp` / Drive / Spreadsheet permissions justified
- No hardcoded tokens in `.gs` / `.js`
- Web app deploy access (anyone vs domain) matches architecture

### Supabase disabled + GAS only

- Do not insist on Postgres RLS; focus on Sheet protection, webapp access, and secret PropertiesService

### Secondary: OWASP-oriented sweep (after stack checklist)

Quick pass for the touch surfaces of this change only:

1. **Injection (Hermes):** search the diff/repo for SQL/shell/template concatenation with user or request input; dynamic SQL inside RPCs; Edge/API routes that string-build queries. Typed Supabase client filters (`.from().eq(...)`) alone → report **Injection: low residual** (internet scanners may still hit public URLs; that is not the classic blog SQLi hole). Any string-built SQL/command path → **Critical/High** with file path.
2. **Broken auth / session** — missing server-side session check on privileged routes; weak cookie flags when cookies are app-owned.
3. **Sensitive data exposure** — secrets/PII in logs, client bundles, URLs; API responses that return more fields than the UI needs (**trim** selects / serializers).
4. **Broken access control** — IDOR, role skip; **field tampering / mass assignment** (client can set `role`, `amount`, `owner_id`, etc. without allowlist).
5. **Misconfiguration** — debug flags, open CORS, missing prod HTTPS/headers.
6. **Deps** — vulnerable/outdated only with evidence (lockfile advisory, CI scan, or known CVE in scope). No tool → list as residual, do not invent “scanned clean”.
7. **XSS** — escape/sanitize any new HTML/Markdown/user content rendering.
8. **Insecure design** vs architecture trust boundaries.
9. **Input validation** — Route Handlers / Edge: schema, types, size limits on body/query (not only DB constraints).
10. **Auth abuse** — rate limit or equivalent throttle on login/signup/reset when those surfaces exist (Hobby-realistic: middleware, provider limits, or documented residual). Bot/CAPTCHA only if public abuse surface is real — optional hardening, not a default Blocker.
11. **Uploads** — if Storage/upload paths exist: allowlisted MIME/extension, size cap, authz + storage policies (not “bucket exists”).

## Output format

```markdown
## Security summary
## Threat model (in scope / out of scope)
## Critical
## High
## Medium
## Hardening ideas
## Residual risk
## Injection path checked: yes (paths…) | N/A (reason)
## Hardening sweep: headers | cookies | rate-limit/auth | uploads | response-trim | deps — each: ok | finding | residual | N/A
## Checks not run live (MCP/CLI missing)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “RLS later; still building” | Data is wrong the moment policies are open; flag as Critical if user data exists |
| “Service role in the browser is just for MVP” | Service role in client is Critical; use anon key + RLS or server routes |
| “No MCP so I can’t audit” | Audit migrations/policies in repo and list residual risk — don’t skip |
| “OWASP is enough without Hermes stack” | Hermes stack order first (RLS/GAS/scopes); OWASP is secondary |
| “Secrets in the commit history are fine if removed now” | Rotate; removal alone is not enough if already pushed |
| “Usamos Supabase así que no hay SQL injection” | Typed Data API + params help; they do not forgive raw SQL, open RLS, or privileged keys in the client |
| “Local is HTTP so the app is insecure” | DX `*.local` is HTTP by design; require HTTPS on the public/prod host, not on laptop hosts |
| “No CAPTCHA = Critical” | Bot protection is optional hardening; rate-limit/auth abuse and open signup residuals are enough unless architecture demands it |
| “If the entitlement API is down, let users in so nothing breaks” | Fail-open turns an outage into an authz bypass; deny unless the architecture defines a time-boxed grace (kill-switch `grace_days`) and the code enforces its limits |
| “I’ll open .env to confirm the key is right” | Presence and name are enough for an audit; reading values leaks them into logs and transcripts |
| “Nobody can guess this URL” | Obscurity is not a control; add a server-side check or signature |

## Red flags

- “Looks secure” with empty Critical/High and no residual risk
- Policies `USING (true)` / `WITH CHECK (true)` on writes without architecture justification
- Frontend bundle imports service role or private VAPID key
- Claiming full Supabase live audit without MCP/advisors when only reading files (mislabel)
- Claiming dependency scan clean without tool/evidence
- Requiring local Caddy/HTTPS against Hermes DX contract
- `catch` / default branch that returns “allowed” on an auth or entitlement error outside a documented grace window
- Secret values (or partial values) quoted in the report or transcript
- Report with no stated threat model, so “secure against whom” is unanswerable

## Verification

- [ ] `orchestra.json` services drove which sections ran
- [ ] Threat model section names in-scope and out-of-scope actors
- [ ] Auth/entitlement error paths checked for fail-closed (paths cited, or N/A)
- [ ] No secret value appears in the report
- [ ] Each Critical/High names a path, policy, or code location
- [ ] Injection path checked line present (`yes` with paths or `N/A` with reason)
- [ ] Hardening sweep line present (each axis ok | finding | residual | N/A)
- [ ] Unrun live checks listed explicitly
- [ ] Residual risk section present (even if “low for current scope”)

## Rules

- Propose fixes; apply only if user asks.
- Free-tier multi-account: warn if orchestra `accountNote` is empty.
- Ship gate / pre-merge consolidate → **hermes-lanzamiento**; bugs without security angle → **hermes-revisor** / **hermes-depurador**.
