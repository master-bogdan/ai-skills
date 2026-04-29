# docs/patterns.md Contract

Explain preferred implementation shapes in this repo.

## Good Topics

- controller or service layering
- DTO and validation patterns
- hook, store, and component boundaries
- adapter patterns
- error-handling patterns
- naming and file placement conventions

## Frontend Patterns

When the repo is UI-focused, prefer patterns like these when they match the repo:

- React components as function declarations
- hooks as exported arrow functions
- one component per file
- subcomponents in their own folders
- kebab-case filenames
- hooks own local orchestration
- services own API interaction
- components focus on rendering and composition
- selectors own derived Redux data
- thunks own async dispatch orchestration
- utilities stay pure

Smells worth calling out:

- components with 15+ props
- components that mix rendering, orchestration, mapping, side effects, and permissions
- hooks that become second components
- direct networking details inside hooks when a service layer exists

## Backend Patterns

When the repo is backend-focused, prefer patterns like these when they match the repo:

- top-level separation between `app`, `common`, `infra`, and `modules`
- DTOs in `dto/`
- repositories in `repositories/`
- multiple small files in `utils/` instead of one dumping-ground file
- one service file equals one exported service function
- routers register routes and middleware only
- controllers validate DTOs and delegate
- services own business workflow
- repositories stay persistence-only
- Zod at request boundaries
- logging in services with identifiers and `traceId` when available

## Examples

Use repo-shaped examples when they clarify the pattern.

Example backend boundary:

```ts
router.post('/imports', requireAuth, createImportController);
```

Example controller boundary:

```ts
const input = createImportDtoSchema.parse(req.body);
const result = await createImportService({
  input,
  userId: req.user.id,
  traceId: req.traceId,
});
```

## Goal

Answer:

`How do we usually implement this here?`

Use concrete repo-shaped examples when they clarify a real pattern.
