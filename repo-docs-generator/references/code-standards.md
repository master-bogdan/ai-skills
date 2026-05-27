# docs/code-standards.md Contract

Define how code should be written in this repo.

## Good Topics

- layering expectations
- file placement conventions
- naming conventions
- validation and error-handling rules
- testing expectations tied to code changes
- documentation update expectations

## Precision Rules

Prefer standards like these when they match the repo:

- names should describe meaning, not just type
- booleans should read like statements: `is...`, `has...`, `can...`, `should...`
- function names should describe action, result, or decision
- collections should use plural names
- lookup maps should be named by meaning, such as `userById`
- use `UPPER_SNAKE_CASE` only for true constants
- use `PascalCase` for types, interfaces, enums, and classes
- comments should explain why, not restate obvious code
- avoid magic business values, strings, booleans, and hidden defaults

## Clean Code Expectations

Prefer standards like these when they match the repo:

- one clear responsibility per function, module, or file
- small cohesive functions
- early returns to flatten logic
- shared helpers for repeated rules or mappings
- clarity over cleverness
- maintainability over short-term convenience
- explicit behavior over hidden behavior
- no circular dependencies
- no hidden business logic in UI, controllers, or repositories

## TypeScript Expectations

Prefer standards like these when they match the repo:

- explicit types where inference is unclear
- narrow types and union types for meaningful state variation
- no `any` unless there is a documented approved exception
- unsafe casts only when the unsafe area is narrow and the reason is documented
- immutable transformations and predictable data flow

## Examples

Use concrete examples when they help clarify what the repo follows.

Example naming guidance:

```ts
const isLoading = requestState === 'loading';
const retryDelayMs = 3000;
const visibleColumns = columns.filter((column) => column.isVisible);
const userById = new Map<string, User>();
```

Example comment guidance:

```ts
// Keep retry delay above upstream timeout because
// the provider may acknowledge the job after timeout.
```

## Keep Out

- review thresholds
- scorecards
- broad architecture explanations

## Style

- concrete
- enforceable
- tied to observable repo patterns
