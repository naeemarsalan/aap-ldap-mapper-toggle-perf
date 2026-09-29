"""Tests for analyze.py. All data is synthetic and generated here."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import analyze  # noqa: E402

FEW, MANY, NOMATCH = "perf-match-few", "perf-match-many", "perf-nomatch"


def rec(scale, toggle, phase, user, it, post, ok=True, status=None, seq=None, rep=None, outcome=None, conc=1, old=False):
    r = {"run": "synthetic", "scale": scale, "toggle": toggle, "concurrency": conc, "phase": phase, "user": user, "iter": it, "slot": 0}
    r.update(ts=1000.0 + it, ok=ok, outcome=outcome or ("logged_in" if ok else f"http_{status}"))
    if post is not None:
        r.update(login_page_ms=300.0, login_post_ms=float(post), login_status=status or (302 if ok else 503))
    if ok:
        r["submit_to_landing_ms"] = post + 1000.0
    if not old:
        r.update(cell_seq=seq or 1, rep=rep or 1)
    return r


def steady(scale, toggle, user, times, seq=1, rep=1, start=0):
    return [rec(scale, toggle, "steady", user, start + i, t, seq=seq, rep=rep) for i, t in enumerate(times)]


def table(tables, title):
    found = [t for t in tables if t.title.startswith(title)]
    return found[0] if found else None


def rows(t, **want):
    return [dict(zip(t.headers, r)) for r in t.rows if all(dict(zip(t.headers, r))[k] == v for k, v in want.items())]


class SteadyGuard(unittest.TestCase):
    def cell(self):
        rs = [rec(500, "off", "steady", MANY, 0, 10010, ok=False, status=503), rec(500, "off", "steady", MANY, 1, 9990, ok=False, status=503)]
        rs.append(rec(500, "off", "steady", MANY, 2, 6858))
        return rs + steady(500, "off", MANY, [3000, 2900] + [2000 + i for i in range(15)], start=3)

    def test_drops_first_success_and_two_more(self):
        rs = self.cell()
        conv, warm, rest = analyze.split_steady(list(reversed(rs)))
        self.assertEqual([r["iter"] for r in conv], [0, 1, 2])
        self.assertEqual([r["iter"] for r in warm], [3, 4])
        self.assertEqual([r["iter"] for r in rest], list(range(5, 20)))

    def test_success_on_first_attempt(self):
        conv, warm, rest = analyze.split_steady(steady(1, "off", FEW, [1300] * 20))
        self.assertEqual((len(conv), len(warm), len(rest)), (1, 2, 17))
        self.assertEqual(rest[0]["iter"], 3)

    def test_failure_after_warmup_stays_in_steady_state(self):
        rs = steady(1, "off", FEW, [1300] * 10) + [rec(1, "off", "steady", FEW, 10, 10020, ok=False, status=503)]
        rest = analyze.split_steady(rs)[2]
        self.assertEqual(len(rest), 8)
        self.assertFalse(rest[-1]["ok"])

    def test_never_successful(self):
        rs = [rec(1500, "on", "steady", NOMATCH, i, 10000, ok=False, status=503) for i in range(5)]
        conv, warm, rest = analyze.split_steady(rs)
        self.assertEqual((len(conv), warm, rest), (5, [], []))

    def test_users_and_cells_are_split_independently(self):
        rs = self.cell() + steady(500, "off", FEW, [1400] * 20) + steady(500, "on", FEW, [3700] * 20, seq=2)
        split = analyze.steady_state(rs)
        self.assertEqual(sorted(split), [(1, 1, 500, "off", FEW), (1, 1, 500, "off", MANY), (1, 2, 500, "on", FEW)])
        self.assertEqual(len(split[(1, 1, 500, "off", MANY)][2]), 15)
        self.assertEqual(len(split[(1, 1, 500, "off", FEW)][2]), 17)

    def test_tables(self):
        tables = analyze.report(self.cell())
        row = rows(table(tables, "Steady state"), user=MANY)[0]
        self.assertEqual((row["dropped"], row["n"], row["fail"], row["p50"]), ("5", "15", "0", "2007"))
        lo, hi = (float(v) for v in row["p50 95% CI"].split(".."))
        self.assertTrue(2000 <= lo <= 2007 <= hi <= 2014)
        row = rows(table(tables, "Convergence"), user=MANY)[0]
        self.assertEqual(row["attempts to first success"], "3")
        self.assertEqual(row["attempt POST ms"], "10010(http_503) 9990(http_503) 6858")
        self.assertEqual(row["following POST ms"], "3000 2900")
        raw = rows(table(tables, "Phase steady"), user=MANY)[0]
        self.assertEqual((raw["n"], raw["fail"], raw["max"]), ("20", "2", "10010"))


class FailuresInTails(unittest.TestCase):
    def test_failed_attempts_are_in_the_tail(self):
        rs = [rec(500, "on", "concurrent", f"perf-user-{i:02d}", 0, 1000 + i, conc=10) for i in range(17)]
        rs += [rec(500, "on", "concurrent", "perf-user-18", 0, 10050, ok=False, status=503, conc=10)]
        rs += [rec(500, "on", "concurrent", "perf-user-19", 0, 6000, ok=False, status=502, conc=10)]
        rs += [rec(500, "on", "concurrent", "perf-user-20", 0, None, ok=False, outcome="error", conc=10)]
        s = analyze.summary(rs)
        self.assertEqual((s["n"], s["fail"], s["no_post"], s["timed"]), (20, 3, 1, 19))
        self.assertEqual((s["max"], s["p99"], s["p95"]), (10050, 10050, 6000))
        self.assertEqual(s["p50"], 1009)
        self.assertEqual(s["p50_ok"], 1008)
        self.assertEqual(s["slow"], [2, 1])
        row = rows(table(analyze.report(rs), "Phase concurrent"))[0]
        self.assertEqual((row["n"], row["fail"], row["fail%"], row["no POST"], row["max"], row["p50 ok"]), ("20", "3", "15.0%", "1", "10050", "1008"))
        self.assertEqual((row[">5s"], row[">10s"], row["user"], row["conc"]), ("10.5%", "5.3%", "pool(20 users)", "10"))

    def test_all_failed(self):
        s = analyze.summary([rec(1500, "on", "steady", NOMATCH, i, 10000 + i, ok=False, status=503) for i in range(4)])
        self.assertEqual((s["fail"], s["p50"], s["p50_ok"], s["max"]), (4, 10001.5, None, 10003))

    def test_failure_table(self):
        rs = steady(1, "off", FEW, [1300] * 3) + [rec(1, "off", "steady", FEW, 3, 10000, ok=False, status=503)] * 2
        row = rows(table(analyze.report(rs), "Failed logins"))[0]
        self.assertEqual((row["outcome"], row["count"]), ("http_503", "2"))


class OldFormat(unittest.TestCase):
    def load(self, recs, extra=""):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "logins.jsonl")
            with open(path, "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in recs) + extra)
            with contextlib.redirect_stderr(io.StringIO()):
                return analyze.load(path)

    def test_cell_seq_and_rep_are_derived(self):
        rs = []
        for scale, toggle in ((1, "off"), (1, "on"), (500, "off")):
            rs += [rec(scale, toggle, "first", FEW, 0, 1400, old=True)] + [rec(scale, toggle, "steady", FEW, i, 1300, old=True) for i in range(5)]
        self.assertNotIn("cell_seq", rs[0])
        got = self.load(rs)
        self.assertEqual({(r["scale"], r["toggle"]): r["cell_seq"] for r in got}, {(1, "off"): 1, (1, "on"): 2, (500, "off"): 3})
        self.assertEqual({r["rep"] for r in got}, {1})

    def test_error_with_http_status_is_an_http_failure(self):
        old = rec(500, "off", "steady", MANY, 0, 9800, ok=False, status=503, outcome="error", old=True)
        old["error"] = "TimeoutError: Timeout 180000ms exceeded."
        plain = rec(500, "off", "steady", MANY, 1, None, ok=False, outcome="error", old=True)
        redirect = rec(500, "off", "steady", MANY, 2, 900, ok=False, status=302, outcome="error", old=True)
        got = self.load([old, plain, redirect])
        self.assertEqual([r["outcome"] for r in got], ["http_503", "error", "error"])
        self.assertEqual(analyze.summary(got)["max"], 9800)

    def test_new_records_keep_their_cell_seq(self):
        got = self.load(steady(1500, "off", FEW, [1] * 2, seq=1) + steady(1500, "on", FEW, [1] * 2, seq=2) + steady(1500, "off", FEW, [1] * 2, seq=3, rep=2))
        self.assertEqual(sorted({(r["rep"], r["cell_seq"]) for r in got}), [(1, 1), (1, 2), (2, 3)])

    def test_truncated_last_line_is_skipped(self):
        self.assertEqual(len(self.load(steady(1, "off", FEW, [1300] * 3), extra='{"run": "synth')), 3)

    def test_old_file_end_to_end(self):
        rs = []
        for scale, toggle, t in ((500, "off", 1400), (500, "on", 3900)):
            rs += [rec(scale, toggle, "steady", FEW, i, t + i, old=True) for i in range(20)]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "logins.jsonl")
            with open(path, "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rs))
            with open(os.path.join(d, "gwlog-scale500-on.log"), "w") as f:
                f.write('client - - [x] "POST /api/gateway/v1/login/ HTTP/1.1" 302 0 (2.656) "-"\nTraceback (most recent call last):\n')
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                analyze.main([path, "--env-name", "Synthetic"])
        self.assertIn("Synthetic", out.getvalue())
        self.assertIn("Toggle effect", out.getvalue())
        self.assertIn("Gateway access log", out.getvalue())


class ToggleEffect(unittest.TestCase):
    def aba(self, off1=1000, on=3500, off2=1100, scale=1500, user=NOMATCH):
        pad = [off1, off1, off1]
        return (
            steady(scale, "off", user, pad + [off1 + i for i in range(-8, 9)], seq=1)
            + steady(scale, "on", user, pad + [on + i for i in range(-8, 9)], seq=2)
            + steady(scale, "off", user, pad + [off2 + i for i in range(-8, 9)], seq=3)
        )

    def test_drift_table_for_aba(self):
        tables = analyze.report(self.aba())
        row = rows(table(tables, "Drift"))[0]
        self.assertEqual((row["off cell before"], row["off cell after"]), ("1", "3"))
        self.assertEqual((row["off p50 before"], row["off p50 after"], row["drift"], row["drift %"]), ("1000", "1100", "+100", "+10.0%"))
        self.assertEqual((row["on p50"], row["on - mean(off)"]), ("3500", "+2450"))
        lo, hi = (float(v) for v in row["95% CI"].split(".."))
        self.assertTrue(80 <= lo <= 100 <= hi <= 120)

    def test_effect_uses_the_off_cell_before(self):
        row = rows(table(analyze.report(self.aba()), "Toggle effect"))[0]
        self.assertEqual((row["off cell"], row["on cell"], row["off p50"], row["on p50"], row["on - off"], row["ratio"]), ("1", "2", "1000", "3500", "+2500", "3.50"))
        lo, hi = (float(v) for v in row["95% CI"].split(".."))
        self.assertTrue(2480 <= lo <= 2500 <= hi <= 2520)

    def test_no_drift_table_without_aba(self):
        rs = [r for r in self.aba() if r["cell_seq"] != 3]
        tables = analyze.report(rs)
        self.assertIsNone(table(tables, "Drift"))
        self.assertIsNotNone(table(tables, "Toggle effect"))

    def test_on_cell_first_uses_the_off_cell_after(self):
        rs = [r for r in self.aba() if r["cell_seq"] != 1]
        tables = analyze.report(rs)
        self.assertIsNone(table(tables, "Drift"))
        row = rows(table(tables, "Toggle effect"))[0]
        self.assertEqual((row["off cell"], row["on - off"]), ("3", "+2400"))

    def test_repeats_are_kept_apart(self):
        rs = self.aba()
        for r in self.aba(off1=2000, on=5000, off2=2000):
            rs.append(dict(r, rep=2))
        effect = rows(table(analyze.report(rs), "Toggle effect"))
        self.assertEqual([(r["rep"], r["on - off"]) for r in effect], [("1", "+2500"), ("2", "+3000")])

    def test_ms_per_non_matching_mapper(self):
        rs = []
        for user, off, on in ((NOMATCH, 1000, 3500), (MANY, 2000, 3750), (FEW, 1400, 3380), ("perf-ctl-150", 1500, 1500)):
            rs += steady(500, "off", user, [off] * 20, seq=1) + steady(500, "on", user, [on] * 20, seq=2)
        rs += steady(1, "off", FEW, [1300] * 20, seq=3) + steady(1, "on", FEW, [1250] * 20, seq=4)
        rs += steady(1, "off", NOMATCH, [1300] * 20, seq=3) + steady(1, "on", NOMATCH, [1310] * 20, seq=4)
        t = table(analyze.report(rs), "Toggle effect")
        got = {(r["mappers"], r["user"]): (r["matched"], r["non-matching"], r["ms per non-matching mapper"]) for r in rows(t)}
        self.assertEqual(got[("500", NOMATCH)], ("0", "500", "5.00"))
        self.assertEqual(got[("500", MANY)], ("150", "350", "5.00"))
        self.assertEqual(got[("500", FEW)], ("5", "495", "4.00"))
        self.assertEqual(got[("500", "perf-ctl-150")], ("0", "500", "0.00"))
        self.assertEqual(got[("1", FEW)], ("1", "0", "-"))
        self.assertEqual(got[("1", NOMATCH)], ("0", "1", "10.00"))

    def test_matched_is_capped_at_scale(self):
        self.assertEqual([analyze.matched(MANY, s) for s in (1, 100, 150, 500)], [1, 100, 150, 150])
        self.assertEqual([analyze.matched(u, 1500) for u in ("perf-user-07", analyze.POOL, "perf-ctl-150", "perf-cold-01")], [10, 10, 0, None])

    def test_concurrent_effect_per_level(self):
        rs = []
        for seq, toggle, base in ((1, "off", 2600), (2, "on", 5500)):
            for conc in (10, 25):
                rs += [rec(500, toggle, "concurrent", f"perf-user-{i:02d}", 0, base + conc, conc=conc, seq=seq) for i in range(1, 26)]
        t = table(analyze.report(rs), "Toggle effect - concurrent")
        self.assertEqual([(r["conc"], r["on - off"], r["non-matching"]) for r in rows(t)], [("10", "+2900", "490"), ("25", "+2900", "490")])


class Bootstrap(unittest.TestCase):
    def test_reproducible_and_brackets_the_median(self):
        vals = [1000 + 37 * i % 211 for i in range(40)]
        a, b = analyze.boot_median_ci(vals), analyze.boot_median_ci(list(vals))
        self.assertEqual(a, b)
        self.assertTrue(a[0] <= sorted(vals)[20] <= a[1])
        self.assertTrue(min(vals) <= a[0] < a[1] <= max(vals))

    def test_too_few_values(self):
        self.assertIsNone(analyze.boot_median_ci([1.0]))
        self.assertIsNone(analyze.boot_diff_ci([1.0, 2.0], []))

    def test_difference_excludes_zero_for_separated_groups(self):
        lo, hi = analyze.boot_diff_ci([1000 + i for i in range(17)], [3000 + i for i in range(17)])
        self.assertTrue(0 < lo <= 2000 <= hi)


class Output(unittest.TestCase):
    def data(self):
        rs = []
        for seq, toggle, t in ((1, "off", 1000), (2, "on", 3500), (3, "off", 1050)):
            rs += [rec(500, toggle, "first", NOMATCH, 0, t + 300, seq=seq)]
            rs += [rec(500, toggle, "cold", f"perf-cold-{seq:02d}", 0, 10000, ok=False, status=503, seq=seq), rec(500, toggle, "cold", f"perf-cold-{seq:02d}", 1, 7000, seq=seq)]
            rs += steady(500, toggle, NOMATCH, [t + i for i in range(20)], seq=seq)
        return rs

    def test_markdown_tables_are_well_formed(self):
        out = analyze.render(analyze.report(self.data()), markdown=True, title="Results - Environment B")
        self.assertTrue(out.startswith("## Results - Environment B"))
        blocks = [b.splitlines() for b in out.split("\n\n")]
        tables = [b for b in blocks if b and b[0].startswith("|")]
        self.assertGreaterEqual(len(tables), 6)
        for t in tables:
            lines = [l for l in t if l.startswith("|")]
            self.assertRegex(lines[1], r"^\|(---:?\|)+$")
            self.assertEqual(len({l.count("|") for l in lines}), 1, lines[0])
        for title in ("Phase cold", "Steady state", "Convergence", "Toggle effect", "Drift (A/B/A)"):
            self.assertIn(f"### {title}", out)

    def test_text_output(self):
        out = analyze.render(analyze.report(self.data()), title="Results - x")
        self.assertIn("## Drift (A/B/A)", out)
        self.assertNotIn("|", out)

    def test_cold_users_in_convergence(self):
        row = rows(table(analyze.report(self.data()), "Convergence"), user="perf-cold-02 (cold)")[0]
        self.assertEqual((row["attempts to first success"], row["attempt POST ms"]), ("2", "10000(http_503) 7000"))

    def test_gateway_logs_of_all_pods(self):
        line = 'client - - [x] "POST /api/gateway/v1/login/ HTTP/1.1" {} 0 ({}) "-"\n'
        with tempfile.TemporaryDirectory() as d:
            for pod, entries in (("gateway-aaa-1", [(302, 1.0), (302, 2.0), (503, 10.0)]), ("gateway-aaa-2", [(302, 3.0)]), ("gateway-aaa-3", [])):
                with open(os.path.join(d, f"gwlog-r1-c02-scale500-on-{pod}.log"), "w") as f:
                    f.write("".join(line.format(*e) for e in entries) + ("worker 3 HARAKIRI\n" if pod.endswith("1") else ""))
            with open(os.path.join(d, "gwlog-scale1-off.log"), "w") as f:
                f.write(line.format(302, 1.5))
            t = analyze.gateway_table(d, [])
        got = {(r["mappers"], r["pod"]): (r["n"], r["max"], r["HTTP 5xx"], r["harakiri lines"]) for r in rows(t)}
        self.assertEqual(got[("500", "gateway-aaa-1")], ("3", "10.00", "1", "1"))
        self.assertEqual(got[("500", "gateway-aaa-2")], ("1", "3.00", "0", "0"))
        self.assertEqual(got[("500", "gateway-aaa-3")], ("0", "-", "0", "0"))
        self.assertEqual(got[("500", "all 3 pods")], ("4", "10.00", "1", "1"))
        self.assertEqual(got[("1", "-")], ("1", "1.50", "0", "0"))


if __name__ == "__main__":
    unittest.main()
