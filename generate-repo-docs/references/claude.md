# CLAUDE.md Contract

`CLAUDE.md` is the Claude Code entrypoint for the repo.

## Rules

- Keep it short.
- Import `AGENTS.md` using `@AGENTS.md` at the top.
- Do not duplicate content from `AGENTS.md`.
- Add only Claude Code-specific behavior not already covered in `AGENTS.md`.

## Required Content

- `@AGENTS.md` import directive
- A `## Claude Code` section with ask-before-guess mode and checkpoint requirement

## Template

```md
@AGENTS.md

## Claude Code

Use ask-before-guess mode.

Before multi-file, schema, API, auth, tenant, queue, WebSocket, file-processing, integration, migration, or infrastructure changes, provide a checkpoint and ask about blocking ambiguity before editing.
```

Customize the checkpoint trigger list to match the repo-specific high-risk areas identified during inspection. Replace the generic list above with the actual categories found in the repo.
