# Drafting the review on GitHub

A PR review ends as a **draft** (pending) review: only the user sees it until they submit it in GitHub. This skill
creates the draft and stops there. Reading, editing, deleting comments, resolving threads, choosing the status and
submitting all belong to the user, so the skill has no path that submits, resolves or deletes.

`scripts/post_review.py` builds the draft from a findings file; its docstring has the full schema.

1. **Write `standard`** from the repo's review rules (review.md step 3), with only what the repo states: `source`
   (e.g. `origin/dev:.github/copilot-instructions.md`, or `"none"`), `labels` (most severe first), `request_changes`
   and `comment` (the labels behind each status), `limits` (the tier for this PR's size, counted the way the repo says,
   using `counted_files` from `--since`), `max_chars`. Every key you leave out falls back to the script's defaults, and
   the dry run names them. If the repo prescribes a comment template other than label/title + Why it matters /
   Evidence / Recommended change, write each finding's `body` to that template.
2. **Write the findings file:**
   - `head`: `head_sha` from `--since`, the commit the agents read. If the PR moves before the draft, the script stops:
     review the new commits as a re-review, then update `head`.
   - `verdict`: one sentence, the main risk or why it's safe to merge.
   - `findings`: every labelled finding, anchored to a changed line, in the repo's template. Cite other code as plain
     repo-relative `path:line` or `path:12-20`: the script checks each one exists at the head commit and turns it into
     a link pinned to that commit. Code in another repo goes in as a full GitHub URL. A finding shared with another
     PR of the ticket gets `shared_with: "owner/repo#N"`. Add a `suggestion` only after reading the types on that line:
     the obvious fix can change behaviour for another type.
   - `previous` (re-review): every thread from `open_threads`, with the verifier's verdict and reply as `note`.
   - `not_posted`: every finding left out, with its reason.
   - `body`: only what has no line (a question, a cross-cutting note).
   - `changes` (optional): 3–5 plain lines for a collapsed "What changed in this PR" section.

   The script builds the summary itself: a status heading (🔴 Changes requested / 🟡 Changes recommended / 🟢
   Approved), the verdict, the issue list with a severity mark per label, then `changes` and `body`. Each comment opens
   with its mark and a bold `[LABEL] title`.
3. **Dry run:** `python3 <this-skill-dir>/scripts/post_review.py <file>`. Fix every problem it lists: move an anchor
   to the nearest changed line, or the finding to `body`; merge findings past a limit or move the weakest to
   `not_posted`; shorten long comments; correct citations; move a re-review finding on an unchanged line to
   `not_posted`. If it reports an existing draft, stop and tell the user. Done when it prints "Dry run: nothing
   created".
4. **Create the draft:** rerun with `--draft`. Done when it prints the draft's link.
5. **Hand over:** show the user the script's output as printed (link, recommended status, comments, replies, not
   posted) under review.md's header line. GitHub's **Submit review** box starts empty and replaces the draft's summary
   with whatever is in it, so the script prints the summary between `----- summary to paste -----` markers: show it to
   the user in a fenced block, ready to copy into that box before submitting. The draft is theirs from here.
