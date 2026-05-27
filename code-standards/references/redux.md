# Redux

## Load When

Load for Redux slices, selectors, thunks, services, shared feature state, and
React code that reads or mutates shared state.

## Preferred Structure

```text
features/
  imports/
    store/
      import.slice.ts
      import.selectors.ts
      import.thunks.ts
      import.types.ts
```

## Ownership

- Components own rendering and UI composition.
- Hooks own local orchestration and component-specific behavior.
- Redux slices own shared feature state and reducers for state transitions.
- Selectors read and derive state.
- Thunks own async workflows and dispatch orchestration.
- Services own API interaction and external communication.
- Utils own pure transformations.

## When To Use Redux

Use Redux for:

- shared state across screens/components
- business-relevant state with centralized transitions
- feature state that benefits from selectors/reducers

Do not use Redux for:

- tiny local toggles
- one-component transient state
- local form state unless there is a real shared need

## Blocking

- A component performs API calls, payload mapping, retry logic, dispatch
  orchestration, and helper component definitions together.
- Redux is used for purely local component state in new code.
- Shared state transitions are scattered outside slices/reducers.
- Selectors or thunks leak unrelated feature internals.

## Advisory

- A selector could be extracted but current derivation is local and obvious.
- Existing Redux organization is slightly inconsistent but outside scope.

## Examples

Good:

```text
WorkbookPage.tsx
  -> renders page
use-workbook-page.ts
  -> combines selectors, dispatch, and local UI behavior
workbook.selectors.ts
  -> derived data
workbook.thunks.ts
  -> async flows
workbook.service.ts
  -> API integration
```

Bad:

```text
WorkbookPage.tsx
  -> renders
  -> API calls
  -> payload mapping
  -> retry logic
  -> dispatch logic
  -> helper components
```
