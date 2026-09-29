# Running the test

## Repository layout

| Path | Purpose |
|---|---|
| `docs/` | The detailed pages linked from the report, and the charts |
| `PLAN.md` | Test plan |
| `seed_idm.py` | Seed / tear down groups and users in FreeIPA, including cold-start users and the LDAP-size control user |
| `aap_setup.py` | Manage the isolated authenticator, mappers and toggle; verify the mapper state |
| `loadtest.py` | Browser login timing (runs in the Playwright container) |
| `run_matrix.sh` | Runs a sequence of cells (default: the full matrix) |
| `analyze.py` | Summary tables from a run, plain text or markdown |
| `make_dashboard.py` | Generates the Grafana dashboard |
| `probe_login.py` | Times what one login spends in the database, in LDAP and in the gateway's code |
| `export_cloudwatch.py` | Exports database and host metrics from Amazon CloudWatch for the span of a run |
| `export_metrics.py` | Exports the gateway metrics behind the dashboard for the span of a run |
| `make_charts.py` | Draws the charts in `docs/charts/` from the raw records and exported metrics (needs matplotlib) |
| `explore.py` | One-off UI exploration used to locate the toggle |
| `tests/` | Unit tests on synthetic data; no system is contacted |
| `.env.example` | Every setting, with placeholder values |
| `CHANGELOG.md` | Changes to the harness and the review finding each one addresses |
| `REVIEW_BRIEF.md`, [`ADVISOR_REVIEW.md`](../ADVISOR_REVIEW.md) | Independent methodology review (Environment A) |
| `results/run1-*`, `results/run2-*` | Environment A raw data |
| `results/envb-*` | Environment B raw data |
| `results/probe/` | Results of `probe_login.py` |

Files written by `run_matrix.sh` to `results/<run-id>/`:

| File | Content |
|---|---|
| `logins.jsonl` | One record per login, copied from the load node after every cell |
| `phases.tsv` | Per browser phase: expected and actual record count, exit code, start and end time |
| `toggle-flip.tsv` | Per cell: duration of the toggle change, mappers changed, failed and retried requests |
| `replicas.tsv` | Gateway pods at the start and at the end of every cell |
| `gwlog-<cell>-<pod>.log` | Gateway log lines of the cell, one file per gateway pod |
| `restarts-<cell>.txt`, `status-<cell>.txt` | Container restart counts per pod, mapper and object counts |
| `run-meta.txt` | Settings of the run, git commit and checksums of the scripts |

A cell is named `r<rep>-c<cell_seq>-scale<mappers>-<toggle>`. `rep` and
`cell_seq` are also fields of every login record and Loki labels.

## Usage

```bash
cp .env.example .env && chmod 600 .env   # fill in credentials

python3 seed_idm.py seed                 # LDAP groups and users
python3 aap_setup.py authenticator       # isolated authenticator + allow mapper
./run_matrix.sh run1 1 500 1500          # full matrix
python3 analyze.py results/run1/logins.jsonl
```

The environment wins over `.env`, so single runs can be set up on the command
line. Every variable is described in `.env.example`.

#### Seeding

```bash
python3 seed_idm.py --pool 100 seed      # or PERF_POOL_SIZE=100
python3 seed_idm.py cold 6 150           # perf-cold-01..06, 150 mapped groups each
python3 seed_idm.py status
```

- `seed` also creates `perf-ctl-150`, a member of 150 groups that have no
  mapper (`perf-unmapped-0001..0150`). It separates the cost of many LDAP
  groups from the cost of many matched mappers.
- `cold` prints a `COLD_USERS=` line for `.env`. A cold user is used in one
  cell only and cannot be reused once it has logged in; remove it from AAP and
  seed it again, or seed more.
- `PERF_POOL_SIZE` must have the same value for `seed_idm.py` and
  `run_matrix.sh`.

#### Choosing what to run

```bash
# drift check: the same toggle-off cell before and after the toggle-on cell
CELLS="1500:off 1500:on 1500:off" ./run_matrix.sh run2

# whole sequence twice, concurrency 10, 25 and 50, one cold user per cell
REPEAT=2 RAMP="10 25 50" COLD_USERS=perf-cold-01,perf-cold-02,perf-cold-03,perf-cold-04 \
    CELLS="500:off 500:on" ./run_matrix.sh run3
```

Phases of a cell, in order:

| Phase | Logins |
|---|---|
| `first` | 1 per user in `SINGLE_USERS` |
| `cold` | `COLD_ITER` per cold user; only when `COLD_USERS` is set |
| `steady` | `STEADY_ITER` per user in `SINGLE_USERS`, sequential |
| `pool-first` | 1 per pool user |
| `concurrent` | `CONC_ITER` per pool user, once for every level in `RAMP` |

Sequential logins are separated by a random pause (`THINK_MIN`..`THINK_MAX`
seconds). The concurrent phase has no pause.

Before each cell the runner sets the mapper count and the toggle, and checks
both with `aap_setup.py verify <mappers> <on|off>`. The run stops, with the
toggle set to off, when:

- mapper setup, the toggle change or the check fails (exit code 1),
- the admin health check fails after a cell (exit code 2),
- a browser phase fails or writes no records (exit code 3; with
  `ON_PHASE_FAIL=continue` the run goes on).

Exit code 4 means the run finished but something was reported on the way, for
example a phase with fewer records than expected.

`loadtest.py` on the load node must be identical to the one in this checkout.
The runner checks this and stops if it is not; `PUSH_LOADTEST=1` copies it.

#### Analysis

```bash
python3 analyze.py results/run2/logins.jsonl
python3 analyze.py --markdown --env-name "Environment B" results/run2/logins.jsonl
```

| Table | Content |
|---|---|
| Phase … - all attempts | Every login of the phase. Failed logins are part of p50 / p95 / p99 / max |
| Steady state | Steady phase without the first successful login of each user and the two logins after it, median with 95% confidence interval |
| Convergence | Per user and cell: attempts until the first successful login, and their timings |
| Toggle effect | Median off and on, difference with confidence interval, ratio, ms per non-matching mapper |
| Drift (A/B/A) | Toggle off before and after the toggle-on cell; only when the sequence contains both |
| Gateway access log | Server-side login time per cell and gateway pod |
| Failed logins by outcome | Counts per cell and phase |

Result files written before `cell_seq` and `rep` existed can be analysed as
well.

#### Tests

```bash
python3 -m unittest discover -s tests -v
```

#### Teardown

Teardown removes everything the test created:

```bash
python3 aap_setup.py teardown
python3 seed_idm.py teardown
```

[Back to the report](../README.md)
