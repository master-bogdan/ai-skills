# I. Codebase

One codebase tracked in version control, many deploys. A twelve-factor app is
always tracked in a version control system. There is exactly one codebase per
app — multiple apps sharing the same code is a violation.

## Explore

- Is there a `.git/` directory at the root?
- Is there a monorepo with multiple apps? If so, does each app have its own
  deployment pipeline?
- Are there multiple repos that share code by copy-paste rather than dependency?

## Pass

- Single git repo per deployable app
- Shared code extracted into libraries/packages with their own versioning
- Multiple environments (staging, prod) deploy from the same repo

## Fail / Partial

- ❌ No version control
- ❌ Same codebase deployed as multiple different apps without separation
- ⚠️ Shared code copy-pasted across repos instead of published as a dependency
- ⚠️ Monorepo with no clear per-app deployment boundaries

## Examples

```
# GOOD — monorepo with clear app boundaries
apps/
  api/          ← deploys independently
  worker/       ← deploys independently
  web/          ← deploys independently
packages/
  shared-utils/ ← versioned internal package

# BAD — shared code duplicated
repo-a/src/utils/format.ts   ← copy
repo-b/src/utils/format.ts   ← copy (drifted)
```
