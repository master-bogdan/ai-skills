#!/usr/bin/env python3
"""Claude Code hook for the clean-code skill (registered in SKILL.md frontmatter).

PostToolUse (Edit|Write): checks the lines just changed in that file and sends rule
  violations straight back to the agent (exit 2 -> stderr is shown to Claude).
Stop / SubagentStop: if this session edited code and violations, kept exceptions, or
  same/similar names (definitions, variant names like fooV2, same-named files) remain that
  the agent hasn't been told about yet, blocks the stop once with the list, so the agent
  fixes them, lists them for the user under "Needs your decision", or looks at both names.

Sessions that never edited a file (e.g. a reviewer) are never blocked. Lines count as changed since the commit the
session started from in each repo, so committing before the final reply hides nothing from the Stop check.
"""

import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check  # noqa: E402

STATE_DIR = os.path.join(tempfile.gettempdir(), "clean-code-hooks")

FIX_OR_FLAG = (
    "Fix each one now. If you are sure a flagged line is justified, keep it, and in your final reply "
    "list it under a 'Needs your decision' heading with the reason, so the user decides."
)


def load_state(session_id):
    try:
        with open(os.path.join(STATE_DIR, f"{session_id}.json")) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"files": [], "reported": [], "bases": {}}


def save_state(session_id, state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, f"{session_id}.json"), "w") as fh:
        json.dump(state, fh)


def repo_root(path):
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    result = subprocess.run(["git", "-C", directory, "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def baseline(root, recorded):
    """The commit the session started from in root while it is still an ancestor of HEAD (no rebase or branch switch
    since), else HEAD."""
    if recorded and subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor", recorded, "HEAD"],
                                   capture_output=True).returncode == 0:
        return recorded
    return "HEAD"


def targets_for(files, bases):
    """Map files to (root, {repo-relative or absolute path: changed lines or None}, base), chdir-ing per repo. Lines
    count as changed since the session's baseline in that repo (bases: {root: commit})."""
    by_root = {}
    for path in files:
        if os.path.isfile(path):
            by_root.setdefault(repo_root(path), []).append(path)
    results = []
    for root, paths in by_root.items():
        if root is None:
            results.append((None, {p: None for p in paths}, None))
            continue
        os.chdir(root)
        base = baseline(root, bases.get(root))
        changed = check.changed_lines(base)
        relative = [os.path.relpath(p, root) for p in paths]
        results.append((root, {r: changed[r] for r in relative if r in changed}, base))
    return results


def run_checks(files, bases):
    """Violations, kept exceptions and same/similar-name lines for the given files, per repo."""
    findings, exceptions, names = [], [], []
    for root, targets, base in targets_for(files, bases):
        if root:
            os.chdir(root)
        f, e, _, symbols = check.collect(targets, base)
        findings += f
        exceptions += e
        if root:
            names += check.related(symbols, check.added_files(base) & set(targets))
    return findings, exceptions, names


def on_edit(event):
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(check.TS_EXT + check.GO_EXT):
        return 0
    session_id = event.get("session_id", "default")
    state = load_state(session_id)
    bases = state.setdefault("bases", {})
    root = repo_root(path)
    head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True) if root else None
    if root and root not in bases and head.returncode == 0:
        bases[root] = head.stdout.strip()  # the edit hasn't been committed yet, so this is the session's baseline
    if path not in state["files"]:
        state["files"].append(path)
    save_state(session_id, state)

    findings = []
    for _, targets, base in targets_for([path], bases):  # one file, so targets_for has left us in its repo
        findings += check.collect(targets, base)[0]
    if not findings:
        return 0
    lines = ["clean-code: the edit you just made breaks the skill's rules.", check.format_findings(findings), FIX_OR_FLAG]
    print("\n".join(lines), file=sys.stderr)
    return 2


def already_flagged(message, items):
    """True when the reply already lists every remaining item under 'Needs your decision'."""
    if "needs your decision" not in message.lower():
        return False
    return all(f"{os.path.basename(path)}:{lineno}" in message for path, lineno, *_ in items)


def on_stop(event):
    session_id = event.get("session_id", "default")
    state = load_state(session_id)
    if event.get("stop_hook_active") or not state["files"]:
        return 0

    findings, exceptions, names = run_checks(state["files"], state.get("bases", {}))
    new_names = [n for n in names if n not in state["reported"]]
    keys = [f"{f[0]}:{f[2]}:{f[4]}" for f in findings + exceptions]
    new_keys = [k for k in keys if k not in state["reported"]] + new_names
    if not new_keys:
        return 0
    if not new_names and already_flagged(event.get("last_assistant_message") or "", findings + exceptions):
        return 0
    state["reported"] += new_keys
    save_state(session_id, state)

    parts = ["clean-code check before finishing:"]
    if findings:
        parts.append("Violations in code you changed:\n" + check.format_findings(findings))
    if exceptions:
        parts.append("Kept exceptions:\n" + check.format_findings(exceptions))
    if findings or exceptions:
        parts.append(FIX_OR_FLAG + " Kept exceptions always go under 'Needs your decision'.")
    if new_names:
        parts.append(check.LOOK_AT_BOTH + "\n" + "\n".join(new_names))
    print(json.dumps({"decision": "block", "reason": "\n\n".join(parts)}))
    return 0


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    name = event.get("hook_event_name", "")
    if name == "PostToolUse":
        return on_edit(event)
    if name in ("Stop", "SubagentStop"):
        return on_stop(event)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:  # a broken hook must never wedge the session
        print(f"clean-code hook error (ignored): {error}", file=sys.stderr)
        sys.exit(0)
