# Security

## Load When

Load for request boundaries, authorization, validation, file parsing, external
input, secrets, logging, unsafe casts, and dangerous defaults.

## Rules

Security is part of design and correctness.

Always check:

- input validation at boundaries
- authorization checks in the correct layer
- secrets are never logged
- unsafe casts do not hide security-sensitive assumptions
- file uploads and parsing paths are validated
- external input is treated as untrusted
- dangerous defaults are visible and intentional

## Blocking

- Missing validation at a request, file, external payload, or persistence
  boundary.
- Authorization is missing, vague, or in the wrong layer.
- Secrets, tokens, passwords, or raw sensitive payloads are logged.
- Unsafe casts hide security-sensitive assumptions.
- External input is treated as trusted.
- Defaults can produce dangerous behavior without explicit naming.

## Advisory

- Validation exists but error shape could be clearer.
- Permission helper naming could be clearer.
- Logging has safe context but could include a better business identifier.

## Examples

Good:

```ts
const input = createImportDtoSchema.parse(req.body);

if (!canEditWorkbook(user, workbook)) {
  throw new ForbiddenError();
}
```

Bad:

```ts
const input = req.body;

if (user.role === 'editor') {
  // maybe okay
}
```

Good logging:

```ts
logger.error(
  { traceId, importJobId, message: error.message },
  'Import failed',
);
```

Bad logging:

```ts
logger.error({ traceId, token, password, payload }, 'Import failed');
```
