# Security

Validate at boundaries. Trust nothing from outside. Never log secrets.

## Do

- Validate all external input at the boundary (controller, route handler, API edge)
- Check authorization in the correct layer (service, not repository)
- Treat external payloads as untrusted until validated
- Use schema validation for request bodies
- Name dangerous defaults explicitly

## Don't

- Pass raw request bodies into services without validation
- Log tokens, passwords, API keys, or PII
- Use unsafe casts to skip validation: `req.body as OrderInput`
- Put authorization logic in repositories or UI only
- Trust client-sent IDs without ownership verification

## Boundary Rule

External input crosses a trust boundary. Validate ONCE at the edge, then internal
code receives typed, validated data.

```
External → [validation boundary] → Internal (trusted types)
```

## Example

```
// BAD — raw input trusted
const createOrder = async (req: Request, res: Response) => {
  await orderService.create(req.body); // anything could be in here
};

// GOOD — validated at boundary
const createOrder = async (req: Request, res: Response) => {
  const input = createOrderSchema.parse(req.body);
  await orderService.create(input); // typed, validated
};
```

```
// BAD — secret in logs
logger.error({ token, requestBody, password }, 'Request failed');

// GOOD — safe context only
logger.error({ userId, orderId, traceId, error: err.message }, 'Request failed');
```
