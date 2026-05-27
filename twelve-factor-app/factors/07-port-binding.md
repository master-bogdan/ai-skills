# VII. Port Binding

Export services via port binding. The app is completely self-contained and does
not rely on runtime injection of a webserver into the execution environment. It
binds to a port and listens for requests on that port.

## Explore

- Server startup code — does it bind its own port or depend on an external server process?
- `Dockerfile` — is there an `EXPOSE` directive?
- Is the port hardcoded or read from `PORT` env var?
- k8s Service / CloudFormation — does it reference the correct port?

## Pass

- App binds its own port via `PORT` env var (or sensible default)
- `Dockerfile` has matching `EXPOSE`
- No dependency on Apache/nginx to run the app (unless nginx is a deliberate reverse proxy layer)
- Port referenced consistently across Dockerfile, k8s Service, and load balancer config

## Fail / Partial

- ❌ App requires external server process injection to handle HTTP
- ❌ Port hardcoded in multiple places that can drift
- ⚠️ Port bound correctly but `EXPOSE` missing from Dockerfile (documentation gap)

## Examples

```ts
// GOOD — self-binding with env var
const port = parseInt(process.env.PORT ?? '3000', 10);
app.listen(port, () => console.log(`Listening on ${port}`));
```

```go
// GOOD
port := os.Getenv("PORT")
if port == "" {
    port = "8080"
}
http.ListenAndServe(":"+port, router)
```

```dockerfile
# GOOD
EXPOSE 8080
ENV PORT=8080
CMD ["./app"]
```

```yaml
# GOOD — k8s Service matches app port
spec:
  ports:
    - port: 80
      targetPort: 8080
```

```yaml
# GOOD — CloudFormation ECS task definition
ContainerDefinitions:
  - PortMappings:
      - ContainerPort: 8080
        Protocol: tcp
```
