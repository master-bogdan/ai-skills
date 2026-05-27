# Magic Values

## Load When

Load when numbers, strings, booleans, defaults, status values, routes, limits, or
business constants appear inline.

## Rules

- Do not inline unexplained business numbers.
- Do not scatter business strings across the codebase.
- Do not pass naked booleans that force readers to guess meaning.
- Defaults must be visible and named when they matter.
- Group related constants into concept objects.

## Blocking

- Magic values encode business rules, limits, status, routes, permissions, or
  data integrity behavior.
- Repeated strings can drift across modules.
- Naked booleans obscure behavior at a callsite.
- Hidden defaults affect business behavior.

## Advisory

- Obvious local values are fine: `0` for first index, `1` for increment,
  `array.length > 0`, local sort direction checks.
- Tiny local defaults are fine when not business-relevant.

## Examples

Good:

```ts
export const IMPORT_LIMITS = {
  MAX_RETRY_COUNT: 3,
  LARGE_IMPORT_TIMEOUT_MS: 15000,
} as const;

export const IMPORT_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
} as const;
```

Bad:

```ts
if (retryCount >= 3) {
  throw new Error('Retry limit exceeded');
}

if (job.status === 'failed') {
  // ...
}

openImportModal(true);
```

Good boolean callsite:

```ts
openImportModal({ isReadOnly: true });
createImportJob({ shouldNotify: false });
```
