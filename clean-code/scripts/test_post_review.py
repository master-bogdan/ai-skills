#!/usr/bin/env python3
"""Offline tests for post_review.py (no network). Run: python3 scripts/test_post_review.py"""
import os
import sys
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
        self.assertEqual(rules["limits"]["[SUGGESTION]"], 8)
        self.assertEqual(set(taken), {"labels", "request_changes", "comment", "max_chars", "limits"})
    def test_defaults_own_labels(self):
        rules, taken = pr.with_defaults({"source": "x", "labels": ["blocker", "nit"]}, 3)
        self.assertEqual(taken, ["max_chars"])
        self.assertEqual(pr.status(rules, {"blocker"}), "COMMENT")
    def test_repo_rule_wins(self):
        rules, taken = pr.with_defaults({"source": "x", "max_chars": 400}, 3)
        self.assertEqual(rules["max_chars"], 400)
        self.assertNotIn("max_chars", taken)
        self.assertEqual(rules["limits"]["[SUGGESTION]"], 3)
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
        f = {"label": "[SUGGESTION]", "title": "t", "why": "w", "evidence": "src/a.ts:12", "fix": "x", "ai_prompt": "p" * 900}
        text, counted = pr.render(SPEC, f)
        self.assertIn("blob/abc1234def/src/a.ts#L12", text)
        self.assertLess(counted, 90)
    def test_ranges(self):
        self.assertEqual(pr.to_ranges({5, 1, 2, 3, 9}), "1-3, 5, 9")
    def test_previous(self):
        threads = [{"comment_id": 1, "label": "[QUESTION]", "title": "a"}, {"comment_id": 2, "label": "[SUGGESTION]", "title": "b"}]
        self.assertEqual(pr.check_previous({"previous": [{"comment_id": 1, "status": "fixed"}, {"comment_id": 2, "status": "open"}]}, threads),
                         ["previous 2: a open thread needs a note (the reply)"])
        self.assertEqual(pr.check_previous({"previous": [{"comment_id": 1, "status": "accepted", "note": "ok"}]}, threads)[0][:40],
                         "open threads not accounted for in previo")
    def test_awaits_verdict(self):
        def thread(resolved, by=None, replies=()):
            return {"resolved": resolved, "resolved_by": by, "replies": [{"author": a} for a in replies]}
        self.assertTrue(pr.awaits_verdict(thread(False, replies=["me"]), "me"))
        self.assertFalse(pr.awaits_verdict(thread(True, "me", ["dev"]), "me"))
        self.assertTrue(pr.awaits_verdict(thread(True, "dev", ["dev"]), "me"))  # the author answered and resolved
        self.assertTrue(pr.awaits_verdict(thread(True, "dev"), "me"))  # resolved without a word
        self.assertFalse(pr.awaits_verdict(thread(True, "dev", ["dev", "me"]), "me"))  # you had the last word
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
                    findings=[{"label": "[SUGGESTION]", "title": "new one", "path": "src/a.ts", "line": 3, "why": "w", "evidence": "e", "fix": "f"}],
                    previous=[{"comment_id": 1, "status": "fixed"}, {"comment_id": 2, "status": "partly_fixed", "note": "n"}, {"comment_id": 3, "status": "accepted", "note": "n"}])
        threads = [{"comment_id": i, "label": l, "title": t, "url": f"u{i}"} for i, l, t in [(1, "[MUST FIX]", "x"), (2, "[MUST FIX]", "y"), (3, "[QUESTION]", "z")]]
        review = pr.payload(spec, threads)
        self.assertEqual(spec["event"], "REQUEST_CHANGES")
        self.assertIn("Since 1112223: 1 fixed, 1 partly fixed, 1 accepted, 1 new.", review["body"])
        self.assertIn("- 🔴 `MUST FIX` [y](u2) · Partly fixed", review["body"])
        self.assertIn("- 🟡 `SUGGESTION` [new one](", review["body"])
        self.assertNotIn("](u3)", review["body"])
        self.assertNotIn("event", review)
        self.assertTrue(review["body"].startswith("### 🔴 Changes requested\n"))
        self.assertTrue(review["comments"][0]["body"].startswith("🟡 **[SUGGESTION] new one**\n"))
    def test_rereview_scope(self):
        spec = dict(SPEC, standard=pr.with_defaults({"source": "none"}, 3)[0],
                    findings=[{"label": "[SUGGESTION]", "title": "old line", "path": "src/a.ts", "line": 3, "why": "w", "evidence": "e", "fix": "f"},
                              {"label": "[MUST FIX]", "title": "bug", "path": "src/a.ts", "line": 4, "why": "w", "evidence": "e", "fix": "f"},
                              {"label": "[SUGGESTION]", "title": "new line", "path": "src/a.ts", "line": 7, "why": "w", "evidence": "e", "fix": "f"}])
        probs = pr.check_findings(spec, {"src/a.ts": {3, 4, 7}}, {"src/a.ts": {7}})
        self.assertEqual(len(probs), 1, probs)
        self.assertIn("finding 1", probs[0])
        self.assertEqual(pr.check_findings(spec, {"src/a.ts": {3, 4, 7}}, None), [])

if __name__ == "__main__":
    unittest.main(verbosity=1)
