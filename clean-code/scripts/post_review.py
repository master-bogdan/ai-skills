#!/usr/bin/env python3
"""Create one GitHub PR review as a draft (pending) review, built from a findings file. It never submits.

Usage:
  python3 post_review.py --since <owner/name> <pr>   PR facts: base branch, head, changed files, your open draft, your
                                                     last review and the lines changed since, everyone's threads
  python3 post_review.py <findings.json>             dry run: check everything and print the review, create nothing
  python3 post_review.py <findings.json> --draft     create the draft; only you see it until you submit it in GitHub

Input:
  {"repo": "owner/name", "pr": 123, "head": "head_sha from --since: the commit the review read",
   "verdict": "One sentence: the main risk, or why it is safe to merge.",
   "body": "optional: only what has no line (a question, a cross-cutting note)",
   "standard": {                                                   only what the repo's base branch states
     "source": "origin/dev:.github/copilot-instructions.md",       required: where the rules were read, or "none"
     "labels": ["[MUST FIX]", "[SUGGESTION]", "..."],             the repo's labels, most severe first
     "request_changes": ["[MUST FIX]"],                           labels that make the review REQUEST_CHANGES
     "comment": ["[QUESTION]"],                                   labels that make it COMMENT; neither -> APPROVE
     "limits": {"[SUGGESTION]": 3, "[OPTIONAL]+[NIT PICK]": 1},   already picked for this PR's size
     "max_chars": 600},                                           per comment, suggestion and AI fix prompt excluded
   "findings": [{"label": "[MUST FIX]", "title": "...", "path": "src/x.ts", "line": 41, "start_line": 37,
                 "why": "...", "evidence": "src/y.ts:12-20 ...", "fix": "...", "ai_prompt": "optional",
                 "shared_with": "optional owner/name#45: the other PR of a ticket split across repos",
                 "body": "optional: the whole comment, written to the repo's own template, instead of why/evidence/fix",
                 "suggestion": "optional code"}],
   "previous": [{"comment_id": 123, "status": "fixed" | "partly_fixed" | "open" | "accepted", "note": "the reply"}],
   "not_posted": [{"title": "...", "reason": "...", "evidence": "optional src/z.ts:8"}],
   "changes": ["optional: 3-5 plain lines for a collapsed 'What changed in this PR' section"]}

Rules: every key the repo states wins. A missing key falls back to DEFAULT_STANDARD (limits by PR size), except that
the label-based rules (request_changes, comment, limits) are not filled in when the repo names its own labels. The
dry run says which rules came from the defaults.

Citations: every `path:line` or `path:12-20` in a comment's text must exist at the head commit; the script turns each
into a link pinned to that commit. A file name without its folder is rejected. Links don't count toward max_chars.

Head: the draft is attached to `head`. If the PR has moved since, nothing is created: review the new commits first.

Re-review: `previous` must list every thread in `open_threads` from --since, each with a verdict. A thread of yours is
open until it is settled: resolved by you, or resolved by someone else after your last reply settled it ("Fixed …" or
"Agreed: …"). Authors often resolve their own threads, including after a "Still open" reply. `closed_threads` (yours, settled) and `other_threads` are read only to avoid repeats.
Replies go into the draft (a fixed one defaults to "Fixed in <head>."); open and partly fixed threads count toward
the status. New findings must sit on lines changed since your last review, unless their label requests changes.

The script checks every anchor against the PR diff (new side), every citation, and the limits; it derives the
recommended status, and fails with every problem listed instead of trimming anything. With --draft it creates the
pending review, adds the replies to it, and prints the summary to paste: GitHub's submit box starts empty and
replaces the draft's summary with its contents, so the user pastes it there. Stdlib + `gh` only.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile

LABEL_IN_TEXT = re.compile(r"^\W*(\[[A-Z][A-Z ]*\])")
SUGGESTION_BLOCK = re.compile(r"```suggestion\n.*?```", re.S)
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
CITATION = re.compile(r"(?P<link>\[[^\]]*\]\([^)]*\)|https?://\S+)|(?<![\w/.-])(?P<tick>`?)"
                      r"(?P<path>(?:[\w@.-]+/)*[\w@-][\w@.-]*\.[A-Za-z]\w*):(?P<first>\d+)(?:-(?P<last>\d+))?(?P=tick)")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
NOT_COUNTED = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|go\.sum|[^/]+\.lock)$"
                         r"|(^|/)(__snapshots__|__fixtures__|fixtures)/|\.snap$")
STATUS_NAMES = {"REQUEST_CHANGES": "Request changes", "COMMENT": "Comment", "APPROVE": "Approve"}
STATUS_HEADINGS = {"REQUEST_CHANGES": "🔴 Changes requested", "COMMENT": "🟡 Changes recommended", "APPROVE": "🟢 Approved"}
LABEL_MARKS = {"[MUST FIX]": "🔴", "[QUESTION]": "🟠", "[SUGGESTION]": "🟡", "[OPTIONAL]": "🔵", "[NIT PICK]": "⚪"}
VERDICTS = {"fixed": "Fixed", "partly_fixed": "Partly fixed", "open": "Still open", "accepted": "Accepted"}
SETTLING_REPLIES = ("fixed", "agreed")  # how the replies that close a thread open (references/review.md step 5)
DEFAULT_STANDARD = {
    "labels": ["[MUST FIX]", "[SUGGESTION]", "[QUESTION]", "[OPTIONAL]", "[NIT PICK]"],
    "request_changes": ["[MUST FIX]"],
    "comment": ["[QUESTION]"],
    "max_chars": 600,
}
DEFAULT_LIMITS = [  # (most counted files, limits): the tiers of the sheets repos' review standard
    (15, {"[SUGGESTION]": 3, "[QUESTION]": 2, "[OPTIONAL]+[NIT PICK]": 1}),
    (40, {"[SUGGESTION]": 8, "[QUESTION]": 4, "[OPTIONAL]+[NIT PICK]": 3}),
    (None, {"[SUGGESTION]": 12, "[QUESTION]": 6, "[OPTIONAL]+[NIT PICK]": 4}),
]
LABEL_RULES = ("request_changes", "comment", "limits")
COMPARE_FILE_CAP = 300  # GitHub's compare API lists at most this many changed files
THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id isResolved isOutdated path line resolvedBy { login }
                comments(first: 100) { pageInfo { hasNextPage }
                                       nodes { databaseId url body author { login } pullRequestReview { databaseId state } } } }
      }
    }
  }
}"""
REPLY_MUTATION = """
mutation($review: ID!, $thread: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewId: $review, pullRequestReviewThreadId: $thread,
                                          body: $body}) { comment { id } }
}"""


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def new_side(patch):
    """(every new-side line of the hunks, the added ones only) for one file's patch."""
    lines, added, current = set(), set(), 0
    for row in (patch or "").splitlines():
        hunk = HUNK.match(row)
        if hunk:
            current = int(hunk.group(1))
            continue
        if row.startswith("-") or row.startswith("\\"):
            continue
        lines.add(current)
        if row.startswith("+"):
            added.add(current)
        current += 1
    return lines, added


def load_pr(repo, pr):
    info = json.loads(gh("pr", "view", str(pr), "-R", repo, "--json", "headRefOid,baseRefName"))
    files = json.loads(gh("api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr}/files?per_page=100"))
    diff = {f["filename"]: new_side(f.get("patch"))[0] for page in files for f in page}
    return info, diff


def counted_files(diff):
    """Changed files, leaving out lock files, fixtures and snapshots."""
    return sum(1 for path in diff if not NOT_COUNTED.search(path))


def with_defaults(standard, counted):
    """The repo's rules, each missing one taken from the defaults. Returns (rules, keys taken from the defaults)."""
    limits = next(tier for most, tier in DEFAULT_LIMITS if most is None or counted <= most)
    defaults = dict(DEFAULT_STANDARD, limits=limits)
    own_labels = "labels" in standard
    taken = [key for key in defaults if key not in standard and not (own_labels and key in LABEL_RULES)]
    return dict(standard, **{key: defaults[key] for key in taken}), taken


def thread_summary(node):
    first, *replies = node["comments"]["nodes"]
    lines = [line for line in first["body"].strip().splitlines() if line.strip()]
    label = LABEL_IN_TEXT.match(lines[0]) if lines else None
    title = lines[0][label.end():] if label else (lines[0] if lines else "")
    if not title.strip() and len(lines) > 1:  # a label alone on the first line
        title = lines[1][:120]
    return {"comment_id": first["databaseId"], "thread_id": node["id"], "label": label.group(1) if label else "",
            "title": title.replace("**", "").strip() or "(untitled)", "body": first["body"].strip(),
            "path": node["path"], "line": node["line"],
            "outdated": node["isOutdated"], "resolved": node["isResolved"], "url": first["url"],
            "resolved_by": (node.get("resolvedBy") or {}).get("login"),
            "review_id": (first.get("pullRequestReview") or {}).get("databaseId"),
            "pending": (first.get("pullRequestReview") or {}).get("state") == "PENDING",
            "author": (first["author"] or {}).get("login"),
            "replies": [{"author": (r["author"] or {}).get("login"), "body": r["body"].strip()} for r in replies]}


def threads_from_pages(pages):
    """Every review thread across the GraphQL pages. Stops when a thread has more comments than one page holds."""
    nodes = [node for page in pages for node in page["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]]
    crowded = [f"{node['path']}:{node['line']}" for node in nodes if node["comments"]["pageInfo"]["hasNextPage"]]
    if crowded:
        sys.exit("Stopped: these threads have more than 100 comments, which this script can't read in full: "
                 + ", ".join(crowded))
    return [thread_summary(node) for node in nodes]


def to_ranges(lines):
    ranges, start = [], None
    for line in sorted(lines):
        if start is None:
            start = end = line
        elif line == end + 1:
            end = line
        else:
            ranges.append(f"{start}-{end}" if end > start else str(start))
            start = end = line
    if start is not None:
        ranges.append(f"{start}-{end}" if end > start else str(start))
    return ", ".join(ranges)


def changed_since(repo, last_sha, head, diff):
    """({path: lines} of the PR diff added since last_sha, None), or (None, why the whole PR needs a review)."""
    try:
        data = json.loads(gh("api", f"repos/{repo}/compare/{last_sha}...{head}"))
    except subprocess.CalledProcessError:
        return None, "your last reviewed commit is no longer on GitHub"
    if data.get("status") not in ("ahead", "identical"):
        return None, "the branch was force-pushed since your last review"
    files = data.get("files", [])
    if len(files) >= COMPARE_FILE_CAP:
        return None, f"GitHub lists at most {COMPARE_FILE_CAP} files changed since your last review"
    changed = {}
    for item in files:
        pr_lines = diff.get(item["filename"], set())
        added = new_side(item["patch"])[1] if item.get("patch") else pr_lines
        if added & pr_lines:
            changed[item["filename"]] = added & pr_lines
    return changed, None


def awaits_verdict(thread, me):
    """True until settled: resolved by you, or resolved by someone else after your last reply settled it."""
    if not thread["resolved"]:
        return True
    if thread["resolved_by"] == me:
        return False
    last = thread["replies"][-1] if thread["replies"] else None
    settled = last and last["author"] == me and last["body"].lstrip("*_ ").lower().startswith(SETTLING_REPLIES)
    return not settled


def load_previous(repo, pr, head, diff):
    """Your open draft, your last review and what changed since, and the PR's threads (yours open or closed, others')."""
    me = gh("api", "user", "-q", ".login").strip()
    owner, name = repo.split("/")
    pages = json.loads(gh("api", "graphql", "--paginate", "--slurp", "-f", f"query={THREADS_QUERY}", "-F",
                          f"owner={owner}", "-F", f"name={name}", "-F", f"number={pr}"))
    threads = threads_from_pages(pages)
    mine = [t for t in threads if t["author"] == me and not t["pending"]]  # a draft's threads belong to the draft
    reviews = [r for page in json.loads(gh("api", "--paginate", "--slurp", f"repos/{repo}/pulls/{pr}/reviews"))
               for r in page if r["user"]["login"] == me]
    pending = [r["html_url"] for r in reviews if r["state"] == "PENDING"]
    submitted = [r for r in reviews if r["state"] != "PENDING"]
    last_sha = submitted[-1]["commit_id"] if submitted else None
    opened = {t["review_id"] for t in mine}
    with_threads = [r for r in submitted if r["id"] in opened]  # an approval or a reply has no summary of its own
    lost = with_threads[-1] if with_threads and not with_threads[-1]["body"].strip() else None
    since, whole_pr = changed_since(repo, last_sha, head, diff) if last_sha else (None, None)
    return {"me": me, "pending_review": pending[0] if pending else None, "last_reviewed_sha": last_sha,
            "summary_missing": lost["html_url"] if lost else None,
            "whole_pr": whole_pr, "changed_since": since,
            "open_threads": [t for t in mine if awaits_verdict(t, me)],
            "closed_threads": [t for t in mine if not awaits_verdict(t, me)],
            "other_threads": [t for t in threads if t["author"] != me]}


def file_size(repo, head, path):
    """Line count of path at the head commit, or None when it isn't there."""
    try:
        text = gh("api", "-H", "Accept: application/vnd.github.raw", f"repos/{repo}/contents/{path}?ref={head}")
    except subprocess.CalledProcessError:
        return None
    return text.count("\n") + (0 if not text or text.endswith("\n") else 1)


def pin_citations(spec, text):
    """Turn every `path:line` or `path:12-20` outside a link into a link pinned at the head commit."""
    def pin(match):
        if match.group("link"):
            return match.group(0)
        first, last = match.group("first"), match.group("last")
        anchor = f"L{first}" + (f"-L{last}" if last else "")
        url = f"https://github.com/{spec['repo']}/blob/{spec['head']}/{match.group('path')}#{anchor}"
        return f"[{match.group(0)}]({url})"
    return CITATION.sub(pin, text)


def citation_problems(spec, where, text):
    problems = []
    for match in CITATION.finditer(text or ""):
        if match.group("link"):
            continue
        path, first = match.group("path"), int(match.group("first"))
        last = int(match.group("last") or first)
        if path not in spec["sizes"]:
            spec["sizes"][path] = file_size(spec["repo"], spec["head"], path)
        size = spec["sizes"][path]
        if size is None:
            problems.append(f"{where}: cites {path}, which is not in the repo at the head commit "
                            "(write the repo-relative path; link another repo's code with a full URL)")
        elif first > last or last > size:
            problems.append(f"{where}: cites {path}:{first}-{last}, but the file has {size} lines at the head commit")
    return problems


def render(spec, finding):
    """The comment, and its visible length without links' URLs, the suggestion block and the AI fix prompt."""
    if finding.get("body"):
        parts = [finding["body"].strip()]
    else:
        label = finding.get("label", "")
        mark = f"{LABEL_MARKS[label]} " if label in LABEL_MARKS else ""
        parts = [f"{mark}**{f'{label} ' if label else ''}{finding['title']}**", "", f"Why it matters: {finding['why']}",
                 f"Evidence: {finding['evidence']}", f"Recommended change: {finding['fix']}"]
    text = pin_citations(spec, "\n".join(parts))
    counted = len(MARKDOWN_LINK.sub(r"\1", SUGGESTION_BLOCK.sub("", text)))
    parts = [text]
    if finding.get("suggestion"):
        parts += ["", "```suggestion", finding["suggestion"].rstrip("\n"), "```"]
    prompt = (finding.get("ai_prompt") or "").strip()
    if prompt:
        quoted = prompt if prompt.startswith(chr(34)) else json.dumps(prompt, ensure_ascii=False)
        parts += ["", f"AI fix prompt: {quoted}"]
    return "\n".join(parts), counted


def check_standard(standard):
    if not standard.get("source"):
        return ["missing standard.source: read the review rules from the repo's base branch and name the file, "
                "or write \"none\" when it has none"]
    labels = standard.get("labels")
    used = standard.get("request_changes", []) + standard.get("comment", []) + [
        label for key in standard.get("limits", {}) for label in key.split("+")]
    unknown = sorted({label for label in used if label not in labels}) if labels else []
    return [f"standard uses labels not in standard.labels: {', '.join(unknown)}"] if unknown else []


def check_findings(spec, diff, since):
    standard = spec["standard"]
    labels, max_chars = standard.get("labels"), standard.get("max_chars")
    blockers = standard.get("request_changes", [])
    problems, counts = [], {}
    for index, finding in enumerate(spec.get("findings", []), 1):
        where = f"finding {index} ({finding.get('path')}:{finding.get('line')})"
        required = ("title", "path", "line") + (() if finding.get("body") else ("why", "evidence", "fix"))
        required += ("label",) if labels else ()
        missing = [key for key in required if not finding.get(key)]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if labels and finding["label"] not in labels:
            problems.append(f"{where}: label must be one of {', '.join(labels)} (from {standard['source']})")
        lines = diff.get(finding["path"])
        anchors = [finding["line"]] + ([finding["start_line"]] if finding.get("start_line") else [])
        if lines is None:
            problems.append(f"{where}: file is not in the PR diff")
        else:
            outside = [str(n) for n in anchors if n not in lines]
            if outside:
                problems.append(f"{where}: line {', '.join(outside)} is not on the new side of a diff hunk")
            if finding.get("start_line") and finding["start_line"] >= finding["line"]:
                problems.append(f"{where}: start_line must be below line")
        if since is not None and finding.get("label") not in blockers and finding["line"] not in since.get(
                finding["path"], set()):
            problems.append(f"{where}: line {finding['line']} is unchanged since your last review; on a re-review only "
                            f"{', '.join(blockers) or 'a blocker'} goes on older lines, so move it to not_posted")
        for key in ("why", "evidence", "fix", "body"):
            problems += citation_problems(spec, f"{where} {key}", finding.get(key))
        length = render(spec, finding)[1]
        if max_chars and length > max_chars:
            problems.append(f"{where}: {length} characters, limit {max_chars} (suggestion and AI fix prompt excluded)")
        counts[finding.get("label", "")] = counts.get(finding.get("label", ""), 0) + 1
    for key, limit in standard.get("limits", {}).items():
        count = sum(counts.get(label, 0) for label in key.split("+"))
        if count > limit:
            problems.append(f"{count} {key} findings, limit {limit} ({standard['source']}): "
                            "merge findings that share a root cause, or move the weakest to not_posted")
    for index, item in enumerate(spec.get("not_posted", []), 1):
        where = f"not_posted {index} ({item.get('title')})"
        if not item.get("title") or not item.get("reason"):
            problems.append(f"{where}: needs a title and a reason")
        problems += citation_problems(spec, where, item.get("evidence"))
    return problems


def check_previous(spec, threads):
    problems = []
    known = {t["comment_id"] for t in threads}
    given = {item.get("comment_id") for item in spec.get("previous", [])}
    for item in spec.get("previous", []):
        if item.get("comment_id") not in known:
            problems.append(f"previous {item.get('comment_id')}: not in open_threads (your threads awaiting a verdict)")
        elif item.get("status") not in VERDICTS:
            problems.append(f"previous {item['comment_id']}: status must be one of {', '.join(VERDICTS)}")
        elif item["status"] != "fixed" and not (item.get("note") or "").strip():
            problems.append(f"previous {item['comment_id']}: a {item['status']} thread needs a note (the reply)")
    missing = [f"{t['comment_id']} ({t['label']} {t['title']})" for t in threads if t["comment_id"] not in given]
    if missing:
        problems.append("open threads not accounted for in previous (give each a verdict): " + "; ".join(missing))
    return problems


def status(standard, labels):
    if "request_changes" not in standard and "comment" not in standard:
        return "COMMENT"
    if labels & set(standard.get("request_changes", [])):
        return "REQUEST_CHANGES"
    if labels & set(standard.get("comment", [])) or labels - set(standard.get("labels") or []):
        return "COMMENT"  # an open thread without a known label (a hand-written comment) still needs an answer
    return "APPROVE"


def code_link(spec, finding):
    anchor = hashlib.sha256(finding["path"].encode()).hexdigest()
    return f"https://github.com/{spec['repo']}/pull/{spec['pr']}/files#diff-{anchor}R{finding['line']}"


def severity(spec, label):
    labels = spec["standard"].get("labels") or []
    return labels.index(label) if label in labels else len(labels)


def still_open(spec, threads):
    """(thread, verdict) for every thread that still counts toward the status."""
    verdicts = {item["comment_id"]: item["status"] for item in spec.get("previous", [])}
    return [(t, verdicts[t["comment_id"]]) for t in threads
            if verdicts.get(t["comment_id"]) in ("open", "partly_fixed")]


def review_body(spec, threads, links):
    """links: one per finding, to its inline comment once created (to its code line before that)."""
    parts = [f"### {STATUS_HEADINGS[spec['event']]}", "", spec["verdict"].strip()]
    previous = spec.get("previous", [])
    if previous:
        counts = [(sum(1 for item in previous if item["status"] == key), word.lower()) for key, word in VERDICTS.items()]
        since = ", ".join(f"{count} {word}" for count, word in counts if count)
        parts += ["", f"Since {spec['last_reviewed_sha'][:7]}: {since}, {len(spec.get('findings', []))} new."]
    rows = [(f.get("label", ""), f["title"], link, "New") for f, link in zip(spec.get("findings", []), links)]
    rows += [(t["label"], t["title"], t["url"], VERDICTS[verdict]) for t, verdict in still_open(spec, threads)]
    if rows:
        ranked = sorted(rows, key=lambda row: severity(spec, row[0]))
        lines = []
        for label, title, link, tag in ranked:
            badge = f"{LABEL_MARKS.get(label, '•')} `{label.strip('[]')}` " if label else ""
            lines.append(f"- {badge}[{title}]({link}) · {tag}")
        parts += ["", "<details open>", f"<summary>{len(rows)} open issue{'s' if len(rows) > 1 else ''}</summary>",
                  "", *lines, "", "</details>"]
    if spec.get("changes"):
        parts += ["", "<details>", "<summary>What changed in this PR</summary>", "",
                  *[f"- {change}" for change in spec["changes"]], "", "</details>"]
    if spec.get("body", "").strip():
        parts += ["", spec["body"].strip()]
    return "\n".join(parts)


def payload(spec, threads):
    comments = []
    for finding in spec.get("findings", []):
        comment = {"path": finding["path"], "line": finding["line"], "side": "RIGHT", "body": render(spec, finding)[0]}
        if finding.get("start_line"):
            comment.update(start_line=finding["start_line"], start_side="RIGHT")
        comments.append(comment)
    labels = {f.get("label", "") for f in spec.get("findings", [])} | {t["label"] for t, _ in still_open(spec, threads)}
    spec["event"] = status(spec["standard"], labels)
    links = [code_link(spec, f) for f in spec.get("findings", [])]
    return {"commit_id": spec["head"], "body": review_body(spec, threads, links), "comments": comments}


def link_comments(spec, posted, threads):
    """Point the issue list at the draft's inline comments instead of code lines. Returns the new summary, or None when
    the comments can't be matched."""
    base = f"repos/{spec['repo']}/pulls/{spec['pr']}/reviews/{posted['id']}"
    try:
        pages = json.loads(gh("api", "--paginate", "--slurp", f"{base}/comments?per_page=100"))
        by_body = {c["body"]: c["html_url"] for page in pages for c in page}
        links = [by_body.get(render(spec, finding)[0]) for finding in spec.get("findings", [])]
        if None in links:
            return None
        body = review_body(spec, threads, links)
        gh("api", base, "--method", "PUT", "-f", f"body={body}")
    except (subprocess.CalledProcessError, ValueError):
        return None
    return body


def add_replies(spec, posted, threads):
    by_id = {t["comment_id"]: t for t in threads}
    for item in spec.get("previous", []):
        note = (item.get("note") or "").strip() or f"Fixed in {spec['head'][:8]}."
        gh("api", "graphql", "-f", f"query={REPLY_MUTATION}", "-f", f"review={posted['node_id']}",
           "-f", f"thread={by_id[item['comment_id']]['thread_id']}", "-f", f"body={note}")


def print_summary(spec, event, threads):
    standard = spec["standard"]
    defaulted = f"; defaults used for {', '.join(spec['defaulted'])}" if spec["defaulted"] else ""
    print(f"Recommended status: {STATUS_NAMES[event]} (rules from {standard['source']}{defaulted})")
    findings = sorted(spec.get("findings", []), key=lambda f: severity(spec, f.get("label", "")))
    print(f"\nComments ({len(findings)}):")
    for finding in findings:
        print(f"  {' '.join(filter(None, [finding.get('label'), finding['title']]))} — {finding['path']}:{finding['line']}")
    if spec.get("previous"):
        by_id = {t["comment_id"]: t for t in threads}
        print("\nReplies on your earlier threads:")
        for item in spec["previous"]:
            thread = by_id[item["comment_id"]]
            note = (item.get("note") or "").strip() or f"Fixed in {spec['head'][:8]}."
            reopen = (f" (resolved by {thread['resolved_by']}: unresolve it in GitHub to keep it open)"
                      if thread.get("resolved") and item["status"] in ("open", "partly_fixed") else "")
            print(f"  {VERDICTS[item['status']]:<13}{thread['label']} {thread['title']} → {note}{reopen}")
    if spec.get("not_posted"):
        print(f"\nNot posted ({len(spec['not_posted'])}):")
        for item in spec["not_posted"]:
            print(f"  {item['title']} — {item['reason']}")


def main(argv):
    if len(argv) == 4 and argv[1] == "--since":
        repo, pr = argv[2], argv[3]
        info, diff = load_pr(repo, pr)
        previous = load_previous(repo, pr, info["headRefOid"], diff)
        since = previous.pop("changed_since")
        print(json.dumps({"base_ref": info["baseRefName"], "head_sha": info["headRefOid"],
                          "changed_files": sorted(diff), "counted_files": counted_files(diff),
                          "changed_since_last_review": None if since is None else {
                              path: to_ranges(lines) for path, lines in sorted(since.items())},
                          **previous}, indent=2, ensure_ascii=False))
        return 0
    args = [a for a in argv[1:] if a != "--draft"]
    if len(args) != 1 or args[0].startswith("--"):
        print(__doc__.strip())
        return 2
    with open(args[0], encoding="utf-8") as handle:
        spec = json.load(handle)
    spec.setdefault("standard", {})
    problems = [] if str(spec.get("verdict", "")).strip() else [
        "missing verdict: one sentence with the main risk, or why it is safe to merge"]
    if len(str(spec.get("head", ""))) < 7:
        problems.append("missing head: head_sha from --since, the commit the review read")
    problems += check_standard(spec["standard"])
    if problems:
        print("Not created:\n" + "\n".join(f"  - {p}" for p in problems), file=sys.stderr)
        return 1
    info, diff = load_pr(spec["repo"], spec["pr"])
    if not info["headRefOid"].startswith(spec["head"]):
        print(f"Not created: the PR moved from {spec['head'][:8]} to {info['headRefOid'][:8]} since the review. Review "
              "the new commits (a re-review), then set head to the new SHA.", file=sys.stderr)
        return 1
    spec.update(head=info["headRefOid"], sizes={})
    previous = load_previous(spec["repo"], spec["pr"], spec["head"], diff)
    spec["last_reviewed_sha"] = previous["last_reviewed_sha"]
    spec["standard"], spec["defaulted"] = with_defaults(spec["standard"], counted_files(diff))
    for finding in spec.get("findings", []):
        if finding.get("shared_with") and finding.get("title"):
            finding["title"] = f"Shared with {finding['shared_with']}: {finding['title']}"
    threads = previous["open_threads"]
    problems = check_findings(spec, diff, previous["changed_since"]) + check_previous(spec, threads)
    if previous["pending_review"]:
        problems.insert(0, f"you already have a draft review on this PR ({previous['pending_review']}); "
                           "submit or discard it in GitHub first")
    if problems:
        print("Not created:\n" + "\n".join(f"  - {p}" for p in problems), file=sys.stderr)
        return 1
    review = payload(spec, threads)
    event = spec["event"]
    if "--draft" not in argv:
        print("Dry run: nothing created. Rerun with --draft to create the draft review.\n")
        print_summary(spec, event, threads)
        print("\n--- Review summary ---\n" + review["body"])
        for comment in review["comments"]:
            print(f"\n--- {comment['path']}:{comment['line']} ---\n{comment['body']}")
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(review, handle)
    posted = json.loads(gh("api", f"repos/{spec['repo']}/pulls/{spec['pr']}/reviews", "--method", "POST",
                           "--input", handle.name))
    try:
        add_replies(spec, posted, threads)
    except subprocess.CalledProcessError as error:
        print(f"The draft exists, but adding the replies failed, so some are missing from it: {error.stderr.strip()}")
    summary = link_comments(spec, posted, threads) if review["comments"] else review["body"]
    if summary is None:
        summary = review["body"]
        print("Note: the summary's issue list still links to code lines (could not match the draft's comments).")
    print(f"Draft review created; only you can see it until you submit: {posted.get('html_url')}\n")
    print_summary(spec, event, threads)
    # GitHub's submit box starts empty and replaces the draft's summary with its contents, so the user pastes it.
    print("\nIn GitHub: Files changed → read each comment, edit or delete it (and its line in the summary), resolve "
          "the threads you agree are done → Submit review → paste the summary below into the empty box (GitHub doesn't "
          "carry it over; change its heading if you pick another status) → choose the status → Submit.")
    print(f"\n----- summary to paste -----\n{summary}\n----- end of summary -----")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
