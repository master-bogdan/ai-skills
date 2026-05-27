# VIII. Concurrency

Scale out via the process model. Scale is achieved by running more processes, not
by making a single process bigger. Different workloads run as different process
types (web, worker, scheduler). Each process type scales independently.

## Explore

- Is there a `Procfile` or equivalent process type declaration?
- k8s — are web and worker deployments separate with independent replica counts?
- Are CPU/memory-heavy background jobs separated from web request handlers?
- Docker Compose — separate services for web and workers?
- Any single-threaded bottleneck that blocks horizontal scaling?

## Pass

- Web and worker processes are separate and scale independently
- Process types declared (Procfile, separate k8s Deployments, separate ECS services)
- No shared mutable state between process instances
- Background jobs don't block request handling

## Fail / Partial

- ❌ Background jobs run inside the web process, blocking request handling
- ❌ Single monolithic process that can't be scaled horizontally
- ⚠️ Web and workers in same process but separated by threading (acceptable if stateless)

## Examples

```yaml
# GOOD — separate k8s Deployments
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3   # scale independently
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
spec:
  replicas: 5   # scale based on queue depth
```

```yaml
# GOOD — Docker Compose process types
services:
  web:
    command: node server.js
    ports: ["3000:3000"]
  worker:
    command: node worker.js
```

```
# GOOD — Procfile
web: node server.js
worker: node worker.js
scheduler: node scheduler.js
```

```yaml
# BAD — workers running inside web process via setInterval
# server.js starts HTTP server AND runs background jobs in same process
```
