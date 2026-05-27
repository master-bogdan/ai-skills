# Naming

A good name eliminates the need for a comment. Names reveal intent, not
implementation.

## Do

- Variables describe meaning: `retryDelayMs`, not `delay`
- Booleans read as true/false statements: `isActive`, `hasPermission`, `canRetry`
- Functions describe action or result: `calculateTotal`, `resolveUser`
- Collections use plurals: `orders`, `activeUsers`
- Maps use lookup meaning: `userById`, `priceByProductId`
- Constants group into concept objects: `ORDER_STATUS.PENDING`

## Don't

- Generic names: `data`, `item`, `value`, `result`, `info`, `temp`
- Implementation names: `userMap`, `orderArray`, `stringValue`
- Abbreviated names that sacrifice clarity: `usr`, `ord`, `cfg` (unless project convention)
- Negated booleans: `isNotReady` (use `isReady` and negate at usage)

## Functions

- Verb for actions: `createOrder`, `sendNotification`
- Question for predicates: `isExpired`, `canSubmit`
- Noun for factories/builders: `orderFromInput`, `userResponse`

## Magic Values

- Named constants for business values: limits, statuses, routes, permissions
- Group related constants: `IMPORT_LIMITS.MAX_RETRY`, not standalone `MAX_RETRY = 3`
- No naked booleans at call sites: `openModal({ isReadOnly: true })` not `openModal(true)`

## Example

```
// BAD
const d = getItems();
const flag = d.length > 0;
if (count >= 3) { throw new Error('limit'); }
openDialog(true, false);

// GOOD
const availableItems = getItems();
const hasItems = availableItems.length > 0;
if (retryCount >= ORDER_LIMITS.MAX_RETRIES) { throw new RetryLimitError(); }
openDialog({ isEditable: true, showHistory: false });
```
