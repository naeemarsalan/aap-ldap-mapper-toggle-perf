# Environment A — lab, single-node OpenShift

A deliberately small, shared lab. Treat results as a **lower bound on
capacity**, not as sizing guidance.

## Infrastructure

| Layer | Detail |
|---|---|
| Platform | OpenShift 4.20, **single node**, 16 vCPU / 64 GB, shared with unrelated workloads (about 35% CPU and 65% memory in use before the test) |
| AAP | 2.6, operator install (`aap-operator.v2.6.0`), controller 4.7.17 |
| Gateway | **1 pod**, no horizontal autoscaling. `api` container: request 50m CPU / 750 Mi, no limits |
| Gateway app server | uWSGI, **5 worker processes**, **`harakiri = 10`** (requests over 10 s are killed), nginx `uwsgi_read_timeout 15s` |
| Gateway database | **External** EDB Postgres Advanced Server 15.18 on a separate VM. `max_connections` 250, `shared_buffers` 908 MB. Not instrumented |
| Redis | Cluster mode, 6 pods |
| LDAP | FreeIPA 4.12, plain LDAP (389), `MemberDNGroupType` |
| Load generator | Separate host, 16 cores / 78 GB, Playwright 1.55 Chromium in podman |
| Network | Load generator, cluster, LDAP and database on the same site LAN |

## Consequences of this environment

- One gateway pod with five workers: concurrent logins queue behind each other.
- The 10-second `harakiri` limit is from the gateway's shipped uWSGI
  configuration, not a lab customisation. Whether it differs in other install
  types has not been checked.
- Database time is invisible here. Any statement about *where* login time is
  spent is inference from client timing and gateway logs.

## Results — Environment A

Run `run1-20260929-1257`: 1,128 browser logins, 15 failed. Single run per
cell. Full tables, confidence intervals and the convergence view are in
[`results/run1-20260929-1257/analysis.md`](../results/run1-20260929-1257/analysis.md).

Login POST time in milliseconds. Sequential logins, steady state: the first
successful login and the two after it are excluded as warm-up, which leaves
17 logins per row, and 15 for the 150-group user at 500 mappers with the
option off, whose first two logins failed. Failed logins inside the steady
state are included in the percentiles; failures before it are in the
convergence table.

| Mappers | Toggle | User | Median | 95% CI of median | p95 | Max | Over 5 s | Failed |
|---|---|---|---|---|---|---|---|---|
| 1 | off | 5 groups | 1,334 | 1,273–1,385 | 1,473 | 1,563 | 0% | 0 |
| 1 | off | 150 groups | 1,359 | 1,336–1,394 | 1,506 | 1,692 | 0% | 0 |
| 1 | off | no match | 1,294 | 1,225–1,369 | 1,426 | 1,460 | 0% | 0 |
| 1 | on | 5 groups | 1,251 | 1,202–1,292 | 1,305 | 1,314 | 0% | 0 |
| 1 | on | 150 groups | 1,337 | 1,294–1,380 | 1,398 | 1,404 | 0% | 0 |
| 1 | on | no match | 1,257 | 1,239–1,287 | 1,401 | 1,422 | 0% | 0 |
| 500 | off | 5 groups | 1,414 | 1,323–1,449 | 1,645 | 1,656 | 0% | 0 |
| 500 | off | 150 groups | 2,172 | 2,108–2,393 | 2,726 | 3,117 | 0% | 0 |
| 500 | off | no match | 1,331 | 1,292–1,386 | 1,446 | 1,516 | 0% | 0 |
| 500 | on | 5 groups | 3,842 | 3,403–4,344 | 6,997 | 7,372 | 18% | 0 |
| 500 | on | 150 groups | 4,553 | 3,912–5,250 | 6,744 | 7,018 | 41% | 0 |
| 500 | on | no match | 3,920 | 3,805–4,506 | 5,104 | 6,757 | 12% | 0 |
| 1,500 | off | 5 groups | 1,484 | 1,437–1,538 | 1,694 | 1,774 | 0% | 0 |
| 1,500 | off | 150 groups | 2,364 | 2,319–2,429 | 2,623 | 3,032 | 0% | 0 |
| 1,500 | off | no match | 1,434 | 1,387–1,554 | 1,767 | 1,850 | 0% | 0 |
| 1,500 | on | 5 groups | 7,014 | 6,553–7,314 | 7,599 | 7,860 | 100% | 0 |
| 1,500 | on | 150 groups | 7,139 | 6,990–7,671 | 9,129 | 10,085 | 100% | 1 |
| 1,500 | on | no match | 7,140 | 6,730–7,530 | 8,465 | 9,029 | 100% | 0 |

One further failure at 1,500 mappers with the toggle on fell inside the
warm-up window and is listed in the convergence table.

**Toggle effect**, sequential, steady state:

| Mappers | User | Off | On | Added | 95% CI of added | Ratio | ms per non-matching mapper |
|---|---|---|---|---|---|---|---|
| 1 | 5 groups | 1,334 | 1,251 | −83 | −165 to −5 | 0.94 | — |
| 1 | 150 groups | 1,359 | 1,337 | −22 | −72 to 25 | 0.98 | — |
| 1 | no match | 1,294 | 1,257 | −37 | −112 to 32 | 0.97 | — |
| 500 | 5 groups | 1,414 | 3,842 | +2,428 | 1,980 to 2,931 | 2.72 | 4.9 |
| 500 | 150 groups | 2,172 | 4,553 | +2,380 | 1,746 to 3,077 | 2.10 | 6.8 |
| 500 | no match | 1,331 | 3,920 | +2,589 | 2,474 to 3,175 | 2.95 | 5.2 |
| 1,500 | 5 groups | 1,484 | 7,014 | +5,529 | 5,054 to 5,833 | 4.72 | 3.7 |
| 1,500 | 150 groups | 2,364 | 7,139 | +4,775 | 4,586 to 5,307 | 3.02 | 3.5 |
| 1,500 | no match | 1,434 | 7,140 | +5,706 | 5,296 to 6,069 | 4.98 | 3.8 |

**10 concurrent browsers**, 100 logins per row, pool users:

| Mappers | Toggle | Median | p95 | Max | Over 5 s | Over 10 s | Failed |
|---|---|---|---|---|---|---|---|
| 1 | off | 2,641 | 3,653 | 4,529 | 0% | 0% | 0 |
| 1 | on | 2,346 | 3,501 | 4,306 | 0% | 0% | 0 |
| 500 | off | 2,599 | 3,948 | 4,712 | 0% | 0% | 0 |
| 500 | on | 5,482 | 9,429 | 10,548 | 67% | 1% | 0 |
| 1,500 | off | 2,956 | 4,298 | 5,204 | 1% | 0% | 0 |
| 1,500 | on | 10,559 | 17,326 | 19,447 | 100% | 58% | 10 |

**Failures**

| Mappers | Toggle | Phase | Error shown to the user | Count |
|---|---|---|---|---|
| 500 | off | first + sequential, 150-group user | Service Unavailable (503) | 3 |
| 1,500 | on | sequential | Service Unavailable (503) | 2 |
| 1,500 | on | 10 concurrent | Service Unavailable (503) | 2 |
| 1,500 | on | 10 concurrent | Gateway Timeout (504) | 8 |

## Results — Environment A, run 2: drift check and cold start

Run `run2-abatest-20260929-1458`: 642 browser logins at 1,500 mappers, in the order
toggle off → on → off. Adds a control user and cold-start users. Full tables
in [`results/run2-abatest-20260929-1458/analysis.md`](../results/run2-abatest-20260929-1458/analysis.md).

**Drift.** Same configuration measured before and after the toggle-on cell.
Sequential logins, steady state, login POST median in ms:

| User | Off, before | On | Off, after | Drift | 95% CI of drift |
|---|---|---|---|---|---|
| 5 groups | 1,525 | 7,079 | 1,524 | −0.1% | −92 to 92 |
| 150 groups | 2,501 | 7,262 | 2,369 | −5.3% | −237 to 56 |
| no match | 1,456 | 6,951 | 1,422 | −2.4% | −104 to 74 |
| control: 150 LDAP groups, none mapped | 1,532 | 7,347 | 1,539 | +0.5% | −106 to 81 |
| 10 concurrent browsers, pool users | 2,827 | 12,073 | 2,836 | +0.3% | −162 to 209 |

Every drift interval contains zero. The slowdown appears when the toggle is
turned on and disappears when it is turned off.

**Control user.** A user in 150 LDAP groups that have no mapper logs in as
fast as a user in 5 groups (1,532 vs 1,525 ms, toggle off). A user in 150
groups that do have mappers takes 2,501 ms. The cost comes from matched
mappers, not from the number of LDAP groups.

**10 concurrent browsers, toggle on:** median 12.1 s, 76% of logins over
10 s, 16 of 100 failed. Run 1 measured 10.6 s, 58% and 10 of 100.

**Cold start.** Users that had never logged in, each in 150 mapped groups
that no other user is in, so the first login must create 150 teams. Five
login attempts each, login POST in ms:

| Toggle | Attempt 1 | 2 | 3 | 4 | 5 | Result |
|---|---|---|---|---|---|---|
| off | 10,434 ✗ | 10,656 ✗ | 9,172 ✗ | 9,999 ✗ | 5,631 ✓ | In on the 5th attempt |
| on | 9,640 ✗ | 9,791 ✗ | 10,066 ✗ | 9,997 ✗ | 10,076 ✗ | Not in after 5 attempts |
| off | 10,602 ✗ | 10,240 ✗ | 10,597 ✗ | 10,688 ✗ | 6,922 ✓ | In on the 5th attempt |

✗ = *Service Unavailable* (HTTP 503).

**Changing the toggle** on 1,500 mappers through the API, one request per
mapper, 8 in parallel: 504 s off → on, 529 s on → off. No request failed.

## Findings — Environment A

1. **At 1,500 mappers the toggle takes a login from about 1.5 s to about
   7 s.** That is 3–5 times slower, on every login, for every user type.
2. **The cost scales with the number of non-matching mappers**, at roughly
   3.5–7 ms each. It was somewhat lower per mapper at 1,500 than at 500, so
   the growth is close to linear but not exactly.
3. **With 10 concurrent logins at 1,500 mappers and the toggle on, the median
   was 10.6 s, 58% of logins took over 10 s, and 10% failed.** With the toggle
   off at the same scale, the median was 3.0 s and nothing failed.
4. **With the toggle off, mapper count is cheap.** 1,500 mappers cost 100–180
   ms more than 1 mapper for users matching few or no groups.
5. **With the toggle off, the number of matched groups drives cost.** The
   150-group user is about 60% slower than the others at the same scale.
6. **Logins that run past 10 s fail.** The gateway kills the worker
   (`harakiri = 10`) and the user sees *Service Unavailable*. Under
   concurrency, requests that queue for a worker can instead hit nginx's 15 s
   read timeout and show *Gateway Timeout*. The second mechanism is inferred
   from the configuration and the failure timings; it was not traced.
7. **A new user in 150 mapped groups cannot log in at first.** Teams and role
   assignments are created inline during login and do not fit in 10 s.
   Partial progress is kept between attempts. With the toggle off, login
   succeeded on the 4th attempt at 500 mappers (run 1) and on the 5th at 1,500
   mappers (run 2, two users). With the toggle on at 1,500 mappers, the user
   was still locked out after 5 attempts.
8. At 1 mapper the toggle has no effect that can be distinguished from noise.
   Expected by construction; a sanity check only.
9. **Changing the toggle on 1,500 mappers took 8.4–8.8 minutes** through the
   API. The UI has no bulk option.
10. **The slowdown is caused by the toggle, not by drift.** Measured
    off → on → off in run 2, the toggle-off figures before and after differ by
    at most 5%, with every confidence interval spanning zero.
11. **The number of LDAP groups a user is in does not matter; the number of
    matched mappers does** (run 2 control user).

## Limitations — Environment A

- One run per configuration, except 1,500 mappers, which was measured in both
  runs with consistent results. Confidence intervals describe variation within
  a run.
- Drift was checked at 1,500 mappers only.
- Cold start was measured with one user per cell and five attempts each.
- Failed logins are recorded at the time they were cut off, so percentiles
  that include failures are lower bounds.
- Run 1: the load script sent each result to the metrics store on the same
  event loop as the browsers, which could inflate concurrent timings
  slightly. Fixed before run 2; the run 2 concurrent figures are slightly
  higher, not lower, so the effect was not material.
- Run 1: the load script's failure detection changed during the run. Timings
  are unaffected.
- Run 2: gateway access-log extracts are incomplete for two of the three
  cells, most likely because the container log had rotated before collection.
  Browser-side measurements are complete.
- Database and LDAP time were not measured. Statements about where login time
  is spent are inference.
- The environment is small and shared. See *Infrastructure* above.

An independent review of the methodology, written while the run was in
progress, is in [`ADVISOR_REVIEW.md`](../ADVISOR_REVIEW.md). [`CHANGELOG.md`](../CHANGELOG.md) lists which of its
findings have since been addressed in the scripts.


[Back to the report](../README.md)
