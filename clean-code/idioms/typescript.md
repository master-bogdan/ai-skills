# TypeScript Idioms

Language-specific conventions for TypeScript/JavaScript projects.

## Type System

- Narrow types: discriminated unions over broad objects
- `as const` for literal constant groups
- Explicit return types on public/exported functions
- Template literal types when they add safety
- `type` over `interface` unless extending/merging is needed

## Never

- `any` — find the real type
- `@ts-ignore` without a ticket reference
- Type assertions (`as X`) to bypass broken data flows
- Broad `Record<string, any>` for structured data

## Function Style

- Arrow functions for: services, utils, handlers, hooks, controllers
- Function declarations for: React components
- Immutable transforms: `.map()`, `.filter()`, spread — not mutation

## Argument Count — Max 3, Then Object

- Hard cap of **3** parameters. At 4+, collapse them into one typed options object.
- An object also wins below 3 args when call sites would otherwise pass bare
  positional booleans or same-typed values that are easy to transpose.
- Name the type after the operation: `CreateOrderInput`, `SearchParams`.
- Don't just bag every param into an object — group params that belong to the
  same concept; keep 1–2 genuinely independent args positional.

```ts
// BAD — 5 positional args, order is a memory test
function createUser(name: string, email: string, age: number, isAdmin: boolean, teamId: string) {}
createUser('Ada', 'ada@x.io', 36, true, 't_1');

// GOOD — one typed object, self-documenting at the call site
type CreateUserInput = {
  name: string;
  email: string;
  age: number;
  isAdmin: boolean;
  teamId: string;
};
const createUser = (input: CreateUserInput) => { /* ... */ };
createUser({ name: 'Ada', email: 'ada@x.io', age: 36, isAdmin: true, teamId: 't_1' });
```

## Naming Conventions

- Variables/functions: `camelCase`
- Types/interfaces: `PascalCase`, no `I` prefix
- Constants: `UPPER_SNAKE` grouped in objects
- Booleans: `is`, `has`, `can`, `should` prefix
- Arrays: plural nouns
- Maps: `xByY` pattern (`userById`)
- Files: follow project convention (check existing files first)

## Conditions and Control Flow

- Never put `if` condition and body on the same line
- Extract into a named boolean when ANY of these are true:
  - Condition has 2+ chained optional access (`?.`)
  - Condition uses negation of a non-trivial expression (`!Object.keys(...)`)
  - Condition contains a callback (`.some()`, `.every()`, `.find()`)
  - Condition is longer than ~60 characters
- Named booleans read as positive statements — negate at usage if needed

```ts
// BAD — compressed, unreadable
if (!Object.keys(lappValues).length) { return null; }
if (cell?.formulaDeps?.lappRefs?.some((name) => name in lappValues)) {
  triggerKeys.add(buildQualifiedKey(sheet.name!, cellKey));
}

// GOOD — readable, named conditions
const hasLappValues = Object.keys(lappValues).length > 0;

if (!hasLappValues) {
  return null;
}

const hasDependentLappRefs = cell?.formulaDeps?.lappRefs?.some(
  (name) => name in lappValues,
);

if (hasDependentLappRefs) {
  triggerKeys.add(buildQualifiedKey(sheet.name!, cellKey));
}
```

## Error Handling

- Custom errors for business logic: `class InsufficientFundsError extends Error`
- Native errors for programming bugs
- Never swallow errors silently
- Throw at boundaries, return result types internally when it helps

## Example

```ts
const ORDER_STATUS = {
  PENDING: 'pending',
  SHIPPED: 'shipped',
  CANCELLED: 'cancelled',
} as const;

type OrderStatus = (typeof ORDER_STATUS)[keyof typeof ORDER_STATUS];

type OrderResult =
  | { status: typeof ORDER_STATUS.SHIPPED; trackingId: string }
  | { status: typeof ORDER_STATUS.CANCELLED; reason: string };

export const shipOrder = async (orderId: string): Promise<OrderResult> => {
  const order = await orderRepository.get(orderId);

  if (!order.canShip) {
    return { status: ORDER_STATUS.CANCELLED, reason: 'Not ready' };
  }

  const trackingId = await shippingService.dispatch(order);
  return { status: ORDER_STATUS.SHIPPED, trackingId };
};
```
