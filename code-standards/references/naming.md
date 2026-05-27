# Naming

## Load When

Load for any TypeScript, React, Redux, or Node.js code generation or review.

## Rules

- Variables describe meaning, not just type.
- Booleans read like true/false statements with `is`, `has`, `can`, `should`,
  `was`, or `did`.
- Functions describe action, result, or decision.
- Collections use plural names.
- Maps and dictionaries are named by lookup meaning.
- Use `UPPER_SNAKE_CASE` only for true constants.
- Group related constants into concept objects.
- Types, interfaces, enums, and classes use `PascalCase`.

## Blocking

- Names hide business meaning enough that logic is hard to understand.
- Ambiguous names obscure a security, validation, or data integrity decision.
- Misnamed booleans invert or hide behavior.

## Advisory

- Names are weak but still understandable.
- A short local expression could be clearer with a named intermediate.
- Standalone true constants could be grouped with related constants.

## Examples

Good:

```ts
const workbookId = params.workbookId;
const retryDelayMs = 3000;
const failedImportsCount = failedImports.length;
const hasValidationErrors = errors.length > 0;
const shouldRetryImport = retryCount < IMPORT_LIMITS.MAX_RETRY_COUNT;
const userById = new Map<string, User>();
```

Bad:

```ts
const id = params.workbookId;
const delay = 3000;
const value = failedImports.length;
const validation = errors.length > 0;
const retry = retryCount < 3;
const userMap = new Map<string, User>();
```

Prefer named business conditions when they carry meaning:

```ts
export const isImportRetryAllowed = (job: ImportJob): boolean => {
  if (job.status !== IMPORT_STATUS.FAILED) {
    return false;
  }

  const hasRetriesLeft = job.retryCount < IMPORT_LIMITS.MAX_RETRY_COUNT;
  return hasRetriesLeft;
};
```
