---
name: generate-swagger-docs
description: Add swagger-ui to a Node.js or Go project, generate a static docs/swagger.json OpenAPI spec for all routes, and generate docs/schemas/*.json for all data models. Use when asked to "add swagger", "generate swagger", "document my API", "add API docs", or "generate OpenAPI spec".
---

# Generate Swagger Docs

## Hard stops

Stop and tell the user if any of these are true:

- No `package.json` or `go.mod` found — stack cannot be determined
- Server entrypoint not found — cannot wire swagger-ui middleware
- Stack not Node.js or Go — not supported

## Workflow

1. **Detect stack** — check for `package.json` (Node) or `go.mod` (Go)
2. **Load stack file** — [stack/node.md](stack/node.md) or [stack/go.md](stack/go.md)
3. **Inspect the codebase**:
   - Find all route/handler files
   - Find all request/response models, DTOs, and types
   - Find server entrypoint where middleware is registered
   - Check if swagger is already partially set up
4. **Produce a plan** showing exactly:
   - Packages to install
   - Files to modify and what changes
   - Files to create (`docs/swagger.json`, `docs/schemas/`)
   - Route swagger-ui will be served at (`/docs`)
5. **Wait for confirmation**
6. **Execute** — install packages, modify entrypoint, add annotations, generate static files

## Output

All generated files go to `docs/` (create it if missing):

- `docs/swagger.json` — static OpenAPI 3.0 spec
- `docs/schemas/` — one JSON schema file per model referenced in the spec
- Swagger-UI served at `/docs` in the running app

## Plan format

```
Packages to install:
  - swagger-ui-express
  - swagger-jsdoc

Files to modify:
  - src/server.ts — add swagger-ui middleware at /docs

Files to create:
  - docs/swagger.json — generated OpenAPI spec
  - docs/schemas/Order.json
  - docs/schemas/CreateOrderInput.json
  - scripts/generate-swagger.ts — script to regenerate static spec

npm scripts to add:
  - "swagger": "ts-node scripts/generate-swagger.ts"
```
