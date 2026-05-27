# DRY — Don't Repeat Knowledge

DRY is about duplicated rules, logic, and contracts that can drift. Not about
eliminating every repeated line.

## Do

- Extract when business logic appears in multiple places and could diverge
- Centralize status values, permission checks, validation rules
- Share DTO/payload shapes that must stay in sync

## Don't

- Force abstraction to remove two similar-looking but independent expressions
- Create a "shared utility" that knows about multiple unrelated domains
- Extract code that happens to look similar but changes for different reasons

## Duplication is OK when

- Two expressions look alike but serve different business reasons
- Extracting would require passing 3+ parameters and a generic name
- The "shared" code would be a one-liner with more ceremony than value

## Example

```
// BAD — duplicated business rule that can drift
// file A:
if (user.role !== 'editor' || workbook.status === 'archived') { ... }
// file B:
if (user.role !== 'editor' || workbook.status === 'archived') { ... }

// GOOD — one source of truth
const canEditWorkbook = (user: User, workbook: Workbook): boolean =>
  user.role === 'editor' && workbook.status !== 'archived';
```

```
// ACCEPTABLE — similar shape, different reasons to change
const isSubmitDisabled = isLoading || !canSubmit;
const isDeleteDisabled = isDeleting || !canDelete;
```
