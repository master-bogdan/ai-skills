# docs/code-quality-scorecard.md Contract

This file has two parts: a stable rubric and a dated assessment. The rubric
stays stable across runs. The assessment section is regenerated each time the
skill runs.

---

## Part 1: Rubric (stable)

### Severity Model

- `blocker`: correctness, security, data integrity, validation boundaries,
  architecture boundaries, dangerous hidden behavior
- `major`: maintainability materially hurt, logic in wrong layer, weak typing,
  poor component/hook/service/repository boundaries
- `minor`: worthwhile improvement exists but current code is still acceptable
- `nit`: small readability improvement, non-blocking

### Review Categories

- Correctness
- Regression risk
- Validation and error handling
- Security and trust boundaries
- Tests
- Readability and maintainability
- Consistency with repo patterns
- Documentation impact

### Review Heuristics

- Is responsibility clear?
- Is the code readable without live explanation?
- Are names explicit?
- Are there hidden magic values?
- Is logic in the right layer?
- Are contracts or props too large?
- Are modules tightly coupled?
- Are DTOs validated?
- Is logging useful?
- Are security boundaries correct?
- Are tests meaningful?
- Are exceptions real and documented?

### Testing Expectations

- UI changes: unit or integration coverage
- API changes: integration or E2E coverage
- Bug fixes: coverage when practical
- Test depth matches risk
- Shallow tests that only prove rendering or plumbing are weak evidence

---

## Part 2: Current Assessment (regenerated each run)

Read enough actual code to give honest scores. Do not rubber-stamp.

Required output format:

```md
## Current Assessment
Generated: YYYY-MM-DD
Overall Grade: B

| Category | Score | Notes |
|----------|-------|-------|
| Correctness | 4/5 | Core logic sound, one edge case unhandled in X |
| Regression risk | 3/5 | No tests for Y flow |
| Validation | 2/5 | Raw req.body passed to service at Z |
| Security | 4/5 | Auth present, one missing ownership check |
| Tests | 3/5 | Good unit coverage, missing integration tests |
| Readability | 4/5 | Clear naming, one god function in X |
| Consistency | 5/5 | Patterns followed consistently |
| Docs impact | 2/5 | No inline docs, stale README |

### Findings

#### Blocker
- [src/controllers/order.ts:45] Raw req.body passed to service without validation

#### Major
- [src/services/order.service.ts:120] Function exceeds 80 lines, mixes 4 concerns

#### Minor
- [src/utils/format.ts:12] Magic number 86400 should be a named constant

### Priority Fix List
1. Add createOrderSchema.parse(req.body) in order controller (Blocker)
2. Split processOrder into focused functions (Major)
3. Name the magic constant in format.ts (Minor)
```

### Grading scale

- A: No blockers, ≤1 major
- B: No blockers, 2–3 majors
- C: 1 blocker or 4+ majors
- D: 2+ blockers
- F: Systemic issues across multiple categories
