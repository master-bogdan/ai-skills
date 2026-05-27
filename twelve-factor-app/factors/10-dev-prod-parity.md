# X. Dev/Prod Parity

Keep development, staging, and production as similar as possible. The gaps
between environments are the primary source of "works on my machine" bugs.
Minimize the time gap (deploy often), personnel gap (devs own what they deploy),
and tools gap (same backing services locally as in production).

## Explore

- `docker-compose.yml` — does local development use the same services as prod?
- Are developers using SQLite locally but Postgres in prod?
- Are there env-specific code branches (`if NODE_ENV === 'development'`)?
- How long does it take from commit to production deploy?
- Are database migrations tested against the same DB engine used in prod?

## Pass

- Local dev uses same backing service types as production (Postgres locally, not SQLite)
- Docker Compose mirrors production service topology
- No environment-specific code branches for core logic
- CI runs against the same service versions as production

## Fail / Partial

- ❌ SQLite/in-memory DB locally, Postgres in production
- ❌ Core logic branches on `NODE_ENV` or `GO_ENV`
- ❌ Mocked backing services in CI that differ from production
- ⚠️ Same service types but different versions locally vs. production

## Examples

```yaml
# GOOD — docker-compose uses same DB engine as prod
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app_dev
  redis:
    image: redis:7-alpine
```

```yaml
# BAD — SQLite locally, Postgres in prod
# No docker-compose.yml, developers run: sqlite3 ./dev.db
```

```ts
// BAD — environment-specific logic
if (process.env.NODE_ENV === 'development') {
  await seedDatabase(); // but prod has real data, so bugs hide
}

// BAD — different auth in dev
const auth = process.env.NODE_ENV === 'production'
  ? realAuthMiddleware
  : (req, res, next) => next(); // bypassed locally
```

```yaml
# GOOD — CI uses same postgres version as prod
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: test
```
