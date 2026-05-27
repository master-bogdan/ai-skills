# Kubernetes — 12-Factor Idioms

## Config (III) — ConfigMap and Secrets

```yaml
# GOOD — config from ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  PORT: "8080"
  AWS_REGION: "us-east-1"

---
# GOOD — secrets from Secret (base64 encoded, use sealed-secrets or external-secrets in prod)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgres://user:pass@db:5432/app"
  JWT_SECRET: "changeme"

---
# Deployment references both
spec:
  containers:
    - envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
```

## Concurrency (VIII) — separate Deployments per process type

```yaml
# GOOD — web and worker scale independently
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      role: web
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
spec:
  replicas: 5          # different scale
  selector:
    matchLabels:
      app: myapp
      role: worker
```

## Disposability (IX) — graceful shutdown

```yaml
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - name: app
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 5"]   # drain connections
      readinessProbe:
        httpGet:
          path: /health
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 10
      livenessProbe:
        httpGet:
          path: /health
          port: 8080
        initialDelaySeconds: 15
        periodSeconds: 20
```

## Port Binding (VII) — Service definition

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    app: myapp
    role: web
  ports:
    - port: 80
      targetPort: 8080   # must match PORT env var in app
```

## Admin Processes (XII) — Jobs and CronJobs

```yaml
# One-off migration Job
apiVersion: batch/v1
kind: Job
metadata:
  name: migrate-v1-2-3
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: registry/app:v1.2.3
          command: ["npm", "run", "migrate"]
          envFrom:
            - secretRef:
                name: app-secrets
      restartPolicy: Never
  backoffLimit: 2

---
# Scheduled CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-cleanup
spec:
  schedule: "0 3 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: cleanup
              image: registry/app:latest
              command: ["node", "scripts/cleanup.js"]
              envFrom:
                - secretRef:
                    name: app-secrets
          restartPolicy: OnFailure
```
