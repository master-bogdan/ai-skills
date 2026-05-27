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
