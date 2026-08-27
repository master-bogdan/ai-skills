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

## When To Split A Function

Split is justified when:
- The extracted piece has a name that teaches you something new
- The extracted piece could be tested independently and that test would be useful
- The remaining function becomes easier to scan

Split is NOT justified when:
- You're just moving 5 lines into a function called `doPartTwo`
- The extraction forces you to pass 4+ parameters that were local variables
- The name is `handleStuff` or `processData`
- It is a one-line / one-action pass-through (that's a tiny wrapper — inline it)

## Extract To Dedupe: The 3+ Rule

Two mistakes pull in opposite directions. Hold both lines:

- **Don't over-extract.** Duplication is cheaper than the wrong abstraction.
  Extract a repeated block for reuse ONLY when the SAME logic appears **3+
  times**. At two copies, leave them inline. Extracting to *name* one genuinely
  complex step is allowed even at one use; extracting to *dedupe* needs 3+.
- **Don't under-compose.** Distinct responsibilities belong in distinct
  functions/modules even if each appears once. See below.

## Composition & Files — Don't Dump Everything In One Place

Split along **responsibility and domain boundaries**, NOT along line-count.
"This file is long" is not a reason to split; "this file does two unrelated
jobs" is.

- One module/file = one reason to change. Validation, transformation,
  persistence, HTTP, and rendering are different reasons.
- A file mixing DB queries, business rules, and formatting is a god file —
  separate the concerns into their own modules.
- No catch-all `utils.ts` / `helpers.ts` dumping ground. Name modules by domain
  (`pricing.ts`, `order-validation.ts`).
- Colocate: types, tests, and helpers live next to what they serve, not in a
  distant shared bucket.
- Prefer composing small, single-purpose modules over one file that imports
  everything and orchestrates it all.

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
