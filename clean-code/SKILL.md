---
name: clean-code
description: Clean, minimal code rules for TypeScript, JavaScript, React, Node.js, and Go — with a required search-before-writing step, plus hooks that check every edit and check again before finishing. Use whenever you write, modify, fix, refactor, or review code in these languages, including small edits and follow-up fixes, even if the user never says "clean code". Stops tiny wrapper functions, premature helper extraction, needless useMemo/useCallback/React.memo, one-line ifs, 4+ parameter functions, reinventing helpers the project already has, and drifting from the project's conventions. Also use it ("/clean-code review") when reviewing another agent's or a PR's changes.
allowed-tools: Bash(python3 *clean-code/scripts/check.py*)
hooks:
  PostToolUse:
    - matcher: "Edit|Write|MultiEdit"
      hooks:
        - type: command
          command: python3 "${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/clean-code}/scripts/hook.py"
  Stop:
    - hooks:
        - type: command
          command: python3 "${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/clean-code}/scripts/hook.py"
---

# Clean Code

The goal: the least code that solves the problem clearly, written the way this
project already writes code.

## Why this skill exists

The rules below target the habits a coding agent falls back on by default:
wrapping a call in a helper "for readability", extracting a function the first
time a block appears, memoizing "for performance", squeezing an `if` onto one
line, and writing a fresh `formatX` helper without checking whether `lib/`
already has one. Each one feels helpful while you write it. A reviewer sees it as
noise: one more name to learn, one more hop to follow, one more dependency array
to keep in sync, or a second helper that will drift away from the first.

Reading the rules once at the start is not enough. Over a long task the defaults
come back. So this skill does not rely on memory alone: the **search step**
happens before you write, and once the skill is active, **hooks check every edit
automatically** and check again before you finish (see step 3).

## Workflow

### 1. Before writing: search, then copy the local shape

**Find what exists.** Before you create a helper, hook, component, type, constant
or error class, search for one that already does the job. Search by likely name
and by behavior, for example:

```bash
rg -n "format(Currency|Money|Price)|toFixed\(2\)|Intl.NumberFormat" src
rg -n "export (function|const) use[A-Z]" src/hooks src/**/hooks
rg -ln "class \w+Error" src
```

Check the shared places (`lib/`, `utils/`, `shared/`, `common/`, `hooks/`,
`components/ui/`, `errors`) and the feature's own folder. If something fits, use
it. If it nearly fits and the gap is small, extend it. Only write a new one when
nothing fits. Keep a short list of what you found, because it goes into the final
report.

**Copy the local shape.** Open 2–3 existing files of the same kind as the one
you're about to write (a sibling component, service or handler). Match how they
name files, export things, declare functions, handle errors, validate input and
structure tests. A new pattern, however good, is drift. Introduce one only when
the user asks for it.

### 2. While writing: the bright lines

These are the rules most often broken. Treat each one as a hard line, and
understand the reason, so you can see the cases the examples don't cover.

**No tiny wrappers.** Don't create a named function whose whole body is one call
or one property read with the arguments passed straight through:
`getName = (u) => u.name`, `fetchUser = (id) => api.get(id)`,
`formatUsd = (n) => formatCurrency(n, 'USD')`, or a service method that only calls
the repository. Call the real thing at the call site. *Why:* a wrapper adds a hop
and a name but no logic, and every reader has to open it to find out it does
nothing. A function earns its place by holding a decision, a transformation or
several steps.

**No premature extraction.** Extract a block to *dedupe* it only when the same
logic appears **3 or more times**. Two copies stay inline. You may extract once
to *name* a genuinely complex step, but never to produce a one-line forwarder.
*Why:* duplication is cheaper than the wrong abstraction. Two copies usually
diverge, and a premature helper then grows flags and parameters to serve both.

**No memoization by default (React).** Write plain values and plain functions.
Don't use `useMemo`, `useCallback` or `React.memo` unless one of these is true:
the value is a dependency of another hook and an unstable reference would loop or
refire it; it's passed to a child that is already wrapped in `React.memo` and
expensive to render; or the computation is measurably heavy on a hot path. When
you do memoize, put a comment on the line above that names the reason. *Why:*
for cheap work, memo costs more than it saves, and its dependency arrays go stale
and cause bugs. Filtering or mapping a list of a few hundred items, string
formatting and inline `onClick={() => ...}` handlers on DOM elements all run
fine on every render. This rule overrides general "React performance" advice
unless a perf problem was actually measured.

**No one-line ifs (TS/JS).** The body always goes in a `{ }` block on its own
lines, including early returns and throws:

```ts
// not this
if (!order) return null;
if (isLocked) { throw new LockedError(); }

// this
if (!order) {
  return null;
}
```

*Why:* the bodies stay where a reader expects them, adding a second statement
can't silently fall outside the `if`, and diffs stay one line per change. In Go,
the `gofmt` form `if err != nil {\n return err\n}` is already correct.

**Max 3 parameters.** At 4 or more, group related ones into one typed object
named after the operation (`refundOrder(input: RefundOrderInput)`). In Go, use a
params struct, not counting a leading `ctx`. Use an object below 3 as well when
a call site would otherwise pass bare booleans or easily swapped same-type
values. *Why:* positional argument lists turn every call site into a memory test.

**Readable conditions.** If a condition has chained `?.`, a callback (`.some`,
`.find`), a negated non-trivial expression, or runs past about 60 characters,
move it into a named boolean that reads as a positive statement
(`const hasOverdueItems = ...`).

**Split by responsibility, not by line count.** One function or file has one
reason to change. A 50-line function that reads top to bottom as one job is
fine. A 30-line function that validates, saves and sends email does three jobs.
When you split, each new piece needs a name that teaches something. No catch-all
`utils.ts`, no `handleStuff`, and splitting must never produce a tiny wrapper.

**No speculative code.** No factories, strategies, config flags, extension
points or generic utilities for a single use case. Solve the stated problem.
Don't rewrite code the task didn't touch. Comments explain a non-obvious *why*,
never restate the code.

### 3. Automatic checks: fix, or flag to the user

While this skill is active, a hook runs `scripts/check.py` on the lines you just
changed after every Edit/Write, and once more when you try to finish. It catches
what a regex can see: one-line ifs, memo hooks without a reason, pass-through
wrappers, 4+ parameters, and new symbols that already exist elsewhere in the repo.

When a hook message appears, treat it as a review comment on the code you just
wrote:

- **Fix it.** This is the normal case. The rule exists for the reasons above.
- **If you're sure it's justified**, keep it, but don't decide alone: list it in
  your reply under **Needs your decision** with the reason, so the user makes the
  call. A memo hook kept with a reason comment always goes there too.

The hooks only see mechanical patterns. Before finishing, also re-read your diff
for what they can't see: reinvention under a different name, drift from the
sibling files, speculative code, and splits that don't follow responsibilities.

If no hook output ever appears (hooks can be disabled), run the check yourself
from the repo root: `python3 <this-skill-dir>/scripts/check.py` (changed lines
vs HEAD), or pass file paths.

### 4. Report

End your reply with a short block, so the user and the reviewer can see the rules
were applied:

```
Clean-code check:
- Reused: formatCurrency (src/lib/format.ts), useDebounce (src/hooks/use-debounce.ts)
- New: OrderSummary component — nothing existing covered it
- check.py: clean

Needs your decision:
- src/hooks/use-polling.ts:14 — kept useCallback: it's a useEffect dependency, an
  unstable ref would restart polling every render
```

Leave out "Needs your decision" when there is nothing to decide.

## When rules collide

- **Bright line vs. a local habit** (for example, the codebase memoizes
  everything): in code you write, the bright line wins. Don't rewrite existing
  code you weren't asked to touch.
- **Another skill's advice** (for example, generic React performance guidance)
  vs. a bright line: the bright line wins unless there's a measured problem.
- **"Function too long" vs. "don't extract"**: extract a piece only if it's a
  distinct responsibility with a name that teaches something. Otherwise leave it
  inline.

## Review mode

When asked to review code (`/clean-code review`, "review this with clean-code",
reviewing another agent's changes or a PR), read
[references/review.md](references/review.md) and follow it. The review is where
the judgment rules get checked properly, so don't shortcut it to a skim.

## Language references

Read the matching file before writing in that language for the first time in a
task. They add idioms. They don't change the rules above.

- [idioms/typescript.md](idioms/typescript.md): types, function style, errors
- [idioms/react.md](idioms/react.md): components, hooks, state, rendering
- [idioms/node.md](idioms/node.md): router / controller / service / repository layers
- [idioms/go.md](idioms/go.md): errors, packages, naming

Read these principle files only when the task is mainly about that concern:
[naming](principles/naming.md), [dry](principles/dry.md),
[single-responsibility](principles/single-responsibility.md),
[minimal-code](principles/minimal-code.md),
[dependencies](principles/dependencies.md), [testing](principles/testing.md),
[security](principles/security.md), [twelve-factor](principles/twelve-factor.md).
