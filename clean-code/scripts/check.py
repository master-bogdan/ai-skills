#!/usr/bin/env python3
"""Mechanical clean-code check for the lines you changed.

Usage:
  python3 check.py              # check lines changed vs HEAD (+ untracked files) in the current git repo
  python3 check.py --base main  # check lines changed since the merge-base of main and HEAD
  python3 check.py FILE...      # check whole files (no git needed; every function counts as new)

Flags the bright-line violations a regex can see (comments are ignored):
  one-line-if   `if (...)` with its body on the same line (TS/JS)
  memo          useMemo / useCallback / React.memo / memo() with no reason comment
  params        new function with 4+ parameters (Go: not counting ctx; Express error handlers exempt)
  wrapper       private named function that only forwards to another call or property
                (exported ones are left to review: they may be a layer's official entry point)
Suggests, without failing:
  params-existing  a function the base already had, touched by the diff, with 4+ parameters
Lists the new top-level symbols you introduced, plus definitions elsewhere with the same
name or a version/variant of it (fooV2, fooAsync...), and new files named like existing ones,
so you can confirm you did not reinvent them.

It is a heuristic: it can miss things and it can flag a line you can justify.
Fix what it flags, or say in your reply why that line is an exception.
Exit code: 0 clean, 1 findings.
"""

import collections
import os
import re
import subprocess
import sys

TS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
GO_EXT = (".go",)
SKIP_DIRS = {"node_modules", "dist", "build", ".next", "vendor", ".git", "coverage"}
SKIP_TAGS = (".test.", ".spec.", ".bench.")
KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "function", "typeof", "await", "new", "super", "import"}
GO_FUNC = re.compile(r"^func\s+(?:\([^)]*\)\s*)?(\w+)\s*(?:\[[^\]]*\])?\(", re.M)
# A declaration at the start of a line; {s} is the whitespace class (POSIX for git grep, \s for Python).
DECL = (r"^{s}*((export|default|declare|async|abstract){s}+)*"
        r"(function\*?|const|let|var|type|interface|class|enum|func({s}*\([^)]*\))?){s}+")
VARIANT = r"V[0-9]+|Async|Sync|Impl|New|Legacy"
LOOK_AT_BOTH = (
    "Same or similar names already exist. Look at both: obviously the same thing -> reuse the existing one; "
    "obviously different -> say nothing; unsure -> add one line to your final report: "
    "'Potential duplicate: X (also in path)'."
)


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


def added_files(base):
    """Files added since base (committed or not), plus untracked ones."""
    return set(git("diff", "--name-only", "--diff-filter=A", base, "--").splitlines()
               + git("ls-files", "--others", "--exclude-standard").splitlines())


def is_checked(path):
    """True for TS/JS/Go source outside build/vendor dirs and test/spec/bench files."""
    return (path.endswith(TS_EXT + GO_EXT)
            and not any(part in SKIP_DIRS for part in path.split(os.sep))
            and not any(tag in path for tag in SKIP_TAGS))


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def mask_comments(text):
    """Blank out // and /* */ comments, keeping positions and newlines, so patterns only see code."""
    out = list(text)
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote or (ch == "\n" and quote != "`"):
                quote = None
        elif ch in "'\"`":
            quote = ch
        elif ch == "\\":  # outside strings only in regex literals: skip the escaped char (e.g. /a\//)
            i += 2
            continue
        elif text.startswith("//", i) or text.startswith("/*", i):
            line_comment = text[i + 1] == "/"
            end = text.find("\n" if line_comment else "*/", i + 2)
            if end < 0:
                end = len(text)
            elif not line_comment:
                end += 2
            for j in range(i, end):
                if out[j] != "\n":
                    out[j] = " "
            i = end
            continue
        i += 1
    return "".join(out)


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


def expression_end(code, start):
    """Index where the arrow-function expression body starting at start ends.

    Stops at a top-level ; or , or an unmatched closing bracket, or at a line break
    unless the next line continues the expression (.map, ?? x, && y...) or this one ends in an operator.
    """
    depth, quote, i = 0, None, start
    while i < len(code):
        ch = code[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            if depth == 0:
                return i
            depth -= 1
        elif depth == 0 and ch in ";,":
            return i
        elif depth == 0 and ch == "\n":
            continues = re.compile(r"\s*[.?:&|+\-*/%=]").match(code, i)
            if not continues and not re.search(r"(=>|[?:&|+\-*/%=<>])\s*$", code[start:i]):
                return i
        i += 1
    return i


def split_top_level(params):
    parts, depth, current = [], 0, ""
    for i, ch in enumerate(params):
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>" and params[i - 1 : i + 1] != "=>":
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


def ts_functions(code):
    """Function definitions in comment-masked TS/JS: (name, start, index of "(", kind, public).

    kind "fn" = function keyword or method, "arrow" = const x = (...) =>.
    public: exported (export keyword, export { x }, export default x) or a class method
    that is neither `private` nor `#name`.
    """
    exported = set(re.findall(r"^export\s+default\s+(\w+)\s*;?\s*$", code, re.M))
    for m in re.finditer(r"^export\s*\{([^}]*)\}", code, re.M):
        exported.update(re.findall(r"(?:^|,)\s*(?:type\s+)?(\w+)", m.group(1)))
    defs = []
    patterns = ((r"\bfunction\s*\*?\s*(\w*)\s*(?:<[^>]*>)?\s*\(", "fn"),
                (r"(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:<[^>]*>)?\s*\(", "arrow"))
    for pattern, kind in patterns:
        for m in re.finditer(pattern, code):
            prefix = code[code.rfind("\n", 0, m.start()) + 1 : m.start()]
            public = (bool(re.fullmatch(r"export\s+(?:default\s+)?(?:async\s+)?", prefix))
                      or (prefix == "" and m.group(1) in exported))
            defs.append((m.group(1), m.start(), m.end() - 1, kind, public))
    method = r"^[ \t]*((?:(?:public|private|protected|static|async|readonly|override)\s+)*)(#?\w+)\s*(?:<[^>]*>)?\s*\("
    for m in re.finditer(method, code, re.M):
        if m.group(2) not in KEYWORDS:
            public = "private" not in m.group(1) and not m.group(2).startswith("#")
            defs.append((m.group(2), m.start(), m.end() - 1, "fn", public))
    return defs


def check_ts(text, wanted, existing):
    """Findings (lineno, rule, message, source) in TS/JS text; existing: function names the base already had."""
    findings = []
    lines = text.splitlines()
    code = mask_comments(text)

    def add(lineno, rule, message):
        if wanted is None or lineno in wanted:
            findings.append((lineno, rule, message, lines[lineno - 1].strip()))

    # one-line-if: anything after the condition's ")" other than "{"
    for m in re.finditer(r"\bif\s*\(", code):
        close = match_paren(code, m.end() - 1)
        if close < 0:
            continue
        rest = code[close + 1 : code.find("\n", close) if "\n" in code[close:] else len(code)].strip()
        if rest and rest != "{":
            add(line_of(code, m.start()), "one-line-if",
                "if-condition and body on one line; put the body in a { } block on its own lines")

    # memo hooks without a stated reason
    for m in re.finditer(r"\b(useMemo|useCallback|React\.memo|memo)\s*\(", code):
        lineno = line_of(code, m.start())
        if has_reason_comment(lines, lineno):
            add(lineno, "memo-kept", f"{m.group(1)} kept with a reason comment")
        else:
            add(lineno, "memo",
                f"{m.group(1)} with no stated reason; use a plain value/function, or add a comment naming the concrete reason")

    # function definitions: params count + tiny wrappers
    seen = set()
    for name, start, open_index, kind, public in ts_functions(code):
        if open_index in seen:
            continue
        close = match_paren(code, open_index)
        if close < 0:
            continue
        after = code[close + 1 : close + 200]
        arrow = re.match(r"\s*(?::\s*[^={;]+?)?\s*=>\s*", after) if kind == "arrow" else None
        block = re.match(r"\s*(?::\s*[^{;]+?)?\s*\{", after) if kind == "fn" else None
        if not (arrow or block):
            continue
        seen.add(open_index)
        lineno = line_of(code, start)
        params = split_top_level(code[open_index + 1 : close])
        # Express only treats (err, req, res, next) as an error handler, so that signature is dictated
        express_error_handler = re.fullmatch(r"(?:err|error|e) req\w* res\w* next",
                                             " ".join(param_name(p).lstrip("_") for p in params))
        touched = wanted is None or not wanted.isdisjoint(range(lineno, line_of(code, close) + 1))
        if len(params) >= 4 and touched and not express_error_handler:
            findings.append((lineno, "params-existing" if name and name in existing else "params",
                             f"{name or 'function'} takes {len(params)} parameters; group related ones into one typed object",
                             lines[lineno - 1].strip()))
        if public or not name or name[0].isupper():  # exported ones are judged in review; components are not wrappers
            continue
        names = {param_name(p) for p in params}
        if arrow:
            body_start = close + 1 + arrow.end()
            if code[body_start] == "{":
                body_end = match_paren(code, body_start)
                body = code[body_start + 1 : body_end].strip() if body_end > 0 else ""
                body = re.sub(r"^return\s+", "", body).rstrip(";").strip()
                if "\n" in body or ";" in body:
                    continue
            else:
                body = code[body_start : expression_end(code, body_start)].strip()
        else:
            body_start = close + 1 + block.end() - 1
            body_end = match_paren(code, body_start)
            body = code[body_start + 1 : body_end].strip() if body_end > 0 else ""
            if body.count(";") > 1 or body.count("\n") > 0 or not body.startswith("return "):
                continue
            body = body[len("return "):].rstrip(";").strip()
        body = re.sub(r"^(?:await|void)\s+", "", body)
        call = re.match(r"([\w$.]+)\(", body)
        member = re.fullmatch(r"(\w+)((?:\??\.\w+)+)", body)
        if call and match_paren(body, call.end() - 1) == len(body) - 1:
            literal = re.compile(r"""^(['"`].*['"`]|-?\d[\d_.]*|true|false|null|undefined)$""")
            args = {param_name(a) for a in split_top_level(body[call.end() : -1]) if not literal.match(a)}
            if args <= names:
                add(lineno, "wrapper",
                    f"{name} only forwards to {call.group(1)}(); call it directly and delete {name}")
        elif member and member.group(1) in names:
            add(lineno, "wrapper", f"{name} only reads {body}; inline the property access")
    return findings


def check_go(text, wanted, existing):
    """Findings (lineno, rule, message, source) in Go text; existing: function names the base already had."""
    findings = []
    lines = text.splitlines()
    code = mask_comments(text)
    for m in GO_FUNC.finditer(code):
        close = match_paren(code, m.end() - 1)
        if close < 0:
            continue
        params = [p for p in split_top_level(code[m.end() : close]) if "context.Context" not in p]
        lineno = line_of(code, m.start())
        touched = wanted is None or not wanted.isdisjoint(range(lineno, line_of(code, close) + 1))
        if len(params) >= 4 and touched:
            findings.append((lineno, "params-existing" if m.group(1) in existing else "params",
                             f"{m.group(1)} takes {len(params)} parameters besides ctx; use a params struct",
                             lines[lineno - 1].strip()))
    return findings


def new_symbols(path, text, wanted):
    pattern = (r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\s+(\w+)|const\s+(\w+)\s*(?::[^=]+)?=|"
               r"(?:type|interface|class)\s+(\w+))")
    if path.endswith(GO_EXT):
        pattern = r"^(?:func\s+(?:\([^)]*\)\s*)?(\w+)|type\s+(\w+)|var\s+(\w+))"
    code = mask_comments(text)
    symbols = []
    for m in re.finditer(pattern, code, re.M):
        lineno = line_of(code, m.start())
        if wanted is None or lineno in wanted:
            symbols.append((next(g for g in m.groups() if g), lineno))
    return symbols


def definitions(name):
    """Declarations of name, or of a version/variant of it (fooV2 <-> foo, fooAsync...), in tracked code.

    Returns [(path, lineno, declared name)]. Imports and export lists are not declarations.
    """
    stem = re.sub(rf"(?<=.)({VARIANT})$", "", name)
    out = git("grep", "-n", "-E", DECL.format(s="[[:space:]]") + rf"{stem}({VARIANT})?([^[:alnum:]_$]|$)",
              "--", *[f"*{e}" for e in TS_EXT + GO_EXT])
    found = []
    for line in out.splitlines():
        path, lineno, source = line.split(":", 2)
        # `type X,` / `type X }` / `type X as Y` on its own line is an item of a multi-line import or export list
        declared = re.match(DECL.format(s=r"\s") + r"(?P<name>\w+)\b(?!\s*(?:[,}]|as\b|$))", source)
        if declared:
            found.append((path, lineno, declared.group("name")))
    return found


def related(symbols, added):
    """Lines naming same-named definitions, version/variant names and same-named files, for the agent to judge."""
    out = []
    for path, name, lineno in symbols:
        found = definitions(name)
        same = [f"{p}:{n}" for p, n, declared in found if declared == name and p != path]
        near = [f"{declared} ({p}:{n})" for p, n, declared in found if declared != name]
        if same:
            out.append(f"{path}:{lineno}  {name}  <- also defined in: {', '.join(same[:3])}")
        if near:
            out.append(f"{path}:{lineno}  {name}  <- similar name: {', '.join(near[:3])}")
    by_basename = collections.defaultdict(list)
    for tracked in git("ls-files").splitlines():
        by_basename[os.path.basename(tracked)].append(tracked)
    for path in sorted(p for p in added if is_checked(p)):
        others = [p for p in by_basename[os.path.basename(path)] if p != path]
        if 0 < len(others) < 3:  # 3+ means a convention like index.ts
            out.append(f"{path}  <- same file name as: {', '.join(others)}")
    return out


EXCEPTION_RULES = {"memo-kept"}
SUGGESTION_RULES = {"params-existing"}


def collect(targets, base=None):
    """targets: {path: set of line numbers or None for whole file}; base: the ref the diff is against
    (None: every function counts as new). Returns (findings, exceptions, suggestions, symbols)."""
    findings, symbols = [], []
    for path, wanted in sorted(targets.items()):
        if not is_checked(path) or not os.path.isfile(path):
            continue
        if wanted is not None and not wanted:
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        old = mask_comments(git("show", f"{base}:{path}")) if base else ""
        if path.endswith(GO_EXT):
            existing = {m.group(1) for m in GO_FUNC.finditer(old)}
            findings += [(path, *f) for f in check_go(text, wanted, existing)]
        else:
            existing = {d[0] for d in ts_functions(old)}
            findings += [(path, *f) for f in check_ts(text, wanted, existing)]
        symbols += [(path, name, lineno) for name, lineno in new_symbols(path, text, wanted)]
    findings = sorted(set(findings))
    exceptions = [f for f in findings if f[2] in EXCEPTION_RULES]
    suggestions = [f for f in findings if f[2] in SUGGESTION_RULES]
    findings = [f for f in findings if f[2] not in EXCEPTION_RULES | SUGGESTION_RULES]
    return findings, exceptions, suggestions, symbols


def format_findings(findings):
    return "\n".join(f"{path}:{lineno}  [{rule}] {message}\n    {source}"
                     for path, lineno, rule, message, source in findings)


def report(results, added):
    """results: collect()'s tuple; added: files the diff adds (for the same-file-name list)."""
    findings, exceptions, suggestions, symbols = results
    out = []
    if findings:
        out.append(f"clean-code check: {len(findings)} finding(s)\n")
        out.append(format_findings(findings))
    else:
        out.append("clean-code check: no mechanical violations in the checked lines.")
    if exceptions:
        out.append("\nKept as exceptions (list each under 'Needs your decision' in your reply):")
        out.append(format_findings(exceptions))
    if suggestions:
        out.append("\nSuggestions (existing functions; switch to one object only if it's cheap):")
        out.append(format_findings(suggestions))
    if symbols:
        out.append("\nNew symbols you introduced. For each, confirm the project had nothing that already does this:")
        out += [f"  {path}:{lineno}  {name}" for path, name, lineno in symbols]
    in_git = git("rev-parse", "--is-inside-work-tree").strip() == "true"
    notes = related(symbols, added) if in_git else []
    if notes:
        out.append("\n" + LOOK_AT_BOTH)
        out += [f"  {note}" for note in notes]
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    ref = None
    if args[:1] == ["--base"]:
        ref, args = args[1], args[2:]
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
        base, added = None, set()
    else:
        if git("rev-parse", "--is-inside-work-tree").strip() != "true":
            sys.exit("Not a git repo: pass the files you changed, e.g. check.py src/a.ts src/b.tsx")
        os.chdir(git("rev-parse", "--show-toplevel").strip())
        base = git("merge-base", ref, "HEAD").strip() if ref else "HEAD"
        if not base:
            sys.exit(f"No merge-base between {ref} and HEAD: is {ref} a valid ref here?")
        print(f"compared against {ref} (merge-base {base[:7]})" if ref else "compared against HEAD")
        targets = changed_lines(base)
        added = added_files(base)

    results = collect(targets, base)
    print(report(results, added))
    sys.exit(1 if results[0] else 0)


if __name__ == "__main__":
    main()
