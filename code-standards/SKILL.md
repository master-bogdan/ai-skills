---
name: code-standards
description: Apply project code standards automatically before generating, modifying, refactoring, fixing, or reviewing TypeScript, React, Redux, or Node.js code. Use for explicit standards questions, code quality checks, reviews, and implementation tasks in these stacks; do not use for unrelated docs, shell config, image generation, or pure planning unless explicitly invoked.
---

# Code Standards

Use this skill to generate and review code against the project standards.

The skill is self-contained. Do not depend on external standards files at
runtime.

## Modes

Infer the mode from the user request:

- Implementation mode: implement, refactor, fix, or generate code.
- Review mode: review, check, audit, or inspect code quality.
- Advisory mode: answer standards questions or recommend a design direction.

## Workflow

1. Identify the target files from the request, open tabs, current working
   directory, or explicit paths. Ask only if the target is ambiguous.
2. Inspect nearby code before editing or reviewing. Existing coherent local
   patterns win unless they violate a Blocking rule.
3. Load only the reference files relevant to the files and concerns involved.
4. Generate or review code according to the loaded references.
5. Treat Blocking rules as must-fix for touched or newly created code.
6. Treat Advisory rules as improvements that should not derail the task unless
   the user asked for cleanup.
7. Run relevant validation when available.

## Blocking vs Advisory

Classify findings only as `Blocking` or `Advisory`.

Use:

- Blocking: security issues, missing validation boundaries, data integrity
  risks, architecture boundary breaks, dangerous hidden behavior, circular
  dependencies, wrong-layer logic, or code that materially harms maintenance.
- Advisory: naming improvements, extraction timing, small local duplication,
  local organization, comment polish, or style improvements.

For new files and touched code, Blocking rules must be fixed before completion.
For existing untouched code, report Blocking issues only when they affect the
requested change or review scope.

## Reference Selection

Load these files as needed:

- [references/naming.md](references/naming.md): symbol naming rules.
- [references/file-naming.md](references/file-naming.md): filename suffixes,
  kebab-case, React file naming, and test scope suffixes.
- [references/responsibility.md](references/responsibility.md): Single
  Responsibility Principle and mixed responsibilities.
- [references/function-size.md](references/function-size.md): small functions
  and readable control flow.
- [references/module-boundaries.md](references/module-boundaries.md): layers,
  public/private module boundaries, and wrong-layer logic.
- [references/coupling-and-cohesion.md](references/coupling-and-cohesion.md):
  cohesion, coupling, cross-feature imports, and circular dependencies.
- [references/dry.md](references/dry.md): duplicated knowledge versus harmless
  local repetition.
- [references/simplicity.md](references/simplicity.md): KISS and unnecessary
  indirection.
- [references/yagni.md](references/yagni.md): speculative future-proofing.
- [references/functional-solid.md](references/functional-solid.md): Open/Closed,
  Interface Segregation, and Dependency Inversion in functional code.
- [references/magic-values.md](references/magic-values.md): magic numbers,
  strings, booleans, and hidden defaults.
- [references/comments-and-exceptions.md](references/comments-and-exceptions.md):
  comments, TODOs, unsafe exceptions, and approved deviations.
- [references/typescript.md](references/typescript.md): TypeScript contracts,
  `any`, casts, arrows, and immutability.
- [references/react.md](references/react.md): React components, hooks, props,
  and component structure.
- [references/redux.md](references/redux.md): Redux state ownership, slices,
  selectors, thunks, and services.
- [references/node-backend.md](references/node-backend.md): Node backend
  routes/controllers/services/repositories/DTO/logging/module structure.
- [references/testing.md](references/testing.md): test strategy and scope.
- [references/security.md](references/security.md): validation, authorization,
  secrets, trust boundaries, and unsafe input.
- [references/review-output.md](references/review-output.md): strict review
  output templates.

## Output

In implementation mode, keep the final answer brief:

- changed files or behavior
- validation run
- any remaining Blocking issue that could not be fixed

In review mode, use [references/review-output.md](references/review-output.md).

In advisory mode, cite the applicable rule and give a direct recommendation.
