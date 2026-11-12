# Minimal Code

Every line must earn its place. If removing code doesn't break behavior, remove it.

## Do

- Solve the current problem, not hypothetical future ones
- Use the simplest approach that's still clear
- Prefer direct solutions over indirection
- Delete dead code — don't comment it out

## Don't

- Add abstractions for a single use case
- Create strategy/factory/builder without multiple implementations NOW
- Add config flags nobody needs yet
- Build generic utilities when a direct solution is shorter
- Create extension points before a second real case exists
- Add layers "for testability" when there's no test that needs it

## Comments

Comments explain the non-obvious **why**, never the **what**.

- Write one when the reason isn't visible in the code: a constraint, a workaround,
  a business rule, a non-obvious edge case, a link to context.
- Don't restate what the code already says (`// increment i`).
- Don't comment out dead code — delete it.
- A comment that just re-narrates the next line is noise; a name usually replaces it.

```ts
// BAD — restates the code
// loop over users and send email
for (const user of users) {
  sendEmail(user);
}

// GOOD — explains the non-obvious why
// Stripe rejects amounts below 50 cents, so bundle micro-charges into a daily sweep.
if (amount < STRIPE_MIN_CHARGE) {
  queueForDailySweep(amount);
}
```

## Example

```
// BAD — generic engine for one case
class ImportProcessorFactory {
  static create(type: string): ImportProcessor { ... }
}

// GOOD — direct solution
const processImport = async (file: UploadedFile): Promise<ImportResult> => {
  const rows = await parseFile(file);
  return validateAndSave(rows);
};
```
