# .github/copilot-instructions.md Contract

This file is review-only guidance for GitHub Copilot review behavior.

## Purpose

Tell Copilot how to review pull requests in this repo without creating noise.

## Required Content

- what to prioritize in review
- what not to comment on
- review labels
- comment structure
- threshold for low-signal issues
- fix-prompt requirement

## Review Priorities

Bias toward:

- bugs
- regressions
- data loss or integrity risks
- security issues
- missing validation
- missing tests for changed behavior
- standards violations
- clear inconsistencies
- unambiguous low-noise typos
- wrong-layer logic
- weak typing or undocumented unsafe casts
- overloaded components, hooks, or services
- weak logging around meaningful failures

## Noise Controls

Tell Copilot to avoid:

- praise
- summaries of the diff
- speculative style feedback
- repeated comments about the same issue
- comments without an actionable change

If there is no actionable issue, it should stay silent.

## Severity Guidance

Map findings like this:

- `[MUST FIX]` for blocker or major issues
- `[SUGGESTION]` for meaningful improvements that should usually be made
- `[OPTIONAL]` for low-risk improvements that are useful but not necessary
- `[NIT PICK]` for small wording, typo, or consistency fixes with low impact

Prefer silence over low-value comments.

## Labels

Use these labels:

- `[MUST FIX]`
- `[SUGGESTION]`
- `[OPTIONAL]`
- `[NIT PICK]`

## Comment Structure

Each comment should contain:

1. label line
2. `Why this matters`
3. `Evidence`
4. `Recommended change`
5. `AI fix prompt`

Keep each comment focused on one issue.

## What Good Review Comments Usually Target

Prefer comments that point to issues such as:

- unclear responsibility boundaries
- hidden magic values
- logic in the wrong layer
- props or contracts that are too large
- tight coupling or circular dependency risk
- missing DTO validation
- poor logging context
- weak security or trust-boundary handling
- tests that do not support confidence
- undocumented exceptions
- unsupported assumptions about contracts, schema, auth, or external services

## Review Labels

Include an `assumption-risk` label for changes that appear to rely on unsupported assumptions.

### assumption-risk

Use when the change appears to rely on an unsupported assumption about contracts, schema, auth, tenant scoping, external services, queues, file processing, or user-visible behavior.

Comment format:

```
Issue: The change appears to assume <assumption>, but the repo evidence does not confirm it.

Risk: <why this may break behavior or contracts>

Fix prompt: Ask for confirmation or inspect <specific files/docs/tests> before implementing this behavior.
```

## Output Style

- concise
- direct
- useful
- no filler
- no generic review language
