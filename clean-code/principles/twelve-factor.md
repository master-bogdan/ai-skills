# Twelve-Factor (Code-Level)

These are the 12-factor principles enforceable at the code level. For full
infrastructure/deployment factors, use the twelve-factor-app skill.

## 1. Config via Environment

Never hardcode connection strings, API URLs, secrets, or environment-specific values.

```
// BAD
const API_URL = 'https://api.production.example.com';
const DB_HOST = 'prod-db-01.internal';

// GOOD
const API_URL = process.env.API_URL;
const DB_HOST = process.env.DB_HOST;
```

## 2. Stateless Processes

Do not store session state, caches, or user data in process memory expecting it
to persist across requests.

```
// BAD — in-memory state that dies with the process
const sessions = new Map<string, Session>();

// GOOD — external backing service
const session = await sessionStore.get(sessionId);
```

## 3. Logs as Streams

Write structured logs to stdout. Do not write to files, manage rotation, or
conditionally log based on environment.

```
// BAD
fs.appendFileSync('/var/log/app.log', message);
if (process.env.NODE_ENV !== 'production') console.log(message);

// GOOD
logger.info({ orderId, action: 'created' }, 'Order created');
```

## 4. Port Binding

The service is self-contained. It binds its own port and does not depend on
runtime injection of a web server.

## 5. Backing Services as Attached Resources

Databases, queues, caches, email services — all accessed via config (URLs/credentials
from environment). Swappable without code changes.

```
// BAD — hardcoded backing service
const redis = new Redis('redis://localhost:6379');

// GOOD — config-driven
const redis = new Redis(process.env.REDIS_URL);
```
