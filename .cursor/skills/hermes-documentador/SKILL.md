---
name: hermes-documentador
description: >-
  Trigger: document, update README, ADR, docs after feature, onboarding guide.
  Documents Hermes projects with low cognitive load: README, usage, JSDoc/TSDoc,
  optional short ADRs. Use when docs lag features or the user asks to document.
---

# Hermes Documentador

## Goal

Make the project usable by future-you and by other agents. Prefer accurate short docs over essays. Lead with the answer; capture the **why** of notable post-contract decisions without cloning `docs/architecture.md`.

## Preconditions

- Read `.cursor/orchestra.json`; honor `roles.documenter`.
- Skim `docs/architecture.md` and current README.

## Decision Gates

| Situation | Action |
| --- | --- |
| Setup / enablement path missing or stale | Update README first |
| Post-contract decision with long-lived consequences | Short ADR under `docs/adr/` |
| Doc feels dense or review-hostile | Apply cognitive-load shape below; do not add essay padding |
| Design drift vs architecture | Flag → **hermes-arquitecto**; do not silently rewrite the contract in README |

## What to update

1. **README.md** — what it is, setup (clone, env, link supabase/vercel/clasp), scripts, profile note (personal vs acebal)
2. **docs/** — only if architecture or runbooks need it (`docs/runbook.md` for ops)
3. **ADRs (optional)** — for a discrete decision *after* the architecture was approved that does **not** deserve reopening the full contract: short file under `docs/adr/` (e.g. `docs/adr/001-short-title.md`) with Context / Decision / Consequences. Do **not** ADR every feature.
4. **Code comments** — JSDoc/TSDoc on exported functions/modules touched; no noise on trivial lines
5. **AGENTS.md** — keep service list and order of roles in sync with orchestra.json

## Cognitive-load rules

- **Lead with the answer** — decision, action, or outcome first; context after.
- **Progressive disclosure** — happy path → details → edge cases → links.
- **Chunking** — small sections; short flat lists; one job per heading.
- **Recognition over recall** — tables, checklists, templates beat prose to memorize.
- **Review empathy** — for PR/review notes: what to read first, what is out of scope, how to verify.

Default shape when writing or rewriting a guide (unless the repo already has a stronger template):

```markdown
# <Outcome-oriented title>

<One paragraph: what changed / who it helps / why it matters.>

## Quick path
1. <First action>
2. <Second action>
3. <Verification or expected result>

## Details
| Topic | Decision |
| --- | --- |
| <area> | <concise> |

## Checklist
- [ ] <Reader can confirm this>

## Next step
<Link or action that continues the workflow.>
```

## Rules

- Never put real secrets in docs; use placeholders.
- If clasp-only project, document `clasp push` / Apps Script deploy, not Vercel.
- If Supabase enabled, document migrations workflow briefly.
- Match language of the repo (Spanish if existing docs are Spanish).
- Architecture remains the design source of truth; README points to it. ADRs supplement, they do not replace.

## Output tips

- Prefer diffs to README sections over wall-of-text rewrites.
- List files touched in the finish note.

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “Code is self-documenting” | Future agents (and you) need setup + service enablement path |
| “ADR for every PR” | Only post-contract decisions with long-lived consequences |
| “Paste secrets into README for convenience” | Names only in `.env.example`; never values |
| “More background makes it clearer” | Lead with the quick path; park lore in Details or skip it |

## Red flags

- Secrets or connection strings in docs
- Documenting Pro-only setups as free defaults
- README contradicts architecture without flagging the drift → **hermes-arquitecto**
- Wall-of-text with no Quick path / checklist for a procedural guide

## Verification

- [ ] README setup path matches enabled services only
- [ ] No secret values in any doc touch
- [ ] If ADR written: context + decision + consequences present
- [ ] Architecture still linked as design source of truth
- [ ] New/rewritten guides lead with answer or Quick path (or cite existing stronger template)

## Done criteria

- README has setup path for enabled services only
- Architecture still the source of truth for design; README points to it

## Forbidden

- Rewriting the product design in README instead of architecture
- Long essays that do not change setup or ops
- Security claims without → **hermes-seguridad** findings
