# II. Dependencies

Explicitly declare and isolate dependencies. A twelve-factor app never relies on
implicit existence of system-wide packages. All dependencies are declared in a
manifest and isolated so no dependencies leak in from the surrounding system.

## Explore

- `package.json` / `package-lock.json` / `yarn.lock`
- `go.mod` / `go.sum`
- `requirements.txt` / `Pipfile` / `pyproject.toml`
- `Gemfile` / `Gemfile.lock`
- `vendor/` directory
- Any shell scripts that call system tools without checking for existence

## Pass

- All dependencies declared in a manifest with pinned or bounded versions
- Lock file committed to version control
- No implicit system tool dependencies (curl, jq, etc.) without a check or container

## Fail / Partial

- ❌ Dependencies installed globally on CI/prod with no manifest
- ❌ Lock file absent or gitignored
- ❌ `npm install -g` or `pip install` in app startup scripts
- ⚠️ Some system tool dependencies undocumented

## Examples

```json
// GOOD — package.json with lockfile committed
{
  "dependencies": { "express": "4.18.2" },
  "engines": { "node": ">=20.0.0" }
}
```

```go
// GOOD — go.mod with go.sum committed
module github.com/org/app
go 1.22
require github.com/gin-gonic/gin v1.9.1
```

```dockerfile
# GOOD — all system deps declared in Dockerfile
FROM node:20-alpine
RUN apk add --no-cache curl=8.5.0-r0
```

```sh
# BAD — assumes curl exists on host
curl -s https://api.example.com/health
```
