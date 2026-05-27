---
name: clean-code
description: Write and review clean, minimal code for React, Node.js, Go, and TypeScript projects. Use when generating, modifying, refactoring, fixing, or reviewing code. Prevents over-engineering, useless wrappers, god functions, and convention drift. Applies universal clean code principles plus language-specific idioms.
---

# Clean Code

## Prime Directive

Write the least code that solves the actual problem clearly.

Before writing ANY code:

1. Read nearby files. Absorb local conventions.
2. Match what exists. Do NOT introduce new patterns unless asked.
3. Solve the stated problem. Nothing more.

## Hard Errors

These are the most common AI failures. Violating any is a hard error:

- **Useless wrappers** — a function that just calls another without adding logic.
- **Over-engineering** — abstractions, patterns, or config for one use case.
- **God functions** — longer than ~40 lines without clear justification.
- **Pointless splitting** — tiny functions that move code without clarifying intent.
- **Convention drift** — introducing patterns the project doesn't use.
- **Noise comments** — restating what code already says.
- **Compressed one-liners** — never collapse logic into a single line unless the language idiom demands it (Go `if err != nil { return err }` is OK; `if(x) return y` in TS/JS is not).

## Loading

Always load all principle files:

- [principles/minimal-code.md](principles/minimal-code.md)
- [principles/single-responsibility.md](principles/single-responsibility.md)
- [principles/dry.md](principles/dry.md)
- [principles/dependencies.md](principles/dependencies.md)
- [principles/naming.md](principles/naming.md)
- [principles/testing.md](principles/testing.md)
- [principles/security.md](principles/security.md)
- [principles/twelve-factor.md](principles/twelve-factor.md)

Load idiom file matching the language being written or reviewed:

- [idioms/typescript.md](idioms/typescript.md)
- [idioms/react.md](idioms/react.md)
- [idioms/node.md](idioms/node.md)
- [idioms/go.md](idioms/go.md)

## Modes

- **Generate** — write code following these rules.
- **Review** — audit code against these rules.

## Review Output

```
Fix:
- [file:line] what's wrong → what to do

Improve:
- [file:line] what's suboptimal → suggested change
```

No findings? Say "Clean." and nothing else.
