# IX. Disposability

Maximize robustness with fast startup and graceful shutdown. Processes should
start quickly (seconds, not minutes) and shut down gracefully when they receive
a SIGTERM. Crash-only design: processes can be killed at any time without data
loss.

## Explore

- Startup time — is there a heavy initialization step that blocks readiness?
- SIGTERM handling — does the app finish in-flight requests before exiting?
- k8s `preStop` hook and `terminationGracePeriodSeconds` configured?
- Database connections / queue consumers — are they closed on shutdown?
- Any work that could be lost if the process is killed mid-operation?

## Pass

- Starts within seconds (no multi-minute initialization)
- Handles `SIGTERM`: stops accepting new requests, finishes in-flight, exits cleanly
- Queue consumers `nack` or requeue messages on shutdown
- k8s lifecycle hooks configured for graceful drain

## Fail / Partial

- ❌ No SIGTERM handler — process killed mid-request, data potentially lost
- ❌ Startup takes minutes, causing slow rollouts and poor recovery
- ⚠️ SIGTERM handled but in-flight requests not given time to complete
- ⚠️ Missing k8s `preStop` hook causing requests dropped during rolling updates

## Examples

```ts
// GOOD — graceful shutdown
const server = app.listen(port);

process.on('SIGTERM', () => {
  server.close(() => {
    db.end();
    process.exit(0);
  });
});
```

```go
// GOOD
quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGTERM, syscall.SIGINT)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
server.Shutdown(ctx)
```

```yaml
# GOOD — k8s lifecycle hook + grace period
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 5"]
```
