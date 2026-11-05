#!/usr/bin/env python3
"""Regression tests for check.py and hook.py. Run: python3 scripts/test_check.py"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import check  # noqa: E402


def rules(text, existing=frozenset()):
    return [(lineno, rule) for lineno, rule, *_ in check.check_ts(text, None, existing)]


def run(cwd, *args, stdin=None):
    return subprocess.run(list(args), cwd=cwd, input=stdin, capture_output=True, text=True)


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(text)
    return full


def commit(repo, message):
    run(repo, "git", "add", "-A")
    run(repo, "git", "commit", "-q", "-m", message)


def make_repo(test):
    """A throwaway git repo on branch main, removed after the test."""
    repo = os.path.realpath(tempfile.mkdtemp())
    test.addCleanup(shutil.rmtree, repo)
    run(repo, "git", "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "t"), ("commit.gpgsign", "false")):
        run(repo, "git", "config", key, value)
    return repo


def check_py(repo, *args):
    return run(repo, sys.executable, os.path.join(SCRIPTS, "check.py"), *args)


class CommentTests(unittest.TestCase):
    def test_if_inside_a_comment_is_ignored(self):
        self.assertEqual(rules("// recompute only if (a) changed\nconst x = 1;\n"), [])
        self.assertEqual(rules("/* only if (a) changed */\nconst x = 1;\n"), [])

    def test_real_one_line_if_is_flagged(self):
        self.assertEqual(rules("if (a) return;\n"), [(1, "one-line-if")])

    def test_if_with_block_and_trailing_comment_is_fine(self):
        self.assertEqual(rules("if (a) { // why\n  return;\n}\n"), [])

    def test_comma_in_a_comment_is_not_a_parameter(self):
        text = "function f(\n  a: number,\n  // note: b, c and d\n  b: number,\n  c: number,\n) {\n  return a + b + c;\n}\n"
        self.assertEqual(rules(text), [])

    def test_slashes_inside_strings_are_not_comments(self):
        masked = check.mask_comments("const u = 'http://x.y'; // note\nconst r = /a\\//g;\n")
        self.assertIn("'http://x.y';", masked)
        self.assertNotIn("note", masked)
        self.assertIn("/a\\//g;", masked)
        self.assertEqual(masked.count("\n"), 2)
        self.assertEqual(rules("const u = 'http://x.y'; if (a) return;\n"), [(1, "one-line-if")])


class ParamsTests(unittest.TestCase):
    def test_callback_typed_param_counts_once(self):
        params = check.split_top_level("a, cb: (x: number, y: number) => void, c, d")
        self.assertEqual(len(params), 4)
        self.assertEqual(rules("function f(a, cb: (x: number, y: number) => void, c, d) {\n  return 1;\n}\n"),
                         [(1, "params")])

    def test_three_params_with_callback_is_fine(self):
        self.assertEqual(rules("function f(a, cb: (x: number, y: number) => void, c) {\n  return 1;\n}\n"), [])

    def test_express_error_handler_is_exempt(self):
        text = ("export function errorHandler(\n  error: Error,\n  _req: Request,\n  res: Response,\n"
                "  // Note: without `next`, express won't treat it as an error handler\n  next: NextFunction,\n"
                ") {\n  return res.status(500);\n}\n")
        self.assertEqual(rules(text), [])

    def test_other_four_param_functions_are_flagged(self):
        self.assertEqual(rules("export function h(a, req, res, next) {\n  return 1;\n}\n"), [(1, "params")])

    def test_existing_function_is_a_suggestion(self):
        text = "export function old(a, b, c, d) {\n  return 1;\n}\n"
        self.assertEqual(rules(text, {"old"}), [(1, "params-existing")])

    def test_go_params_exclude_ctx(self):
        text = ("func Three(ctx context.Context, a string, b int, c int) error {\n}\n"
                "func Four(ctx context.Context, a string, b int, c int, d int) error {\n}\n")
        self.assertEqual([(lineno, rule) for lineno, rule, *_ in check.check_go(text, None, set())], [(3, "params")])


class WrapperTests(unittest.TestCase):
    def test_multi_line_expression_arrow_is_read_whole(self):
        text = ("const resolveFwbCellType = (fwbRef, getCellType) =>\n  getSchemaPathCandidates(fwbRef)\n"
                "    .map(getCellType)\n    .find((cellType) => cellType != null) ?? null;\n")
        self.assertEqual(rules(text), [])

    def test_multi_line_forwarder_is_a_wrapper(self):
        self.assertEqual(rules("const load = (id) =>\n  fetchUser(id);\n"), [(1, "wrapper")])

    def test_chained_call_is_not_a_wrapper(self):
        self.assertEqual(rules("const f = (a) => g(a).h(a);\n"), [])

    def test_void_forwarders_are_wrappers(self):
        block = "function C() {\n  const startRecompute = () => {\n    void recompute();\n  };\n}\n"
        self.assertEqual(rules(block), [(2, "wrapper")])
        self.assertEqual(rules("const start = () => void recompute();\n"), [(1, "wrapper")])

    def test_transforming_arguments_are_not_wrappers(self):
        self.assertEqual(rules("const saveCents = (n) => save(n * 100);\n"), [])
        self.assertEqual(rules("const loadOrZero = (n) => load(n ?? 0);\n"), [])
        self.assertEqual(rules("const run = (...args) => exec(...args);\n"), [(1, "wrapper")])

    def test_exported_forwarders_are_left_to_review(self):
        self.assertEqual(rules("export const selectLastRecomputedAt = (state) => selectX(state);\n"), [])
        self.assertEqual(rules("export const selectA = (state) => state.a.b;\n"), [])
        self.assertEqual(rules("const a = (x) => b(x);\nexport { a };\n"), [])
        self.assertEqual(rules("const a = (x) => b(x);\nexport default a;\n"), [])
        self.assertEqual(rules("export async function load(id) {\n  return repo.get(id);\n}\n"), [])
        self.assertEqual(rules("class S {\n  get(id) {\n    return this.repo.get(id);\n  }\n}\n"), [])

    def test_private_forwarders_are_flagged(self):
        self.assertEqual(rules("const selectA = (state) => state.a.b;\n"), [(1, "wrapper")])
        self.assertEqual(rules("function load(id) {\n  return repo.get(id);\n}\n"), [(1, "wrapper")])
        methods = ("class S {\n  private load(id) {\n    return this.repo.get(id);\n  }\n"
                   "  #find(id) {\n    return this.repo.get(id);\n  }\n}\n")
        self.assertEqual(rules(methods), [(2, "wrapper"), (5, "wrapper")])

    def test_nested_function_with_exported_name_elsewhere_is_still_private(self):
        text = "export function a() {\n  const b = (x) => c(x);\n  return b;\n}\nexport { b };\n"
        self.assertEqual(rules(text), [(2, "wrapper")])


class MemoTests(unittest.TestCase):
    def test_memo_without_reason_is_flagged(self):
        self.assertEqual(rules("const v = useMemo(() => 1, []);\n"), [(1, "memo")])

    def test_memo_with_reason_is_kept(self):
        self.assertEqual(rules("// stable dep of useEffect\nconst v = useMemo(() => 1, []);\n"), [(2, "memo-kept")])

    def test_memo_in_comment_is_ignored(self):
        self.assertEqual(rules("// no useMemo(...) here\nconst v = 1;\n"), [])


class CollectTests(unittest.TestCase):
    def test_bench_test_and_spec_files_are_skipped(self):
        folder = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        paths = [write(folder, name, "if (a) return;\n") for name in ("x.ts", "x.bench.ts", "x.test.ts", "x.spec.ts")]
        findings = check.collect({p: None for p in paths})[0]
        self.assertEqual([os.path.basename(f[0]) for f in findings], ["x.ts"])

    def test_whole_file_mode_treats_every_function_as_new(self):
        folder = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, folder)
        path = write(folder, "a.ts", "export function old(a, b, c, d) {\n  return 1;\n}\n")
        findings, _, suggestions, _ = check.collect({path: None})
        self.assertEqual([f[2] for f in findings], ["params"])
        self.assertEqual(suggestions, [])


class GitTests(unittest.TestCase):
    def test_base_compares_from_the_merge_base(self):
        repo = make_repo(self)
        write(repo, "c.ts", "export function c(x) {\n  if (x) return 1;\n  return 2;\n}\n")
        commit(repo, "A")
        fork = run(repo, "git", "rev-parse", "--short=7", "HEAD").stdout.strip()
        run(repo, "git", "checkout", "-q", "-b", "feature")
        write(repo, "f.ts", "export function f(y) {\n  if (y) return 1;\n  return 2;\n}\n")
        commit(repo, "feature")
        run(repo, "git", "checkout", "-q", "main")
        write(repo, "c.ts", "export function c(x) {\n  if (x) {\n    return 1;\n  }\n  return 2;\n}\n")
        commit(repo, "B: main fixes c.ts")
        run(repo, "git", "checkout", "-q", "feature")

        result = check_py(repo, "--base", "main")
        self.assertTrue(result.stdout.startswith(f"compared against main (merge-base {fork})"), result.stdout)
        self.assertIn("f.ts:2  [one-line-if]", result.stdout)
        self.assertNotIn("c.ts", result.stdout)  # main's tip differs, but the branch never touched c.ts

    def test_params_new_vs_existing(self):
        repo = make_repo(self)
        write(repo, "a.ts", "export function old(a, b, c) {\n  return a + b + c;\n}\n")
        commit(repo, "base")
        write(repo, "a.ts", "export function old(a, b, c, d) {\n  return a + b + c + d;\n}\n\n"
                            "export function fresh(a, b, c, d) {\n  return a;\n}\n")
        result = check_py(repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("a.ts:5  [params] fresh", result.stdout)
        suggestions = result.stdout.split("Suggestions (existing functions; switch to one object only if it's cheap):")
        self.assertEqual(len(suggestions), 2, result.stdout)
        self.assertIn("a.ts:1  [params-existing] old", suggestions[1])

        write(repo, "a.ts", "export function old(a, b, c, d) {\n  return a + b + c + d;\n}\n")
        result = check_py(repo)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("[params-existing] old", result.stdout)

    def test_type_imports_are_not_definitions(self):
        repo = make_repo(self)
        write(repo, "use.ts", "import { type Outcome } from './types';\nimport type { Outcome as O } from './types';\n"
                              "export { type Outcome };\nimport {\n  type Outcome,\n  type Other\n} from './types';\n")
        write(repo, "types.ts", "export type Outcome = 'ok' | 'fail';\n")
        write(repo, "other.go", "type Outcome struct{}\n")
        commit(repo, "base")
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir(repo)
        found = sorted((path, declared) for path, _, declared in check.definitions("Outcome"))
        self.assertEqual(found, [("other.go", "Outcome"), ("types.ts", "Outcome")])

    def test_same_named_files_and_near_names_are_listed(self):
        repo = make_repo(self)
        write(repo, "src/v2/recompute.service.ts", "export const recomputeWorkbookV2 = async () => {\n  return 1;\n};\n")
        write(repo, "src/count.ts", "export const recomputeWorkbookCount = 1;\n")
        for name in "abc":
            write(repo, f"src/{name}/index.ts", f"export const {name}Value = 1;\n")
        commit(repo, "base")
        write(repo, "src/recompute.service.ts", "export const recomputeWorkbook = async () => {\n  return 2;\n};\n")
        write(repo, "src/d/index.ts", "export const dValue = 1;\n")

        out = check_py(repo).stdout
        self.assertIn("src/recompute.service.ts  <- same file name as: src/v2/recompute.service.ts", out)
        self.assertIn("recomputeWorkbook  <- similar name: recomputeWorkbookV2 (src/v2/recompute.service.ts:1)", out)
        self.assertNotIn("recomputeWorkbookCount", out)
        self.assertNotIn("src/d/index.ts  <-", out)  # index.ts is shared by 3+ files: a convention

        run(repo, "git", "add", "-A")
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir(repo)
        self.assertIn("recomputeWorkbook", {declared for *_, declared in check.definitions("recomputeWorkbookV2")})


class HookTests(unittest.TestCase):
    def test_duplicates_are_reported_once_at_stop_not_after_edits(self):
        repo = make_repo(self)
        write(repo, "a.ts", "export const helper = (x) => x * 2;\n")
        commit(repo, "base")
        path = write(repo, "b.ts", "export const helper = (x) => x + 1;\n")
        session = f"test-{uuid.uuid4()}"
        state = os.path.join(tempfile.gettempdir(), "clean-code-hooks", f"{session}.json")
        self.addCleanup(lambda: os.path.exists(state) and os.remove(state))
        hook = os.path.join(SCRIPTS, "hook.py")

        edit = {"hook_event_name": "PostToolUse", "session_id": session, "tool_input": {"file_path": path}}
        result = run(repo, sys.executable, hook, stdin=json.dumps(edit))
        self.assertEqual((result.returncode, result.stderr), (0, ""))

        stop = json.dumps({"hook_event_name": "Stop", "session_id": session})
        reason = json.loads(run(repo, sys.executable, hook, stdin=stop).stdout)["reason"]
        self.assertIn("b.ts:1  helper  <- also defined in: a.ts:1", reason)
        self.assertIn("Potential duplicate", reason)
        self.assertEqual(run(repo, sys.executable, hook, stdin=stop).stdout, "")

    def test_commit_before_stop_still_reports_duplicates(self):
        repo = make_repo(self)
        write(repo, "a.ts", "export const helper = (x) => x * 2;\n")
        commit(repo, "base")
        path = write(repo, "b.ts", "export const helper = (x) => x + 1;\n")
        session = f"test-{uuid.uuid4()}"
        state = os.path.join(tempfile.gettempdir(), "clean-code-hooks", f"{session}.json")
        self.addCleanup(lambda: os.path.exists(state) and os.remove(state))
        hook = os.path.join(SCRIPTS, "hook.py")

        edit = {"hook_event_name": "PostToolUse", "session_id": session, "tool_input": {"file_path": path}}
        run(repo, sys.executable, hook, stdin=json.dumps(edit))
        commit(repo, "the agent commits before its final reply")

        stop = json.dumps({"hook_event_name": "Stop", "session_id": session})
        reason = json.loads(run(repo, sys.executable, hook, stdin=stop).stdout)["reason"]
        self.assertIn("b.ts:1  helper  <- also defined in: a.ts:1", reason)


if __name__ == "__main__":
    unittest.main()
