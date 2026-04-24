# docs/code-quality-scorecard.md Contract

This file is the evaluation rubric for reviewing changes.

## Required Categories

- correctness
- regression risk
- validation and error handling
- security and trust boundaries
- tests
- readability and maintainability
- consistency with repo patterns
- documentation impact

## Purpose

Use this file to explain how changes should be assessed.

Do not duplicate code-writing rules from `docs/code-standards.md`.

## Severity Model

Prefer a severity model like this when the repo does not already define one:

- `blocker`: correctness, security, data integrity, validation boundaries, architecture boundaries, dangerous hidden behavior
- `major`: maintainability is materially hurt, logic is in the wrong layer, weak typing, poor component or hook or service or repository boundaries
- `minor`: worthwhile improvement exists and should usually be made, but current code is still acceptable
- `nit`: readability improvement is small and non-blocking

## Review Heuristics

This rubric should help answer questions like:

- is responsibility clear
- is the code readable without live explanation
- are names explicit
- are there hidden magic values
- is logic in the right layer
- are contracts or props too large
- are modules tightly coupled
- are DTOs validated
- is logging useful
- are security boundaries correct
- are tests meaningful
- are exceptions real and documented

## Testing Expectations

Prefer expectations like these when they fit the repo:

- UI changes usually want unit or integration coverage
- API changes usually want integration or E2E coverage
- bug fixes should normally add coverage when practical
- test depth should match risk
- shallow tests that only prove rendering or plumbing are weak evidence
