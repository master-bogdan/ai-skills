# Function Size

## Load When

Load when functions, hooks, handlers, services, or components are hard to scan
or include nested branching.

## Rules

- Functions should be small enough to read without too much scrolling.
- Function size is a readability rule, not a line-count rule.
- Use early returns to flatten control flow.
- Extract helpers when extraction improves understanding.
- Keep validation, transformation, persistence, and side effects separated unless
  they clearly support one coherent workflow.

## Blocking

- A function becomes hard to reason about because it does too much.
- Deep nested branching hides business rules or error paths.
- One function owns orchestration, persistence, response shaping, and unrelated
  side effects.

## Advisory

- A function is slightly larger than ideal but still clear.
- A named helper would improve scanability in touched code.

## Examples

Good:

```ts
export const buildImportPayload = (input: Input): ImportPayload => {
  if (!input.sheetId) {
    throw new Error('sheetId is required');
  }

  return {
    sheetId: input.sheetId,
    templateId: input.templateId ?? null,
  };
};
```

Bad:

```ts
export const handleImport = async (input: Input, req: Request, res: Response) => {
  // validate
  // lookup sheet
  // check permissions
  // create job
  // audit log
  // analytics
  // send email
  // map response
  // return HTTP response
};
```
