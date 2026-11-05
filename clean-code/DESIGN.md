# clean-code: design decisions

For whoever changes this skill. Nothing in `SKILL.md` points here, so agents running the skill never load it.
Agreed with the owner in November 2026, while reviewing LenderAI/sheets-ui#541 and LenderAI/sheets-api#420.

## Scope

- Works the same in any repo. It uses the repo's own rules first and falls back to its own defaults rule by rule.
  The defaults are the sheets repos' review standard.
- Repo docs (architecture, patterns, models) are context. A finding based on a doc is a rule only when the repo's
  rule files say so; otherwise it is a recommendation, `[SUGGESTION]` at most.
- A project changes or switches off a rule in its own `AGENTS.md` / `CLAUDE.md`. The skill names no project.
- Python is not covered by the coding rules.
- The sheets repos have their own, separate copies (`sheets-code-standards`, `sheets-pr-review`, `code-review` in the
  sheets-api hub). A change here does not reach them.

## Review

- `code-review` (Standards and Spec axes) is a required dependency: it is what makes the Standards and Spec findings
  accurate. Next to it run Correctness (traced failure paths), Reinvention (search by behaviour and file name), the
  clean-code rules (`check.py` plus judgement), and Conventions only when the repo documents no standards.
- One fresh verifier per PR tries to disprove every finding; `post_review.py` checks every cited `path:line` at the
  head commit. Unconfirmed findings are never posted.
- One label scale from the start: the repo's labels, or "Not posted" with a reason. `[MUST FIX]` needs a traced
  failure path with every hop cited; otherwise it is a `[QUESTION]`.
- A ticket split across repos: a shared finding goes on each PR, only that PR's part, marked "Shared with".

## Posting

- The skill creates a GitHub **draft** (pending) review and stops. The human reads, edits, resolves, picks the status
  and submits. The skill has no path that submits, resolves or deletes.
- GitHub's Submit review box starts empty for an API-created draft and replaces the draft's summary with its contents.
  A prefilled box is impossible from outside the browser, so the script prints the summary between markers and the
  user pastes it. No clipboard: the user asked for text on screen.
- Summary format (Copilot-like): status heading (🔴 / 🟡 / 🟢), the verdict, a collapsible "N open issues" list with
  a severity mark per label, then the optional "What changed in this PR" (left out where the repo standard forbids a
  diff summary, as sheets does), then `body`. Each comment opens with its mark and a bold `[LABEL] title`.

## Re-review

- Started by hand. New comments only on lines changed since your last review (base merges excluded), except a traced
  `[MUST FIX]` anywhere. After a force-push, the whole PR, repeating nothing already raised.
- A thread of yours needs a verdict until it is settled: resolved by you, or resolved by someone else after your
  last reply settled it ("Fixed …" / "Agreed: …"). Authors often resolve their own threads (both pilot PRs: all 25
  resolved by the author), sometimes right after a "Still open". An open thread with no known label (hand-written)
  keeps the recommendation at Comment or above.
- The draft is pinned to the commit the review read (`head` in the findings file); if the PR moved, nothing is created.
  More changed files than GitHub's compare lists (300) means a whole-PR re-review, like a force-push.
- Verdicts: Fixed / Partly fixed / Still open / Accepted, with a drafted reply in the same draft. Pushback that
  doesn't hold is Still open with a counter-reason; "follow-up" counts as Accepted only with a ticket link.
- Other people's threads are read only to avoid repeats: no verdicts, no replies.

## check.py

- Compares from the merge-base; masks comments; flags only private pass-through wrappers (an exported entry point to a
  layer is judged in review); max 3 params binds new functions, framework-dictated signatures exempt; lists same-named
  files and near-names (`recomputeWorkbook` / `recomputeWorkbookV2`) once, at the end, as "Potential duplicate".

## Pilot results (sheets-ui#541, sheets-api#420)

25 comments posted, none called wrong by the author. 18 fixed in the PR (both `[MUST FIX]`), 2 agreed but deferred,
2 by design (both scope `[QUESTION]`s, answered as intended), 3 declined without a reason (both `[OPTIONAL]`s and one
design suggestion). `[OPTIONAL]` went 0 for 2: watch it before posting more of them.
