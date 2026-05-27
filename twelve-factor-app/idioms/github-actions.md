# GitHub Actions — 12-Factor Idioms

## Build/Release/Run (V) — immutable releases

```yaml
# GOOD — build once, tag with commit SHA, deploy that tag
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push image
        run: |
          docker build -t ${{ secrets.REGISTRY }}/app:${{ github.sha }} .
          docker push ${{ secrets.REGISTRY }}/app:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy immutable release
        run: |
          kubectl set image deployment/app \
            app=${{ secrets.REGISTRY }}/app:${{ github.sha }}

# BAD — building latest, no versioning
# docker build -t app:latest && docker push app:latest
```

## Config (III) — secrets in GitHub Secrets, not in YAML

```yaml
# GOOD — secrets injected from GitHub Secrets store
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}

# BAD — hardcoded in workflow file
env:
  DATABASE_URL: postgres://prod-db:5432/app
  API_KEY: sk-live-abc123
```

## Dev/Prod Parity (X) — CI uses same service versions as prod

```yaml
# GOOD — same Postgres version as production
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_PASSWORD: test
      POSTGRES_DB: app_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Admin Processes (XII) — migrations in pipeline

```yaml
# GOOD — migrations run before deploying new code
jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - name: Run migrations
        run: |
          kubectl run migrate \
            --image=${{ secrets.REGISTRY }}/app:${{ github.sha }} \
            --restart=Never \
            --rm \
            --env="DATABASE_URL=${{ secrets.DATABASE_URL }}" \
            -- npm run migrate
        timeout-minutes: 10

  deploy:
    needs: migrate
    # ...
```

## Dependencies (II) — pin action versions

```yaml
# GOOD — pinned versions for reproducibility
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

# BAD — floating version
- uses: actions/checkout@main
```
