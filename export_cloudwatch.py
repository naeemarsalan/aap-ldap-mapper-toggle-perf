#!/usr/bin/env python3
"""Export database and host metrics from Amazon CloudWatch for the time span of a run.

usage: export_cloudwatch.py --rds ID [--ec2 NAME=INSTANCE_ID ...] results/<run>/logins.jsonl

Uses the `aws` command line (profile and region from the environment). Writes next to logins.jsonl:
  database-metrics.csv   one row per minute: CPU, memory, connections, load, IOPS, latency
  database-by-phase.tsv  mean and peak of each metric for every (cell, phase, concurrency)
  hosts-metrics.csv      one row per period and host: CPU utilisation
Standard library only.
"""
import argparse
import collections
import csv
import json
import os
import statistics
import subprocess
import time

import analyze
from export_metrics import PAD, windows

RDS = {
    "cpu_pct": ("CPUUtilization", "Average"),
    "cpu_pct_max": ("CPUUtilization", "Maximum"),
    "freeable_memory_bytes": ("FreeableMemory", "Average"),
    "connections": ("DatabaseConnections", "Maximum"),
    "db_load_sessions": ("DBLoad", "Average"),
    "db_load_cpu_sessions": ("DBLoadCPU", "Average"),
    "db_load_non_cpu_sessions": ("DBLoadNonCPU", "Average"),
    "read_iops": ("ReadIOPS", "Average"),
    "write_iops": ("WriteIOPS", "Average"),
    "write_latency_s": ("WriteLatency", "Average"),
    "commit_throughput_bytes": ("TransactionLogsGeneration", "Average"),
}


def utc(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def get(namespace, dim, value, metrics, start, end, period):
    queries = [
        {
            "Id": f"m{i}",
            "Label": name,
            "MetricStat": {"Metric": {"Namespace": namespace, "MetricName": m, "Dimensions": [{"Name": dim, "Value": value}]}, "Period": period, "Stat": stat},
        }
        for i, (name, (m, stat)) in enumerate(metrics.items())
    ]
    cmd = ["aws", "cloudwatch", "get-metric-data", "--start-time", utc(start), "--end-time", utc(end), "--metric-data-queries", json.dumps(queries), "--output", "json"]
    out = json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)
    series = collections.defaultdict(dict)
    for r in out["MetricDataResults"]:
        for ts, v in zip(r["Timestamps"], r["Values"]):
            series[r["Label"]][int(time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone)] = v
    return series


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="logins.jsonl of one run")
    ap.add_argument("--rds", help="DB instance identifier")
    ap.add_argument("--ec2", action="append", default=[], help="NAME=INSTANCE_ID; NAME is what is written to the file")
    a = ap.parse_args()

    recs = analyze.load(a.path)
    start = int(min(r["ts"] for r in recs)) - PAD
    end = int(max(r["ts"] for r in recs)) + PAD
    start -= start % 60
    wins = windows(recs)
    out_dir = os.path.dirname(a.path)

    def label(t):
        # a one-minute datapoint covers [t, t + 60)
        for key, (lo, hi) in wins.items():
            if lo - 60 < t <= hi:
                return key
        return ("",) * 6

    if a.rds:
        series = get("AWS/RDS", "DBInstanceIdentifier", a.rds, RDS, start, end, 60)
        names = [n for n in RDS if series.get(n)]
        times = sorted({t for n in names for t in series[n]})
        with open(os.path.join(out_dir, "database-metrics.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_utc", "epoch", "rep", "cell", "mappers", "toggle", "phase", "concurrency"] + names)
            for t in times:
                w.writerow([utc(t), t, *label(t)] + ["" if t not in series[n] else f"{series[n][t]:.6g}" for n in names])
        with open(os.path.join(out_dir, "database-by-phase.tsv"), "w", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["rep", "cell", "mappers", "toggle", "phase", "concurrency", "seconds", "samples"] + [f"{n}_{s}" for n in names for s in ("mean", "max")])
            for key, (lo, hi) in wins.items():
                ts = [t for t in times if lo - 60 < t <= hi]
                row = list(key) + [f"{hi - lo:.0f}", len(ts)]
                for n in names:
                    vals = [series[n][t] for t in ts if t in series[n]]
                    row += [f"{statistics.mean(vals):.6g}", f"{max(vals):.6g}"] if vals else ["", ""]
                w.writerow(row)
        print(f"database: {len(times)} minutes, metrics: {', '.join(names)}")

    if a.ec2:
        with open(os.path.join(out_dir, "hosts-metrics.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time_utc", "epoch", "host", "period_s", "cpu_pct_mean", "cpu_pct_max"])
            for item in a.ec2:
                name, iid = item.split("=", 1)
                # detailed monitoring gives 60 s periods; without it only 300 s periods hold data
                for period in (60, 300):
                    s = get("AWS/EC2", "InstanceId", iid, {"mean": ("CPUUtilization", "Average"), "max": ("CPUUtilization", "Maximum")}, start - start % period, end, period)
                    if s.get("mean"):
                        break
                times = sorted(s.get("mean", {}))
                if len(times) > 1:
                    # without detailed monitoring a 60 s query still answers with one point per 5 minutes
                    period = max(period, min(b - a for a, b in zip(times, times[1:])))
                for t in times:
                    w.writerow([utc(t), t, name, period, f"{s['mean'][t]:.4g}", f"{s['max'].get(t, float('nan')):.4g}"])
                print(f"host {name}: {len(s.get('mean', {}))} datapoints of {period} s")


if __name__ == "__main__":
    main()
