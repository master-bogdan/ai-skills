# Node Backend

## Load When

Load for Node.js API routes, controllers, services, repositories, DTOs,
validators, module structure, logging, and backend tests.

Do not add framework-specific rules unless the repo already uses that framework.
Follow repo-specific structure when coherent, but enforce responsibility
boundaries and module structure.

## Module Structure

For new backend code, enforce:

- DTOs in `dto/`
- repositories in `repositories/`
- services in `services/`
- utilities split by purpose, not one dumping-ground file
- one service file equals one exported service function/class responsibility
- feature/module public imports through `index.ts` or the established public
  boundary
- role suffixes from [file-naming.md](file-naming.md)

Existing structure is advisory unless the task touches that area or the boundary
violation blocks the requested change.

## Router

Routers should:

- register routes
- bind middleware
- call controllers

Routers should not:

- contain business logic
- query persistence directly
- transform business rules

## Controller

Controllers should:

- validate request DTOs at the boundary
- parse request context
- delegate to services
- map service result to HTTP response
- avoid leaking request/response objects into services

## Service

Services should:

- own business workflow only
- use meaningful try/catch when failure handling or logging adds value
- log meaningful business events
- not leak HTTP request/response concerns
- orchestrate collaborators for one coherent use case

## Repository

Repositories should:

- own persistence only
- avoid business rules
- avoid HTTP concerns

## DTO And Validation

- Validate request boundaries.
- Use the repo's established validation pattern.
- If no pattern exists, prefer explicit schema validation.
- Do not pass raw request bodies into services without validation.

## Logging

Log in meaningful service paths. Include:

- event name
- business identifiers
- `traceId` when available
- relevant actor ids
- meaningful failure context

Never log secrets, tokens, passwords, or raw sensitive payloads.

## Blocking

- Business logic lives in router/controller/repository instead of service.
- Request/response objects leak into services.
- Raw input crosses a boundary without validation.
- Persistence code contains business authorization or HTTP errors.
- New backend files ignore module structure or role suffixes.
- Module internals are imported through private paths when a public boundary
  exists.

## Advisory

- Existing code uses a different but coherent folder layout.
- A service is slightly broad but still one use case.
- Logging could include more context but is not harmful.

## Examples

Good controller:

```ts
export const createImportController = async (
  req: Request,
  res: Response,
): Promise<void> => {
  try {
    const input = createImportDtoSchema.parse(req.body);
    const result = await createImportService({
      input,
      userId: req.user.id,
      traceId: req.traceId,
    });

    res.status(201).json(result);
  } catch (error) {
    handleControllerError(error, res);
  }
};
```

Bad service:

```ts
export const createImportService = async (req: Request, res: Response) => {
  res.status(201).json({});
};
```
