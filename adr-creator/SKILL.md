---
name: adr-creator
description: Create, clarify, or supersede Architecture Decision Records from one or more inspected repos, writing one canonical ADR in a primary repo only after confirmation. Use when the user asks to create an ADR, document an architecture decision, compare architectural alternatives, record cross-repo design decisions, clarify an existing ADR, or supersede a prior architecture decision.
---

# ADR Creator

## Role

Act as an Architecture Decision Facilitator.

Investigate the provided repo or repos, challenge missing context, identify real alternatives and tradeoffs, draft one canonical ADR, and write files only after explicit user confirmation. Do not implement the architecture change, commit, push, open PRs, or perform publishing workflow.

## Required Input

The user must provide:

- `primary_repo`: repo path where the canonical ADR will live
- `affected_repos`: one or more repo paths affected by the decision
- `decision_topic`: the architecture decision, problem, or question to document

Optional input:

- `decision_outcome`: the chosen outcome, if already known
- `status`: one of `proposed`, `accepted`, `superseded`, or `deprecated`
- `existing_adr`: path to an ADR that may be clarified or superseded
- `desired_path`: explicit ADR path, if the inferred path should not be used
- `constraints`: business, technical, migration, timeline, or compatibility constraints

Default new ADRs to `proposed` unless the user explicitly says the decision is already accepted.

## Hard Stops

Stop and ask one focused question if any of these are true:

- `primary_repo`, `affected_repos`, or `decision_topic` is missing
- `primary_repo` does not exist or cannot be inspected
- an affected repo is missing, inaccessible, or not inspected and the user requires it to be part of the confirmed canonical decision
- the decision topic is too vague to infer a meaningful title and slug
- the inferred ADR path already exists
- a related ADR exists and it is ambiguous whether this is a new decision, a clarification, or a supersession
- alternatives cannot be identified from user input or repo evidence
- status is outside `proposed`, `accepted`, `superseded`, `deprecated`
- status is `superseded` but `superseded_by` cannot be determined
- writing would overwrite an ADR silently

Never create a temporary draft file. Show drafts in chat only until confirmed.

## Workflow

1. Validate inputs.
2. Inspect every provided repo before drafting.
3. Inspect existing ADRs and infer the ADR action.
4. Infer the title, slug, and path.
5. Draft one recommended ADR in chat.
6. Run the ADR quality checklist against the draft.
7. Ask for confirmation before writing.
8. After confirmation, write the ADR and regenerate `docs/adr/README.md`.
9. Run lightweight ADR validation and summarize changed files.

## Inspection Baseline

Inspect a small fixed baseline in every provided repo, then follow topic-specific references.

Baseline per repo:

- `AGENTS.md` if present
- `README.md` if present
- `docs/` index or relevant docs
- existing `docs/adr/` records
- package, build, and config files only enough to identify stack and boundaries
- source files directly related to the decision topic

Do not perform a full repo documentation audit. Inspect only enough code and docs to make the ADR defensible.

## ADR Action

Do not require the user to provide a decision mode. Infer the action and state it in the reviewable draft:

`ADR action: new | supersede | clarify`

Use these rules:

- No related ADR found: draft a new ADR.
- Related ADR found and the topic changes the decision: recommend superseding the old ADR with a new ADR.
- Related ADR found and the topic only improves wording or context: recommend clarifying the existing ADR.
- Ambiguous related ADR: hard-stop and ask whether this is new, supersede, or clarify.

For supersession, create a new ADR and update the old ADR's frontmatter only after confirmation. For clarification, update the existing ADR only if the core decision is unchanged.

## Canonical Location

Write one canonical ADR in the primary repo:

`docs/adr/YYYY-MM-DD-short-title.md`

Infer the short title and slug from the decision topic and repo evidence. If `desired_path` is provided, use it only if it stays under `docs/adr/` in the primary repo.

If the inferred path already exists:

- If the existing ADR appears related, recommend `clarify` or `supersede`.
- If it appears unrelated but has the same date or slug, propose a different slug and ask for confirmation.
- Never overwrite an ADR silently.

## ADR Format

Use YAML frontmatter plus Markdown body.

Frontmatter:

```yaml
---
title: Short Decision Title
status: proposed
date: YYYY-MM-DD
primary_repo: /path/to/primary-repo
affected_repos:
  - /path/to/repo
supersedes: null
superseded_by: null
---
```

Allowed statuses:

- `proposed`
- `accepted`
- `superseded`
- `deprecated`

Body headings:

```md
# Short Decision Title

## Context

## Decision

## Alternatives Considered

## Consequences

## Affected Repos

## Repo Evidence

## Implementation Notes

## Validation

## Open Questions
```

Do not add a second machine-readable summary block in the body. Frontmatter is the machine-readable source.

## Draft Requirements

Produce one recommended ADR draft, not multiple competing ADRs. Alternatives belong inside `Alternatives Considered`.

If the user provided the outcome, draft around that decision. If the user provided only a problem or topic, recommend a decision from evidence and mark the status `proposed`. If evidence is insufficient to recommend a decision, hard-stop with one focused question.

The reviewable chat draft must include:

- `ADR action`
- proposed file path
- frontmatter
- full Markdown body
- suggested follow-up doc links, if broader docs should link to the ADR

The final ADR should include concrete alternatives and tradeoffs. At least one consequence must be a downside or risk.

## Repo Evidence

Show repo evidence in the draft with concise bullets:

`repo path -> relevant files/modules -> why they matter`

Do not invent repo impact. If an affected repo path is missing, inaccessible, or not inspected, either:

- omit it from confirmed impact and list it under `Unverified affected repos`, or
- hard-stop if the user requires it to be part of the canonical decision.

## ADR Index

After confirmation, regenerate `docs/adr/README.md` in the primary repo. The index is fully generated and replaceable.

Include all ADRs, including `proposed`, `accepted`, `superseded`, and `deprecated`, sorted newest first. Include visible columns for:

- date
- title
- status
- supersedes
- superseded_by

Do not preserve custom prose in `docs/adr/README.md`.

## Scope Limits

By default, edit only:

- the target ADR file under `docs/adr/`
- an existing ADR being clarified
- an old ADR being marked as superseded
- `docs/adr/README.md`

Do not update `AGENTS.md`, `README.md`, `docs/architecture.md`, or other broader docs unless the user explicitly asks. Report suggested follow-up doc links instead.

Do not commit, push, open PRs, or run publishing workflows.

## Validation

After writing, verify:

- the ADR file exists at the confirmed path
- required frontmatter keys are present
- status is one of the allowed values
- `docs/adr/README.md` includes the ADR
- if superseding, old and new ADR links are consistent

Do not run the repo test suite for ADR-only changes.

## Quality Checklist

Before asking for confirmation, ensure:

- decision is stated in one clear sentence
- alternatives are concrete and not strawmen
- consequences include at least one downside
- affected repos are explicit
- repo evidence is specific to inspected files or modules
- implementation notes are actionable but not a full implementation plan
- validation is docs-specific
- unresolved questions are either empty or clearly blocking

If any required item fails, fix it or ask one focused question before presenting the draft.

## Example Invocation

```text
Use adr-creator.
primary_repo: /work/api
affected_repos:
  - /work/api
  - /work/ui
decision_topic: Decide where formula recalculation authority should live.
constraints: UI freeze mitigation is the near-term priority.
```

## Example Draft Shape

```text
ADR action: new
Path: /work/api/docs/adr/2026-04-24-move-formula-recalculation-authority.md

Repo Evidence
- /work/api -> src/... -> owns persisted spreadsheet state.
- /work/ui -> src/... -> currently performs expensive recalculation in user flows.

Draft
---
title: Move Formula Recalculation Authority
status: proposed
...
---

# Move Formula Recalculation Authority
...

Confirm before I write this ADR and regenerate docs/adr/README.md.
```
