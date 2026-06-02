# AGENTS.md Contract

`AGENTS.md` is the primary navigation document for both humans and AI agents.

## Required Sections

- `Purpose`
- `Start Here`
- `Repo Map`
- `Canonical Docs`
- `Task Routing`
- `Ask Before Guessing`
- `Working Rules`
- `Verification`
- `Change Safety`
- `Additional Repo Docs`
- `Needs Confirmation`

## Section Guidance

### `Purpose`

- one short paragraph
- what the repo is for
- what kind of work happens here

### `Start Here`

- first files to read
- shortest path to understanding the repo

### `Repo Map`

- top-level folders or modules
- one-line purpose for each

### `Canonical Docs`

- list each canonical file with one-line purpose

### `Task Routing`

Use concrete routing rules. Prefer patterns like:

- if changing X, read Y first
- if debugging Y, inspect Z before editing
- if changing a contract, inspect the boundary files first

This is one of the highest-value sections. It must use real paths from the repo.

### `Working Rules`

- repo-specific operating rules
- where contracts live
- how to avoid changing the wrong layer

### `Verification`

Split into:

- `Minimum Checks`
- `Full Checks`

Use real repo commands only.

### `Ask Before Guessing`

This section must be repo-specific. Identify the actual high-risk change categories from the inspected repo and list them here.

Include:

- when to ask (list repo-specific high-risk areas: API contracts, auth, tenant scoping, migrations, queues, integrations, etc.)
- when to proceed with a stated assumption (non-blocking, safe default exists)
- when to stop (blocking ambiguity with no safe default)
- a pre-change checkpoint format
- the exact question format

Pre-change checkpoint:

1. Understanding of the task
2. Assumptions
3. Files likely to change
4. Proposed approach
5. Blocking questions, if any

Ask a focused question before continuing when:
- the requested behavior is ambiguous
- there are multiple valid implementation paths with different tradeoffs
- the change affects repo-specific high-risk areas
- required environment variables, sample payloads, services, credentials, commands, or expected behavior are missing
- tests, migrations, rollout, or backwards compatibility expectations are unclear

If the question is blocking, stop and wait.

If the question is non-blocking, state the assumption, use the recommended default, and continue with the smallest safe change.

Use this exact question format:

```
I need one decision before I continue.

Question: <specific question>
Recommended default: <what I would choose and why>
Options:
1. <option A> — <tradeoff>
2. <option B> — <tradeoff>
```

### `Change Safety`

Include rules such as:

- inspect before editing
- preserve existing contracts unless the task requires change
- prefer narrow diffs
- update related docs when behavior changes
- verify references after renames
- do not invent facts

### `Additional Repo Docs`

- list preserved non-canonical docs worth surfacing
- keep this short

### `Needs Confirmation`

- unresolved or weakly supported points
- use only when evidence is missing

## Style

- plain English
- concise
- path-heavy
- low duplication with `README.md` and `docs/*.md`
