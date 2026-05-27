# Testing

Tests verify behavior through public interfaces. Testing is proportional to risk.

## Do

- Test behavior, not implementation: "when X happens, Y is the result"
- Test through public APIs — the same way a consumer would use the code
- Cover edge cases and error paths for risky logic
- Name tests as behavior descriptions: "creates order when inventory available"
- Match the project's test framework and patterns exactly

## Don't

- Assert that internal methods were called (spy-heavy tests)
- Test plumbing: "renders component", "calls function"
- Mock everything — prefer integration over unit when feasible for backend
- Write tests that break on any refactor without behavior change
- Add tests for trivial code with no logic

## Test Proportionality

| Risk | Strategy |
|------|----------|
| Business logic, calculations | Thorough unit tests |
| API endpoints | Integration tests against real layers |
| UI interactions | Behavior tests (user events → visible result) |
| Pure utilities | Light unit tests, only if logic is non-trivial |
| Config, constants, types | No tests needed |

## Example

```
// BAD — tests implementation
it('calls repository.save', async () => {
  const spy = jest.spyOn(repo, 'save');
  await createOrder(input);
  expect(spy).toHaveBeenCalled();
});

// GOOD — tests behavior
it('creates order with calculated total', async () => {
  const order = await createOrder({ items: [{ id: '1', qty: 2, price: 10 }] });
  expect(order.total).toBe(20);
  expect(order.status).toBe('pending');
});
```
