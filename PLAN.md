# AAP 2.6 LDAP mapper toggle — performance test plan

Target: AAP 2.6 gateway (operator 2.6.0+0.1789677985)
LDAP: FreeIPA
Load node: 16 cores / 78 GB, podman
Metrics: Grafana 12.3.3, Prometheus, Loki
Cluster: single-node OpenShift

## Goal

Quantify the login-time and gateway resource cost of the "block non-matching
users" toggle on LDAP authenticator mappers at a scale of about 1,500 LDAP
groups / mappers), toggle OFF vs ON.

## Baseline state (2026-09-29, before any changes)

| Item | Value |
|---|---|
| Authenticators | Local (id 1), IdM - LDAP (id 2, remove_users=true) |
| Authenticator maps | 2 (is_superuser -> aap_admins, allow -> aap_admins/aap_users) |
| AAP users / teams / orgs | 5 / 0 / 1 |
| IdM groups / users | 9 / 10 |
| Gateway | 1 pod, api container has no CPU limit |

## Toggle identity — resolved

UI checkbox **Options -> Block non-matching users** on the mapping form is the
API field `revoke` on /authenticator_maps/ (input id `revoke`, confirmed in a
real browser). With revoke=true a non-matching mapper becomes DENY instead of
SKIP in create_claims(), so every non-matching mapper produces reconcile work
on each login.

## Safety rules

- Never modify maps or settings on the live `IdM - LDAP` authenticator.
- All created objects are prefixed `perf-` (IdM) / `PERF` (AAP).
- teardown.sh removes everything created; baseline counts above are the target.

## Phases

### 1. Isolation
- Create authenticator `PERF - LDAP` against the same IdM, dedicated bind user.
- USER_SEARCH restricted to perf users so real users never hit perf maps.

### 2. Seed IdM
- Groups: perf-grp-0001 .. perf-grp-1500
- Users:
  - perf-match-few   — member of 5 mapped groups
  - perf-match-many  — member of 150 mapped groups
  - perf-nomatch     — member of no mapped group
  - perf-user-01..25 — concurrency pool, 10 groups each

### 3. Seed AAP mappers
- Scales: 2 (baseline), 500, 1500 — one team mapper per perf group.
- Toggle state applied in bulk via API between runs.

### 4. Browser tests (Playwright / Chromium, from load node)
- 4.0 Screenshot mapper create/edit form — confirm toggle label.
- 4.1 Sequential: 30 logins per cell, fresh browser context each time.
- 4.2 Concurrent: 10 and 25 simultaneous browsers.
- Timings captured: form submit -> landing page rendered, login POST duration,
  /me/ duration, total navigation.

Matrix: toggle {OFF, ON} x mappers {2, 500, 1500} x user {few, many, nomatch}

### 5. Metrics
- Client: per-login result lines pushed to Loki, summary gauges to Prometheus.
- Server: gateway pod CPU / memory, gateway DB activity, LDAP search time,
  gateway log timings for the login request.
- One Grafana dashboard with run annotations (scale / toggle state).

### 6. Deliverables
- results/ raw JSON per run, summary table (p50 / p95 / p99 / max), dashboard link.
