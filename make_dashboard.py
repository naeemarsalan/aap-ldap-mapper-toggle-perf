#!/usr/bin/env python3
"""Generate the Grafana dashboard JSON for the AAP LDAP mapper toggle test.

env: AAP_NAMESPACE (default aap), GRAFANA_PROM_UID, GRAFANA_LOKI_UID
"""
import json
import os

NS = os.environ.get("AAP_NAMESPACE") or "aap"
LOKI = {"type": "loki", "uid": os.environ.get("GRAFANA_LOKI_UID") or "loki"}
PROM = {"type": "prometheus", "uid": os.environ.get("GRAFANA_PROM_UID") or "openshift-thanos-aap-perf"}
SEL = '{job="aap-perf", run=~"$run", phase=~"$phase"}'
GW = f'namespace=~"{NS}.*", pod=~".*gateway-.*", container!="", container!="POD"'

panels, y, pid = [], 0, 0


def panel(title, ptype, targets, w=12, h=8, unit=None, x=None, **opts):
    global y, pid
    pid += 1
    px = x if x is not None else (0 if not panels or panels[-1]["gridPos"]["x"] + panels[-1]["gridPos"]["w"] >= 24 else panels[-1]["gridPos"]["x"] + panels[-1]["gridPos"]["w"])
    if px == 0 and panels:
        y = panels[-1]["gridPos"]["y"] + panels[-1]["gridPos"]["h"]
    p = {
        "id": pid,
        "title": title,
        "type": ptype,
        "gridPos": {"x": px, "y": y, "w": w, "h": h},
        "targets": [dict(t, refId=chr(65 + i)) for i, t in enumerate(targets)],
        "fieldConfig": {"defaults": {"unit": unit} if unit else {}, "overrides": []},
        "options": opts.get("options", {}),
    }
    panels.append(p)


def lq(expr, legend):
    return {"datasource": LOKI, "expr": expr, "legendFormat": legend, "queryType": "range"}


def pq(expr, legend):
    return {"datasource": PROM, "expr": expr, "legendFormat": legend}


def quant(q, field, by="scale, toggle, rep, cell_seq"):
    return f'quantile_over_time({q}, {SEL} | json | outcome="logged_in" | unwrap {field} [$__interval]) by ({by})'


LEG = "mappers={{scale}} toggle={{toggle}} rep={{rep}} cell={{cell_seq}}"
panel("Login POST time — p50 (browser)", "timeseries", [lq(quant(0.5, "login_post_ms"), LEG)], unit="ms")
panel("Login POST time — p95 (browser)", "timeseries", [lq(quant(0.95, "login_post_ms"), LEG)], unit="ms")
panel("Submit → landing page rendered — p50", "timeseries", [lq(quant(0.5, "submit_to_landing_ms"), LEG)], unit="ms")
panel("Submit → landing page rendered — p95", "timeseries", [lq(quant(0.95, "submit_to_landing_ms"), LEG)], unit="ms")
panel("Login POST time by user type — p50", "timeseries", [lq(quant(0.5, "login_post_ms", "user, toggle, scale, rep, cell_seq"), "{{user}} " + LEG)], unit="ms", w=24)
panel("Logins per minute by outcome", "timeseries", [lq(f'sum by (outcome) (count_over_time({SEL} | json [1m]))', "{{outcome}}")], w=12)
panel("Failed / denied logins", "timeseries", [lq(f'sum by (scale, toggle, rep, cell_seq, outcome) (count_over_time({SEL} | json | outcome!="logged_in" [1m]))', LEG + " {{outcome}}")], w=12)
panel("Gateway CPU (cores) per pod", "timeseries", [pq(f"sum by (pod, container) (rate(container_cpu_usage_seconds_total{{{GW}}}[2m]))", "{{pod}} {{container}}")], unit="short")
panel("Gateway memory per pod", "timeseries", [pq(f"sum by (pod, container) (container_memory_working_set_bytes{{{GW}}})", "{{pod}} {{container}}")], unit="bytes")
panel("Gateway replicas", "timeseries", [pq(f'count(count by (pod) (container_memory_working_set_bytes{{{GW}}}))', "pods")], unit="short")
panel("Gateway network (bytes/s)", "timeseries", [pq(f'sum(rate(container_network_receive_bytes_total{{namespace=~"{NS}.*", pod=~".*gateway-.*"}}[2m]))', "rx"), pq(f'sum(rate(container_network_transmit_bytes_total{{namespace=~"{NS}.*", pod=~".*gateway-.*"}}[2m]))', "tx")], unit="Bps")
panel("Redis + other AAP pods CPU (top 8)", "timeseries", [pq(f'topk(8, sum by (pod) (rate(container_cpu_usage_seconds_total{{namespace=~"{NS}.*", container!="", container!="POD"}}[2m])))', "{{pod}}")], unit="short")
panel("Hammer node CPU busy %", "timeseries", [pq('100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[2m])))', "node")], unit="percent")
panel("Raw login records", "logs", [lq(f"{SEL} | json | line_format \"{{{{.phase}}}} mappers={{{{.scale}}}} toggle={{{{.toggle}}}} c={{{{.concurrency}}}} {{{{.user}}}} {{{{.outcome}}}} post={{{{.login_post_ms}}}}ms landing={{{{.submit_to_landing_ms}}}}ms\"", "")], w=12)


def var(name, label):
    return {
        "name": name,
        "label": label,
        "type": "query",
        "datasource": LOKI,
        "query": {"label": name, "stream": '{job="aap-perf"}', "type": 1},
        "includeAll": True,
        "multi": True,
        "allValue": ".*",
        "current": {"text": "All", "value": "$__all"},
        "refresh": 2,
    }


dash = {
    "uid": "aap-ldap-mapper-toggle",
    "title": "AAP 2.6 — LDAP mapper 'Block non-matching users' toggle",
    "tags": ["aap", "perf"],
    "timezone": "browser",
    "schemaVersion": 39,
    "refresh": "30s",
    "time": {"from": "now-3h", "to": "now"},
    "templating": {"list": [var("run", "Run"), var("phase", "Phase")]},
    "annotations": {
        "list": [
            {
                "name": "Test cells",
                "datasource": {"type": "grafana", "uid": "-- Grafana --"},
                "enable": True,
                "iconColor": "orange",
                "target": {"type": "tags", "tags": ["aap-perf"], "matchAny": True},
            }
        ]
    },
    "panels": panels,
}
print(json.dumps({"dashboard": dash, "overwrite": True, "message": "aap-perf"}))
