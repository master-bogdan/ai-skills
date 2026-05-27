# File Naming

## Load When

Load before creating, moving, renaming, or reviewing files.

## Baseline

Inspect existing repo naming first. For new files, use these standards unless the
repo already has a stronger consistent convention.

Existing files are advisory unless touched, the task is a naming cleanup, or the
name hides a responsibility boundary.

## General Rules

- Use `kebab-case` filenames.
- Use role suffixes for new TypeScript and Node files.
- Keep index barrels only when they are established public boundaries.
- Do not create dumping-ground names such as `helpers.ts`, `utils.ts`, or
  `common.ts` for unrelated responsibilities.

## Role Suffixes

- Services: `*.service.ts`
- Controllers: `*.controller.ts`
- Routers: `*.router.ts`
- Repositories: `*.repository.ts`
- DTOs: `*.dto.ts`
- Schemas and validators: `*.schema.ts` or existing repo validator suffix
- Constants: `*.constants.ts`
- Types: `*.types.ts`
- Utilities: `*.util.ts` for one utility module, or specific kebab-case purpose
  names when the repo already uses them
- Mappers: `*.mapper.ts`
- Adapters: `*.adapter.ts`
- Guards: `*.guard.ts`
- Middleware: `*.middleware.ts`

## Test Suffixes

New tests should encode test scope unless the repo already has a stronger
consistent convention:

- Unit tests: `*.unit.spec.ts` or `*.unit.test.ts`
- Integration tests: `*.integration.spec.ts` or `*.integration.test.ts`
- E2E tests: `*.e2e.spec.ts` or `*.e2e.test.ts`
- Component/UI tests: prefer explicit scope when adding new patterns, such as
  `*.component.spec.tsx` or `*.integration.spec.tsx`
- Fixtures and builders: `*.fixture.ts`, `*.builder.ts`, or repo convention, not
  `*.spec.ts`

If a touched area consistently uses `*.spec.ts`, follow that pattern unless the
task introduces a new convention or explicitly asks for scope suffixes.

## React Naming

- Component function and type names use `PascalCase`.
- React component folders use `kebab-case`.
- React component filenames use `kebab-case`, for example
  `workbook-toolbar.tsx`.
- Hooks use `use-*.ts`, for example `use-workbook-toolbar.ts`.
- Services use `*.service.ts`.
- Shared or feature-level constants and types use `*.constants.ts` and
  `*.types.ts`.
- Local constants and types inside a focused component folder may stay
  `constants.ts` and `types.ts`.
- Existing PascalCase component files are advisory unless touched or the task is
  a naming cleanup.

## Blocking

- New files ignore mandatory role suffixes.
- A filename hides the role or layer enough to encourage wrong imports.
- A test filename misrepresents its scope.
- A touched file keeps a misleading dumping-ground name while adding more
  unrelated behavior.

## Advisory

- Existing filenames do not match the preferred suffix but are outside scope.
- A local component folder uses an older naming pattern consistently.
