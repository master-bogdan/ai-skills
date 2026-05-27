# Comments And Exceptions

## Load When

Load when adding comments, TODOs, unsafe casts, suppressions, workaround code, or
exceptions to standards.

## Comments

Comments should explain:

- why something exists
- why a decision was made
- why a workaround is necessary

Comments should not restate obvious code.

## Exceptions

Exceptions are allowed only when:

- there is a real practical reason
- the reason is written in the PR or task context
- a tech lead approved it where relevant
- the code has an explicit comment at the exception point

## Blocking

- A comment is misleading.
- A TODO or temporary hack has no context.
- An unsafe exception hides security, validation, or data integrity assumptions.
- An exception bypasses architecture without explanation.

## Advisory

- A comment is noisy but harmless.
- A short clarifying comment could improve a non-obvious business rule.

## Examples

Good:

```ts
// Keep retry delay above upstream timeout because the provider may acknowledge
// the job after timeout.
```

Good exception:

```ts
// Tech lead approved exception:
// Third-party SDK returns unstable payload types.
// Narrow cast kept local until SDK wrapper is added in IBF-1234.
const payload = rawPayload as ExternalImportPayload;
```

Bad:

```ts
// Increment retry count.
retryCount += 1;

// TODO fix later.
```
