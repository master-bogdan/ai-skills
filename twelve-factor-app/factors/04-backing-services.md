# IV. Backing Services

Treat backing services as attached resources. A backing service is any service
the app consumes over the network: databases, message queues, caches, email
services, S3. They should be swappable via config change with no code change.

## Explore

- Database connection setup — hardcoded host or env var?
- Redis/cache connection — hardcoded or configurable?
- Email/SMS service — SDK initialized with hardcoded key or env var?
- S3/blob storage — hardcoded bucket name or env var?
- Any service URL that differs between local and production

## Pass

- All backing service URLs and credentials come from environment variables
- Local and production services are interchangeable via config swap
- No code changes required to point at a different database or queue

## Fail / Partial

- ❌ Hardcoded database host, Redis URL, or S3 bucket name
- ❌ Different code paths for local vs. production backing services
- ⚠️ Service URL in env var but credentials hardcoded

## Examples

```ts
// BAD — hardcoded backing service
const redis = new Redis('redis://localhost:6379');
const s3 = new S3Client({ region: 'us-east-1', bucket: 'my-prod-bucket' });

// GOOD — attached resource via config
const redis = new Redis(process.env.REDIS_URL);
const s3 = new S3Client({
  region: process.env.AWS_REGION,
  bucket: process.env.S3_BUCKET,
});
```

```go
// GOOD
db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
```

```yaml
# GOOD — CloudFormation parameter for RDS endpoint
Parameters:
  DatabaseUrl:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /app/prod/database-url
```
