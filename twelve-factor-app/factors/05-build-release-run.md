# V. Build, Release, Run

Strictly separate build and run stages. The build stage transforms code into an
executable bundle. The release stage combines the build with config. The run
stage executes the release. These three stages must be strictly separated —
you cannot change code at runtime, and a release is immutable.

## Explore

- `Dockerfile` — does it bake config into the image (violates build/release separation)?
- CI pipeline — is there a clear build → release → deploy sequence?
- Are releases versioned/tagged or overwritten in place?
- Can you roll back to a previous release without rebuilding?
- Is there any runtime code modification (writing to app files, `eval` of fetched code)?

## Pass

- Docker image built without environment-specific config
- Config injected at runtime via env vars or secrets
- Releases are tagged/versioned (git tag, image tag)
- Rollback is possible by redeploying a previous image tag

## Fail / Partial

- ❌ Config baked into Docker image at build time
- ❌ No release versioning — always deploying `latest`
- ❌ Code modified at runtime (writing to mounted source, fetching and eval-ing scripts)
- ⚠️ Release versioning exists but rollback process is manual and undocumented

## Examples

```dockerfile
# BAD — config baked into image
ARG DB_PASSWORD=secret123
ENV DB_PASSWORD=$DB_PASSWORD
RUN echo "DB_PASSWORD=$DB_PASSWORD" >> /app/.env

# GOOD — image is config-free
FROM node:20-alpine
WORKDIR /app
COPY package*.json .
RUN npm ci --production
COPY . .
CMD ["node", "server.js"]
# Config injected at runtime via docker run -e or k8s env
```

```yaml
# GOOD — GitHub Actions: build once, deploy immutable tag
- name: Build and push
  run: |
    docker build -t app:${{ github.sha }} .
    docker push app:${{ github.sha }}

- name: Deploy
  run: kubectl set image deployment/app app=app:${{ github.sha }}
```

```yaml
# BAD — always deploying latest, no versioning
- run: docker build -t app:latest . && docker push app:latest
```
