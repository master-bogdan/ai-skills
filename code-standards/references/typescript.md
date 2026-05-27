# TypeScript

## Load When

Load for any TypeScript code generation, refactor, or review.

## Rules

- Use explicit types where inference is unclear.
- Prefer narrow types and discriminated unions for state variations.
- Keep input and output contracts clear.
- Avoid `any`, weak object bags, and broad return types that hide meaning.
- Prefer arrow functions for services, repositories, utils, hooks, controllers,
  handlers, and transformations.
- Prefer immutable transformations and predictable data flow.
- Unsafe casts and suppressions are allowed only when narrow, practical,
  documented, and approved where relevant.

## Blocking

- `any` or broad `unknown` usage hides business, security, validation, or data
  integrity assumptions.
- Unsafe casts or `@ts-ignore` hide real type problems.
- Mutation is unintentional or makes data flow unpredictable.
- Public contracts are weak enough to make callers guess shape or behavior.

## Advisory

- A return type could be more explicit but inference is still clear.
- A local mutation is intentional and contained but could be clearer.
- Function declaration versus arrow style differs from standards in old code.

## Examples

Good union:

```ts
type ImportResult =
  | { status: 'success'; jobId: string }
  | { status: 'validation_error'; errors: string[] };
```

Bad:

```ts
type ImportResult = any;
```

Good arrow utility:

```ts
export const normalizeSheetName = (name: string): string =>
  name.trim().toLowerCase();
```

Good immutable transform:

```ts
const normalizedRows = rows.map(normalizeRow);
```

Bad hidden mutation:

```ts
rows.forEach((row) => {
  row.name = row.name.trim();
});
```
