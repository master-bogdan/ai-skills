# Go — 12-Factor Idioms

## Config (III)

```go
// Centralized config struct, loaded from env at startup
type Config struct {
    Port        string
    DatabaseURL string
    RedisURL    string
    JWTSecret   string
}

func LoadConfig() (*Config, error) {
    cfg := &Config{
        Port:        getEnv("PORT", "8080"),
        DatabaseURL: requireEnv("DATABASE_URL"),
        RedisURL:    requireEnv("REDIS_URL"),
        JWTSecret:   requireEnv("JWT_SECRET"),
    }
    return cfg, nil
}

func requireEnv(key string) string {
    val := os.Getenv(key)
    if val == "" {
        log.Fatalf("required env var %s is not set", key)
    }
    return val
}

func getEnv(key, fallback string) string {
    if val := os.Getenv(key); val != "" {
        return val
    }
    return fallback
}
```

## Backing Services (IV)

```go
db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
rdb := redis.NewClient(&redis.Options{Addr: os.Getenv("REDIS_URL")})
```

## Port Binding (VII)

```go
port := os.Getenv("PORT")
if port == "" {
    port = "8080"
}
if err := http.ListenAndServe(":"+port, router); err != nil {
    log.Fatal(err)
}
```

## Disposability (IX)

```go
srv := &http.Server{Addr: ":" + port, Handler: router}

go func() {
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatal(err)
    }
}()

quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGTERM, syscall.SIGINT)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
defer cancel()
srv.Shutdown(ctx)
db.Close()
```

## Logs (XI)

```go
// Structured JSON to stdout with slog
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("order created",
    slog.String("orderId", order.ID),
    slog.String("userId", userID),
    slog.String("action", "order.created"),
)
```

## Admin Processes (XII)

```go
// cmd/ directory pattern — separate binaries for admin tasks
cmd/
  server/main.go      // web server
  worker/main.go      // background worker
  migrate/main.go     // run migrations
  backfill/main.go    // one-off data scripts

// Each shares the same config loading, same DATABASE_URL
```
