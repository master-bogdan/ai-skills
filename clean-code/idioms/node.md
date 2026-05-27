# Node.js Backend Idioms

Language-specific conventions for Node.js backend projects.

## Layer Responsibilities

| Layer | Owns | Never Does |
|-------|------|------------|
| Router | Route registration, middleware binding | Business logic, DB queries |
| Controller | Request parsing, response shaping | Business rules, direct DB |
| Service | Business workflow, orchestration | HTTP concerns, raw SQL |
| Repository | Data access, query building | Business rules, HTTP codes |

## Service Design

One service function = one use case. May call multiple repositories but all steps
serve one coherent business operation.

## Validation

- Validate at the boundary (controller/handler) with schema validation
- Never pass raw `req.body` into a service
- Services receive validated, typed inputs

## Error Handling

- Let errors bubble — don't catch and re-throw without adding context
- Centralized error handler at app level for HTTP responses
- Business errors are named and specific: `InsufficientFundsError`
- Log at service level with business context (IDs, action, trace)

## Anti-Patterns to Reject

- Controller that queries DB directly
- Service that receives `req` or `res`
- Repository that throws HTTP errors
- Service that just forwards to repository without adding logic (useless wrapper)
- Catch-all `utils.ts` dumping ground

## Logging

Always include: correlation/trace ID, entity IDs, action name.
Never log: tokens, passwords, full request bodies, PII.

## Example

```ts
// Controller — parse, delegate, respond
export const createOrder = async (req: Request, res: Response) => {
  const input = createOrderSchema.parse(req.body);
  const order = await orderService.create(input, req.user.id);
  res.status(201).json(order);
};

// Service — business logic
export const create = async (input: CreateOrderInput, userId: string): Promise<Order> => {
  const user = await userRepository.findById(userId);
  if (!user.canCreateOrders) throw new ForbiddenError();

  const total = calculateTotal(input.items);
  return orderRepository.create({ ...input, userId, total });
};
```
