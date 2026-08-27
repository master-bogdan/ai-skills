---
name: clean-code
description: Write and review clean, minimal code for React, Node.js, Go, and TypeScript projects. Use when generating, modifying, refactoring, fixing, or reviewing code. Prevents over-engineering, useless wrappers, god functions, too-many-arguments, reinventing existing code, needless React memoization, and convention drift. Applies universal clean code principles plus language-specific idioms.
---

# Clean Code

## Prime Directive

Write the least code that solves the actual problem clearly.

Before writing ANY code:

1. Read nearby files. Absorb local conventions.
2. **Search for what already exists.** Before writing a helper, component, hook,
   type, or constant, grep the project for one that already does it (by name and
   by behavior). Reuse or extend it instead of creating a parallel version.
3. Match what exists. Do NOT introduce new patterns unless asked.
4. Solve the stated problem. Nothing more.

## Hard Errors

These are the most common AI failures. Violating any is a hard error. The
numbered thresholds are bright lines — do not argue your way around them.

- **Tiny wrappers** — NEVER create a function that is one line or one action and
  just forwards to another (`getName = (u) => u.name`, `fetchUser = (id) =>
  api.get(id)`). Inline it. A function must add logic, a decision, or a name that
  hides real complexity — not just relay a call.
- **Premature extraction** — do NOT extract a block into a function the first or
  second time you write it. Extract for reuse ONLY when the SAME block appears
  **3+ times**. Two copies is fine — leave them inline. (Extracting to *name* a
  genuinely complex step is allowed even once; extracting to *dedupe* needs 3+.)
- **Too many arguments** — hard cap of **3** parameters. At 4+, group them into a
  single typed options/params object (`createOrder(input: CreateOrderInput)`).
  Never add a 4th positional arg. (TS/JS rule; in Go prefer a params struct past
  3, excluding a leading `ctx context.Context`.)
- **God functions** — longer than ~40 lines without clear justification.
- **God files** — do NOT dump unrelated code into one file. Split by
  *responsibility/domain*, not by line count. One module = one reason to change.
  No catch-all `utils.ts`, no 500-line component.
- **Needless memoization (React)** — do NOT wrap in `useMemo`/`useCallback`/
  `React.memo` unless there is a measured, concrete reason (a real perf problem,
  a referentially-stable dep a hook/child actually depends on). Default is plain
  values and plain functions.
- **Reinvention** — writing a new helper/component/hook/type when the project
  already has one. Search first (step 2 above); reuse or extend before creating.
- **Over-engineering** — abstractions, patterns, or config for one use case.
- **Convention drift** — introducing patterns the project doesn't use.
- **Noise comments** — restating what code already says.
- **Compressed one-liners** — never put `if` condition and body on the same line in TS/JS (Go `if err != nil { return err }` is OK).
- **Unreadable conditions** — extract complex conditions into named booleans. If a condition has chained `?.`, negated non-trivial expressions, callbacks, or exceeds ~60 chars, it MUST be extracted into a named variable that reads like English.

## Loading

The Hard Errors above are the always-on core — follow them without loading
anything else. Load detail files **only when the task touches them**, so the
bright lines above stay in focus instead of drowning in prose.

Always load the idiom file for the language you're writing or reviewing:

- [idioms/typescript.md](idioms/typescript.md) — any TS/JS
- [idioms/react.md](idioms/react.md) — React components/hooks
- [idioms/node.md](idioms/node.md) — Node backend (router/controller/service/repo)
- [idioms/go.md](idioms/go.md) — Go

Load a principle file when the change touches its concern:

- [principles/minimal-code.md](principles/minimal-code.md) — new abstraction, util, or config
- [principles/single-responsibility.md](principles/single-responsibility.md) — splitting/extracting functions or files
- [principles/dry.md](principles/dry.md) — duplication, shared logic, reuse decisions
- [principles/dependencies.md](principles/dependencies.md) — module boundaries, imports, layering
- [principles/naming.md](principles/naming.md) — naming anything non-trivial
- [principles/testing.md](principles/testing.md) — writing or reviewing tests
- [principles/security.md](principles/security.md) — external input, auth, secrets, logging
- [principles/twelve-factor.md](principles/twelve-factor.md) — config, state, backing services, logs

When in doubt or doing a broad review, load all of them.

## Modes

- **Generate** — write code following these rules.
- **Review** — audit code against these rules.

## Generate Self-Check

Before finishing, verify the code against the bright lines. Fix any that fail:

- [ ] Searched for and reused existing helpers/components/types (no reinvention)
- [ ] No one-line / one-action wrapper functions
- [ ] No block extracted for reuse before its 3rd occurrence
- [ ] No function with 4+ params (grouped into an options object)
- [ ] No `useMemo`/`useCallback`/`React.memo` without a stated concrete reason
- [ ] No new file mixing unrelated responsibilities
- [ ] Matched existing project conventions; no new patterns introduced
- [ ] Complex conditions extracted into named booleans

## Review Output

```
Fix:
- [file:line] what's wrong → what to do

Improve:
- [file:line] what's suboptimal → suggested change
```

No findings? Say "Clean." and nothing else.

### Review Example

```ts
// Reviewing this diff:

// 1
function getUserName(u: User) {
  return u.name;
}

// 2
async function loadUser(id: string) {
  return api.get(id);
}

// 3
function renderRow(
  name: string,
  age: number,
  city: string,
  isAdmin: boolean,
  teamId: string,
) {
  // ...
}

// 4
const label = useMemo(() => `${first} ${last}`, [first, last]);
```

```
Fix:
- [1] Tiny wrapper — inline `u.name` at call sites, delete `getUserName`
- [2] Tiny wrapper — call `api.get(id)` directly, delete `loadUser`
- [3] 5 params — group into `RenderRowInput` options object
- [4] Needless useMemo on a trivial string — use `const label = ` + template
```
