# docs/how-system-works.md Contract

Explain how the important flows behave by tracing real execution paths through
the code.

## Focus

Document the main execution paths such as:

- request handling
- startup and shutdown
- authentication and authorization flow
- background jobs and queue processing
- event handling
- integration and webhook flows
- save/sync flows

## Depth requirement

Trace real execution paths by reading the code. Show actual file paths and
function names for each step — not just "controller calls service calls
repository."

Example of acceptable depth:

```
1. POST /orders hits src/routes/orders.router.ts
2. requireAuth middleware validates JWT via src/middleware/auth.ts:verifyToken
3. createOrderController (src/controllers/order.controller.ts:34) parses body
   with createOrderSchema.parse(req.body)
4. Delegates to createOrderService (src/services/order.service.ts:12)
5. Service calls getOwnedSheet repository, then createOrderRepository
6. Returns 201 with order payload
```

## Structure

For each flow:
1. Short one-line description of what this flow does
2. Numbered steps naming actual files and functions
3. ASCII sequence diagram for flows with 3+ participants
4. Brief note on why this flow matters or what can go wrong

## Diagrams

Include simple ASCII sequence diagrams for complex flows:

```
Client → Router → Auth Middleware → Controller → Service → Repository → DB
                                                         ↓
                                                   Queue (async)
```

## Naming rule

This file replaces `docs/runtime-flows.md` when that legacy file exists.
