---
name: generate-repo-docs
description: Create or update a repo's full documentation set — architecture, flows, patterns, models, onboarding, code quality scorecard, and AI navigation files. Use when bootstrapping repo docs, refreshing stale docs, or asked to document a codebase.
---

Create or update a repo's canonical documentation set from the codebase.

## What this skill generates

**AI-first files** — terse, structured, routing-focused, machine-parseable:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Primary AI navigation — task routing, entry points, run commands, working rules |
| `.github/copilot-instructions.md` | AI review guidance — severity labels, comment structure, fix prompts |
| `CONTEXT.md` | Domain language glossary — canonical terms, relationships, ambiguities resolved |

**Human-first files** — narrative, friendly, explain the why, include mental models and flow walkthroughs:

| File | Purpose |
|------|---------|
| `README.md` | Project overview, setup, usage |
| `docs/architecture.md` | System structure, request lifecycle, data flow, key design decisions |
| `docs/how-system-works.md` | Real execution flows traced through actual files and functions |
| `docs/models.md` | Domain entities, transport shapes, layer transformations |
| `docs/patterns.md` | How code is structured — layers, conventions, smells |
| `docs/onboarding.md` | First-hour guide: setup, verification, first safe change |
| `docs/code-standards.md` | Coding rules specific to this repo |
| `docs/code-quality-scorecard.md` | Review rubric + current dated assessment with grades and findings |

## Required input

The user must provide the target repo path with the skill invocation.

Do not infer the target repo path from the current working directory. If the
path is not provided, stop and ask for it before doing any inspection.

## Hard stops

Stop and tell the user what is missing if any of these are true:

- the repo path is missing
- the repo path does not exist
- the path is not a git repo

## Workflow

1. Inspect the repo before proposing any doc changes.
2. Use current code and executable repo config as the source of truth.
3. Use existing docs as supporting context only.
4. Load [references/canonical-docs.md](references/canonical-docs.md) for the canonical file set, ownership rules, plan statuses, and rename mapping.
5. Load only the per-doc reference files needed for the docs you are creating or updating.
6. Every time the skill is invoked, audit the full canonical doc set plus existing non-canonical docs.
7. Decide from repo inspection what to create, update, rewrite, rename, preserve, skip, or mark as needs confirmation.
8. Produce a terse pre-write plan using only `action path` lines. Valid actions are listed in `references/canonical-docs.md`.
9. The pre-write plan must account for every canonical doc and every preserved or renamed non-canonical doc.
10. Ask for confirmation before writing.
11. After confirmation, create, update, rewrite, rename, preserve, or skip files according to the plan.

## Inspection baseline

Before drafting docs, inspect at least:

- root files such as `README.md`, `package.json`, build config, lint config, and test config when present
- existing `docs/`
- main source entrypoints
- top-level feature or module folders
- repo scripts for setup, build, lint, and test

Read deeply — trace actual execution paths, read service/handler/model files, follow imports. Surface-level inspection produces shallow docs.

## Audience split

Know the primary reader for each file before writing:

- `AGENTS.md` and `.github/copilot-instructions.md` — AI-first: terse, structured, routing-focused, machine-parseable
- All `docs/*.md` files — human-first: narrative, friendly, explain the why, include mental models and flow walkthroughs

Do not write `docs/*.md` files in the same dry style as `AGENTS.md`. A human should be able to read `docs/architecture.md` and understand the system without asking anyone.

## Content rules

- Write in plain English.
- Keep docs concise, practical, and repo-specific.
- Avoid marketing language and generic AI phrasing.
- Prefer concrete file paths and real commands over abstractions.
- Do not invent unsupported details.
- When evidence is missing, write `Needs confirmation`.
- Preserve extra non-canonical docs unless they are explicitly covered by the legacy rename mapping.
- Surface preserved extra docs in `AGENTS.md` under `Additional Repo Docs`.

## Decision Rules

Every canonical doc must be created or updated on every invocation — no exceptions. `skip` is not allowed for canonical docs.

After inspection, decide the action for each canonical doc:

- `create` when a canonical doc is missing
- `update` when a canonical doc exists and mostly fits but needs improvement
- `rewrite` when a canonical doc exists but is too stale, too thin, or off-contract
- `rename` when a legacy file matches an allowed mapping
- `preserve` when a non-canonical doc should remain as an additional repo doc

Do not ask the user to choose between `create`, `update`, and `rewrite`.
The skill must infer the right action from the repo state and then show it in the plan.

If the user asks for one specific doc, still audit the full canonical set. Keep
the plan complete, but do not write any changes until the user confirms the
specific planned actions.

## Rename rules

Auto-rename only the exact legacy mappings listed in [references/canonical-docs.md](references/canonical-docs.md).

After a mapped rename:

- update in-repo references to the old path
- remove the old file

Do not guess mappings for unknown docs. Preserve them as extra docs.

## Ownership

- `AGENTS.md` is fully generated and replaceable.
- `.github/copilot-instructions.md` is fully generated and replaceable.
- canonical `docs/*.md` files are full-file skill-owned.
- preserved extra docs remain untouched unless the user asks otherwise.

## Canonical doc generation

Use the matching reference file for each canonical doc:

- `AGENTS.md`: [references/agents.md](references/agents.md)
- `.github/copilot-instructions.md`: [references/copilot-instructions.md](references/copilot-instructions.md)
- `CONTEXT.md`: [references/context.md](references/context.md)
- `README.md`: [references/readme.md](references/readme.md)
- `docs/architecture.md`: [references/architecture.md](references/architecture.md)
- `docs/how-system-works.md`: [references/how-system-works.md](references/how-system-works.md)
- `docs/code-standards.md`: [references/code-standards.md](references/code-standards.md)
- `docs/code-quality-scorecard.md`: [references/code-quality-scorecard.md](references/code-quality-scorecard.md)
- `docs/patterns.md`: [references/patterns.md](references/patterns.md)
- `docs/models.md`: [references/models.md](references/models.md)
- `docs/onboarding.md`: [references/onboarding.md](references/onboarding.md)

## AGENTS.md expectations

`AGENTS.md` is the main repo navigation doc for both humans and AI agents. It should route common tasks toward the right files first, not duplicate the deeper docs line by line.

Always include real task-routing guidance such as:

- if changing X, read Y first
- if validating Y, run Z
- if changing an API contract, inspect the DTO or boundary files first

## Copilot instructions expectations

`.github/copilot-instructions.md` is review-focused, not a copy of `AGENTS.md`.

It should:

- reduce review noise
- focus on actionable findings
- define review labels and comment structure
- include AI fix prompts in each review comment template

## Write safety

- Preserve existing contracts unless the task requires a change.
- Prefer narrow diffs, but allow rewrites when the current file is off-contract or too stale to salvage.
- Verify renamed references after edits.
- Keep the pre-write plan terse.
- Do not write before user confirmation.
