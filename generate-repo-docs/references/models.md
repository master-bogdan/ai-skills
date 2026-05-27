# docs/models.md Contract

Document the important models and their relationships. Not every type — only the
ones that matter for understanding the system.

## Focus

- Core domain entities with actual field names and types
- Transport models (API request/response shapes)
- Persistence models (DB row shapes)
- UI or adapter models
- Where translation between shapes happens and why

## Depth requirement

Document actual field names, types, and relationships from the code. Do not
describe models abstractly — read the source and reproduce real shapes.

Show where models transform between layers:

```
DB model (users table)
  → UserRecord { id, email, password_hash, created_at }
  → Service layer { id, email, createdAt }
  → API response { id, email }  ← password never returned
```

## Relationship diagrams

Include a simple ASCII relationship diagram when models have meaningful
relationships:

```
Order (1) ──── (*) OrderItem
  │
  └── (1) User
  └── (1) ShippingAddress
```

## Goal

Help a reader understand:
- what data the system works with and what shape it takes at each layer
- where they should make changes vs. where they should not
- what transforms between layers and why
