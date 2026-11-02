#!/usr/bin/env python3
"""Claude Code hook for the clean-code skill (registered in SKILL.md frontmatter).

PostToolUse (Edit|Write|MultiEdit): checks the lines just changed in that file and
  sends violations straight back to the agent (exit 2 -> stderr is shown to Claude).
Stop / SubagentStop: if this session edited code and violations or kept exceptions
  remain that the agent hasn't been told about yet, blocks the stop once with the list,
  so the agent fixes them or lists them for the user under "Needs your decision".

Sessions that never edited a file (e.g. a reviewer) are never blocked.
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
        return {"files": [], "reported": []}


def save_state(session_id, state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, f"{session_id}.json"), "w") as fh:
        json.dump(state, fh)


def repo_root(path):
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    result = subprocess.run(["git", "-C", directory, "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def targets_for(files):
    """Map files to {repo-relative or absolute path: changed lines or None}, chdir-ing per repo."""
    by_root = {}
    for path in files:
        if os.path.isfile(path):
            by_root.setdefault(repo_root(path), []).append(path)
    results = []
    for root, paths in by_root.items():
        if root is None:
            results.append((None, {p: None for p in paths}))
            continue
        os.chdir(root)
        changed = check.changed_lines("HEAD")
        relative = [os.path.relpath(p, root) for p in paths]
        results.append((root, {r: changed[r] for r in relative if r in changed}))
    return results


def run_checks(files):
    findings, exceptions, duplicates = [], [], []
    for root, targets in targets_for(files):
        if root:
            os.chdir(root)
        f, e, symbols = check.collect(targets)
        findings += f
        exceptions += e
        if root:
            for path, name, lineno in symbols:
                elsewhere = check.find_definitions(name, path)
                if elsewhere:
                    where = ", ".join(":".join(l.split(":")[:2]) for l in elsewhere[:3])
                    duplicates.append(f"{path}:{lineno}  {name} is also defined in {where}; reuse it instead")
    return findings, exceptions, duplicates


def on_edit(event):
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if not path.endswith(check.TS_EXT + check.GO_EXT):
        return 0
    session_id = event.get("session_id", "default")
    state = load_state(session_id)
    if path not in state["files"]:
        state["files"].append(path)
        save_state(session_id, state)

    findings, _, duplicates = run_checks([path])
    if not findings and not duplicates:
        return 0
    lines = ["clean-code: the edit you just made breaks the skill's rules."]
    if findings:
        lines.append(check.format_findings(findings))
    if duplicates:
        lines.append("Possible reinvention:\n" + "\n".join(duplicates))
    lines.append(FIX_OR_FLAG)
    print("\n".join(lines), file=sys.stderr)
    return 2


def already_flagged(message, items, duplicates):
    """True when the reply already lists every remaining item under 'Needs your decision'."""
    if "needs your decision" not in message.lower() or duplicates:
        return False
    return all(f"{os.path.basename(path)}:{lineno}" in message for path, lineno, *_ in items)


def on_stop(event):
    session_id = event.get("session_id", "default")
    state = load_state(session_id)
    if event.get("stop_hook_active") or not state["files"]:
        return 0

    findings, exceptions, duplicates = run_checks(state["files"])
    keys = [f"{f[0]}:{f[2]}:{f[4]}" for f in findings + exceptions] + duplicates
    new_keys = [k for k in keys if k not in state["reported"]]
    if not new_keys or already_flagged(event.get("last_assistant_message") or "", findings + exceptions, duplicates):
        return 0
    state["reported"] += new_keys
    save_state(session_id, state)

    parts = ["clean-code check before finishing:"]
    if findings:
        parts.append("Violations in code you changed:\n" + check.format_findings(findings))
    if duplicates:
        parts.append("Possible reinvention:\n" + "\n".join(duplicates))
    if exceptions:
        parts.append("Kept exceptions:\n" + check.format_findings(exceptions))
    parts.append(FIX_OR_FLAG + " Kept exceptions always go under 'Needs your decision'.")
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
