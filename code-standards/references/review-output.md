# Review Output

## Load When

Load for review mode.

## Review Rules

- Findings come first.
- Use only `Blocking` and `Advisory`.
- Omit empty sections.
- Include concrete file and line references when available.
- Every Blocking finding must include a fix.
- Advisory findings should be concise and should not derail the task.
- Do not list personal preference when the standards or local pattern already
  answer the question.

## Template

```md
Blocking
- [path/to/file.ts:12] Rule: <standard violated>
  Problem: <what is wrong and why it matters>
  Fix: <specific change>

Advisory
- [path/to/file.ts:34] Rule: <standard or local pattern>
  Problem: <what could be clearer>
  Suggestion: <specific improvement>
```

If there are no findings:

```md
No Blocking findings.

Advisory risk: <short residual risk or test gap, if any>
```

## Implementation Final Response

For implementation mode, do not emit the review template. Keep the final answer
to:

- what changed
- validation run
- remaining Blocking issue, only if one could not be fixed
