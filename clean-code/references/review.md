# Clean-code review

You are reviewing code someone else (often another agent) wrote. Every finding a human reads must be **verified**: a
fresh agent read the cited code at the head commit, failed to disprove it, and checked that the suggested fix is safe.
Unverified findings are listed as not posted, never presented as fact. Don't edit the code under review.

| Request                                  | Reviews                                                             | Result                                                         |
| ---------------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------- |
| a PR link                                | the PR; on a PR you reviewed before, what changed since (re-review) | a **draft** GitHub review that only the user sees until submit |
| a PR link, local (`--local`, "locally")  | the same                                                            | the same review in the terminal; nothing is written to GitHub  |
| no link: a branch or uncommitted changes | the current branch against its base, uncommitted changes included   | the review in the terminal; nothing is written to GitHub       |

Local modes read GitHub (threads, so nothing is repeated) but never write to it, and never run `--draft`.

## 1. Pre-flight

Check before anything else and name every skip in the report header:

- `python3` runs.
- The `code-review` skill is installed (it runs the Standards and Spec axes). If it's missing, stop: "clean-code
  review needs the `code-review` skill".
- `gh auth status` succeeds. Without it, review from the clone and skip everything that reads or writes GitHub.
- The ticket is reachable (Jira, GitHub issue or a spec file). Without it, the Spec axis skips.
- PR: run `python3 <this-skill-dir>/scripts/post_review.py --since <owner/repo> <N>`. If `pending_review` is set and
  the mode posts a draft, stop: the user already has a draft on this PR and must submit or discard it first (GitHub
  allows one per person). Local mode carries on.

Done when each check passed or its skip is named.

## 2. Scope

- **Review copy.** Review in a worktree of the repo's clone, so the user's checkout stays untouched.
  - PR: fetch the base first (`git -C <clone> fetch origin <base_ref>`), so the diff and the rules use the current
    base, then `git -C <clone> fetch origin pull/<N>/head` and `git -C <clone> worktree add <scratch>/pr<N> FETCH_HEAD`.
  - Branch: `git -C <clone> fetch origin <base>`, `git -C <clone> worktree add <scratch>/branch HEAD`, then carry the
    uncommitted work over: `git -C <clone> diff HEAD --binary | git -C <scratch>/branch apply`, and copy each file from
    `git -C <clone> ls-files --others --exclude-standard`.

  Check it with `git -C <worktree> rev-parse HEAD` before briefing any agent.
- **Packages** (JS/TS repos), so agents can run tests: always use the user's local ones,
  `ln -s <clone>/node_modules <worktree>/node_modules`. Nothing is installed. A test that can't run (a package missing)
  is named in the report, and the review goes on without it.
- **Base, always explicit.** A PR's base is `base_ref` from `--since`. A branch's base is the one the user named, else
  the repo's default branch. Compare from the merge-base (`git diff origin/<base>...HEAD`), never from the base's tip.
- **Re-review** (`last_reviewed_sha` is set): new findings belong on the lines in `changed_since_last_review`, except
  a traced blocker anywhere. If `whole_pr` is set (it says why: a force-push, or more changed files than GitHub's
  compare lists), review the whole PR. Repeat nothing raised in `open_threads`, `closed_threads` or `other_threads`.
  Your `open_threads` (unresolved, or resolved by someone else without a settling reply from you) get verdicts in
  step 5. If `summary_missing` is set, tell the user that review went out without its summary.
- **Other reviewers' blockers:** `others_blocking` lists their unresolved `[MUST FIX]` threads, Copilot's included.
  They get a verdict in step 5, never a reply.
- **Another agent's work:** when the writer left "Needs your decision" items, rule on each in the report (accept with
  the reason, or reject with what to do instead).
- **Ticket:** find it from the branch name, commits, PR title or body. When it links PRs in other repos, the Spec
  agent reads them for context.

Done when you can state base, merge-base, head, changed files, ticket, and mode (first review, re-review, whole-PR
re-review, branch).

## 3. Rules: the repo's first, this skill's otherwise

Read the repo's rule files from `origin/<base>` (the rules the change merges under): `AGENTS.md` / `CLAUDE.md` and the
files they point to, `.github/copilot-instructions.md`, `.github/instructions/`, `CONTRIBUTING.md`. Copy them into
`<scratch>/<name>-standard/`, keeping their paths.

- **Coding standards.** When the rule files document coding standards, the Standards axis covers conventions. When
  they document none, also run the conventions brief.
- **Posting rules** (labels, comment template, limits, status rule) come from the repo's review section, or fall back
  to the defaults in `scripts/post_review.py`: the labels of the owner's PR Review Guide (`[MUST FIX]`, `[QUESTION]`,
  `[PROPOSAL]`, `[NIT PICK]`, `[OPTIONAL]`).
- **Repo docs** (`docs/architecture.md`, `patterns.md`, `models.md`, `how-system-works.md`, ADRs, a glossary) are
  context for every agent. A finding that rests on a doc is a rule only when a rule file makes it one (for example
  "a route change updates `docs/system/` in the same PR"); otherwise it's a recommendation, at most `[PROPOSAL]` (or
  the repo's equivalent). When the change touches something a doc describes and leaves the doc as it was, name the
  doc and section, and suggest the `generate-repo-docs` skill to refresh it when it's installed.
- **clean-code's own rules** apply unless the project's `AGENTS.md` / `CLAUDE.md` changes or switches one off.
  Whether a clean-code finding gets posted depends on the repo's bar (step 5).

Done when you can name the rule files, the posting rules' source (or "defaults"), and whether conventions run.

## 4. Find

Run `python3 <this-skill-dir>/scripts/check.py --base origin/<base>` in the worktree first (TS/JS/Go repos).

**Small change:** a re-review that isn't `whole_pr` with `changed_lines_since_last_review` under 150, or a branch
whose diff has under 150 changed lines. Do step 4 yourself instead of spawning agents: trace correctness on the
changed lines per [agents/correctness.md](agents/correctness.md), and judge the check.py output per
[agents/clean-code-rules.md](agents/clean-code-rules.md). Then go to step 5.

**Otherwise**, spawn every agent in **one message**, each with a fresh context:

| Agent       | Brief                                                                                                                                                                                                      |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Standards   | built per the `code-review` skill (its steps 1–4, smell baseline included) with the standards folder as its sources, plus [agents/clean-code-rules.md](agents/clean-code-rules.md) and the check.py output |
| Spec        | built per the `code-review` skill, with the ticket text and any linked PRs                                                                                                                                 |
| Correctness | [agents/correctness.md](agents/correctness.md)                                                                                                                                                             |
| Reinvention | [agents/reinvention.md](agents/reinvention.md)                                                                                                                                                             |
| Conventions | [agents/conventions.md](agents/conventions.md), only when the repo documents no coding standards                                                                                                          |

Every prompt carries: the worktree path, the diff command, head SHA, changed files, the standards folder, the repo
docs list, the ticket, on a re-review the `changed_since_last_review` ranges, and the instruction to report in the
format of [agents/finding.md](agents/finding.md). Existing threads (everyone's, from `--since`) go in only as a list of
titles not to repeat: a claim someone else made that needs checking goes to the verifier alone. For this skill's own
agents, pass the brief's path and tell the agent to read it first. `code-review`'s own "do not merge" rule covers its
standalone report; here its findings feed the steps below.

Done when every agent has returned, or you've named the one that failed (small change: every changed line was traced
and every check.py line has a verdict).

## 5. Verify, then label

Merge findings that share a root cause into one entry and keep every source tag (`Standards`, `Spec`, `Correctness`,
`Reinvention`, `Conventions`). Then spawn **one verifier** with [agents/verifier.md](agents/verifier.md), the merged
list, and on a re-review your `open_threads` with their replies and the `others_blocking` threads. It returns each
finding as confirmed, wrong or unverified, with its fix checked, and gives each thread a verdict.

Then give every confirmed finding exactly one label from the repo's scale (or the defaults):

- `[MUST FIX]` (or the repo's blocker label): a bug, data loss, contract break or security issue with a traced failure
  path (input → steps → wrong result, every hop cited); or a break of an architecture boundary, of validation at a
  boundary, or of a rule the repo marks blocking, with the rule and the line cited. A suspected bug with a missing hop
  is a `[QUESTION]`.
- `[QUESTION]`: the author must answer before approval (intent, an edge case, a constant, a business rule).
- `[PROPOSAL]`: a recommended improvement with a clear payoff, clean-code rule breaks and missing doc updates
  included. The author fixes it or replies `[WON'T FIX] <reason>`.
- `[NIT PICK]`: a small readability or naming tweak; same reply rule. `[OPTIONAL]`: an idea for later; no reply needed.
- **The fix:** keep the code suggestion only when the verifier showed it safe. Otherwise keep the label, drop the
  suggestion, and name the risk instead ("a fix must keep the late-update guard at `path:line`").
- **Data questions:** a question only stored data (templates, database rows, environment config) can answer goes in
  the summary `body` as "Note for whoever owns <the data>: …". It is not a comment and doesn't change the status.
- **Not posted**, with the reason, when it's: below the repo's bar (its "do not comment on" list); a clean-code rule
  the repo doesn't hold; already raised in anyone's thread; unverified; over the repo's limit; or, on a re-review, on
  a line unchanged since your last review.
- A ticket split across repos: a finding that belongs to both PRs goes on each, covering only that PR's part, marked
  `shared_with` the other PR.

Re-review thread verdicts (yours only, including comments you wrote by hand):

| Verdict        | When                                                                                            | Reply                                    | Counts toward status |
| -------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------- | -------------------- |
| `fixed`        | the root cause is gone, not just the line moved                                                 | "Fixed in `<sha>`."                      | no                   |
| `partly_fixed` | some of it is left                                                                              | "Partly fixed: what's left, `path:line`" | yes                  |
| `open`         | no relevant change, or the author's pushback doesn't hold                                       | "Still open: why, `path:line`"           | yes                  |
| `accepted`     | the author's reason holds (checked); a `[WON'T FIX] <reason>` on a `[PROPOSAL]` or `[NIT PICK]` | "Agreed: why."                           | no                   |

Open each reply with its verdict as in the table: the next re-review counts a thread as settled only after your
"Fixed …" or "Agreed: …". A `[PROPOSAL]` or `[NIT PICK]` left `open` doesn't block; the summary lists it as skipped
without `[WON'T FIX]`. An `[OPTIONAL]` thread needs no verdict unless it was fixed.

Other reviewers' blocking threads get `open` (still holds at the head), `fixed`, or `wrong` (never held), with a note
for the user and no reply. One still `open` keeps the status at Comment or above.

Done when every finding has a label or a not-posted reason, and every thread a verdict.

## 6. Output

**Draft (PR link):** follow [post-review.md](post-review.md) to create the draft, then show the user the script's
output under a header line:

```
Review of owner/repo#N · base origin/dev (merge-base 1a2b3c4) · head 5d6e7f8 · 16 files · first review
Skipped: Jira (no access)
```

**Local PR:** the same findings file, checked with `post_review.py <file> --local` instead of the dry run and
`--draft` (post-review.md steps 1–3); show its output under the header line.

**Branch or uncommitted changes:** there is no PR for the script, so show the same content in the terminal yourself
under the header line: findings grouped by label, each as `path:line — what's wrong → fix (sources)`, then the
not-posted list, one line each with its reason.

Then remove the worktree (`git -C <clone> worktree remove --force <worktree>`). Throwaway tests go with it.

No praise and no summary of what the code does. If nothing survived, say "Clean." and stop.
