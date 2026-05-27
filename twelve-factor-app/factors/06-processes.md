# VI. Processes

Execute the app as one or more stateless processes. Processes are stateless and
share nothing. Any data that needs to persist must be stored in a stateful
backing service (database, cache). In-process memory and filesystem are
ephemeral — never assume they survive a restart.

## Explore

- Request handlers — do they write to in-memory state that must survive restarts?
- Session storage — stored in process memory or in an external store?
- File uploads — written to local disk or to object storage?
- Caches — in-process caches that can't be shared across instances?
- Any use of global mutable state that accumulates across requests

## Pass

- Sessions stored in Redis/database, not in-process memory
- File uploads sent to object storage (S3, GCS), not local disk
- No in-process state that must survive a restart
- Multiple instances of the process can run without conflict

## Fail / Partial

- ❌ Sessions stored in process memory (`Map`, global variable)
- ❌ Uploaded files written to local disk with no external storage
- ❌ In-memory job queue with no persistence
- ⚠️ In-process cache acceptable if cache miss is non-fatal and backing service is source of truth

## Examples

```ts
// BAD — in-memory session state
const sessions = new Map<string, Session>();
app.post('/login', (req, res) => {
  sessions.set(req.body.userId, { loggedInAt: Date.now() });
});

// GOOD — session in Redis
app.post('/login', async (req, res) => {
  await redis.set(`session:${req.body.userId}`, JSON.stringify({ loggedInAt: Date.now() }));
});
```

```go
// BAD — global mutable state
var requestCount int64

// GOOD — emit metric to external store
metrics.Increment("request.count")
```

```yaml
# BAD — k8s with local volume for uploads
volumes:
  - name: uploads
    emptyDir: {}

# GOOD — use S3/GCS, no local volume needed
env:
  - name: UPLOAD_BUCKET
    value: my-app-uploads
```
