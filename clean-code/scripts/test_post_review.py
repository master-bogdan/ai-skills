#!/usr/bin/env python3
"""Offline tests for post_review.py (no network). Run: python3 scripts/test_post_review.py"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import post_review as pr  # noqa: E402

SPEC = {"repo": "o/r", "pr": 1, "head": "abc1234def", "verdict": "v", "sizes": {"src/a.ts": 50, "AGENTS.md": 300, "adapters.ts": None},
        "standard": {}, "last_reviewed_sha": "1112223334"}

class T(unittest.TestCase):
    def test_new_side(self):
        patch = "@@ -1,3 +1,4 @@\n ctx\n-old\n+new\n+new2\n ctx2"
        self.assertEqual(pr.new_side(patch), ({1, 2, 3, 4}, {2, 3}))
    def test_defaults_all(self):
        rules, taken = pr.with_defaults({"source": "none"}, 28)
        self.assertEqual(rules["limits"]["[PROPOSAL]"], 8)
        self.assertEqual(set(taken), {"labels", "request_changes", "comment", "no_reply", "max_chars", "limits"})
    def test_defaults_own_labels(self):
        rules, taken = pr.with_defaults({"source": "x", "labels": ["blocker", "nit"]}, 3)
        self.assertEqual(taken, ["max_chars"])
        self.assertEqual(pr.status(rules, {"blocker"}), "COMMENT")
    def test_repo_rule_wins(self):
        rules, taken = pr.with_defaults({"source": "x", "max_chars": 400}, 3)
        self.assertEqual(rules["max_chars"], 400)
        self.assertNotIn("max_chars", taken)
        self.assertEqual(rules["limits"]["[PROPOSAL]"], 3)
    def test_pin(self):
        out = pr.pin_citations(SPEC, "See `src/a.ts:12-20` and AGENTS.md:31, not [x](http://h/src/a.ts:1) or https://g.com/src/a.ts:2")
        self.assertIn("[`src/a.ts:12-20`](https://github.com/o/r/blob/abc1234def/src/a.ts#L12-L20)", out)
        self.assertIn("[AGENTS.md:31](https://github.com/o/r/blob/abc1234def/AGENTS.md#L31)", out)
        self.assertIn("[x](http://h/src/a.ts:1)", out)
        self.assertIn("https://g.com/src/a.ts:2", out)
        self.assertEqual(out.count("](https://github.com/o/r/blob"), 2)
    def test_no_version_numbers(self):
        self.assertEqual(pr.pin_citations(SPEC, "TTL 10.30:45 and v1.2:3"), "TTL 10.30:45 and v1.2:3")
    def test_citation_problems(self):
        probs = pr.citation_problems(SPEC, "f1", "src/a.ts:49-51 and adapters.ts:3 and src/a.ts:50")
        self.assertEqual(len(probs), 2, probs)
        self.assertIn("file has 50 lines", probs[0])
        self.assertIn("adapters.ts", probs[1])
    def test_render_counts_visible(self):
        f = {"label": "[PROPOSAL]", "title": "t", "why": "w", "evidence": "src/a.ts:12", "fix": "x", "ai_prompt": "p" * 900}
        text, counted = pr.render(SPEC, f)
        self.assertIn("blob/abc1234def/src/a.ts#L12", text)
        self.assertLess(counted, 90)
    def test_ranges(self):
        self.assertEqual(pr.to_ranges({5, 1, 2, 3, 9}), "1-3, 5, 9")
    def test_previous(self):
        threads = [{"comment_id": 1, "label": "[QUESTION]", "title": "a"}, {"comment_id": 2, "label": "[PROPOSAL]", "title": "b"}]
        self.assertEqual(pr.check_previous({"standard": {}, "previous": [{"comment_id": 1, "status": "fixed"}, {"comment_id": 2, "status": "open"}]}, threads),
                         ["previous 2: a open thread needs a note (the reply)"])
        self.assertEqual(pr.check_previous({"standard": {}, "previous": [{"comment_id": 1, "status": "accepted", "note": "ok"}]}, threads)[0][:40],
                         "open threads not accounted for in previo")
    def test_awaits_verdict(self):
        def thread(resolved, by=None, replies=()):
            return {"resolved": resolved, "resolved_by": by,
                    "replies": [{"author": a, "body": b} for a, b in replies]}
        fixed, agreed, still_open = ("me", "Fixed in `abc1234`."), ("me", "**Agreed:** fine."), ("me", "Still open: x")
        self.assertTrue(pr.awaits_verdict(thread(False, replies=[fixed]), "me"))
        self.assertFalse(pr.awaits_verdict(thread(True, "me", [("dev", "done")]), "me"))
        self.assertTrue(pr.awaits_verdict(thread(True, "dev", [("dev", "done")]), "me"))  # the author answered and resolved
        self.assertTrue(pr.awaits_verdict(thread(True, "dev"), "me"))  # resolved without a word
        self.assertFalse(pr.awaits_verdict(thread(True, "dev", [("dev", "done"), fixed]), "me"))
        self.assertFalse(pr.awaits_verdict(thread(True, "dev", [agreed]), "me"))
        self.assertTrue(pr.awaits_verdict(thread(True, "dev", [still_open]), "me"))  # resolved over your "Still open"
    def test_thread_summary(self):
        node = {"id": "T1", "isResolved": True, "isOutdated": False, "path": "a.ts", "line": 3,
                "resolvedBy": {"login": "dev"},
                "comments": {"nodes": [
                    {"databaseId": 7, "url": "u", "body": "🟠 **[QUESTION] Why?**\n\nWhy it matters: x",
                     "author": {"login": "me"}, "pullRequestReview": {"databaseId": 70, "state": "COMMENTED"}},
                    {"databaseId": 8, "url": "u2", "body": "Agreed.", "author": {"login": "dev"},
                     "pullRequestReview": {"databaseId": 80, "state": "COMMENTED"}}]}}
        t = pr.thread_summary(node)
        self.assertEqual((t["label"], t["title"], t["resolved_by"], t["review_id"], t["pending"]),
                         ("[QUESTION]", "Why?", "dev", 70, False))
        self.assertEqual(t["replies"], [{"author": "dev", "body": "Agreed."}])
    def test_rereview_body_and_status(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0],
                    findings=[{"label": "[PROPOSAL]", "title": "new one", "path": "src/a.ts", "line": 3, "why": "w", "evidence": "e", "fix": "f"}],
                    previous=[{"comment_id": 1, "status": "fixed"}, {"comment_id": 2, "status": "partly_fixed", "note": "n"}, {"comment_id": 3, "status": "accepted", "note": "n"}])
        threads = [{"comment_id": i, "label": l, "title": t, "url": f"u{i}"} for i, l, t in [(1, "[MUST FIX]", "x"), (2, "[MUST FIX]", "y"), (3, "[QUESTION]", "z")]]
        review = pr.payload(spec, threads)
        self.assertEqual(spec["event"], "REQUEST_CHANGES")
        self.assertIn("Since 1112223: 1 fixed, 1 partly fixed, 1 accepted, 1 new.", review["body"])
        self.assertIn("- 🔴 `MUST FIX` [y](u2) · Partly fixed", review["body"])
        self.assertIn("- 🟡 `PROPOSAL` [new one](", review["body"])
        self.assertNotIn("](u3)", review["body"])
        self.assertNotIn("event", review)
        self.assertTrue(review["body"].startswith("### 🔴 Changes requested\n"))
        self.assertTrue(review["comments"][0]["body"].startswith("🟡 **[PROPOSAL] new one**\n"))
    def test_rereview_scope(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0],
                    findings=[{"label": "[PROPOSAL]", "title": "old line", "path": "src/a.ts", "line": 3, "why": "w", "evidence": "e", "fix": "f"},
                              {"label": "[MUST FIX]", "title": "bug", "path": "src/a.ts", "line": 4, "why": "w", "evidence": "e", "fix": "f"},
                              {"label": "[PROPOSAL]", "title": "new line", "path": "src/a.ts", "line": 7, "why": "w", "evidence": "e", "fix": "f"}])
        probs = pr.check_findings(spec, {"src/a.ts": {3, 4, 7}}, {"src/a.ts": {7}})
        self.assertEqual(len(probs), 1, probs)
        self.assertIn("finding 1", probs[0])
        self.assertEqual(pr.check_findings(spec, {"src/a.ts": {3, 4, 7}}, None), [])

    def test_unlabelled_open_thread_blocks_approval(self):
        rules = pr.with_defaults({"source": "none"}, 3)[0]
        self.assertEqual(pr.status(rules, set()), "APPROVE")
        self.assertEqual(pr.status(rules, {""}), "COMMENT")
        self.assertEqual(pr.status(rules, {"", "[MUST FIX]"}), "REQUEST_CHANGES")
        self.assertEqual(pr.status(rules, {"[PROPOSAL]"}), "APPROVE")
    def test_threads_from_pages(self):
        def node(i, more=False):
            return {"id": f"T{i}", "isResolved": False, "isOutdated": False, "path": "a.ts", "line": i, "resolvedBy": None,
                    "comments": {"pageInfo": {"hasNextPage": more}, "nodes": [
                        {"databaseId": i, "url": f"u{i}", "body": "[NIT PICK] t", "author": {"login": "me"},
                         "pullRequestReview": {"databaseId": 9, "state": "COMMENTED"}}]}}
        def page(*nodes):
            return {"data": {"repository": {"pullRequest": {"reviewThreads": {"nodes": list(nodes)}}}}}
        threads = pr.threads_from_pages([page(node(1)), page(node(2))])
        self.assertEqual([t["comment_id"] for t in threads], [1, 2])
        with self.assertRaises(SystemExit) as stop:
            pr.threads_from_pages([page(node(1)), page(node(3, more=True))])
        self.assertIn("a.ts:3", str(stop.exception.code))
    def test_link_comments_reads_every_page(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0], findings=[
            {"label": "[PROPOSAL]", "title": t, "path": "src/a.ts", "line": 3, "why": "w", "evidence": "e", "fix": "f"}
            for t in ("one", "two")])
        pr.payload(spec, [])
        pages = [[{"body": pr.render(spec, f)[0], "html_url": f"https://c/{i}"}] for i, f in enumerate(spec["findings"])]
        calls = []
        def fake_gh(*args):
            calls.append(args)
            return json.dumps(pages) if "--slurp" in args else ""
        real, pr.gh = pr.gh, fake_gh
        try:
            body = pr.link_comments(spec, {"id": 5}, [], [])
        finally:
            pr.gh = real
        self.assertIn("[one](https://c/0)", body)
        self.assertIn("[two](https://c/1)", body)
        self.assertIn("PUT", calls[-1])
    def test_head_is_kept(self):
        findings = {"repo": "o/r", "pr": 1, "verdict": "v", "standard": {"source": "none"}, "findings": []}
        def run(spec):
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
                json.dump(spec, handle)
            real, pr.load_pr = pr.load_pr, lambda repo, number: ({"headRefOid": "b" * 40}, {})
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    code = pr.main(["post_review.py", handle.name])
            finally:
                pr.load_pr = real
                os.unlink(handle.name)
            return code, err.getvalue()
        code, err = run(findings)
        self.assertEqual(code, 1)
        self.assertIn("missing head", err)
        code, err = run(dict(findings, head="a" * 40))
        self.assertEqual(code, 1)
        self.assertIn("the PR moved from aaaaaaaa to bbbbbbbb", err)

    def test_changed_since_cap(self):
        patch = "@@ -1,1 +1,2 @@\n ctx\n+new"
        def compare(count):
            files = [{"filename": f"f{i}.ts", "patch": patch} for i in range(count)]
            return lambda *args: json.dumps({"status": "ahead", "files": files})
        diff = {"f0.ts": {1, 2}, "f299.ts": {1, 2}}
        real = pr.gh
        try:
            pr.gh = compare(299)
            self.assertEqual(pr.changed_since("o/r", "a", "b", diff), ({"f0.ts": {2}}, None))
            pr.gh = compare(300)  # f299.ts and beyond may be missing from GitHub's list
            changed, whole_pr = pr.changed_since("o/r", "a", "b", diff)
        finally:
            pr.gh = real
        self.assertIsNone(changed)
        self.assertIn("at most 300 files", whole_pr)

    def test_citations_dont_count(self):
        short = {"label": "[PROPOSAL]", "title": "t", "why": "w", "evidence": "e", "fix": "x"}
        cited = dict(short, evidence="e src/a.ts:12-20")
        self.assertEqual(pr.render(SPEC, short)[1] + 1, pr.render(SPEC, cited)[1])  # only the space counts
    def test_others_blocker_keeps_comment(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0], findings=[],
                    others=[{"comment_id": 9, "status": "open", "note": "still there, src/a.ts:3"}])
        theirs = [{"comment_id": 9, "label": "[MUST FIX]", "title": "race", "url": "u9", "author": "copilot",
                   "resolved": False, "pending": False},
                  {"comment_id": 10, "label": "[MUST FIX]", "title": "done", "url": "u10", "author": "dev",
                   "resolved": True, "pending": False}]
        self.assertEqual(pr.check_others(spec, theirs), [])
        review = pr.payload(spec, [], theirs)
        self.assertEqual(spec["event"], "COMMENT")
        self.assertTrue(review["body"].startswith("### 🟡 Questions open\n"))
        self.assertIn("<summary>Still open from others (1)</summary>", review["body"])
        self.assertIn("[race](u9) · copilot", review["body"])
        spec["others"] = [{"comment_id": 9, "status": "fixed", "note": "guarded at src/a.ts:3"}]
        pr.payload(spec, [], theirs)
        self.assertEqual(spec["event"], "APPROVE")
        spec["others"] = []
        self.assertIn("not checked in others", pr.check_others(spec, theirs)[0])
        spec["others"] = [{"comment_id": 10, "status": "open", "note": "n"}]
        self.assertIn("not an unresolved blocking thread", pr.check_others(spec, theirs)[0])
    def test_skipped_and_no_reply(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0], findings=[],
                    previous=[{"comment_id": 1, "status": "open", "note": "Still open: x"}])
        threads = [{"comment_id": 1, "label": "[PROPOSAL]", "title": "p", "url": "u1"},
                   {"comment_id": 2, "label": "[OPTIONAL]", "title": "o", "url": "u2"}]
        self.assertEqual(pr.check_previous(spec, threads), [])  # [OPTIONAL] needs no verdict
        review = pr.payload(spec, threads)
        self.assertEqual(spec["event"], "APPROVE")
        self.assertIn("[p](u1) · Skipped without [WON'T FIX]", review["body"])
        self.assertNotIn("](u2)", review["body"])
    def test_local_never_posts(self):
        findings = {"repo": "o/r", "pr": 1, "head": "b" * 40, "verdict": "v", "standard": {"source": "none"},
                    "findings": []}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(findings, handle)
        previous = {"me": "me", "pending_review": "https://draft", "last_reviewed_sha": None, "summary_missing": None,
                    "whole_pr": None, "changed_since": None, "open_threads": [], "closed_threads": [],
                    "other_threads": [], "others_blocking": []}
        calls = []
        real = pr.load_pr, pr.load_previous, pr.gh
        pr.load_pr = lambda repo, number: ({"headRefOid": "b" * 40}, {})
        pr.load_previous = lambda *args: dict(previous)
        pr.gh = lambda *args: calls.append(args)
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                local = pr.main(["post_review.py", handle.name, "--local"])
                dry = pr.main(["post_review.py", handle.name])
                both = pr.main(["post_review.py", handle.name, "--local", "--draft"])
        finally:
            pr.load_pr, pr.load_previous, pr.gh = real
            os.unlink(handle.name)
        self.assertEqual((local, dry, both), (0, 1, 2))
        self.assertIn("Local review: nothing is posted.", out.getvalue())
        self.assertIn("you already have a draft review", err.getvalue())
        self.assertEqual(calls, [])

if __name__ == "__main__":
    unittest.main(verbosity=1)
