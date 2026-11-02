# Clean-code review

You are reviewing code someone else (often another agent) wrote. The writer had
the same rules, and hooks caught the mechanical slips. What gets through to you
is mostly what needs judgment: reinvention under a different name, drift from the
project's conventions, premature extraction, and exceptions the writer chose to
keep. Your fresh attention is the point, so go through every pass below. Don't
stop at the first few findings.

Don't edit code unless you're asked to. Your output is the report.

## 1. Scope

Work out what changed:

- The user named a base (branch, commit, PR): `git diff <base>...HEAD` plus any
  uncommitted changes.
- Otherwise, if there are uncommitted changes, review those (`git diff HEAD`, plus
  untracked files from `git status`).
- Otherwise, review the branch against its merge-base with `main`/`master`.

List the changed files. Read each changed file whole, not just the hunks, because
drift and duplication only show up in context.

If the writer's reply is available, read its "Clean-code check" and "Needs your
decision" sections. You'll rule on those in step 6.

## 2. Mechanical pass

```bash
python3 <this-skill-dir>/scripts/check.py --base <base>   # or with no args for uncommitted changes
```

Every finding is a **Fix**, unless the writer listed that exact line under "Needs
your decision". Those go to step 6.

## 3. Reinvention pass

For **every new symbol** (check.py lists them) **and every new file**, search the
project for something that already does the job. Search by name and by behavior:

```bash
rg -n "export (const|function|class|type) \w*(Format|Currency|Money)\w*" src
rg -n "Intl\.NumberFormat|toFixed\(|createObjectURL|setTimeout\(|class \w+Error" src
```

Also look for reinvention inside function bodies, where no new symbol shows it.
Typical cases:
- Formatting money or dates by hand when a formatter exists.
- A hand-rolled debounce, fetch wrapper, download or CSV routine.
- Manual `if (!body.x)` validation where the project validates with a schema.
- A new error class next to existing ones.

A finding is only valid if you name the existing thing and its path:
`src/x.ts:12 — re-implements currency formatting → use formatCurrency (src/lib/format.ts)`.

## 4. Conventions pass

For each new or substantially changed file, open 1–2 sibling files of the same
kind (component next to component, service next to service). Compare:

- file naming
- export style
- function style (declaration vs arrow)
- `type` vs `interface`
- error handling
- where validation happens
- layering (router → controller → service → repository)
- test style

Each divergence the change introduced is a finding. A pattern the project
doesn't use is drift, even if it's a good pattern.

## 5. Judgment pass

Check each rule from SKILL.md that a regex can't fully see:

- **Wrappers the regex missed:** class methods or multi-line functions that still
  only forward, or a service method that only calls the repository.
- **Premature extraction:** a helper used once or twice that isn't a genuinely
  complex step. Inline it unless the same logic appears 3+ times.
- **Memoization:** does each `useMemo`/`useCallback`/`React.memo` meet one of
  the three allowed reasons? Is the reason comment true?
- **Responsibility:** a function or file mixing jobs (validation + persistence +
  notification + formatting), or a split into pieces whose names teach nothing.
- **Speculative code:** factories, options or flags for a single use case.
- **Readable conditions** and **noise comments**.
- **Scope:** edits to code the task didn't need.

## 6. Rule on the writer's exceptions

For each item under the writer's "Needs your decision", give a verdict:
- **Accept:** the reason is concrete and true, so say why.
- **Reject:** it moves to Fix, with what to do instead.

You advise. The user still decides.

## 7. Report

```
Fix:
- path:line — [rule] what's wrong → what to do

Improve:
- path:line — [rule] what's suboptimal → suggested change

Exceptions:
- path:line — accept | reject — reason
```

- **Fix:** breaks a bright line, reinvents something that exists, or drifts from
  conventions.
- **Improve:** a real but smaller judgment call.
- Leave out empty sections. If there's nothing at all, reply "Clean." and
  nothing else.
- No praise, no summary of what the code does, no style nits outside these rules.
