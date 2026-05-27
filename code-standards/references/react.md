# React

## Load When

Load for React components, hooks, props, component folders, UI orchestration, and
React tests.

## Component Style

- React components are preferred as function declarations.
- Component symbols use `PascalCase`.
- Component folders and filenames use `kebab-case` for new files.
- Every subcomponent gets its own folder.
- Do not create multiple components in one file.
- Keep internal subcomponents private unless intentionally exported.

## Component Structure

Preferred shape for a complex component:

```text
workbook-toolbar/
  workbook-toolbar.tsx
  components/
    toolbar-button/
      toolbar-button.tsx
      index.ts
  hooks/
    use-workbook-toolbar.ts
  services/
    workbook-toolbar.service.ts
  constants.ts
  types.ts
  utils/
    map-toolbar-actions.ts
  index.ts
```

## Huge Component Smells

- 15+ props
- 10+ custom hooks
- rendering, orchestration, mapping, side effects, and permissions mixed
- hard to understand without a lot of scrolling

## Props

- Use smaller focused prop contracts.
- Group related `state`, `actions`, and `config` props when useful.
- Avoid giant prop bags.

## Hooks

- Hooks are preferred as exported arrow functions.
- Hooks own local UI orchestration.
- Hooks expose small predictable public APIs.
- Hooks stay focused on one concern.
- Hooks avoid raw transport details when a service/API layer exists.

## Blocking

- A component mixes rendering, orchestration, API calls, permissions, mapping,
  and unrelated side effects.
- Multiple components are added to one file.
- Props are a confusing everything bag.
- A hook becomes a second component or hides many unrelated side effects.
- A hook owns networking details directly when a service/API layer exists.

## Advisory

- A component is larger than ideal but still easy to scan.
- Existing PascalCase component filenames are outside scope.
- A few extra props still form one coherent contract.

## Examples

Good component:

```tsx
export function WorkbookToolbar() {
  return <div />;
}
```

Not preferred:

```tsx
export const WorkbookToolbar = () => {
  return <div />;
};
```

Good composition:

```tsx
export function WorkbookPage(props: WorkbookPageProps) {
  const viewModel = useWorkbookPage(props);

  return (
    <>
      <WorkbookHeader {...viewModel.header} />
      <WorkbookToolbar {...viewModel.toolbar} />
      <WorkbookTable {...viewModel.table} />
    </>
  );
}
```
