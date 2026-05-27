# React — 12-Factor Idioms

## Config (III)

React apps run in the browser — never put secrets in client-side code.

```ts
// .env.example — commit this, shows available config
REACT_APP_API_URL=https://api.example.com
REACT_APP_ANALYTICS_ID=UA-XXXXXXX

// .env.local — gitignored, developer-specific
// .env.production — gitignored, injected by CI/platform
```

```ts
// BAD — secret in client bundle
const apiKey = process.env.REACT_APP_SECRET_KEY; // visible to anyone

// GOOD — secrets never leave the server; frontend only gets public config
const apiUrl = process.env.REACT_APP_API_URL;
// Actual API calls go through your backend which holds the secrets
```

## Processes — Stateless (VI)

React frontends are stateless by nature (browser holds state). Pitfalls:

```ts
// BAD — module-level mutable state shared across SSR renders (if using SSR)
let currentUser: User | null = null; // shared across all requests on server

// GOOD — state scoped to component or context
const [currentUser, setCurrentUser] = useState<User | null>(null);
```

## Dev/Prod Parity (X)

```ts
// BAD — bypassing auth or mocking APIs in development
if (process.env.NODE_ENV === 'development') {
  // skip auth check
  return <App />;
}

// GOOD — use real dev credentials, .env.local for local config
// Never branch on NODE_ENV for core logic
```

## Logs (XI)

```ts
// BAD — logging sensitive data to browser console
console.log('Auth token:', token);
console.log('User:', JSON.stringify(user)); // PII in console

// GOOD — log only safe, actionable info
console.error('Failed to load orders', { orderId, status });
// In production, route errors to a monitoring service (Sentry, Datadog)
```

## Build/Release/Run (V)

```dockerfile
# GOOD — React SPA: build static assets, serve with nginx
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```sh
# BAD — different build per environment (violates build/release/run)
# npm run build:production
# npm run build:staging

# GOOD — one build, config via env at build time or runtime
# docker build --build-arg REACT_APP_API_URL=$API_URL .
```
