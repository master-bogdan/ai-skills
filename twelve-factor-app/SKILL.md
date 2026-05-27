---
name: twelve-factor-app
description: Audit a repository for 12-factor app compliance and write a scored report to docs/twelve-factor-report.md. Use when explicitly invoked with /twelve-factor, "audit 12-factor", "check 12-factor compliance", or "is this app 12-factor".
---

# 12-Factor App Audit

## Workflow

1. **Detect stack** — scan repo root for: `package.json`, `go.mod`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`, `.github/`, `k8s/`, `kubernetes/`, `cloudformation/`, `*.tf`
2. **Load all factor files** — always load all 12:
   - [factors/01-codebase.md](factors/01-codebase.md)
   - [factors/02-dependencies.md](factors/02-dependencies.md)
   - [factors/03-config.md](factors/03-config.md)
   - [factors/04-backing-services.md](factors/04-backing-services.md)
   - [factors/05-build-release-run.md](factors/05-build-release-run.md)
   - [factors/06-processes.md](factors/06-processes.md)
   - [factors/07-port-binding.md](factors/07-port-binding.md)
   - [factors/08-concurrency.md](factors/08-concurrency.md)
   - [factors/09-disposability.md](factors/09-disposability.md)
   - [factors/10-dev-prod-parity.md](factors/10-dev-prod-parity.md)
   - [factors/11-logs.md](factors/11-logs.md)
   - [factors/12-admin-processes.md](factors/12-admin-processes.md)
3. **Load idiom files** matching detected stack:
   - [idioms/node.md](idioms/node.md) — if `package.json` present
   - [idioms/go.md](idioms/go.md) — if `go.mod` present
   - [idioms/react.md](idioms/react.md) — if React detected
   - [idioms/docker.md](idioms/docker.md) — if `Dockerfile` or `docker-compose.yml` present
   - [idioms/github-actions.md](idioms/github-actions.md) — if `.github/workflows/` present
   - [idioms/kubernetes.md](idioms/kubernetes.md) — if `k8s/` or `kubernetes/` present
   - [idioms/aws-cloudformation.md](idioms/aws-cloudformation.md) — if `cloudformation/` or `template.yaml` present
4. **Explore** files relevant to each factor (see exploration map in each factor file)
5. **Assess** each factor: ✅ Pass / ❌ Fail / ⚠️ Partial / N/A
6. **Write report** to `docs/twelve-factor-report.md` (create `docs/` if missing)
7. **Print summary** — score + list of failures to conversation

## Report Format

```md
# 12-Factor App Report
Generated: YYYY-MM-DD

## Score: X/12

| Factor | Status | Notes |
|--------|--------|-------|
| I. Codebase | ✅ Pass | Single repo, tracked in git |
| III. Config | ❌ Fail | DB_URL hardcoded in config/database.go:14 |

## Findings

### ❌ III. Config
**Problem:** `DB_URL` hardcoded in `config/database.go:14`
**Fix:** Load from `os.Getenv("DB_URL")`, document in `.env.example`

## Compliant Factors
I, IV, VII — no action needed.
```
