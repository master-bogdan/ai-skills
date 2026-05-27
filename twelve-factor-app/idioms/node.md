# Node.js — 12-Factor Idioms

## Config (III)

```ts
// Load and validate all env vars at startup — fail fast if missing
const config = {
  port: parseInt(process.env.PORT ?? '3000', 10),
  databaseUrl: required('DATABASE_URL'),
  redisUrl: required('REDIS_URL'),
  jwtSecret: required('JWT_SECRET'),
};

function required(key: string): string {
  const val = process.env[key];
  if (!val) throw new Error(`Missing required env var: ${key}`);
  return val;
}
```

## Backing Services (IV)

```ts
// Always config-driven, never hardcoded
const db = new Pool({ connectionString: process.env.DATABASE_URL });
const redis = new Redis(process.env.REDIS_URL);
const s3 = new S3Client({ region: process.env.AWS_REGION });
```

## Processes — Stateless (VI)

```ts
// BAD — in-memory session
const sessions = new Map();

// GOOD — Redis-backed session
app.use(session({
  store: new RedisStore({ client: redis }),
  secret: process.env.SESSION_SECRET,
}));
```

## Port Binding (VII)

```ts
const port = parseInt(process.env.PORT ?? '3000', 10);
const server = app.listen(port, () => {
  console.log(`Listening on :${port}`);
});
```

## Disposability (IX)

```ts
process.on('SIGTERM', async () => {
  await server.close();
  await db.end();
  await redis.quit();
  process.exit(0);
});
```

## Logs (XI)

```ts
// Use pino for structured JSON to stdout
import pino from 'pino';
const logger = pino({ level: process.env.LOG_LEVEL ?? 'info' });

// Good log entry
logger.info({ orderId, userId, action: 'order.created' }, 'Order created');

// Never log secrets
// BAD: logger.info({ token, password }, 'Auth')
```

## Admin Processes (XII)

```json
// package.json scripts for admin tasks
{
  "scripts": {
    "migrate": "node-pg-migrate up",
    "migrate:down": "node-pg-migrate down",
    "seed": "node scripts/seed.js",
    "backfill": "node scripts/backfill.js"
  }
}
```
