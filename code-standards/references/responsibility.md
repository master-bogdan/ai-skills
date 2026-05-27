# Responsibility

## Load When

Load when creating or reviewing functions, modules, files, services,
controllers, components, hooks, or utilities.

## Single Responsibility Principle

A function, module, or file should have one clear reason to change.

This does not mean:

- one service can call only one repository
- one controller can call only one service
- one service can never orchestrate multiple operations

It means:

- all work belongs to one coherent responsibility
- all steps support one use case
- unrelated concerns are not mixed

## Blocking

- A unit mixes unrelated use cases.
- Backend and frontend concerns are mixed in the same unit.
- Validation, transformation, persistence, UI state, analytics, and side effects
  are combined without one coherent workflow.
- A file becomes a multi-purpose dumping ground.

## Advisory

- A unit is slightly broad but still coherent and easy to understand.
- A helper extraction would improve readability but the current code remains
  local and understandable.

## Examples

Good service orchestration for one use case:

```ts
export const createImportService = async ({
  input,
  userId,
  traceId,
}: CreateImportServiceParams) => {
  const sheet = await getOwnedSheetRepository({
    sheetId: input.sheetId,
    userId,
  });

  validateSheetCanBeImported(sheet);

  return createImportRepository({
    sheetId: sheet.id,
    createdBy: userId,
    traceId,
  });
};
```

Bad mixed responsibility:

```ts
export const processImportRows = async (rows: RawRow[], userId: string) => {
  // normalize rows
  // validate rows
  // save rows
  // send email
  // compute dashboard stats
  // export CSV
  // update billing usage
  // track UI analytics
};
```
