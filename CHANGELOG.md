# Changelog

## Report, time split and component metrics

- `README.md` is now a short report. The detailed pages moved to `docs/`.
- `probe_login.py` times every database statement and LDAP call of a real login inside the gateway. Addresses the review findings on missing server-side attribution (1.6, 4.4) for the database and LDAP.
- `export_cloudwatch.py` exports database and host metrics for the span of a run; `export_metrics.py` also exports worker node and namespace CPU and memory.
- `docs/what-affects-login-time.md` holds the account of what drives login time, with CPU and memory for every test.

## Charts and server-side metrics

- `make_charts.py` draws the README charts from the raw login records, for a light and a dark surface.
- `export_metrics.py` exports gateway CPU, memory, pods and route metrics from the cluster's monitoring for the span of a run. Addresses the review finding that no server-side data was kept (1.6), for the gateway only; database and LDAP time are still open.

## Unreleased - preparation for Environment B

Changes to the harness after the independent review of the Environment A run.
"Review" refers to `ADVISOR_REVIEW.md`, section and item. No result of
Environment A was changed.

### run_matrix.sh

| Change | Review finding |
|---|---|
| Exit status and record count of every browser phase are checked and written to `phases.tsv`. A failed or empty phase stops the run (`ON_PHASE_FAIL`) | 1.11 |
| Results are copied from the load node after every cell | 1.11 |
| Every setup call is checked; `aap_setup.py verify` runs before each cell | 1.11, 2.5 |
| Duration and failures of the toggle change are written to `toggle-flip.tsv` | 2.5, 4.10 |
| `CELLS` sets the cell sequence, so an off / on / off sequence can be run. `cell_seq` identifies a cell in the records and in Loki | 1.1, 2.3, 4.1 |
| `REPEAT` repeats the sequence, `rep` is recorded | 1.3, 4.9 |
| `RAMP` runs the concurrent phase at several concurrency levels | 1.9, 4.8 |
| Optional `cold` phase with users that have never logged in, each used in one cell | 1.2, 4.2 |
| Random pause between sequential logins | 1.10 |
| Namespace, kubeconfig, load node, Grafana host and gateway pod selector come from the environment. Grafana is optional | - |
| Gateway logs are collected from every gateway pod; pods are counted at the start and end of each cell (`replicas.tsv`) | 1.8 |
| `loadtest.py` on the load node is compared with the checkout before the run; checksums and git commit are written to `run-meta.txt` | 1.5 |
| The environment wins over `.env` | - |

### loadtest.py

| Change | Review finding |
|---|---|
| New record fields `cell_seq`, `rep`, `think_ms`, `think_seed` | 1.1, 1.10 |
| New record fields `post_ttfb_ms`, `post_wait_ms`, `post_response_end_ms` from the browser's timing of the login POST. Existing fields are measured as before | 3.7 |
| `login_post_ms` and `login_status` are recorded whenever the POST response was received, whatever fails afterwards. Such a record has outcome `http_<status>` when the status is 400 or higher | 1.3, 1.5 |
| Selectors are constants at the top of the file | - |
| Records are written with one `write` per record under a lock, and synced to disk | 1.11 |
| The push to Loki no longer blocks the other browsers of a concurrent phase | - |
| Failure screenshots have one name per cell, phase, user and iteration | - |

### analyze.py

| Change | Review finding |
|---|---|
| Failed logins are part of p50 / p95 / p99 / max. Failure rate and the share of logins over 5 s and 10 s are reported | 1.3 |
| Steady state excludes the first successful login of a user in a cell and the two logins after it | 1.4, 2.1, 4.5 |
| Convergence table: attempts until the first successful login | 1.4, 4.5 |
| Bootstrap 95% confidence interval of the median, and of the difference of medians | 1.3 |
| Toggle effect per scale and user, with ms per non-matching mapper | 2.4 |
| Drift table when a toggle-off cell ran before and after the toggle-on cell | 1.1, 2.3, 4.1 |
| Old result files are read: `cell_seq` from the order of appearance, `rep` 1, outcome `error` with an HTTP status of 400 or higher counted as HTTP failure | 1.5 |
| Gateway logs of all pods; HTTP 5xx and harakiri lines counted | 3.7, 3.8 |
| `--markdown`, `--env-name` | - |

### seed_idm.py

| Change | Review finding |
|---|---|
| Pool size from `PERF_POOL_SIZE` or `--pool` | 4.8 |
| `cold <count> <groups_per_user>` creates `perf-cold-NN` | 1.2, 4.2 |
| Control user `perf-ctl-150` in 150 groups without a mapper | 3.3, 4.6 |
| `teardown` removes every user and group whose name starts with `perf-`, whatever pool size it is called with | - |
| `status` prints counts of all of the above | - |

### aap_setup.py

| Change | Review finding |
|---|---|
| `toggle` prints elapsed time and failed requests, and fails if one failed | 2.5, 4.10 |
| `maps`, `toggle` and list requests are retried up to 3 times. Answers 4xx are not retried, except 408 and 429 | 2.5 |
| `verify <expected_maps> <on|off>` | 2.5 |
| A request without any HTTP answer is counted as failed | - |

### Not addressed by this change

| Review finding | Status |
|---|---|
| 1.6, 4.4 Server-side database and LDAP timings | Open. Needs access to the database and the LDAP server of the environment |
| 1.7 Isolation from the live authenticator | Open. To be checked in the gateway logs of the environment |
| 4.3 Creation benchmark through the API, without login | Open |
| 4.7 User with about 750 matched groups | Open |
