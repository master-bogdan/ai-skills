# Dependencies & Boundaries

Things that change together live together. Things that evolve independently stay
decoupled.

## Do

- Keep module boundaries explicit — use public entry points
- Business logic depends on abstractions, not infrastructure directly
- Colocate related code: feature owns its services, types, utils
- Dependencies flow inward: UI → service → repository (never reversed)

## Don't

- Import another module's private internals when a public API exists
- Create circular dependencies between features/modules
- Let a shared utility know about specific business domains
- Let infrastructure concerns leak into business logic

## Module Boundary Rules

- Feature exposes a public API (index file or explicit exports)
- Consumers import from the public boundary, never reach into internals
- If you need something from another module's internals, it should be exported or you're crossing a boundary wrong

## Dependency Direction

```
UI components
  → hooks / view models
    → services (business logic)
      → repositories (data access)
        → external APIs / DB
```

Never reverse this flow. A repository never imports a component. A service never
knows about HTTP request/response.

## Example

```
// BAD — feature reaches into another's internals
import { privateMapper } from '../imports/services/internal-mapper';

// GOOD — use public boundary
import { formatImport } from '../imports';
```

```
// BAD — business logic depends on infrastructure
const createOrder = async (req: Request) => {
  const db = new PostgresClient();
  ...
};

// GOOD — infrastructure injected or abstracted
const createOrder = async (input: CreateOrderInput): Promise<Order> => {
  return orderRepository.create(input);
};
```
