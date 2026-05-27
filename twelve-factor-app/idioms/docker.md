# Docker — 12-Factor Idioms

## Build/Release/Run (V) — Config-free image

```dockerfile
# GOOD — no config baked in, config injected at runtime
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci --production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
# No ENV with real values here — injected at runtime
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

```dockerfile
# BAD — config baked into image
ENV DATABASE_URL=postgres://prod-db:5432/app
ENV API_KEY=sk-live-abc123
```

## Port Binding (VII)

```dockerfile
# Document the port the app binds
EXPOSE 8080
# Always read PORT from env in app code
```

## Dev/Prod Parity (X) — docker-compose

```yaml
# GOOD — same service types as production
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=postgres://postgres:password@db:5432/app_dev
      - REDIS_URL=redis://redis:6379
    depends_on: [db, redis]

  db:
    image: postgres:16-alpine         # same major version as prod
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app_dev

  redis:
    image: redis:7-alpine             # same major version as prod

  worker:
    build: .
    command: node worker.js           # separate process type
    environment:
      - DATABASE_URL=postgres://postgres:password@db:5432/app_dev
      - REDIS_URL=redis://redis:6379
```

## Disposability (IX) — signals in Docker

```dockerfile
# Use exec form of CMD so signals reach the app, not sh
CMD ["node", "server.js"]       # GOOD — PID 1 gets SIGTERM
CMD node server.js              # BAD — sh gets SIGTERM, app does not
```

## Processes — no local state (VI)

```yaml
# BAD — local volume for uploads (not shared across instances)
volumes:
  - ./uploads:/app/uploads

# GOOD — no local volume, use S3/GCS
# App writes to process.env.S3_BUCKET
```

## Logs (XI)

```yaml
# Docker captures stdout/stderr automatically
# No log driver config needed in Compose for local dev
# In production, use a log driver:
services:
  app:
    logging:
      driver: awslogs
      options:
        awslogs-group: /app/production
        awslogs-region: us-east-1
```
