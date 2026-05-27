# Single Responsibility

A function, module, or file has one clear reason to change. All steps serve one
coherent purpose.

## Do

- Keep functions under ~40 lines
- Use early returns to flatten control flow
- Split when each piece has a genuinely distinct responsibility
- Separate validation, transformation, persistence, and side effects

## Don't

- Mix unrelated use cases in one function
- Create god functions that orchestrate everything
- Split into tiny functions that just relocate code without adding clarity
- Extract a helper that's called exactly once and adds a layer for nothing

## When To Split

Split is justified when:
- The extracted piece has a name that teaches you something new
- The extracted piece could be tested independently and that test would be useful
- The remaining function becomes easier to scan

Split is NOT justified when:
- You're just moving 5 lines into a function called `doPartTwo`
- The extraction forces you to pass 4+ parameters that were local variables
- The name is `handleStuff` or `processData`

## Example

```
// BAD — god function
async function handleOrder(req, res) {
  // validate → lookup user → check inventory → calculate price →
  // apply discount → charge payment → create order → send email →
  // update analytics → return response
}

// GOOD — orchestrator delegates clearly named steps
const createOrder = async (input: CreateOrderInput): Promise<Order> => {
  const user = await getVerifiedUser(input.userId);
  const items = await resolveInventory(input.items);
  const total = calculateTotal(items, input.coupon);
  const order = await orderRepository.create({ userId: user.id, items, total });
  await notifyOrderCreated(order);
  return order;
};
```
