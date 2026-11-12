# Reinvention brief

You find code the change **re-implements** that already exists in the repo, its shared packages, or its declared
dependencies. A second copy drifts from the first; finding it before merge is cheap, after merge it isn't.

For **every new file, every new exported symbol, and every new function with real logic**:

1. **Search by name:** the symbol, its variants (`V2`, `Async`, plural, other casing), and the file's basename in
   other folders. Start from check.py's lists of same names, same-named files and near-names.
2. **Search by behaviour:** the key calls, literals, regexes, endpoints and query shapes in the new body (a date
   library call, `Intl.`, the same repository query, the same loop over sheets). Check the shared places (`lib/`,
   `utils/`, `shared/`, `common/`, `hooks/`, versioned folders like `v2/`) and the feature's own and sibling modules.
3. **Open both** for every match and decide: the same job → a finding that names the existing code with `path:line`
   and how many callers it has; similar but different → say what differs, and what the existing one would need to fit.

Also report a change that adds a 3rd or later copy of the same logic, listing every copy.

A finding counts only when it names the existing code and its path. Report in the format of
[finding.md](finding.md), then end with a checklist: each new file and symbol with its result ("reuses X", "nothing
found: searched A, B").

Done when every new file and new symbol has a line in that checklist.
