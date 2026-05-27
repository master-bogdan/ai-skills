# Go Idioms

Language-specific conventions for Go projects.

## Core

- Accept interfaces, return structs
- Handle errors immediately after the call
- `context.Context` as first parameter for cancellation/deadlines
- Composition over inheritance (embed structs)
- Look at the standard library for style guidance

## Never

- Interfaces before you have 2+ implementations (or tests needing a mock)
- `interface{}` / `any` when a concrete type works
- `panic` — return errors
- Packages named `util`, `common`, `helpers`
- `init()` unless truly necessary
- Goroutine without clear lifecycle ownership
- Channel where a mutex is simpler

## Error Handling

```go
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doing something for order %s: %w", orderID, err)
}
```

- Wrap with context: WHO was doing WHAT for WHICH entity
- `%w` to preserve error chain
- Sentinel errors for expected conditions: `var ErrNotFound = errors.New("not found")`
- Custom error types only when callers need structured info

## Naming Conventions

- Short names for short scopes: `i`, `n`, `r`, `w`
- Longer names for longer scopes and exported symbols
- Package names: lowercase single words, no underscores
- No stutter: `user.User` not `user.UserStruct`
- No `Get` prefix on getters: `user.Name()` not `user.GetName()`
- Acronyms all caps: `HTTPClient`, `userID`, `parseJSON`

## Package Design

- One package = one idea
- Flat structure preferred over deep nesting
- `internal/` for private implementation

```
orders/
  orders.go
  repository.go
  handler.go
  orders_test.go
```

## Testing

- Table-driven tests for multiple cases
- `testdata/` for fixtures
- Test behavior, not implementation
- `_test.go` same package for white-box, `_test` suffix package for black-box

## One-Line Statements

Go idiomatically uses one-line error returns. This is correct:

```go
if err != nil {
    return err
}
```

But do NOT collapse multi-statement logic into one-liners. Stick to `gofmt` style.
