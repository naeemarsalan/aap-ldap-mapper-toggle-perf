"""Tests for loadtest.py with a fake browser. Playwright is not needed and nothing is contacted."""
import asyncio
import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.update(AAP_URL="https://aap.invalid", PERF_PASS="stub", LOKI_URL="")


class Request:
    method = "POST"
    timing = {"startTime": 1.0, "requestStart": 2.0, "responseStart": 52.5, "responseEnd": 60.0}


class Response:
    url = "https://aap.invalid/api/gateway/v1/login/"
    request = Request()

    def __init__(self, status):
        self.status = status

    async def finished(self):
        return None


class Locator:
    def __init__(self, page, selector):
        self.page, self.selector, self.first = page, selector, self

    def or_(self, other):
        return self

    async def wait_for(self, **kw):
        if self.page.mode == "stuck":
            raise TimeoutError("Timeout 180000ms exceeded.")

    async def count(self):
        return 1

    async def is_visible(self):
        return self.page.mode != "denied"

    async def inner_text(self):
        if self.page.mode == "503-then-crash":
            raise RuntimeError("page closed")
        return "Invalid username\nor password"


class Expect:
    def __init__(self, page, predicate):
        self.page, self.predicate = page, predicate

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    @property
    def value(self):
        async def get():
            if self.page.mode == "lost-response":
                raise RuntimeError("Target closed")
            assert self.predicate(self.page.response)
            return self.page.response

        return get()


class Page:
    """mode is taken from the user name typed into the form."""

    def __init__(self):
        self.mode, self.handlers, self.response = "", [], None

    def on(self, event, handler):
        self.handlers.append(handler)

    async def goto(self, *a, **kw):
        pass

    async def wait_for_selector(self, *a, **kw):
        pass

    async def fill(self, selector, value):
        if "username" in selector:
            self.mode = value.split("_")[0]

    async def click(self, selector):
        if self.mode == "no-response":
            raise TimeoutError("Timeout 180000ms exceeded.")
        await asyncio.sleep(0.01)
        self.response = Response(503 if self.mode in ("503", "503-then-crash", "lost-response") else 302)
        for h in self.handlers:
            other = Response(200)
            other.url = "https://aap.invalid/api/gateway/v1/ui_auth/"
            h(other)
            h(self.response)

    def expect_response(self, predicate, timeout=0):
        return Expect(self, predicate)

    async def wait_for_timeout(self, ms):
        pass

    async def screenshot(self, path):
        pass

    def locator(self, selector):
        return Locator(self, selector)


class Context:
    async def new_page(self):
        return Page()

    async def close(self):
        pass


class Browser:
    async def new_context(self, **kw):
        return Context()

    async def close(self):
        pass


class Playwright:
    chromium = types.SimpleNamespace(launch=lambda: asyncio.sleep(0, Browser()))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


fake = types.ModuleType("playwright.async_api")
fake.async_playwright = Playwright
sys.modules.setdefault("playwright", types.ModuleType("playwright"))
sys.modules["playwright.async_api"] = fake
import loadtest  # noqa: E402

class LoadTest(unittest.TestCase):
    def run_phase(self, *args):
        with tempfile.TemporaryDirectory() as d:
            loadtest.RESULTS_DIR = loadtest.SHOTS_DIR = d
            argv, sys.argv = sys.argv, ["loadtest.py", "--run", "t", "--scale", "500", "--toggle", "on"] + list(args)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    asyncio.run(loadtest.main())
            finally:
                sys.argv = argv
            with open(os.path.join(d, "t.jsonl")) as f:
                return [json.loads(l) for l in f]

    def test_record_fields(self):
        recs = self.run_phase("--users", "ok_1", "--iterations", "2", "--phase", "cold", "--cell-seq", "3", "--rep", "2", "--think-min", "0.01", "--think-max", "0.02", "--think-seed", "7")
        self.assertEqual(len(recs), 2)
        r = recs[1]
        old = {"run", "scale", "toggle", "concurrency", "phase", "user", "iter", "slot", "ts", "ok", "outcome", "login_page_ms", "login_post_ms", "login_status", "submit_to_landing_ms"}
        self.assertEqual(set(r) - old, {"cell_seq", "rep", "think_ms", "think_seed", "post_ttfb_ms", "post_wait_ms", "post_response_end_ms"})
        self.assertEqual(old - set(r), set())
        self.assertEqual((r["phase"], r["cell_seq"], r["rep"], r["scale"], r["think_seed"], r["outcome"], r["ok"]), ("cold", 3, 2, 500, 7, "logged_in", True))
        self.assertEqual((r["post_ttfb_ms"], r["post_wait_ms"], r["post_response_end_ms"]), (52.5, 50.5, 60.0))
        self.assertEqual(recs[0]["think_ms"], 0)
        self.assertTrue(10 <= r["think_ms"] <= 20)
        self.assertGreaterEqual(r["login_post_ms"], 10)

    def test_think_times_are_reproducible(self):
        args = ["--users", "ok_1", "--iterations", "4", "--think-min", "0.001", "--think-max", "0.03", "--think-seed", "7"]
        a = [r["think_ms"] for r in self.run_phase(*args)]
        self.assertEqual(a, [r["think_ms"] for r in self.run_phase(*args)])
        self.assertNotEqual(a, [r["think_ms"] for r in self.run_phase(*args[:-1], "8")])

    def test_no_think_time(self):
        recs = self.run_phase("--users", "ok_1", "--iterations", "3", "--think-min", "0", "--think-max", "0")
        self.assertEqual([r["think_ms"] for r in recs], [0, 0, 0])

    def failed(self, mode):
        return self.run_phase("--users", f"{mode}_1", "--iterations", "1")[0]

    def test_http_failure(self):
        r = self.failed("503")
        self.assertEqual((r["ok"], r["outcome"], r["login_status"], r["message"]), (False, "http_503", 503, "Invalid username | or password"))
        self.assertIn("login_post_ms", r)
        self.assertNotIn("submit_to_landing_ms", r)

    def test_failure_after_the_response_keeps_timing(self):
        r = self.failed("503-then-crash")
        self.assertEqual((r["outcome"], r["login_status"]), ("http_503", 503))
        self.assertIn("login_post_ms", r)
        self.assertIn("RuntimeError", r["error"])
        r = self.failed("stuck")
        self.assertEqual((r["ok"], r["outcome"], r["login_status"]), (False, "error", 302))
        self.assertIn("login_post_ms", r)

    def test_response_seen_by_the_listener_only(self):
        r = self.failed("lost-response")
        self.assertEqual((r["ok"], r["outcome"], r["login_status"]), (False, "http_503", 503))
        self.assertGreaterEqual(r["login_post_ms"], 10)

    def test_no_response(self):
        r = self.failed("no-response")
        self.assertEqual((r["ok"], r["outcome"]), (False, "error"))
        self.assertNotIn("login_post_ms", r)
        self.assertNotIn("login_status", r)

    def test_denied(self):
        r = self.failed("denied")
        self.assertEqual((r["ok"], r["outcome"]), (False, "denied"))

    def test_concurrent_records_are_whole_lines(self):
        users = ",".join(f"ok_{i}" for i in range(25))
        recs = self.run_phase("--users", users, "--iterations", "4", "--concurrency", "10", "--phase", "concurrent", "--think-max", "0", "--think-min", "0")
        self.assertEqual(len(recs), 100)
        self.assertEqual(len({(r["user"], r["iter"]) for r in recs}), 100)
        self.assertEqual({r["slot"] for r in recs}, set(range(10)))
        self.assertEqual({r["concurrency"] for r in recs}, {10})


if __name__ == "__main__":
    unittest.main()
