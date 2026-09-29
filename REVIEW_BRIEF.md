# Review brief for the advisor

You are acting as an independent judge of a performance test design and its
interim findings. Be critical. Disagreement is more useful than agreement.

## Hard rules

- READ-ONLY review. A test is running right now against shared systems.
- Do NOT run anything against AAP, IdM/LDAP, the OpenShift cluster, the load
  node, or Grafana. No ssh, curl, oc, podman, or python scripts from this repo.
- Do NOT read `.env`. Do NOT edit any existing file.
- The only file you may write is `ADVISOR_REVIEW.md` in this directory.
- You may read: PLAN.md, seed_idm.py, aap_setup.py, loadtest.py, run_matrix.sh,
  analyze.py, make_dashboard.py, and results/*.partial.jsonl.

## Background

Customer question: what is the performance impact of the "Block non-matching
users" toggle on LDAP authenticator mappers in Ansible Automation Platform 2.6,
at roughly 1,500 LDAP groups / mappers?

Verified facts:
- The UI checkbox "Block non-matching users" is the API field `revoke` on
  /api/gateway/v1/authenticator_maps/.
- In ansible_base create_claims(): for each map, if the trigger does not match
  the result is SKIP (no work). If `revoke` is true, SKIP becomes DENY, and for
  team/org/role maps a has_permission=False entry is recorded, which is later
  reconciled (role removal) for every such map.
- Gateway uWSGI has `harakiri = 10`; nginx uwsgi_read_timeout is 15s. A login
  request over 10 s gets its worker killed and the browser receives HTTP 503.
- Environment: single-node OpenShift, 1 gateway pod, external gateway database,
  FreeIPA as LDAP. Lab, not production sizing.

## Test design

- Isolated authenticator "PERF - LDAP" (order 1, tried before the live one),
  USER_SEARCH restricted to members of group perf-all.
- 1,500 LDAP groups perf-grp-0001..1500. One `team` mapper per group:
  group N -> team perf-team-N in org PERF, role "Team Member".
  One `allow` mapper on perf-all, revoke=false, order 0.
- Users: perf-match-few (5 mapped groups), perf-match-many (150 mapped groups),
  perf-nomatch (0 mapped groups), pool perf-user-01..25 (10 groups each).
- Matrix: mappers {1, 500, 1500} x toggle {off, on}, run in that order,
  off before on within each scale.
- Per cell: 1 "first" login per user, 20 sequential logins per user,
  1 login per pool user, then 100 logins at 10 concurrent browsers.
- Real browser (Playwright Chromium), fresh context per login. Metrics:
  login_post_ms (click submit -> POST /login/ response) and
  submit_to_landing_ms (click submit -> nav rendered).
- The toggle is flipped in bulk via API PATCH on all team mappers.

## Interim results (login POST, ms, sequential)

| mappers | toggle | user       | p50  | p95  | max  | failed |
|---------|--------|------------|------|------|------|--------|
| 1       | off    | 5 groups   | 1309 | 1473 | 1563 | 0/20   |
| 1       | off    | 150 groups | 1382 | 1509 | 1692 | 0/20   |
| 1       | off    | no match   | 1322 | 1460 | 1476 | 0/20   |
| 1       | on     | 5 groups   | 1275 | 1354 | 1360 | 0/20   |
| 1       | on     | 150 groups | 1337 | 1398 | 1404 | 0/20   |
| 1       | on     | no match   | 1262 | 1401 | 1422 | 0/20   |
| 500     | off    | 5 groups   | 1414 | 1645 | 1656 | 0/20   |
| 500     | off    | 150 groups | 2237 | 3117 | 6858 | 2/20   |
| 500     | off    | no match   | 1340 | 1516 | 1545 | 0/20   |

10 concurrent browsers, 1 mapper: p50 ~2.3-2.6 s, 0 failures, both toggle states.

Observed at 500 mappers, toggle OFF: the 150-group user's first login returned
503 after ~9.8 s (harakiri). 143 teams were created during that request.
Progress persisted; after two failed attempts 64 of 150 role assignments
existed. Three failures in total before logins succeeded.

Remaining cells (500 on, 1500 off, 1500 on) are still running.

## What I want from you

Write ADVISOR_REVIEW.md with these sections, concise and specific:

1. Methodology flaws — anything that would make the conclusions wrong or
   unconvincing to a performance engineer. Consider ordering effects,
   state carry-over between cells, warm-up, sample sizes, what is and is not
   being isolated.
2. Is the test actually measuring the toggle? In particular: does running
   "off" then "on" at each scale, with teams already created, measure the
   steady-state cost, the one-time transition cost, or a mix?
3. Alternative explanations for the 503 / slow first login that I should rule
   out before attributing it to mapper processing.
4. Missing test cases, ranked by value.
5. Predictions: what do you expect for 500-on and 1500-on, and why. State them
   so they can be checked against the results.
6. Verdict on the interim conclusions below: supported / partly / unsupported.
   a. "The toggle has no cost at 1 mapper."
   b. "Mapper count alone barely affects users who match few or no groups."
   c. "Number of matched groups, not mapper count, drives login cost."
   d. "New users with many mapped groups cannot log in on first attempt."
