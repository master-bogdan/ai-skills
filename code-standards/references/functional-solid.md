# Functional SOLID

## Load When

Load when designing function contracts, strategies, dependencies, or reusable
business logic.

## Open/Closed

Prefer extending behavior through composition, new functions, or clear strategy
branches instead of editing unrelated code paths everywhere.

Blocking:

- New behavior requires changes across many unrelated files.
- Branching grows in a place that is no longer a clear boundary.

Advisory:

- A short `if` or `switch` is stable, local, and easier than a strategy map.

## Interface Segregation

Prefer small focused contracts over giant parameter or prop bags.

Blocking:

- A parameter object or prop contract mixes unrelated state, actions, config,
  infrastructure, navigation, permissions, and UI state.
- The contract is easy to misuse because it accepts too much.

Advisory:

- A contract is slightly wide but still one coherent API.

## Dependency Inversion

Business logic should depend on contracts and capabilities, not concrete
infrastructure details.

Blocking:

- Reusable core logic directly creates DB clients, message clients, loggers, or
  SDKs.
- Direct infrastructure coupling makes business logic hard to test or evolve.

Advisory:

- Thin integration code imports concrete infrastructure locally.

## Examples

Good strategy boundary:

```ts
type ImportStrategy = (file: UploadedFile) => Promise<ImportResult>;

const strategyByType: Record<FileType, ImportStrategy> = {
  csv: importCsvFile,
  xlsx: importXlsxFile,
};
```

Bad everything-bag contract:

```ts
type SaveWorkbookParams = {
  workbookId: string;
  title: string;
  currentUser: User;
  permissions: Permission[];
  selectedSheetName: string;
  theme: Theme;
  analytics: AnalyticsClient;
  navigate: NavigateFunction;
};
```
