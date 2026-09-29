#!/usr/bin/env python3
"""Summarise a run: browser timings per cell plus gateway-side login durations.

usage: analyze.py [--markdown] [--env-name NAME] [--gwlog-dir DIR] results/<run>/logins.jsonl

Failed logins are part of every tail statistic. Steady-state figures exclude
the first successful login of each user in a cell and the WARMUP logins after
it; those are reported in the convergence table instead.
"""
import argparse
import collections
import glob
import json
import os
import random
import re
import statistics
import sys

# mappers matched by each user once all 1500 exist, capped at the scale of the cell
MATCHED = {"perf-match-few": 5, "perf-match-many": 150, "perf-nomatch": 0}
MATCHED_PREFIX = {"perf-user-": 10, "perf-ctl-": 0}
POOL_MATCHED = 10
POOL = "pool"

WARMUP = 2  # logins dropped after the first successful one
BOOT_RESAMPLES = 2000
BOOT_SEED = 20260929
SLOW_MS = (5000, 10000)
PHASES = ("first", "cold", "steady", "pool-first", "concurrent")
PER_USER_PHASES = ("first", "cold", "steady")
ACCESS_RE = re.compile(r'"POST /api/gateway/v1/login/ HTTP/[\d.]+" (\d+) \d+ \(([\d.]+)\)')
GWLOG_RE = re.compile(r"gwlog-(?:r(\d+)-c(\d+)-)?scale(\d+)-(on|off)(?:-(.+))?\.log$")

Table = collections.namedtuple("Table", "title headers rows notes")


def pct(vals, q):
    if not vals:
        return float("nan")
    s = sorted(vals)
    return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]


def ms(v):
    return "-" if v is None or v != v else f"{v:.0f}"


def share(part, whole):
    return "-" if not whole else f"{100 * part / whole:.1f}%"


def ci(pair):
    return "-" if not pair else f"{pair[0]:.0f}..{pair[1]:.0f}"


def load(path):
    """Read a JSONL file, filling in what records written by older loadtest.py lack."""
    recs, order, bad = [], {}, 0
    with open(path) as f:
        lines = [line for line in f if line.strip()]
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            bad += 1
            continue
        r.setdefault("rep", 1)
        r.setdefault("concurrency", 1)
        r.setdefault("iter", 0)
        if "cell_seq" not in r:
            r["cell_seq"] = order.setdefault((r["scale"], r["toggle"]), len(order) + 1)
        status = r.get("login_status")
        if not r.get("ok") and r.get("outcome") == "error" and isinstance(status, int) and status >= 400:
            r["outcome"] = f"http_{status}"
        recs.append(r)
    if bad:
        print(f"warning: {bad} unreadable line(s) skipped in {path}", file=sys.stderr)
    return recs


def who(r):
    return r["user"] if r["phase"] in PER_USER_PHASES else POOL


def cell_of(r):
    return (r["rep"], r["cell_seq"], r["scale"], r["toggle"])


def post_times(rs, ok_only=False):
    return [r["login_post_ms"] for r in rs if "login_post_ms" in r and (r.get("ok") or not ok_only)]


def summary(rs):
    """Statistics of login_post_ms over ALL attempts that have one, failed or not."""
    post, good = post_times(rs), post_times(rs, ok_only=True)
    return {
        "n": len(rs),
        "fail": len([r for r in rs if not r.get("ok")]),
        "no_post": len(rs) - len(post),
        "p50": statistics.median(post) if post else None,
        "p95": pct(post, 0.95) if post else None,
        "p99": pct(post, 0.99) if post else None,
        "max": max(post) if post else None,
        "p50_ok": statistics.median(good) if good else None,
        "slow": [len([v for v in post if v > limit]) for limit in SLOW_MS],
        "timed": len(post),
    }


def summary_cells(s):
    return [
        str(s["n"]),
        str(s["fail"]),
        share(s["fail"], s["n"]),
        str(s["no_post"]),
        ms(s["p50"]),
        ms(s["p95"]),
        ms(s["p99"]),
        ms(s["max"]),
        ms(s["p50_ok"]),
    ] + [share(n, s["timed"]) for n in s["slow"]]


SUMMARY_HEADERS = ["n", "fail", "fail%", "no POST", "p50", "p95", "p99", "max", "p50 ok"] + [f">{limit // 1000}s" for limit in SLOW_MS]


def boot_median_ci(vals, seed=BOOT_SEED):
    """Bootstrap 95% confidence interval of the median."""
    if len(vals) < 2:
        return None
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choices(vals, k=len(vals))) for _ in range(BOOT_RESAMPLES))
    return meds[int(0.025 * BOOT_RESAMPLES)], meds[int(0.975 * BOOT_RESAMPLES) - 1]


def boot_diff_ci(a, b, seed=BOOT_SEED):
    """Bootstrap 95% confidence interval of median(b) - median(a)."""
    if len(a) < 2 or len(b) < 2:
        return None
    rng = random.Random(seed)
    diffs = sorted(
        statistics.median(rng.choices(b, k=len(b))) - statistics.median(rng.choices(a, k=len(a))) for _ in range(BOOT_RESAMPLES)
    )
    return diffs[int(0.025 * BOOT_RESAMPLES)], diffs[int(0.975 * BOOT_RESAMPLES) - 1]


def split_steady(rs):
    """One user's steady records of one cell -> (convergence, warm-up, steady-state)."""
    rs = sorted(rs, key=lambda r: (r["iter"], r.get("ts", 0)))
    first = next((i for i, r in enumerate(rs) if r.get("ok")), None)
    if first is None:
        return rs, [], []
    return rs[: first + 1], rs[first + 1 : first + 1 + WARMUP], rs[first + 1 + WARMUP :]


def matched(user, scale):
    n = POOL_MATCHED if user == POOL else MATCHED.get(user)
    if n is None:
        n = next((v for p, v in MATCHED_PREFIX.items() if user.startswith(p)), None)
    return None if n is None else min(n, scale)


def attempt(r):
    t = ms(r.get("login_post_ms"))
    return t if r.get("ok") else f"{t}({r.get('outcome', 'error')})"


def group(recs, phase):
    out = collections.defaultdict(list)
    for r in recs:
        if r["phase"] == phase:
            out[cell_of(r) + (who(r), r["concurrency"])].append(r)
    return out


def phase_tables(recs):
    tables = []
    for phase in PHASES:
        groups = group(recs, phase)
        if not groups:
            continue
        rows = []
        for k in sorted(groups):
            rs = groups[k]
            user = k[4] if k[4] != POOL else f"pool({len({r['user'] for r in rs})} users)"
            land = [r["submit_to_landing_ms"] for r in rs if r.get("ok") and "submit_to_landing_ms" in r]
            rows.append([str(k[0]), str(k[1]), str(k[2]), k[3], user, str(k[5])] + summary_cells(summary(rs)) + [ms(statistics.median(land) if land else None)])
        notes = ["Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only."]
        if phase == "steady":
            notes.append("Raw phase: includes convergence and warm-up logins. See the steady-state table.")
        tables.append(Table(f"Phase {phase} - all attempts", ["rep", "cell", "mappers", "toggle", "user", "conc"] + SUMMARY_HEADERS + ["landing p50"], rows, notes))
    return tables


def steady_state(recs):
    """(rep, cell_seq, scale, toggle, user) -> (convergence, warm-up, steady-state) records."""
    return {k[:5]: split_steady(rs) for k, rs in group(recs, "steady").items()}


def steady_table(split):
    rows = []
    for k in sorted(split):
        conv, warm, steady = split[k]
        s = summary(steady)
        rows.append(
            [str(k[0]), str(k[1]), str(k[2]), k[3], k[4], str(len(conv) + len(warm))]
            + summary_cells(s)[:5]
            + [ci(boot_median_ci(post_times(steady)))]
            + summary_cells(s)[5:]
        )
    headers = ["rep", "cell", "mappers", "toggle", "user", "dropped"] + SUMMARY_HEADERS[:5] + ["p50 95% CI"] + SUMMARY_HEADERS[5:]
    notes = [
        f"Steady state = logins after the first successful login of the user in the cell and the {WARMUP} logins following it ('dropped').",
        f"Failed logins are included in p50/p95/p99/max. CI: bootstrap, {BOOT_RESAMPLES} resamples, seed {BOOT_SEED}.",
        "A login killed at the gateway time limit is recorded with the time at which it was killed, so values with failures are lower bounds.",
    ]
    return Table("Steady state - login POST ms", headers, rows, notes)


def convergence_table(recs, split):
    first = {k[:5]: rs for k, rs in group(recs, "first").items()}
    rows = []
    for k in sorted(split):
        conv, warm, steady = split[k]
        reached = bool(conv) and conv[-1].get("ok")
        rows.append(
            [
                str(k[0]),
                str(k[1]),
                str(k[2]),
                k[3],
                k[4],
                " ".join(attempt(r) for r in sorted(first.get(k, []), key=lambda r: r["iter"])) or "-",
                str(len(conv)) if reached else f"never ({len(conv)} tried)",
                " ".join(attempt(r) for r in conv) or "-",
                " ".join(attempt(r) for r in warm) or "-",
            ]
        )
    for k, rs in sorted(group(recs, "cold").items()):
        conv, warm, rest = split_steady(rs)
        reached = bool(conv) and conv[-1].get("ok")
        rows.append(
            [str(k[0]), str(k[1]), str(k[2]), k[3], k[4] + " (cold)", "-", str(len(conv)) if reached else f"never ({len(conv)} tried)"]
            + [" ".join(attempt(r) for r in conv) or "-", " ".join(attempt(r) for r in warm + rest) or "-"]
        )
    headers = ["rep", "cell", "mappers", "toggle", "user", "'first' phase", "attempts to first success", "attempt POST ms", "following POST ms"]
    notes = [
        "Attempts are counted inside the steady phase (inside the cold phase for cold users); the 'first' phase login precedes them.",
        "'following' = the warm-up logins dropped from steady state; for cold users, every login after the first success.",
    ]
    return Table("Convergence - attempts until the first successful login", headers, rows, notes)


def pairs(cells):
    """cells: [(rep, cell_seq, scale, toggle)] -> [(on cell, off cell before or None, off cell after or None)]."""
    out = []
    for on in sorted(c for c in cells if c[3] == "on"):
        offs = sorted(c for c in cells if c[3] == "off" and c[0] == on[0] and c[2] == on[2])
        before = [c for c in offs if c[1] < on[1]]
        after = [c for c in offs if c[1] > on[1]]
        out.append((on, before[-1] if before else None, after[0] if after else None))
    return out


def effect_tables(values, label):
    """values: (rep, cell_seq, scale, toggle, user, conc) -> [login_post_ms]."""
    effect, drift = [], []
    series = sorted({k[4:] for k in values})
    for on, before, after in pairs({k[:4] for k in values}):
        for user, conc in series:
            v = {name: values.get(c + (user, conc), []) if c else [] for name, c in (("on", on), ("before", before), ("after", after))}
            off, off_cell = (v["before"], before) if v["before"] else (v["after"], after)
            if not v["on"] or not off:
                continue
            m_on, m_off = statistics.median(v["on"]), statistics.median(off)
            hit = matched(user, on[2])
            rest = None if hit is None else on[2] - hit
            lead = [str(on[0]), str(on[2]), user, str(conc)]
            effect.append(
                lead
                + [str(off_cell[1]), str(on[1]), "-" if hit is None else str(hit), "-" if rest is None else str(rest), str(len(off)), str(len(v["on"]))]
                + [ms(m_off), ms(m_on), f"{m_on - m_off:+.0f}", ci(boot_diff_ci(off, v["on"])), f"{m_on / m_off:.2f}" if m_off else "-"]
                + [f"{(m_on - m_off) / rest:.2f}" if rest else "-"]
            )
            if v["before"] and v["after"]:
                m_a, m_b = statistics.median(v["before"]), statistics.median(v["after"])
                drift.append(
                    lead
                    + [str(before[1]), str(after[1]), ms(m_a), ms(m_b), f"{m_b - m_a:+.0f}", ci(boot_diff_ci(v["before"], v["after"])), f"{100 * (m_b - m_a) / m_a:+.1f}%" if m_a else "-"]
                    + [ms(m_on), f"{m_on - (m_a + m_b) / 2:+.0f}"]
                )
    tables = []
    if effect:
        headers = ["rep", "mappers", "user", "conc", "off cell", "on cell", "matched", "non-matching", "n off", "n on", "off p50", "on p50", "on - off", "95% CI", "ratio", "ms per non-matching mapper"]
        notes = [
            "Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.",
            "CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.",
            "non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.",
        ]
        tables.append(Table(f"Toggle effect - {label}", headers, effect, notes))
    if drift:
        headers = ["rep", "mappers", "user", "conc", "off cell before", "off cell after", "off p50 before", "off p50 after", "drift", "95% CI", "drift %", "on p50", "on - mean(off)"]
        notes = [
            "Same configuration measured before and after the toggle-on cell. Drift is what the system changed by without any change to the toggle.",
            "A toggle effect smaller than the drift is not evidence of a toggle effect.",
        ]
        tables.append(Table(f"Drift (A/B/A) - {label}", headers, drift, notes))
    return tables


def gateway_table(gwdir, recs):
    files = [(GWLOG_RE.search(os.path.basename(f)), f) for f in sorted(glob.glob(os.path.join(gwdir, "gwlog-*.log")))]
    files = [(m, f) for m, f in files if m]
    if not files:
        return None
    seq_of = {}
    for r in recs:
        seq_of.setdefault((r["scale"], r["toggle"]), r["cell_seq"])
    cells = collections.defaultdict(dict)
    for m, f in files:
        scale, toggle = int(m.group(3)), m.group(4)
        key = (int(m.group(1) or 1), int(m.group(2) or seq_of.get((scale, toggle), 0)), scale, toggle)
        times, errors, killed = [], 0, 0
        with open(f, errors="replace") as fh:
            lines = fh.readlines()
        for line in lines:
            hit = ACCESS_RE.search(line)
            if hit:
                times.append(float(hit.group(2)))
                errors += int(hit.group(1)) >= 500
            killed += "harakiri" in line.lower()
        cells[key][m.group(5) or "-"] = (times, errors, killed)
    rows = []
    for key in sorted(cells):
        pods = cells[key]
        if len(pods) > 1:
            pods = dict(pods, **{f"all {len(pods)} pods": tuple(sum((p[i] for p in pods.values()), [] if i == 0 else 0) for i in range(3))})
        for pod in sorted(pods, key=lambda p: (p.startswith("all "), p)):
            t, errors, killed = pods[pod]
            stats = [f"{statistics.median(t):.2f}", f"{pct(t, 0.95):.2f}", f"{pct(t, 0.99):.2f}", f"{max(t):.2f}"] if t else ["-"] * 4
            rows.append([str(key[0]), str(key[1]), str(key[2]), key[3], pod, str(len(t))] + stats + [str(errors), str(killed)])
    headers = ["rep", "cell", "mappers", "toggle", "pod", "n", "p50", "p95", "p99", "max", "HTTP 5xx", "harakiri lines"]
    return Table("Gateway access log - POST /login/ server time (s)", headers, rows, ["One log file per gateway pod per cell. Requests killed by the gateway may have no access log line."])


def failure_table(recs):
    counts = collections.Counter((cell_of(r), r["phase"], r["concurrency"], r.get("outcome", "error")) for r in recs if not r.get("ok"))
    if not counts:
        return None
    rows = [[str(c[0]), str(c[1]), str(c[2]), c[3], phase, str(conc), outcome, str(n)] for (c, phase, conc, outcome), n in sorted(counts.items())]
    return Table("Failed logins by outcome", ["rep", "cell", "mappers", "toggle", "phase", "conc", "outcome", "count"], rows, [])


def report(recs, gwdir=None):
    split = steady_state(recs)
    tables = phase_tables(recs)
    if split:
        tables.append(steady_table(split))
        tables.append(convergence_table(recs, split))
        tables += effect_tables({k + (1,): post_times(v[2]) for k, v in split.items()}, "steady state, sequential logins")
    tables += effect_tables({k: post_times(rs) for k, rs in group(recs, "concurrent").items()}, "concurrent logins, pool users")
    tables.append(gateway_table(gwdir, recs) if gwdir else None)
    tables.append(failure_table(recs))
    return [t for t in tables if t]


def render(tables, markdown=False, title=None):
    out = []
    if title:
        out += [f"## {title}" if markdown else f"# {title}", ""]
    for t in tables:
        out.append(f"### {t.title}" if markdown else f"## {t.title}")
        if markdown:
            out.append("")
            out.append("| " + " | ".join(t.headers) + " |")
            out.append("|" + "|".join("---" if i in text_columns(t) else "---:" for i in range(len(t.headers))) + "|")
            out += ["| " + " | ".join(c.replace("|", "\\|") for c in row) + " |" for row in t.rows]
            out.append("")
            out += [f"- {n}" for n in t.notes]
        else:
            width = [max(len(r[i]) for r in [t.headers] + t.rows) for i in range(len(t.headers))]
            for row in [t.headers] + t.rows:
                out.append("  ".join(c.ljust(w) if i in text_columns(t) else c.rjust(w) for i, (c, w) in enumerate(zip(row, width))).rstrip())
            out += [f"  note: {n}" for n in t.notes]
        out.append("")
    return "\n".join(out)


def text_columns(t):
    return {i for i, h in enumerate(t.headers) if h in ("toggle", "user", "pod", "phase", "outcome", "'first' phase", "attempt POST ms", "following POST ms")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", help="logins.jsonl of one run")
    ap.add_argument("--markdown", action="store_true", help="GitHub-flavoured markdown tables")
    ap.add_argument("--env-name", default="", help="environment the results belong to, used in the title")
    ap.add_argument("--gwlog-dir", default=None, help="directory with gwlog-*.log, default: next to the JSONL file")
    a = ap.parse_args(argv)
    recs = load(a.path)
    runs = ", ".join(sorted({str(r.get("run")) for r in recs}))
    title = f"Results - {a.env_name or 'environment not named'} - run {runs} ({len(recs)} logins)"
    print(render(report(recs, a.gwlog_dir or os.path.dirname(os.path.abspath(a.path))), a.markdown, title))


if __name__ == "__main__":
    main()
