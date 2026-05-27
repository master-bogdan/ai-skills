# DRY

## Load When

Load when logic, mappings, constants, permission checks, or contracts appear in
multiple places.

## Rule

Do not repeat knowledge in multiple places. DRY is about duplicated rules,
logic, mappings, and contracts that can drift, not every repeated line.

## Blocking

- Business rules are copied across services, controllers, UI, or tests.
- DTO or payload mapping is repeated in several layers and can drift.
- Status strings, permission checks, or constants are scattered across modules.

## Advisory

- Small local duplication is clearer than forced abstraction.
- Repeated UI expressions are local, obvious, and unlikely to drift.

## Examples

Good shared permission rule:

```ts
export const canEditWorkbook = (user: User, workbook: Workbook): boolean => {
  return user.role === USER_ROLE.EDITOR && workbook.status !== WORKBOOK_STATUS.ARCHIVED;
};
```

Bad copied business rule:

```ts
if (user.role !== 'editor' || workbook.status === 'archived') {
  throw new Error('Forbidden');
}
```

Acceptable local duplication:

```ts
const isDisabled = isLoading || !canSubmit;
const isDeleteDisabled = isDeleting || !canDelete;
```
