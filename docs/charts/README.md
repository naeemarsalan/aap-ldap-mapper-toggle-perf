# Charts

Drawn by `make_charts.py` from the raw records in `results/`. To redraw:

```bash
python3 make_charts.py \
  --env "Environment A — lab=1 gateway pod, shared single node=results/run1-20260929-1257/logins.jsonl" \
  --env "Environment B — AWS=2 gateway pods, RDS, dedicated nodes=results/envb-r2-matrix-20260929-1733/logins.jsonl" \
  --probe "Environment A|option off=results/probe/environment-a-1500-off.json" \
  --probe "Environment A|option on=results/probe/environment-a-1500-on.json" \
  --probe "Environment B|option off=results/probe/environment-b-1500-off-other-zone.json" \
  --probe "Environment B, option on|gateway in the database's zone=results/probe/environment-b-1500-on-same-zone.json" \
  --probe "Environment B, option on|gateway in another zone=results/probe/environment-b-1500-on-other-zone.json"
```
