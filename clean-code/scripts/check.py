#!/usr/bin/env python3
"""Mechanical clean-code check for the lines you changed.

Usage:
  python3 check.py              # check lines changed vs HEAD (+ untracked files) in the current git repo
  python3 check.py --base main  # check lines changed vs another ref
  python3 check.py FILE...      # check whole files (no git needed)

Flags the bright-line violations a regex can see:
  one-line-if   `if (...)` with its body on the same line (TS/JS)
  memo          useMemo / useCallback / React.memo / memo() with no reason comment
  params        function with 4+ parameters (Go: not counting ctx)
  wrapper       named function that only forwards to another call or property
and lists the new top-level symbols you introduced, with same-named
definitions elsewhere in the repo, so you can confirm you did not reinvent them.

It is a heuristic: it can miss things and it can flag a line you can justify.
Fix what it flags, or say in your reply why that line is an exception.
Exit code: 0 clean, 1 findings.
"""

import os
import re
import subprocess
import sys

TS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
GO_EXT = (".go",)
SKIP_DIRS = {"node_modules", "dist", "build", ".next", "vendor", ".git", "coverage"}
KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "function", "typeof", "await", "new", "super", "import"}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def changed_lines(base):
    """Map file -> set of changed line numbers (None means the whole file)."""
    result = {}
    current = None
    for line in git("diff", "-U0", "--no-color", base, "--").splitlines():
        if line.startswith("+++ "):
            path = line[4:]
            current = path[2:] if path.startswith("b/") else None
            if current:
                result.setdefault(current, set())
            continue
        match = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", line)
        if match and current:
            start = int(match.group(1))
            count = int(match.group(2) or 1)
            result[current].update(range(start, start + count))
    for path in git("ls-files", "--others", "--exclude-standard").splitlines():
        result[path] = None
    return result


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def match_paren(text, open_index):
    """Return index of the bracket closing text[open_index], or -1."""
    pairs = {"(": ")", "[": "]", "{": "}", "<": ">"}
    stack = []
    quote = None
    i = open_index
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
        elif ch in "([{":
            stack.append(pairs[ch])
        elif ch in ")]}":
            if not stack or stack.pop() != ch:
                return -1
            if not stack:
                return i
        i += 1
    return -1


def split_top_level(params):
    parts, depth, current = [], 0, ""
    for ch in params:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    parts.append(current)
    return [p.strip() for p in parts if p.strip()]


def param_name(param):
    param = param.lstrip(".")
    return re.split(r"[\s:=?]", param, maxsplit=1)[0]


def has_reason_comment(lines, lineno):
    """True if the line or the line above carries a comment (the stated reason)."""
    here = lines[lineno - 1]
    above = lines[lineno - 2].strip() if lineno >= 2 else ""
    return "//" in here or above.startswith("//") or above.startswith("/*") or above.startswith("*")


def check_ts(path, text, wanted):
    findings = []
    lines = text.splitlines()

    def add(lineno, rule, message):
        if wanted is None or lineno in wanted:
            findings.append((path, lineno, rule, message, lines[lineno - 1].strip()))

    # one-line-if: anything after the condition's ")" other than "{"
    for m in re.finditer(r"\bif\s*\(", text):
        close = match_paren(text, m.end() - 1)
        if close < 0:
            continue
        rest = text[close + 1 : text.find("\n", close) if "\n" in text[close:] else len(text)].strip()
        if rest and rest != "{" and not rest.startswith("//"):
            add(line_of(text, m.start()), "one-line-if",
                "if-condition and body on one line; put the body in a { } block on its own lines")

    # memo hooks without a stated reason
    for m in re.finditer(r"\b(useMemo|useCallback|React\.memo|memo)\s*\(", text):
        lineno = line_of(text, m.start())
        if has_reason_comment(lines, lineno):
            add(lineno, "memo-kept", f"{m.group(1)} kept with a reason comment")
        else:
            add(lineno, "memo",
                f"{m.group(1)} with no stated reason; use a plain value/function, or add a comment naming the concrete reason")

    # function definitions: params count + tiny wrappers
    # (name, start, index of "(", kind): kind "fn" = function keyword or method, "arrow" = const x = (...)
    defs = []
    for m in re.finditer(r"\bfunction\s*\*?\s*(\w*)\s*(?:<[^>]*>)?\s*\(", text):
        defs.append((m.group(1), m.start(), m.end() - 1, "fn"))
    for m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:<[^>]*>)?\s*\(", text):
        defs.append((m.group(1), m.start(), m.end() - 1, "arrow"))
    for m in re.finditer(r"^[ \t]*(?:(?:public|private|protected|static|async|readonly)\s+)*(\w+)\s*(?:<[^>]*>)?\s*\(", text, re.M):
        if m.group(1) not in KEYWORDS:
            defs.append((m.group(1), m.start(), m.end() - 1, "fn"))

    seen = set()
    for name, start, open_index, kind in defs:
        if open_index in seen:
            continue
        close = match_paren(text, open_index)
        if close < 0:
            continue
        after = text[close + 1 : close + 200]
        arrow = re.match(r"\s*(?::\s*[^={;]+?)?\s*=>\s*", after) if kind == "arrow" else None
        block = re.match(r"\s*(?::\s*[^{;]+?)?\s*\{", after) if kind == "fn" else None
        if not (arrow or block):
            continue
        seen.add(open_index)
        lineno = line_of(text, start)
        params = split_top_level(text[open_index + 1 : close])
        if len(params) >= 4:
            add(lineno, "params",
                f"{name or 'function'} takes {len(params)} parameters; group related ones into one typed object")
        if not name or name[0].isupper():  # components are not wrappers
            continue
        names = {param_name(p) for p in params}
        if arrow:
            body_start = close + 1 + arrow.end()
            if text[body_start] == "{":
                body_end = match_paren(text, body_start)
                body = text[body_start + 1 : body_end].strip() if body_end > 0 else ""
                body = re.sub(r"^return\s+", "", body).rstrip(";").strip()
                if "\n" in body or ";" in body:
                    continue
            else:
                end = text.find("\n", body_start)
                body = text[body_start : end if end > 0 else len(text)].strip().rstrip(";,").strip()
        else:
            body_start = close + 1 + block.end() - 1
            body_end = match_paren(text, body_start)
            body = text[body_start + 1 : body_end].strip() if body_end > 0 else ""
            if body.count(";") > 1 or body.count("\n") > 0 or not body.startswith("return "):
                continue
            body = body[len("return "):].rstrip(";").strip()
        body = re.sub(r"^await\s+", "", body)
        call = re.fullmatch(r"([\w$.]+)\((.*)\)", body, re.S)
        member = re.fullmatch(r"(\w+)((?:\??\.\w+)+)", body)
        if call:
            literal = re.compile(r"""^(['"`].*['"`]|-?\d[\d_.]*|true|false|null|undefined)$""")
            args = {param_name(a) for a in split_top_level(call.group(2)) if not literal.match(a)}
            if args <= names:
                add(lineno, "wrapper",
                    f"{name} only forwards to {call.group(1)}(); call it directly and delete {name}")
        elif member and member.group(1) in names:
            add(lineno, "wrapper", f"{name} only reads {body}; inline the property access")
    return findings


def check_go(path, text, wanted):
    findings = []
    lines = text.splitlines()
    for m in re.finditer(r"^func\s+(?:\([^)]*\)\s*)?(\w+)\s*(?:\[[^\]]*\])?\(", text, re.M):
        close = match_paren(text, m.end() - 1)
        if close < 0:
            continue
        params = [p for p in split_top_level(text[m.end() : close]) if "context.Context" not in p]
        lineno = line_of(text, m.start())
        if len(params) >= 4 and (wanted is None or lineno in wanted):
            findings.append((path, lineno, "params",
                             f"{m.group(1)} takes {len(params)} parameters besides ctx; use a params struct",
                             lines[lineno - 1].strip()))
    return findings


def new_symbols(path, text, wanted):
    pattern = (r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\s+(\w+)|const\s+(\w+)\s*(?::[^=]+)?=|"
               r"(?:type|interface|class)\s+(\w+))")
    if path.endswith(GO_EXT):
        pattern = r"^(?:func\s+(?:\([^)]*\)\s*)?(\w+)|type\s+(\w+)|var\s+(\w+))"
    symbols = []
    for m in re.finditer(pattern, text, re.M):
        lineno = line_of(text, m.start())
        if wanted is None or lineno in wanted:
            symbols.append((next(g for g in m.groups() if g), lineno))
    return symbols


def find_definitions(name, exclude):
    out = git("grep", "-n", "-E",
              rf"(function|const|let|type|interface|class|func)[[:space:]]+(\([^)]*\)[[:space:]]*)?{name}([^[:alnum:]_]|$)", "--",
              *[f"*{e}" for e in TS_EXT + GO_EXT])
    return [l for l in out.splitlines() if not l.startswith(exclude + ":")]


EXCEPTION_RULES = {"memo-kept"}


def collect(targets):
    """targets: {path: set of line numbers or None for whole file}. Returns (findings, exceptions, symbols)."""
    findings, symbols = [], []
    for path, wanted in sorted(targets.items()):
        if not path.endswith(TS_EXT + GO_EXT) or not os.path.isfile(path):
            continue
        if any(part in SKIP_DIRS for part in path.split(os.sep)) or ".test." in path or ".spec." in path:
            continue
        if wanted is not None and not wanted:
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        findings += check_go(path, text, wanted) if path.endswith(GO_EXT) else check_ts(path, text, wanted)
        symbols += [(path, name, lineno) for name, lineno in new_symbols(path, text, wanted)]
    findings = sorted(set(findings))
    exceptions = [f for f in findings if f[2] in EXCEPTION_RULES]
    findings = [f for f in findings if f[2] not in EXCEPTION_RULES]
    return findings, exceptions, symbols


def format_findings(findings):
    return "\n".join(f"{path}:{lineno}  [{rule}] {message}\n    {source}"
                     for path, lineno, rule, message, source in findings)


def report(findings, exceptions, symbols):
    out = []
    if findings:
        out.append(f"clean-code check: {len(findings)} finding(s)\n")
        out.append(format_findings(findings))
    else:
        out.append("clean-code check: no mechanical violations in the checked lines.")
    if exceptions:
        out.append("\nKept as exceptions (list each under 'Needs your decision' in your reply):")
        out.append(format_findings(exceptions))
    if symbols:
        out.append("\nNew symbols you introduced. For each, confirm the project had nothing that already does this:")
        in_git = git("rev-parse", "--is-inside-work-tree").strip() == "true"
        for path, name, lineno in symbols:
            elsewhere = find_definitions(name, path) if in_git else []
            note = ("  <- also defined in: " + ", ".join(":".join(l.split(":")[:2]) for l in elsewhere[:3])) if elsewhere else ""
            out.append(f"  {path}:{lineno}  {name}{note}")
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    base = "HEAD"
    if args[:1] == ["--base"]:
        base, args = args[1], args[2:]
    if args:
        targets = {}
        for arg in args:
            if os.path.isdir(arg):
                for root, dirs, files in os.walk(arg):
                    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                    for f in files:
                        targets[os.path.join(root, f)] = None
            else:
                targets[arg] = None
    else:
        if git("rev-parse", "--is-inside-work-tree").strip() != "true":
            sys.exit("Not a git repo: pass the files you changed, e.g. check.py src/a.ts src/b.tsx")
        os.chdir(git("rev-parse", "--show-toplevel").strip())
        targets = changed_lines(base)

    findings, exceptions, symbols = collect(targets)
    print(report(findings, exceptions, symbols))
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
