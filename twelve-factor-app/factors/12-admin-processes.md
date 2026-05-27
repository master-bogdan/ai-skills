# XII. Admin Processes

Run admin/management tasks as one-off processes. Admin tasks (database
migrations, data backups, one-off scripts) should run in the same environment
as regular processes — same release, same config, same codebase. They should
not be run ad-hoc on production servers via SSH.

## Explore

- `scripts/` or `bin/` directory — how are one-off tasks run?
- Database migrations — are they automated in CI/CD or run manually?
- Is there a `Makefile`, `package.json` scripts, or `Taskfile` for admin tasks?
- k8s `Job` or `CronJob` resources for scheduled tasks?
- Any SSH access patterns for running tasks directly on production instances?

## Pass

- Migrations run automatically as part of deployment pipeline
- One-off scripts run via CI/CD job or k8s Job, not SSH into containers
- Admin scripts use the same environment config as the app
- Scheduled tasks defined as k8s CronJob or equivalent, not cron on a server

## Fail / Partial

- ❌ Migrations run manually via SSH into production
- ❌ Admin scripts have hardcoded credentials separate from app config
- ❌ Scheduled tasks set up as cron jobs on EC2 instances
- ⚠️ Migrations automated but one-off data scripts still run manually

## Examples

```yaml
# GOOD — migration as part of CI/CD deploy step
- name: Run migrations
  run: |
    kubectl run migrate --image=app:${{ github.sha }} \
      --restart=Never --rm \
      -- npm run migrate
```

```yaml
# GOOD — k8s Job for one-off task
apiVersion: batch/v1
kind: Job
metadata:
  name: backfill-orders
spec:
  template:
    spec:
      containers:
        - name: backfill
          image: app:v1.2.3
          command: ["node", "scripts/backfill-orders.js"]
          envFrom:
            - secretRef:
                name: app-secrets
      restartPolicy: Never
```

```yaml
# GOOD — k8s CronJob for scheduled task
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: report
              image: app:latest
              command: ["node", "scripts/generate-report.js"]
```

```sh
# BAD — SSH into production to run a script
ssh prod-server "cd /app && node scripts/fix-data.js"
```
