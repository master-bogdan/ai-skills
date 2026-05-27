# React Idioms

Language-specific conventions for React projects.

## Components

- Function declarations: `export function MyComponent() {}`
- One component per file
- Props interface co-located, destructured in signature
- Keep under 80 lines — extract when responsibility is genuinely distinct
- Composition over prop drilling: children, render props, context

## Hooks

- One concern per hook
- Minimal return API: `{ data, isLoading, error }` — not a kitchen sink
- Custom hooks for reusable state logic
- If a hook just wraps `useState` + one setter, inline it — that's a useless wrapper

## State

- Local state for local things: `useState`
- Shared state for shared things: context, store, URL params
- Derive don't store: if computable, don't put it in state
- Lift state only when 2+ components actually need it

## Rendering

- Early return for loading/error/empty states
- Named booleans for complex conditions
- No logic in JSX beyond simple conditionals and `.map()`
- Never nest ternaries more than one level

## Anti-Patterns to Reject

- `useEffect` to sync derived state (compute it directly)
- `React.memo` / `useCallback` on everything without measured need
- Props bags with 10+ unrelated fields (split the component)
- `forwardRef` + `useImperativeHandle` when a callback prop works
- Hooks that secretly do rendering logic (they're components in disguise)

## Naming Conventions

- Components: `PascalCase`
- Component files: match project (check existing — could be kebab or Pascal)
- Hooks: `use-` prefix, `camelCase` function name
- Event handlers: `onAction` for props, `handleAction` internally

## Structure

Only create folders when complexity justifies it:

```
feature/
  feature.tsx
  components/
    feature-header.tsx
  hooks/
    use-feature-data.ts
  types.ts
```

A 50-line component does NOT need a folder with 5 files.

## Example

```tsx
interface OrderCardProps {
  order: Order;
  onCancel: (id: string) => void;
}

export function OrderCard({ order, onCancel }: OrderCardProps) {
  const isOverdue = order.dueAt < Date.now();

  if (order.status === 'cancelled') return null;

  return (
    <Card>
      <CardTitle>{order.title}</CardTitle>
      {isOverdue && <Badge variant="warning">Overdue</Badge>}
      <Button onClick={() => onCancel(order.id)}>Cancel</Button>
    </Card>
  );
}
```
