# Canonical Docs

Use this file for the canonical file set, ownership rules, plan actions, and allowed legacy renames.

## Fixed Canonical Files

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `README.md`
- `docs/architecture.md`
- `docs/how-system-works.md`
- `docs/code-standards.md`
- `docs/code-quality-scorecard.md`
- `docs/patterns.md`
- `docs/models.md`
- `docs/onboarding.md`

## Ownership

- `AGENTS.md`: full-file generated
- `.github/copilot-instructions.md`: full-file generated
- `README.md`: full-file skill-owned
- `docs/*.md`: full-file skill-owned
- non-canonical extra docs: preserve unless explicitly renamed by the mapping below

## Pre-write Plan Actions

Use only these actions in the pre-write plan:

- `create`
- `update`
- `rewrite`
- `rename`
- `preserve`
- `skip`
- `needs confirmation`

The plan must stay terse:

```text
create AGENTS.md
rename docs/runtime-flows.md -> docs/how-system-works.md
preserve docs/core-rmq-coverage-matrix.md
```

## Allowed Legacy Renames

Auto-rename only these exact mappings:

- `docs/runtime-flows.md` -> `docs/how-system-works.md`
- `docs/engineering-standards.md` -> `docs/code-standards.md`
- `docs/common-patterns.md` -> `docs/patterns.md`
- `docs/code-quality-balanced-scorecard.md` -> `docs/code-quality-scorecard.md`

After a mapped rename:

1. update in-repo references to the old path
2. remove the old file

Do not infer additional rename mappings.

## Source Priority

When sources disagree, use this order:

1. current code and executable repo config
2. existing canonical docs
3. existing non-canonical docs

## Missing Evidence

If a required section does not have enough support from the repo, keep the section and write:

`Needs confirmation`
