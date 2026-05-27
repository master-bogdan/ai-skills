# AGENTS.md Contract

`AGENTS.md` is the primary navigation document for both humans and AI agents.

## Required Sections

- `Purpose`
- `Start Here`
- `Repo Map`
- `Canonical Docs`
- `Task Routing`
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
