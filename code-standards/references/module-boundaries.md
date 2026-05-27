# Module Boundaries

## Load When

Load when code crosses layers, features, modules, public exports, or private
internals.

## Rules

- Keep boundaries between layers and modules explicit.
- Use public entry points between features and modules.
- Keep local internals private unless intentionally exported.
- Do not bypass agreed architecture with ad hoc shortcuts.
- Stable public boundaries are preferred over cross-module shortcuts.

## Blocking

- UI code owns backend persistence, HTTP response handling, or server-only
  business rules.
- Controllers/routers own business logic instead of validating and delegating.
- Repositories own business rules or HTTP behavior.
- A module imports another module's private files when a public boundary exists.
- A shortcut bypasses an agreed architecture boundary.

## Advisory

- Public boundary exports are slightly awkward but safe.
- Folder placement could be improved without changing behavior.

## Examples

Good:

```text
features/
  imports/
    index.ts
  workbooks/
    index.ts

workbooks imports from features/imports/index.ts
```

Bad:

```text
features/workbooks/hooks/use-workbook-toolbar.ts
  imports from features/imports/services/private-import-mapper.ts
```
