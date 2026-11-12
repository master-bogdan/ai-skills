# .github/copilot-instructions.md Contract

Review-only guidance: how GitHub Copilot, and any agent reviewing a PR in this repo, reviews it. Labels and the status
rule follow the [PR Review Guide](https://ibusinessfunding.atlassian.net/wiki/spaces/CO/pages/3540156418/PR+Review+Guide).
Not a copy of `AGENTS.md`.

## Structure

1. **Repo-specific checks**, from the inspected repo, never generic. One short section per high-risk area, each saying
   what to check and which label a break gets:
   - the contracts and boundaries a break of which is `[MUST FIX]` ("`[MUST FIX]` if a query skips the tenant
     filter"): auth, tenant scoping, API and message contracts, migrations, queues, layer boundaries, validation at
     boundaries. Use the same high-risk categories as `AGENTS.md` "Ask Before Guessing".
   - docs drift: a change to a contract or flow a doc describes, without updating that doc, is `[PROPOSAL]`; name the
     doc that should change.
   - `Code style` (`[PROPOSAL]` if violated; full rules in `docs/code-standards.md`): 3–6 bright lines from
     `docs/code-standards.md`, when the repo has one.
   - an assumption the change makes about contracts, schema, auth, external services or user-visible behavior that
     the repo doesn't confirm is a `[QUESTION]`: name the files or docs that would settle it.
2. **The "Review output" block below**, copied verbatim between its markers. Change nothing but the guide link when a
   team uses another guide. In a set of repos that share it (a hub and its spokes), the hub's copy is the source and
   the others stay identical.

Prioritise in the repo-specific part: bugs, regressions, data loss or integrity risks, security and trust boundaries,
missing validation, missing tests for changed behavior, wrong-layer logic, weak typing or unsafe casts, overloaded
components, hooks or services, weak logging around meaningful failures.

## Review output block

````markdown
<!-- review-output:start -->

## Review output

### Labels

From the team's [PR Review Guide](https://ibusinessfunding.atlassian.net/wiki/spaces/CO/pages/3540156418/PR+Review+Guide):

- `[MUST FIX]` — blocking: a bug, data loss, contract break or security issue whose failure path is traced and cited in
  the code; or a break of an architecture boundary, of validation at a boundary, or of a rule marked `[MUST FIX]`
  here, citing the rule and the line
- `[QUESTION]` — the author must answer before approval (unclear intent, edge case, constant, business rule, or an
  assumption the repo doesn't confirm); also a suspected bug not yet traced end to end
- `[PROPOSAL]` — recommended improvement with a clear payoff; the author fixes it or replies `[WON'T FIX] <reason>`
- `[NIT PICK]` — small readability or naming tweak, only when truly low-noise; fix it or reply `[WON'T FIX] <reason>`
- `[OPTIONAL]` — an idea for later; can be skipped without a reply

Status: any `[MUST FIX]` → Request changes; otherwise any `[QUESTION]` → Comment; otherwise Approve. `[PROPOSAL]`,
`[NIT PICK]` and `[OPTIONAL]` never block approval.

### Comments

- One comment per issue, anchored to the line it is about. Skip a root issue already raised in this PR's review threads.
- The review body opens with the status, a one-sentence verdict (the main risk, or why it is safe to merge), and the
  list of findings, most severe first, each linking to its comment. Below that goes only what has no line (a question,
  a cross-cutting note). No summary of the diff, no praise. If nothing is actionable, stay silent.
- Each comment, at most 600 characters (not counting a suggestion block, the AI fix prompt, links or cited
  `path:line`):

```text
[LABEL] Short title

Why it matters: one sentence.
Evidence: path/to/file — function, and the code path that fails.
Recommended change: the minimal safe change, not a rewrite.
AI fix prompt: "In <file>, <change> so that <expected end-state>; add or update <test>."
```

- Add a `suggestion` block only after reading the types on that line.

### Do not comment on

- formatting or lint issues the tooling already owns
- naming preferences, unless the name is misleading or breaks a public API
- refactors or micro-optimisations without a concrete bug, regression risk, or standards violation
- "add more tests", unless behaviour changed

### Limits

Count changed files, leaving out lock files, test fixtures, and snapshots. These are ceilings, not targets. Past one,
merge findings that share a root cause, or drop the weakest. `[MUST FIX]` has no limit: a traced blocker is always
posted.

| Changed files | `[QUESTION]` | `[PROPOSAL]` | `[NIT PICK]` + `[OPTIONAL]` |
| ------------- | ------------ | ------------ | --------------------------- |
| ≤ 15          | 2            | 3            | 1                           |
| 16–40         | 4            | 8            | 3                           |
| > 40          | 6            | 12           | 4                           |

<!-- review-output:end -->
````

## Style

- concise, direct, path-heavy
- a label on every rule that sets one; no generic review language
