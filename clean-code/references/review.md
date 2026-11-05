# Clean-code review

You are reviewing code someone else (often another agent) wrote. Your output is a report and, for a PR, a draft
review on GitHub that only the user sees until they submit it. Don't edit code unless you're asked to.

Every finding a human reads must be **verified**: a fresh agent read the cited code at the head commit and failed to
disprove it. Unverified findings are listed as not posted, never presented as fact.

## 1. Pre-flight

For a PR or branch, check before anything else and name every skip in the report header:

- `python3` runs.
- The `code-review` skill is installed (it runs the Standards and Spec axes). If it's missing, stop: "clean-code
  review needs the `code-review` skill".
- PR: `gh auth status` succeeds. Without it, review locally from the clone and skip the draft.
- The ticket is reachable (Jira, GitHub issue or a spec file). Without it, the Spec axis skips.
- PR: run `python3 <this-skill-dir>/scripts/post_review.py --since <owner/repo> <N>`. If `pending_review` is set, stop:
  the user already has a draft on this PR and must submit or discard it first (GitHub allows one per person).

Done when each check passed or its skip is named.

## 2. Scope

- **Base, always explicit.** A PR's base is `base_ref` from `--since`. Otherwise use the base the user named, or ask.
  Compare from the merge-base (`git diff <base>...HEAD`), never from the base's tip.
- **PR:** review the code at the PR head in a worktree of the repo's clone, so your own checkout stays untouched.
  Fetch the base first (`git -C <clone> fetch origin <base_ref>`), so the diff and the rules use the current base, then
  `git -C <clone> fetch origin pull/<N>/head` and `git -C <clone> worktree add <scratch>/pr<N> FETCH_HEAD`.
- **Re-review** (`last_reviewed_sha` is set): new findings belong on the lines in `changed_since_last_review`, except
  a traced blocker anywhere. If `whole_pr` is set (it says why: a force-push, or more changed files than GitHub's
  compare lists), review the whole PR. Repeat nothing raised in `open_threads`, `closed_threads` or `other_threads`.
  Your `open_threads` (unresolved, or resolved by someone else without a settling reply from you) get verdicts in
  step 5. If `summary_missing` is set, tell the user that review went out without its summary.
- **Uncommitted changes** (reviewing another agent's work): `git diff HEAD` plus untracked files. Skip the sub-agents:
  run check.py and the clean-code rules, reinvention and correctness briefs yourself, then rule on the writer's "Needs
  your decision" items (accept with the reason, or reject with what to do instead). Report locally.
- **Ticket:** find it from the branch name, commits, PR title or body. When it links PRs in other repos, the Spec
  agent reads them for context.

Done when you can state base, merge-base, head, changed files, ticket, and mode (first review, re-review, whole-PR
re-review).

## 3. Rules: the repo's first, this skill's otherwise

Read the repo's rule files from `origin/<base_ref>` (the rules the PR merges under): `AGENTS.md` / `CLAUDE.md` and the
files they point to, `.github/copilot-instructions.md`, `.github/instructions/`, `CONTRIBUTING.md`. Copy them into
`<scratch>/pr<N>-standard/`, keeping their paths.

- **Coding standards.** When the rule files document coding standards, the Standards axis covers conventions. When
  they document none, also run the conventions brief.
- **Posting rules** (labels, comment template, limits, status rule) come from the repo's review section, or fall back
  to the defaults in `scripts/post_review.py`.
- **Repo docs** (`docs/architecture.md`, `patterns.md`, `models.md`, `how-system-works.md`, ADRs, a glossary) are
  context for every agent. A finding that rests on a doc is a rule only when a rule file makes it one (for example
  "a route change updates `docs/system/` in the same PR"); otherwise it's a recommendation, at most `[SUGGESTION]`.
  When the PR changes something a doc describes and leaves the doc as it was, name the doc and section, and suggest
  the `generate-repo-docs` skill to refresh it when it's installed.
- **clean-code's own rules** apply unless the project's `AGENTS.md` / `CLAUDE.md` changes or switches one off.
  Whether a clean-code finding gets posted depends on the repo's bar (step 5).

Done when you can name the rule files, the posting rules' source (or "defaults"), and whether conventions run.

## 4. Find: sub-agents in parallel

Run `python3 <this-skill-dir>/scripts/check.py --base <base>` in the worktree first; its output goes to the clean-code
rules agent.

Then spawn every agent in **one message**, each with a fresh context:

| Agent | Brief |
|---|---|
| Standards | built per the `code-review` skill (its steps 1–4, smell baseline included), standards from `<scratch>/pr<N>-standard/` |
| Spec | built per the `code-review` skill, with the ticket text and any linked PRs |
| Correctness | [agents/correctness.md](agents/correctness.md) |
| Reinvention | [agents/reinvention.md](agents/reinvention.md) |
| clean-code rules | [agents/clean-code-rules.md](agents/clean-code-rules.md), plus the check.py output |
| Conventions | [agents/conventions.md](agents/conventions.md), only when the repo documents no coding standards |

Every prompt carries: the worktree path, the diff command, head SHA, changed files, the standards folder, the repo
docs list, the ticket, everyone's existing threads (from `--since`), on a re-review the `changed_since_last_review`
ranges, and the instruction to report in the format of [agents/finding.md](agents/finding.md). For this skill's own
agents, pass the brief's path and tell the agent to read it first. `code-review`'s own "do not merge" rule covers its
standalone report; here its findings feed the steps below.

Done when every agent has returned, or you've named the one that failed.

## 5. Verify, then label

Merge findings that share a root cause into one entry and keep every source tag (`Standards`, `Spec`, `Correctness`,
`Reinvention`, `clean-code`). Then spawn **one verifier per PR** with [agents/verifier.md](agents/verifier.md), the
merged list, and on a re-review your `open_threads` with their replies. It returns each finding as confirmed, wrong or
unverified, and gives each thread a verdict and a drafted reply.

Then give every confirmed finding exactly one label from the repo's scale (or the defaults):

- `[MUST FIX]` (or the repo's blocker label) only with a traced failure path: input → steps → wrong result, every hop
  cited. A suspected blocker with a missing hop is a `[QUESTION]`.
- **Not posted**, with the reason, when it's: below the repo's bar (its "do not comment on" list); a clean-code rule
  the repo doesn't hold; already raised in anyone's thread; unverified; over the repo's limit; or, on a re-review, on
  a line unchanged since your last review.
- A ticket split across repos: a finding that belongs to both PRs goes on each, covering only that PR's part, marked
  `shared_with` the other PR.

Re-review thread verdicts (yours only, including comments you wrote by hand; others' threads get none):

| Verdict | When | Reply | Counts toward status |
|---|---|---|---|
| `fixed` | the root cause is gone, not just the line moved | "Fixed in `<sha>`." | no |
| `partly_fixed` | some of it is left | "Partly fixed: what's left, `path:line`" | yes |
| `open` | no relevant change, or the author's pushback doesn't hold | "Still open: why, `path:line`" | yes |
| `accepted` | the author's reason holds (checked), or a follow-up links a ticket | "Agreed: why." | no |

Open each reply with its verdict as in the table: the next re-review counts a thread as settled only after your
"Fixed …" or "Agreed: …".

Done when every finding has a label or a not-posted reason, and every thread a verdict and a reply.

## 6. Output

**PR:** follow [post-review.md](post-review.md) to create the draft, then show the user the script's output under a
header line:

```
Review of owner/repo#N · base origin/dev (merge-base 1a2b3c4) · head 5d6e7f8 · 16 files · first review
Skipped: Jira (no access)
```

**Branch or uncommitted changes:** the same content in the terminal: findings grouped by label, each as
`path:line — what's wrong → fix (sources)`, then the not-posted list, one line each with its reason.

No praise and no summary of what the code does. If nothing survived, say "Clean." and stop.
