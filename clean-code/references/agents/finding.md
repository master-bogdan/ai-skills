# Finding format

Report each finding in this shape, in plain words a reviewer understands without opening the code:

```
### <one sentence naming the problem>
- Where: path:line — the changed line the comment belongs on (repo-relative path, line number at the head commit)
- Here: what the change does at that spot, one sentence.
- Problem: what is wrong.
- Why it matters: the consequence. For a bug, the failure path: input or state → each step as path:line → wrong result.
- Fix: the smallest safe change.
- Evidence: every other location as path:line or path:12-20; each rule quoted with its file:line.
- Confidence: certain | likely | unsure, and what would settle it.
```

Cite repo-relative paths with line numbers you read at the head commit; code in another repo as a full GitHub URL.
Report findings only: no praise, no summary of the diff. With nothing to report, write "No findings." and the list
of what you checked.
