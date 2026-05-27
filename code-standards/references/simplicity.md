# Simplicity

## Load When

Load when a solution introduces indirection, generic utilities, managers,
builders, pipelines, strategies, or frameworks.

## Rule

Keep the solution as simple as the problem allows.

Prefer:

- clear control flow
- direct solutions
- simple composition
- obvious abstractions

Avoid:

- unnecessary indirection
- premature architecture
- generic utilities for future use

## Blocking

- Overengineering materially hurts readability or maintainability.
- A simple mapping or filter becomes a framework, strategy engine, or builder.
- The abstraction hides behavior needed to understand correctness.

## Advisory

- Complexity is slightly unnecessary but contained.
- A smaller direct helper would be clearer.

## Examples

Good:

```ts
export const getVisibleColumns = (columns: Column[]): Column[] => {
  return columns.filter((column) => column.isVisible);
};
```

Bad:

```ts
export const executeColumnVisibilityStrategyPipeline = (
  columns: Column[],
): Column[] => {
  return columns.filter((column) => column.isVisible);
};
```
