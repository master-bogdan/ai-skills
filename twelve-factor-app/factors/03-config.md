# III. Config

Store config in the environment. Config is everything that varies between
deploys (staging, prod, dev). This includes database URLs, credentials, API
keys, and per-environment feature flags. Config must never be committed to the
repo.

## Explore

- Scan source files for hardcoded URLs, IPs, credentials, API keys
- Check `.env*` files — are any committed (not just `.env.example`)?
- Check `config/` directories for environment-specific files with real values
- Check CI configs for secrets hardcoded in plain text
- Check Dockerfiles and k8s manifests for hardcoded env values

## Pass

- All config loaded from environment variables
- `.env.example` committed, `.env` gitignored
- Secrets managed via secret store (AWS SSM, k8s Secrets, GitHub Secrets)
- No environment-specific config files with real values committed

## Fail / Partial

- ❌ Database URLs, API keys, or passwords hardcoded in source
- ❌ `.env` file committed to git
- ❌ `config/production.json` with real credentials committed
- ⚠️ Some config in env vars but some still hardcoded

## Examples

```ts
// BAD
const db = new Client({ host: 'prod-db.internal', password: 'secret123' });

// GOOD
const db = new Client({
  host: process.env.DB_HOST,
  password: process.env.DB_PASSWORD,
});
```

```go
// BAD
const apiKey = "sk-live-abc123"

// GOOD
apiKey := os.Getenv("API_KEY")
if apiKey == "" {
    log.Fatal("API_KEY is required")
}
```

```yaml
# BAD — k8s manifest with hardcoded value
env:
  - name: DB_PASSWORD
    value: "secret123"

# GOOD — k8s manifest referencing a Secret
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: password
```
