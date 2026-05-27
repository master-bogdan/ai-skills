# YAGNI

## Load When

Load when code adds extension points, config flags, plugin systems, optional
behaviors, or generalized engines for hypothetical future needs.

## Rule

Do not build for hypothetical future requirements.

Prefer:

- solve the current problem cleanly
- leave room for extension where obvious
- add structure only for real current use cases

Avoid:

- config flags no one needs yet
- generic engines for one use case
- extension points before there is a second real case

## Blocking

- Speculative design creates meaningful complexity in touched code.
- Unused flags or options change the contract without a current requirement.
- A plugin or strategy architecture exists for exactly one real behavior.

## Advisory

- A small amount of future-friendly structure directly supports the current
  problem.
- An obvious enum-to-label map is slightly extensible but simple.

## Examples

Bad:

```ts
export const createImportService = async ({
  input,
  userId,
  enableNotifications = false,
  enableAuditTracking = false,
  useLegacyMode = false,
  skipCacheInvalidation = false,
}: CreateImportServiceParams) => {
  // ...
};
```

Acceptable:

```ts
const labelByStatus = {
  pending: 'Pending',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
} satisfies Record<ImportStatus, string>;
```
