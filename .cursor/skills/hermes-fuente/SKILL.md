---
name: hermes-fuente
description: >-
  Grounds framework and API decisions in official documentation: verify, cite,
  and flag unverified claims for Next.js, Supabase, Vercel, GAS, Baileys, and
  other stack pieces. Use when implementing against an unfamiliar API, when
  free-tier limits are disputed, or when the user asks to source-check / citar
  docs before coding.
---

# Hermes Fuente

## Goal

Prevent invented APIs and fake free-tier rules. Every non-trivial framework claim should be **verified**, **cited**, or explicitly **unverified**.

## Bootstrap

1. Read `.cursor/orchestra.json` for enabled services.
2. List the claims or APIs under doubt (versions matter).
3. Prefer live docs over memory. When Context7 MCP is available, use it for library/framework/SDK/CLI/cloud docs: `resolve-library-id` → pick a High/Medium `/org/project` (version pin if the project has one) → `query-docs` with **one concept per query**. Prefer Context7 over web search for those docs. If Context7 or network is missing, use official sites or the provider’s own MCP; say so and mark claims `UNVERIFIED` when you cannot verify.
4. Do not rewrite architecture unless sources contradict it → then **hermes-arquitecto**.

## Procedure

1. **Extract claims** — endpoint shapes, limits, config keys, deprecated patterns.
2. **Source** — Context7 (when available), official docs, or provider MCP (e.g. Supabase for project advisors/RLS). Prefer current stable docs for the project’s version when known. Do **not** use Context7 for refactors, business logic, code review, or general programming concepts.
3. **Cite** — doc title + URL (or path) + what it supports.
4. **Apply** — update code or recommendations only under the verified subset.
5. **Flag** — anything still assumed: `UNVERIFIED:` with why (no network, no Context7/MCP, no version pin, conflicting sources).

## Output contract

```markdown
## Claims checked
## Verified (claim → source)
## Unverified (claim → risk)
## Code / advice changes
## Recommended pins (package/version if relevant)
```

## Common rationalizations

| Rationalization | Reality |
| --- | --- |
| “I know this API” | Models drift; for stack libs prefer Context7 or official cite |
| “Hobby limits changed probably” | Only state limits with a source or hermes free-tier hard rules already codified |
| “Stack Overflow is enough” | Secondary; Context7 / official docs win on APIs and quotas |
| “No Context7 so I skip sourcing” | Fall back to official sites or provider MCP; else mark UNVERIFIED |
| “Unverified is fine to ship” | Mark UNVERIFIED and do not present as fact |

## Red flags

- Concrete API snippets with no source after a fuente session
- Contradicting Hermes free-tier hard limits without an official citation
- Pasting secret keys from examples into the repo

## Verification

- [ ] Each coding recommendation has Verified or Unverified tag
- [ ] At least one primary source consulted when network/tools allow (Context7 if available, else official/provider docs)
- [ ] Unverified items cannot be described as certain in the summary
- [ ] If Context7 was unavailable, the report says so (not silent skip)

## Done criteria

- Writer/architect has a citable basis or explicit risk list
- No secret values copied from samples into project docs as real

## Forbidden

- Implementing large features here — hand back to **hermes-escritor**
- Using unofficial random gists as sole authority for security-critical paths
