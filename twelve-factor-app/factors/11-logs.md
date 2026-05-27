# XI. Logs

Treat logs as event streams. A twelve-factor app never concerns itself with
routing or storage of its output stream. It writes to stdout. The execution
environment captures that stream and routes it to its destination (log
aggregator, file, terminal).

## Explore

- Logger setup — writing to stdout or to files?
- Any `fs.createWriteStream`, `winston.transports.File`, log rotation setup?
- Are logs structured (JSON) or unstructured plain text?
- Sensitive data (tokens, passwords, PII) in log output?
- k8s / CloudWatch / Datadog configured to collect stdout?

## Pass

- All logs written to stdout (or stderr for errors)
- Structured JSON logging in production
- No log file management in application code
- Log aggregation handled by platform (k8s, CloudWatch, Datadog)
- No secrets in log output

## Fail / Partial

- ❌ App writes logs to files and manages rotation itself
- ❌ Secrets, tokens, or PII logged
- ❌ Unstructured `console.log` strings in production with no context
- ⚠️ Stdout logging but no structured format, making aggregation hard

## Examples

```ts
// BAD — file-based logging
const logger = winston.createLogger({
  transports: [new winston.transports.File({ filename: '/var/log/app.log' })],
});

// GOOD — stdout structured logging
const logger = pino({ level: process.env.LOG_LEVEL ?? 'info' });
logger.info({ userId, orderId, action: 'order.created' }, 'Order created');
```

```go
// GOOD — structured stdout
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("order created", "orderId", order.ID, "userId", userID)
```

```yaml
# GOOD — k8s forwards stdout to log aggregator automatically
# No app-level log config needed beyond writing to stdout

# GOOD — CloudWatch log group for ECS stdout
LogConfiguration:
  LogDriver: awslogs
  Options:
    awslogs-group: /app/production
    awslogs-region: us-east-1
    awslogs-stream-prefix: app
```
