# Coupling And Cohesion

## Load When

Load when code is spread across features, shared utilities, or modules, or when
dependencies feel brittle.

## Rules

- Things that change together should live together.
- Things that should evolve independently should not be tightly coupled.
- Shared helpers must be truly domain-agnostic or intentionally shared.
- Avoid circular dependencies between features or backend modules.

## Blocking

- Circular dependencies are introduced or extended.
- One feature depends on another feature's internals.
- A shared utility knows too much about many domains.
- A change requires editing unrelated code paths because boundaries are brittle.

## Advisory

- Organization is slightly awkward but local and stable.
- A helper could move closer to the feature it belongs to.

## Examples

Good cohesive feature:

```text
modules/
  imports/
    controller.ts
    dto/
    repositories/
    services/
    utils/
```

Bad scattered feature:

```text
features/
  imports/
    components/
  shared/
    import-hooks/
  random/
    import-utils/
```
