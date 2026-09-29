#!/usr/bin/env python3
"""Draw the comparison charts for the README from the raw login records.

usage: make_charts.py --env "LABEL=SUBTITLE=results/<run>/logins.jsonl" [--env ...] [--out docs/charts]

Writes, for a light and a dark surface:
  toggle-cost-{light,dark}.svg   sequential logins, median login time against mapper count
  concurrency-{light,dark}.svg   concurrent logins at the largest mapper count
  gateway-cpu-{light,dark}.svg   gateway CPU over each run, from gateway-metrics.csv (export_metrics.py)
  time-split-{light,dark}.svg    where one login spends its time, from --probe files (probe_login.py)
Needs matplotlib. Everything else in this repository runs without it.
"""
import argparse
import csv
import json
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

import analyze  # noqa: E402

USER = "perf-nomatch"
USER_LABEL = "user that matches no mapper"
LIMIT_S = 10  # gateway uWSGI harakiri

THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "ink2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "off": "#2a78d6",
        "on": "#eb6834",
        "ldap": "#1baf7a",
        "db": "#4a3aa7",
        "code": "#eda100",
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#ffffff",
        "ink2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "off": "#3987e5",
        "on": "#d95926",
        "ldap": "#199e70",
        "db": "#9085e9",
        "code": "#c98500",
    },
}
PARTS = (("ldap", "ldap_ms", "LDAP"), ("db", "db_ms", "Database"), ("code", "other_ms", "Gateway code"))
SERIES = (("off", "Option off"), ("on", "Option on"))

plt.rcParams.update(
    {
        "font.family": ["DejaVu Sans", "sans-serif"],
        "font.size": 10,
        "svg.fonttype": "none",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def seconds(ms):
    return f"{ms / 1000:.1f} s"


def sequential(recs):
    """(scale, toggle) -> median login POST ms of USER, steady state, first cell of each kind."""
    out = {}
    for key, (_, _, steady) in sorted(analyze.steady_state(recs).items()):
        _, _, scale, toggle, user = key
        times = analyze.post_times(steady)
        if user == USER and times and (scale, toggle) not in out:
            out[(scale, toggle)] = statistics.median(times)
    return out


def concurrent(recs):
    """(scale, concurrency, toggle) -> summary of the first concurrent phase of each kind."""
    out = {}
    for key, rs in sorted(analyze.group(recs, "concurrent").items()):
        _, _, scale, toggle, _, conc = key
        if (scale, conc, toggle) not in out:
            out[(scale, conc, toggle)] = analyze.summary(rs)
    return out


def style(ax, t):
    ax.set_facecolor(t["surface"])
    ax.grid(axis="y", color=t["grid"], linewidth=1)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(t["axis"])
    ax.tick_params(colors=t["muted"], length=0, labelsize=9)


def limit_line(ax, t, x, label=True, ha="left"):
    ax.axhline(LIMIT_S, color=t["muted"], linewidth=1)
    if label:
        ax.text(x, LIMIT_S + 0.25, "gateway stops a request at 10 s", color=t["ink2"], fontsize=8.5, ha=ha, va="bottom")


def legend(fig, t, handles):
    fig.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.055, 0.90),
        ncols=len(handles),
        frameon=False,
        fontsize=9.5,
        labelcolor=t["ink2"],
        handlelength=1.6,
        columnspacing=1.8,
    )


def titles(fig, t, title, subtitle):
    fig.text(0.06, 0.965, title, color=t["ink"], fontsize=13, fontweight="bold", ha="left", va="top")
    fig.text(0.06, 0.918, subtitle, color=t["ink2"], fontsize=9.5, ha="left", va="top")


def toggle_cost(envs, t, path):
    fig, axes = plt.subplots(1, len(envs), figsize=(5.2 * len(envs), 4.6), sharey=True, facecolor=t["surface"])
    axes = [axes] if len(envs) == 1 else list(axes)
    top = max(LIMIT_S + 1.5, max(v for _, _, recs, _ in envs for v in sequential(recs).values()) / 1000 + 1)
    for n, (ax, (label, sub, recs, _)) in enumerate(zip(axes, envs)):
        data = sequential(recs)
        scales = sorted({s for s, _ in data})
        style(ax, t)
        limit_line(ax, t, scales[0], label=n == 0)
        for toggle, _ in SERIES:
            xs = [s for s in scales if (s, toggle) in data]
            ys = [data[(s, toggle)] / 1000 for s in xs]
            ax.plot(xs, ys, color=t[toggle], linewidth=2, solid_capstyle="round", solid_joinstyle="round", zorder=3)
            ax.plot(xs, ys, linestyle="none", marker="o", markersize=8.5, markerfacecolor=t[toggle], markeredgecolor=t["surface"], markeredgewidth=2, zorder=4)
            # direct label on the last point only
            ax.annotate(seconds(data[(xs[-1], toggle)]), (xs[-1], ys[-1]), xytext=(9, 0), textcoords="offset points", color=t["ink"], fontsize=9.5, va="center")
        ax.set_xticks(scales)
        ax.set_xticklabels([f"{s:,}" for s in scales])
        ax.set_xlim(-90, max(scales) * 1.17)
        ax.set_ylim(0, top)
        ax.set_xlabel("LDAP mappers", color=t["ink2"], fontsize=9.5)
        ax.set_title(f"{label}\n", color=t["ink"], fontsize=10.5, fontweight="bold", loc="left", pad=2)
        ax.text(0, 1.015, sub, transform=ax.transAxes, color=t["ink2"], fontsize=9, ha="left", va="bottom")
        if n == 0:
            ax.set_ylabel("Login time, median (s)", color=t["ink2"], fontsize=9.5)
    titles(fig, t, 'Login time with "Block non-matching users"', f"One login at a time, {USER_LABEL}. Time from submitting the form to the login response.")
    legend(fig, t, [Line2D([], [], color=t[k], linewidth=2, marker="o", markersize=7, markeredgecolor=t["surface"], label=name) for k, name in SERIES])
    fig.subplots_adjust(left=0.075, right=0.975, top=0.72, bottom=0.13, wspace=0.08)
    fig.savefig(path, facecolor=t["surface"])
    fig.savefig(path[:-4] + ".png", facecolor=t["surface"], dpi=110)
    plt.close(fig)


def bar(ax, x, h, width, color):
    """Column with a rounded data end; the square baseline end comes from clipping at y = 0."""
    box = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    aspect = ((y1 - y0) / box.height) / ((x1 - x0) / box.width)
    r = width * 0.2
    drop = r * aspect * 2
    ax.add_patch(
        FancyBboxPatch((x - width / 2, -drop), width, h + drop, boxstyle=f"round,pad=0,rounding_size={r}", mutation_aspect=aspect, linewidth=0, facecolor=color, zorder=3, clip_on=True)
    )


def concurrency(envs, t, path, levels):
    groups = []
    for label, _, recs, _ in envs:
        data = concurrent(recs)
        scale = max(s for s, _, _ in data)
        for conc in levels:
            if (scale, conc, "off") in data and (scale, conc, "on") in data:
                groups.append((f"{label}\n{conc} browsers at once", scale, data[(scale, conc, "off")], data[(scale, conc, "on")]))
    fig, ax = plt.subplots(figsize=(1.9 + 2.2 * len(groups), 4.9), facecolor=t["surface"])
    style(ax, t)
    top = max(LIMIT_S + 2.5, max(g[3]["p50"] for g in groups) / 1000 + 3)
    ax.set_xlim(-0.5, len(groups) - 0.5)
    ax.set_ylim(0, top)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.77, bottom=0.29)
    fig.canvas.draw()
    limit_line(ax, t, len(groups) - 0.52, ha="right")
    width, gap = 0.13, 0.02
    for i, (_, _, off, on) in enumerate(groups):
        for k, s in (("off", off), ("on", on)):
            x = i + (-1 if k == "off" else 1) * (width / 2 + gap / 2)
            h = s["p50"] / 1000
            bar(ax, x, h, width, t[k])
            ax.text(x, h + 0.2, seconds(s["p50"]), color=t["ink"], fontsize=9.5, ha="center", va="bottom", zorder=5)
        over = on["slow"][1] / on["timed"] if on["timed"] else 0
        note = f"option on: {over:.0%} over 10 s,\n{on['fail'] / on['n']:.0%} failed"
        ax.text(i, -0.235, note, transform=ax.get_xaxis_transform(), color=t["ink2"], fontsize=8.5, ha="center", va="top", linespacing=1.35)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g[0] for g in groups], color=t["ink"], fontsize=9.5, linespacing=1.4)
    ax.set_ylabel("Login time, median (s)", color=t["ink2"], fontsize=9.5)
    scale = groups[0][1]
    titles(fig, t, f"Concurrent logins at {scale:,} mappers", "Pool users, each matching 10 mappers. Failed logins count at the time they were cut off.")
    legend(fig, t, [Patch(facecolor=t[k], label=name) for k, name in SERIES])
    fig.savefig(path, facecolor=t["surface"])
    fig.savefig(path[:-4] + ".png", facecolor=t["surface"], dpi=110)
    plt.close(fig)


def metrics(path):
    """Rows of gateway-metrics.csv next to the login records, or [] when it was not exported."""
    path = os.path.join(os.path.dirname(path), "gateway-metrics.csv")
    if not os.path.exists(path):
        return []
    return [r for r in csv.DictReader(open(path)) if r["cpu_api_cores"]]


def gateway_cpu(envs, t, path):
    envs = [e for e in envs if e[3]]
    if not envs:
        return
    fig, axes = plt.subplots(len(envs), 1, figsize=(10.4, 3.1 * len(envs) + 1.0), facecolor=t["surface"])
    axes = [axes] if len(envs) == 1 else list(axes)
    top = max(float(r["cpu_api_cores"]) for e in envs for r in e[3]) * 1.22
    for ax, (label, sub, _, rows) in zip(axes, envs):
        t0 = int(rows[0]["epoch"])
        xs = [(int(r["epoch"]) - t0) / 60 for r in rows]
        ys = [float(r["cpu_api_cores"]) for r in rows]
        style(ax, t)
        # one band per cell; a toggle-on cell carries a wash of the 'on' hue
        cells = {}
        for x, r in zip(xs, rows):
            if r["cell"]:
                lo, hi = cells.get((r["cell"], r["mappers"], r["toggle"]), (x, x))
                cells[(r["cell"], r["mappers"], r["toggle"])] = (min(lo, x), max(hi, x))
        for (_, mappers, toggle), (lo, hi) in cells.items():
            if toggle == "on":
                ax.axvspan(lo, hi, color=t["on"], alpha=0.12, linewidth=0, zorder=1)
            ax.text((lo + hi) / 2, top * 0.97, f"{int(mappers):,}\n{toggle}", color=t["ink2"], fontsize=8.5, ha="center", va="top", linespacing=1.3)
        ax.fill_between(xs, ys, color=t["off"], alpha=0.10, linewidth=0, zorder=2)
        ax.plot(xs, ys, color=t["off"], linewidth=2, solid_joinstyle="round", zorder=3)
        ax.set_ylim(0, top)
        ax.set_xlim(0, max(xs))
        ax.set_ylabel("CPU cores in use", color=t["ink2"], fontsize=9.5)
        ax.set_title(label, color=t["ink"], fontsize=10.5, fontweight="bold", loc="left", pad=16)
        ax.text(0, 1.03, sub, transform=ax.transAxes, color=t["ink2"], fontsize=9, ha="left", va="bottom")
    axes[-1].set_xlabel("Minutes from the start of the run", color=t["ink2"], fontsize=9.5)
    fig.text(0.06, 0.975, "Gateway CPU during each run", color=t["ink"], fontsize=13, fontweight="bold", ha="left", va="top")
    fig.text(
        0.06,
        0.945,
        "All gateway pods together, application container. Shaded: option on. Labels: mappers and option. Each cell ends with concurrent logins.",
        color=t["ink2"],
        fontsize=9.5,
        ha="left",
        va="top",
    )
    fig.subplots_adjust(left=0.075, right=0.975, top=0.86, bottom=0.09, hspace=0.62)
    fig.savefig(path, facecolor=t["surface"])
    fig.savefig(path[:-4] + ".png", facecolor=t["surface"], dpi=110)
    plt.close(fig)


def probe(path, user=USER):
    rows = [r for r in json.load(open(path)) if r["user"] == user and r["ok"]]
    out = {k: statistics.median(r[k] for r in rows) for k in ("total_ms", "db_ms", "ldap_ms", "other_ms", "db_statements")}
    return out


def time_split(probes, t, path):
    """Horizontal stacked bars: one login split into LDAP, database and gateway code."""
    if not probes:
        return
    rows = [(label, probe(p)) for label, p in probes]
    fig, ax = plt.subplots(figsize=(10.4, 1.35 + 0.72 * len(rows)), facecolor=t["surface"])
    ax.set_facecolor(t["surface"])
    ax.grid(axis="x", color=t["grid"], linewidth=1)
    ax.set_axisbelow(True)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=t["muted"], length=0, labelsize=9)
    top = max(r["total_ms"] for _, r in rows) / 1000
    gap = top * 0.004  # surface gap between segments
    for i, (label, r) in enumerate(rows):
        y, left = len(rows) - 1 - i, 0.0
        for key, field, _ in PARTS:
            w = r[field] / 1000
            ax.barh(y, max(w - gap, 0), left=left, height=0.42, color=t[key], linewidth=0, zorder=3)
            if w / top > 0.075:
                ink = "#ffffff" if key == "db" and t is THEMES["light"] else "#0b0b0b"
                ax.text(left + w / 2, y, seconds(r[field]), color=ink, fontsize=9, ha="center", va="center", zorder=4)
            left += w
        ax.text(left + top * 0.012, y, f"{seconds(r['total_ms'])}  ·  {r['db_statements']:,.0f} statements", color=t["ink"], fontsize=9.5, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([label.replace("|", "\n") for label, _ in reversed(rows)], color=t["ink"], fontsize=9.5, linespacing=1.3)
    ax.set_xlim(0, top * 1.3)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("Seconds", color=t["ink2"], fontsize=9.5)
    fig.text(0.03, 0.975, "Where one login spends its time", color=t["ink"], fontsize=13, fontweight="bold", ha="left", va="top")
    fig.text(0.03, 0.915, f"1,500 mappers, {USER_LABEL}. Every database statement and LDAP call timed inside the gateway.", color=t["ink2"], fontsize=9.5, ha="left", va="top")
    fig.legend(
        handles=[Patch(facecolor=t[k], label=name) for k, _, name in PARTS],
        loc="upper left",
        bbox_to_anchor=(0.025, 0.875),
        ncols=3,
        frameon=False,
        fontsize=9.5,
        labelcolor=t["ink2"],
        handlelength=1.4,
        columnspacing=1.8,
    )
    fig.subplots_adjust(left=0.27, right=0.98, top=0.76, bottom=0.13)
    fig.savefig(path, facecolor=t["surface"])
    fig.savefig(path[:-4] + ".png", facecolor=t["surface"], dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", action="append", required=True, help="LABEL=SUBTITLE=path to logins.jsonl")
    ap.add_argument("--out", default="docs/charts")
    ap.add_argument("--levels", default="10,25", help="concurrency levels to show")
    ap.add_argument("--probe", action="append", default=[], help="LABEL=path to a probe_login.py result; '|' in LABEL is a line break")
    a = ap.parse_args()
    envs = []
    for e in a.env:
        label, sub, path = e.split("=", 2)
        envs.append((label, sub, analyze.load(path), metrics(path)))
    os.makedirs(a.out, exist_ok=True)
    levels = [int(x) for x in a.levels.split(",")]
    for name, t in THEMES.items():
        toggle_cost(envs, t, os.path.join(a.out, f"toggle-cost-{name}.svg"))
        concurrency(envs, t, os.path.join(a.out, f"concurrency-{name}.svg"), levels)
        gateway_cpu(envs, t, os.path.join(a.out, f"gateway-cpu-{name}.svg"))
        time_split([p.split("=", 1) for p in a.probe], t, os.path.join(a.out, f"time-split-{name}.svg"))
    for label, _, recs, _ in envs:
        print(label, {f"{s}/{tg}": round(v) for (s, tg), v in sorted(sequential(recs).items())})


if __name__ == "__main__":
    main()
