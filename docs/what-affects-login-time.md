# What affects login time

A plain account of what the measurements in this repository show. Figures are
from the two environments described in the [README](../README.md). Everything
here was measured unless it says otherwise.

## The short version

1. **With the option off, a login is mostly LDAP.** Three binds, each costing
   password hashing on the directory server. The number of mappers and the
   number of LDAP groups barely matter.
2. **With the option on, a login is mostly the same two database lookups,
   repeated once per mapper.** At 1,500 mappers that is 3,000 extra
   statements. Nothing is written.
3. **The cost is round trips, not load.** No server was busy. The database
   ran at about 2.5% CPU and the gateway at half a core while logins took
   seconds.
4. **So network distance to the database matters more than its size.** Half a
   millisecond more per statement added 1.7 s to every login.
5. **Logins that pass 10 s are cut off.** That turns slow into failed, and it
   is what locks out new users who are in many groups.
6. **Under concurrent logins the limits are, in order:** five workers per
   gateway pod, the directory server's bind capacity, and the time each login
   holds a worker.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="charts/time-split-dark.svg">
  <img alt="One login split into LDAP, database and gateway code at 1,500 mappers. Environment A: 1.2 seconds with the option off, of which 0.7 is LDAP; 6.9 seconds with it on, of which 2.6 is database and 3.5 gateway code. Environment B: 0.6 seconds off; with the option on 2.4 seconds when the gateway is in the database's zone and 4.1 seconds when it is in another zone, the difference being database time of 0.8 against 2.4 seconds." src="charts/time-split-light.svg">
</picture>

## Where one login spends its time

Measured inside a gateway pod by performing real logins through the same
authentication code the login page uses, and timing every database statement
and every LDAP call ([`probe_login.py`](../probe_login.py)). What remains of
the total is the gateway's own Python code. 1,500 mappers, a user that matches
none of them, median of 4 or 5 logins.

| Environment | Option | Login | LDAP | Database | Gateway code | Database statements | Time per statement |
|---|---|---|---|---|---|---|---|
| Environment A | off | 1.2 s | 703 ms (57%) | 94 ms (8%) | 414 ms (34%) | 46 | 1.08 ms |
| Environment A | on | 6.9 s | 733 ms (11%) | 2608 ms (38%) | 3488 ms (51%) | 3,049 | 0.71 ms |
| Environment B | off | 0.6 s | 387 ms (61%) | 64 ms (10%) | 180 ms (29%) | 46 | 0.86 ms |
| Environment B, gateway in the database's zone | on | 2.4 s | 382 ms (16%) | 762 ms (32%) | 1224 ms (52%) | 3,049 | 0.23 ms |
| Environment B, gateway in another zone | on | 4.1 s | 386 ms (9%) | 2407 ms (59%) | 1276 ms (31%) | 3,049 | 0.77 ms |

The probe agrees with the browsers: 6.9 s against 7.0–7.1 s in Environment A,
and 2.4 s and 4.1 s against the two clusters of browser logins at 2.4 s and
4.3 s in Environment B.

## What the option adds

With the option on, a login runs **3,049 database statements instead of 46**.
The 3,003 extra ones are two lookups:

| Statement | Times per login | Time, Environment A | Time, Environment B (other zone) |
|---|---|---|---|
| `SELECT` from `dab_rbac_roledefinition` | 1,501 | 1.3 s | 1.2 s |
| `SELECT` from `dab_rbac_dabcontenttype` | 1,500 | 1.2 s | 1.1 s |

- Every mapper in the test grants the same role, so these fetch **the same
  two rows 1,500 times each**.
- **Nothing is written.** The number of `UPDATE` statements is 7 with the
  option off and 7 with it on. The user holds none of the permissions, so
  there is nothing to remove; the lookups happen anyway.
- The count is identical in both environments, so it is a property of the
  code, not of the installation.
- The gateway's own time rises with it (0.4 s to 3.5 s in Environment A),
  because building 3,000 queries and turning 3,000 results into objects takes
  Python time.

## Why better hardware only partly helps

Environment B has a larger, dedicated, managed database, and the option still
makes logins 3.5 times slower. The time is not spent inside the database:

| | Environment A | Environment B |
|---|---|---|
| Statements per login, option on | 3,049 | 3,049 |
| Time per statement | 0.71 ms | 0.23 ms in the database's zone, 0.77 ms from another zone |
| Database CPU during these logins | not measured | 2.5% of 8 vCPU |

A statement this small costs almost nothing to execute. What it costs is the
trip: network, protocol, and the driver on the gateway side. 3,000 trips at
0.23 ms are 0.7 s; at 0.77 ms they are 2.3 s.

**The two gateway pods of Environment B sit in different availability zones.**
The database's primary is in one of them. Logins served by the pod in the same
zone took 2.4 s; logins served by the other took 4.1 s. In the browser data,
45 of 80 logins cluster at 2.4 s and 35 at 4.3 s. A highly available layout,
with pods spread across zones, is what makes half the logins slower.

## What does not matter

| Factor | Evidence |
|---|---|
| Number of LDAP groups a user is in | A user in 150 groups that have no mapper logs in as fast as a user in 5 groups: 1323 ms against 1373 ms |
| Number of mappers, with the option off | 1 to 1,500 mappers adds 100–180 ms in Environment A and about 90 ms in Environment B |
| Server CPU and memory | Nothing was saturated in any sequential test; see the tables below |
| Database size or class | 2.5% CPU on the database during the slowest logins |
| LDAP group lookup | 9 ms for a user in 152 groups, against 130 ms for one bind |

What does matter with the option off is the number of mappers a user
*matches*: the user in 150 mapped groups runs 502 statements and takes about
twice as long as the others.

## CPU and memory in every test

Means over each test phase, from the cluster's monitoring and, for the
database and hosts of Environment B, from Amazon CloudWatch. "One at a time" is
the sequential phase of 80 logins; "10 at once" is 10 concurrent browsers.
Phases shorter than about two minutes are summarised from one to four samples.

### Environment A — lab

1 gateway pod. The single node is shared with unrelated workloads, which is
why about 5 of its 16 cores are busy before any login.

| Mappers | Option | Logins | Gateway CPU, mean (cores) | Gateway CPU, peak | Gateway memory (GiB) | All of AAP, CPU (cores) | All of AAP, memory (GiB) | Worker nodes busy (cores) | Worker nodes memory used (GiB) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | off | one at a time | 0.36 | 0.48 | 1.2 | 0.66 | 7.2 | 5.5 of 16 | 43 of 63 |
| 1 | off | 10 at once | 0.77 | 1.18 | 1.2 | 1.52 | 7.3 | 6.1 of 16 | 43 of 63 |
| 1 | on | one at a time | 0.73 | 1.31 | 1.3 | 1.38 | 7.3 | 5.1 of 16 | 43 of 63 |
| 1 | on | 10 at once | 0.82 | 1.62 | 1.3 | 1.54 | 7.3 | 6.1 of 16 | 43 of 63 |
| 500 | off | one at a time | 0.26 | 0.52 | 1.3 | 0.52 | 7.4 | 5.0 of 16 | 43 of 63 |
| 500 | off | 10 at once | 0.72 | 1.34 | 1.4 | 1.10 | 7.4 | 5.6 of 16 | 43 of 63 |
| 500 | on | one at a time | 0.61 | 0.98 | 1.4 | 1.95 | 7.5 | 9.5 of 16 | 43 of 63 |
| 500 | on | 10 at once | 1.49 | 2.39 | 1.4 | 2.27 | 7.3 | 8.3 of 16 | 43 of 63 |
| 1,500 | off | one at a time | 0.57 | 0.68 | 1.3 | 0.88 | 7.3 | 5.0 of 16 | 41 of 63 |
| 1,500 | off | 10 at once | 0.61 | 0.61 | 1.3 | 0.95 | 7.3 | 6.3 of 16 | 41 of 63 |
| 1,500 | on | one at a time | 0.65 | 0.91 | 1.4 | 0.85 | 7.3 | 5.2 of 16 | 40 of 63 |
| 1,500 | on | 10 at once | 2.02 | 2.78 | 1.4 | 2.35 | 7.3 | 7.1 of 16 | 40 of 63 |

Database and directory server: **no CPU or memory was recorded.** Neither host
was monitored during the runs. Their share of login time is known from the
probe above.

### Environment B — AWS

2 gateway pods, 3 dedicated worker nodes (24 cores, 92 GiB), database with
8 vCPU and 32 GiB.

| Mappers | Option | Logins | Gateway CPU, mean (cores) | Gateway CPU, peak | Gateway memory (GiB) | All of AAP, CPU (cores) | All of AAP, memory (GiB) | Worker nodes busy (cores) | Worker nodes memory used (GiB) | Database CPU, mean | Database CPU, peak | Database free memory (GiB) | Database connections |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | off | one at a time | 0.24 | 0.28 | 1.4 | 0.49 | 7.2 | 1.3 of 24 | 21 of 92 | 2.3% | 2.5% | 21.3 | 54 |
| 1 | off | 10 at once | 0.57 | 0.88 | 1.5 | 1.16 | 7.3 | 2.2 of 24 | 21 of 92 | 11.2% | 15.8% | 21.3 | 71 |
| 1 | off | 25 at once | 2.08 | 2.08 | 1.6 | 3.46 | 7.4 | 4.2 of 24 | 21 of 92 | 15.8% | 15.8% | 21.3 | 71 |
| 1 | on | one at a time | 0.31 | 0.58 | 1.9 | 0.64 | 7.7 | 1.5 of 24 | 22 of 92 | 2.4% | 2.9% | 21.2 | 103 |
| 1 | on | 10 at once | 0.39 | 0.39 | 1.9 | 0.85 | 7.8 | 2.1 of 24 | 22 of 92 | 8.5% | 14.7% | 21.2 | 98 |
| 1 | on | 25 at once | 1.97 | 2.46 | 2.0 | 3.49 | 7.9 | 4.5 of 24 | 22 of 92 | 13.1% | 14.7% | 21.2 | 101 |
| 500 | off | one at a time | 0.38 | 1.14 | 2.0 | 0.87 | 8.0 | 1.8 of 24 | 22 of 92 | 2.8% | 3.8% | 21.2 | 113 |
| 500 | off | 10 at once | 0.45 | 0.45 | 2.0 | 1.04 | 8.0 | 2.2 of 24 | 22 of 92 | 10.5% | 10.5% | 21.2 | 115 |
| 500 | off | 25 at once | 1.83 | 2.16 | 2.1 | 3.26 | 8.0 | 4.4 of 24 | 22 of 92 | 13.8% | 17.1% | 21.2 | 115 |
| 500 | on | one at a time | 0.42 | 0.78 | 2.1 | 0.65 | 8.1 | 1.5 of 24 | 22 of 92 | 2.5% | 3.0% | 21.2 | 119 |
| 500 | on | 10 at once | 0.74 | 1.11 | 2.1 | 1.24 | 8.1 | 2.1 of 24 | 22 of 92 | 10.8% | 16.2% | 21.2 | 110 |
| 500 | on | 25 at once | 3.14 | 3.14 | 2.1 | 4.81 | 8.1 | 5.9 of 24 | 22 of 92 | 17.9% | 19.7% | 21.2 | 111 |
| 1,500 | off | one at a time | 0.49 | 1.19 | 2.1 | 0.70 | 8.1 | 1.6 of 24 | 22 of 92 | 2.6% | 3.5% | 21.2 | 117 |
| 1,500 | off | 10 at once | 0.37 | 0.37 | 2.1 | 0.76 | 8.2 | 1.8 of 24 | 23 of 92 | 8.6% | 14.2% | 21.2 | 111 |
| 1,500 | off | 25 at once | 2.28 | 2.28 | 2.1 | 3.79 | 8.2 | 4.7 of 24 | 23 of 92 | 14.6% | 15.1% | 21.2 | 113 |
| 1,500 | on | one at a time | 0.45 | 0.94 | 2.1 | 0.64 | 8.2 | 1.5 of 24 | 22 of 92 | 2.5% | 2.9% | 21.2 | 117 |
| 1,500 | on | 10 at once | 2.06 | 4.02 | 2.1 | 2.72 | 8.3 | 3.7 of 24 | 22 of 92 | 13.1% | 17.7% | 21.2 | 126 |
| 1,500 | on | 25 at once | 4.35 | 5.03 | 2.2 | 5.67 | 8.3 | 7.4 of 24 | 23 of 92 | 20.3% | 24.4% | 21.2 | 133 |

Hosts over the whole run (five-minute periods):

| Host | Size | CPU, mean | CPU, busiest period | CPU, highest instant |
|---|---|---|---|---|
| Directory server | 16 vCPU | 1.9% | 5.4% | 11.4% |
| Load generator | 16 vCPU | 10.3% | 33.0% | 63.1% |

Memory of these two hosts was not recorded for this run; a recorder has been
running on both since.

### Reading the tables

- **One login at a time never uses more than about half a core of gateway**,
  option off or on, in either environment. A 7-second login that is mostly
  waiting looks the same to the CPU as a 1-second one.
- **Gateway CPU rises only with concurrency**, and most with the option on:
  2.0 cores in Environment A and 2.1–4.4 in Environment B at 1,500 mappers.
- **Memory does not move with the option.** It is flat in Environment A. In
  Environment B gateway memory grew from 1.4 to 2.1 GiB over the run,
  independent of the option; whether it levels off was not observed.
- **The database is never busy:** at most 24% CPU for an instant, with 25
  browsers and the option on.
- **Connections to the database rose from 54 to 133** over the run. The
  gateway opens a new connection for every request.

## What limits concurrent logins

| Limit | Value | Effect |
|---|---|---|
| Workers per gateway pod | 5, not configurable | A sixth simultaneous login waits |
| Time limit per request | 10 s (`harakiri`), from a 30 s route timeout divided by 3 | A login past it is cut off: *Service Unavailable* |
| Wait for a free worker | 15 s (nginx) | A queued login past it: *Gateway Timeout* |
| Directory server | about 130 ms of CPU per bind, 3 binds per login | 4 vCPU: 15 binds/s, so 5 logins/s whatever the gateway; 16 vCPU: 60 binds/s |
| Time a login holds a worker | 0.7–1.5 s off, 2.4–7 s on | With the option on, each worker serves 3–5 times fewer logins |

Because a slow login is mostly waiting, **gateway CPU is a poor sign of
trouble**. Under a load that raised response time from 0.6 s to 7 s, the
gateway pods stayed at 9–27% of their CPU request. The number of requests in
flight followed the load from the first sample.

New users are a special case. On first login the gateway creates teams and
role assignments inline. For a user in 150 mapped groups that does not fit in
10 s:

| Environment | Option | Failed logins before the first success |
|---|---|---|
| A | off | 4, 4 (two users) |
| A | on | 5 of 5 failed; not in after five attempts |
| B | off | 1, 2 (two users) |
| B | on | 2 |

Progress is kept between attempts, so the user gets in eventually.

## How this was measured, and its limits

- Browser timings: real Chromium logins, fresh browser for each.
- Time split: `probe_login.py` inside a gateway pod. It times statements and
  LDAP calls from the gateway's side, so database time includes the network.
  It runs in its own process, not in a web worker; totals agree with the
  browsers within a few percent.
- The probe used one user type for the chart and 4 or 5 logins per case. The
  statement counts are exact; the timings are medians of few samples.
- Environment A's database and directory hosts were not monitored.
- "Gateway code" is what is left after database and LDAP time. It was not
  profiled further.
- All mappers in the test are team mappers granting the same role. With
  several different roles the number of lookups is the same, but they would
  no longer all fetch the same row.
