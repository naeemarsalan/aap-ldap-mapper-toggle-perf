#!/usr/bin/env python3
"""Export the gateway metrics behind the Grafana dashboard for the time span of a run.

usage: export_metrics.py --prom-url URL --token-file FILE --namespace NS results/<run>/logins.jsonl

Reads the same Prometheus (Thanos) source as the dashboard and writes next to logins.jsonl:
  gateway-metrics.csv   one row per 30 s: gateway CPU, memory, pods, restarts, router sessions and
                        response rate, worker node CPU and memory, CPU and memory of the whole namespace
  gateway-by-phase.tsv  mean and peak of each metric for every (cell, phase, concurrency) of the run
Values are sums over all gateway pods. Standard library only.
"""
import argparse
import collections
import csv
import json
import os
import ssl
import statistics
import urllib.parse
import urllib.request

import analyze

STEP = 30
PAD = 60


def queries(ns, pods, route):
    sel = f'namespace="{ns}", pod=~"{pods}"'
    rt = f'exported_namespace="{ns}", route="{route}"'
    return {
        "cpu_api_cores": f'sum(rate(container_cpu_usage_seconds_total{{{sel}, container="api"}}[2m]))',
        "cpu_proxy_cores": f'sum(rate(container_cpu_usage_seconds_total{{{sel}, container="proxy"}}[2m]))',
        "memory_api_bytes": f'sum(container_memory_working_set_bytes{{{sel}, container="api"}})',
        "pods_ready": f'sum(kube_pod_status_ready{{namespace="{ns}", pod=~"{pods}", condition="true"}})',
        "restarts": f'sum(kube_pod_container_status_restarts_total{{{sel}}})',
        "route_in_flight": f"sum(haproxy_server_current_sessions{{{rt}}})",
        "route_responses_per_s": f"sum(rate(haproxy_server_http_responses_total{{{rt}}}[2m]))",
        "route_5xx_per_s": f'sum(rate(haproxy_server_http_responses_total{{{rt}, code="5xx"}}[2m]))',
        # the nodes the gateway can run on: all workers, or the single node of a one-node cluster
        "nodes_cpu_cores_busy": 'sum(rate(node_cpu_seconds_total{mode!~"idle|iowait|steal"}[2m]) * on(instance) group_left() (label_replace(kube_node_role{role="worker"}, "instance", "$1", "node", "(.*)")))',
        "nodes_cpu_cores_total": 'sum(count by (instance) (node_cpu_seconds_total{mode="idle"}) * on(instance) group_left() (label_replace(kube_node_role{role="worker"}, "instance", "$1", "node", "(.*)")))',
        "nodes_memory_used_bytes": 'sum((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) * on(instance) group_left() (label_replace(kube_node_role{role="worker"}, "instance", "$1", "node", "(.*)")))',
        "nodes_memory_total_bytes": 'sum(node_memory_MemTotal_bytes * on(instance) group_left() (label_replace(kube_node_role{role="worker"}, "instance", "$1", "node", "(.*)")))',
        "namespace_cpu_cores": f'sum(rate(container_cpu_usage_seconds_total{{namespace="{ns}", container!="", container!="POD"}}[2m]))',
        "namespace_memory_bytes": f'sum(container_memory_working_set_bytes{{namespace="{ns}", container!="", container!="POD"}})',
    }


def query_range(url, token, expr, start, end):
    q = urllib.parse.urlencode({"query": expr, "start": start, "end": end, "step": STEP})
    req = urllib.request.Request(f"{url.rstrip('/')}/api/v1/query_range?{q}", headers={"Authorization": f"Bearer {token}"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        data = json.load(resp)
    if data.get("status") != "success":
        raise SystemExit(f"query failed: {expr}: {data}")
    result = data["data"]["result"]
    return {int(float(t)): float(v) for t, v in result[0]["values"]} if result else {}


def windows(recs):
    """(rep, cell_seq, scale, toggle, phase, concurrency) -> (first login start, last login end)."""
    out = collections.OrderedDict()
    for r in sorted(recs, key=lambda r: r["ts"]):
        key = analyze.cell_of(r) + (r["phase"], r["concurrency"])
        took = (r.get("login_page_ms", 0) + r.get("submit_to_landing_ms", r.get("login_post_ms", 0))) / 1000
        lo, hi = out.get(key, (r["ts"], r["ts"]))
        out[key] = (min(lo, r["ts"]), max(hi, r["ts"] + took))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="logins.jsonl of one run")
    ap.add_argument("--prom-url", required=True)
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--namespace", default="aap")
    ap.add_argument("--pod-regex", default=".*gateway-[a-z0-9]+-[a-z0-9]+")
    ap.add_argument("--route", default="aap")
    a = ap.parse_args()

    recs = analyze.load(a.path)
    token = open(a.token_file).read().strip()
    start = int(min(r["ts"] for r in recs)) - PAD
    end = int(max(r["ts"] for r in recs)) + PAD
    start -= start % STEP

    series = {name: query_range(a.prom_url, token, expr, start, end) for name, expr in queries(a.namespace, a.pod_regex, a.route).items()}
    names = [n for n, s in series.items() if s]
    missing = [n for n, s in series.items() if not s]
    out_dir = os.path.dirname(a.path)

    wins = windows(recs)

    def label(t):
        for (rep, seq, scale, toggle, phase, conc), (lo, hi) in wins.items():
            if lo <= t <= hi:
                return rep, seq, scale, toggle, phase, conc
        return ("",) * 6

    with open(os.path.join(out_dir, "gateway-metrics.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_utc", "epoch", "rep", "cell", "mappers", "toggle", "phase", "concurrency"] + names)
        for t in range(start, end + 1, STEP):
            row = [series[n].get(t) for n in names]
            if all(v is None for v in row):
                continue
            w.writerow([analyze_time(t), t, *label(t)] + ["" if v is None else f"{v:.6g}" for v in row])

    with open(os.path.join(out_dir, "gateway-by-phase.tsv"), "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["rep", "cell", "mappers", "toggle", "phase", "concurrency", "seconds", "samples"] + [f"{n}_{s}" for n in names for s in ("mean", "max")])
        for key, (lo, hi) in wins.items():
            # rate() looks back 2 minutes, so short phases are dominated by what ran before them
            ts = [t for t in range(start, end + 1, STEP) if lo <= t <= hi]
            row = list(key) + [f"{hi - lo:.0f}", len(ts)]
            for n in names:
                vals = [series[n][t] for t in ts if t in series[n]]
                row += [f"{statistics.mean(vals):.6g}", f"{max(vals):.6g}"] if vals else ["", ""]
            w.writerow(row)

    print(f"{a.path}: {len(recs)} logins, {(end - start) // 60} min, metrics: {', '.join(names)}")
    if missing:
        print(f"  no data for: {', '.join(missing)}")


def analyze_time(t):
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


if __name__ == "__main__":
    main()
