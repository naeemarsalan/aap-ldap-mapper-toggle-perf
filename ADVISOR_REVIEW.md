# Advisor review — AAP 2.6 LDAP mapper toggle performance test

Scope: read-only review of PLAN.md, seed_idm.py, aap_setup.py, loadtest.py,
run_matrix.sh, analyze.py, make_dashboard.py and
results/run1-20260929-1257.partial.jsonl (440 records, ending at 500-mapper /
toggle-off / pool-first user-01). Reviewed 2026-09-29 ~14:45 BST while the run
was in progress. Where I verified numbers in the raw data, I cite them.

---

## 1. Methodology flaws

Ranked roughly by how much they threaten the conclusions.

1. **Fixed ordering: off before on, scales ascending, one run.** Every ON cell
   runs on a warmer system with all user/team objects already created. This is
   not hypothetical noise — it is visible in the data: at 1 mapper, concurrent
   POST p50 is 2645 ms with toggle OFF and 2347 ms with toggle ON (~11%
   *faster* with the toggle). No mechanism makes `revoke=true` faster; that is
   ordering/warm-up noise. Any "toggle adds X ms" claim must survive an A/B/A
   (off → on → off) at one scale before I would believe its sign, let alone its
   size.
2. **State carries over across scales.** Teams and memberships persist, so the
   "first" phase creates different amounts of work per cell: perf-match-many
   creates 1 team at scale 1, ~149 at scale 500, and **0 at scale 1500**. The
   1500/off "first" phase will look trivially fast and must not be reported as
   "first login at 1500 mappers is fast" — the creation cost was absorbed at
   scale 500. The matrix measures object creation once per user, at whichever
   scale first exposes their groups. There is no cold-start measurement at
   1500 mappers at all.
3. **Failures are excluded from the summary statistics.** analyze.py computes
   p50/p95/max only over `ok` records. The two 10.0–10.1 s 503 attempts inside
   the 500/off/many steady cell vanish from the quantiles; the real tail
   (P(request > 10 s)) survives only as a count in the "failed" column. Also,
   with n=20, "p95" is the 2nd-largest sample (e.g. the 3117 figure is one
   observation) — effectively noise. There are no confidence intervals
   anywhere. Report per-iteration series and CIs, or state plainly that tails
   are unmeasured.
4. **The 500/off/many steady cell is contaminated.** Iterations 0–1 are 10 s
   503s, iteration 2 (first success) is 6.86 s finishing leftover creation, and
   only iterations 3–19 (~2.0–3.1 s) are true steady state. The reported
   p50 2237 mixes two populations. Split the cell: report post-convergence
   (iterations ≥ 3) separately from the convergence trajectory.
5. **The instrument changed mid-run.** loadtest.py was edited ~13:22 UTC —
   after the 500/off steady failures (13:17–13:23 UTC), before pool-first
   (13:30 UTC). The old failure path waited 180 s for a landing page after a
   503 (records show `outcome=error` + TimeoutError); the new path records
   `outcome=http_503` in ~0.5 s. Timings and status codes are comparable;
   failure classification and wall-clock per failure are not. Do not merge the
   first three failures with later 503s without noting they came from
   different code.
6. **No server-side attribution exists.** The dashboard has gateway
   CPU/memory/network only. PLAN §5 promised gateway DB activity and LDAP
   search time; neither is captured. Without those, section 3 below cannot be
   closed and the mapper-processing story remains an inference from client
   timings.
7. **The isolation claim is unverified.** PERF - LDAP is order 1, the live
   IdM authenticator order 2. If the gateway evaluates authenticators past the
   first success, every perf user is also processed by the live authenticator
   (they exist in IdM, and its USER_SEARCH is not restricted away from them).
   PLAN's "so perf users never touch it" is only true if evaluation stops at
   the first success — check the gateway logs. Constant overhead wouldn't bias
   the toggle comparison, but it inflates all absolute times, and
   remove_users/create_objects on the live authenticator could interact with
   perf users.
8. **Environment ceilings distort the headline finding.** 1 gateway pod, 10 s
   uWSGI harakiri, external DB. Latency above 10 s becomes a 503, so
   "N failures" is an environment property, not an AAP property. The
   relevant number is the latency curve (9.8–10.1 s POSTs); the 503s
   are a timeout interaction. Keep both, but don't let the failure count
   become the story.
9. **Coverage gaps vs. the plan.** PLAN says 30 steady iterations; the script
   runs 20 (STEADY_ITER=20). PLAN says 10 *and* 25 concurrent browsers;
   run_matrix.sh only implements 10. First-phase n=1, pool-first n=1/user,
   concurrent n=4/user. Concurrent data exists only for 1 mapper so far.
   Document these deviations in the final report.
10. **No think-time randomization.** Sequential logins arrive at a fixed
    cadence; a periodic server job (reconciler sweep, cron) could align with
    the same phase every cell and look like a scale/toggle effect.
11. **Data-flow hazard (operational, but it can invalidate the run).**
    run_matrix.sh does not check the exit status of the `browser()` ssh/podman
    calls and has no `set -e`, so a dead phase silently produces zero records.
    As of 14:45 BST the 500/off cell is short 124 records: pool-first has 1 of
    the expected 25, concurrent has 0 of 100, even though the cell-end
    artifacts (gwlog/restarts/status for scale-500-off) arrived at
    14:33–14:34 BST and the run log is still growing. Either the load-node
    record file stopped growing (phases died) or the partial sync stalled.
    Verify the load node's /work/results/run1-*.jsonl now — the only full copy
    is scp'd at the end of the whole matrix, so a crash loses everything not
    yet synced.

## 2. Is the test actually measuring the toggle?

Off-then-on at each scale, with teams already created, measures **a mix, but a
labelable one**:

- **OFF cells**: `first` = one-time object creation (teams + memberships) +
  claim processing with SKIP; `steady` = steady-state SKIP cost.
- **ON cells**: `first` = one-time transition (deny claims recorded +
  reconciliation for every non-matching map) + steady; `steady` = repeated
  logins under revoke semantics.

The steady-state cost of the toggle *is* what ON-steady measures — provided
the framework re-does the deny work each login. If `has_permission=False`
recording is idempotent (update_or_create-style no-op), ON-steady collapses to
OFF-steady plus a reconcile check, and the client cannot distinguish "cheap
because idempotent" from "cheap because fast" without server-side counters.
That is exactly the mechanism the customer is asking about, so server-side
instrumentation (section 4, item 4) is not optional.

The real problems with the ordering:

1. The OFF first/steady boundary is **not clean** — creation spilled past
   `first` into steady iterations 0–2 (and into two failures) at 500/off. The
   ON cells don't have this problem because their `first` phase runs warm.
2. Cross-scale comparisons of any `first` phase are meaningless (different
   creation counts per cell, per section 1.2).
3. There is no OFF-again cell, so drift cannot be separated from the toggle.
4. At **1 mapper the toggle has nothing to do for 2 of the 3 users**: toggle
   cost is proportional to *non-matching* maps, and perf-match-few /
   perf-match-many match the only team map (0 non-matching), while
   perf-nomatch has exactly 1. The scale-1 ON cell is structurally blind to
   the toggle — treat scale 1 as a sanity baseline, not toggle evidence.
5. The toggle flip itself (bulk PATCH of 500→1500 maps) is untimed and its
   partial-failure behavior unchecked (cmd_toggle prints failures and
   continues). If flipping 1500 maps is slow or leaves stragglers, that is
   itself a customer-visible cost of the toggle.

Verdict: the design measures steady-state (both states), one-time creation
(OFF, at first exposure), and the transition (ON `first`) — but only if each
phase is reported separately, OFF-steady is purged of creation-contaminated
iterations, and `first` phases are never compared across scales.

## 3. Alternative explanations for the 503 / slow first login

Rule these out before attributing the 503s to mapper processing:

1. **First-time object creation, not map iteration.** 143 teams in ~9.8 s ≈
   60–70 ms per team. Iteration 2 (first success) took 6.86 s to finish the
   remainder; post-convergence steady is ~2.0–2.4 s. The data already says
   creation dominates. Confirm the mechanism by timing direct API creation of
   ~150 teams + memberships (no login) and comparing per-object cost.
2. **External gateway DB write latency.** 60–70 ms per created object is
   consistent with DB round-trips. There are no DB metrics; pull them from the
   DB host for 13:17–13:24 UTC.
3. **LDAP-side cost specific to match-many.** 151 memberOf entries; the
   GROUP_SEARCH filter matches ~1500+ groups. If group enumeration were the
   driver, steady logins would stay slow — they don't — but the control user
   (150 groups, 0 mapped) doesn't exist. Check FreeIPA access-log search times
   for the failure window.
4. **Background reconciler / remove_users=true sweeps** overlapping the cell.
   Check gateway logs for reconcile activity at 13:17 / 13:20 / 13:23 UTC.
5. **Gateway state after bulk map creation.** 499 maps were created via the
   API minutes before the cell; caches and DB buffers differ from the 1-mapper
   cells. The elevated 500/off first-few (1845 ms vs 1398 ms at scale 1) with
   only 4 teams to create hints at this.
6. **Coincident cluster load.** SNO, single pod, no CPU limit. The dashboard's
   CPU/memory panels with cell annotations can rule this in or out.
7. **Client artifact.** Ruled out for the status code (the server returned
   503), but confirm the server-side duration ≈ 9.8 s in gwlog (analyze.py
   parses those lines). If server time is much lower, the latency is in
   nginx/proxy/network.
8. **Where does the 503 come from?** nginx uwsgi_read_timeout is 15 s and the
   responses arrived at 9.8–10.1 s, so an nginx timeout alone doesn't explain
   it. The harakiri story needs the actual uWSGI log line at those timestamps,
   plus which component wrote the 503.

## 4. Missing test cases, ranked by value

1. **A/B/A reversal** — 500/on then 500/off again (all phases). Cheap,
   decisive for ordering drift. Highest value of anything not yet planned.
2. **Cold start at 1500** — fresh user + fresh teams per scale (e.g. a
   perf-cold-150 user seeded only for the 1500 cell). Without it, "first login
   at 1500 mappers" is simply unmeasured.
3. **Direct-API creation benchmark** — create N teams + memberships via the
   API without a login. Decomposes creation cost from claim processing and
   closes section 3.1.
4. **Server-side instrumentation** — gateway DB query/write counts and times,
   LDAP search counts/times per login, harakiri confirmation in uWSGI logs.
   Promised in PLAN §5, absent from make_dashboard.py.
5. **Steady-phase guard** — define steady as iterations after the first
   successful login (+2 warm-ups), and report the convergence trajectory
   separately. Fixable in analysis; don't rerun for it.
6. **LDAP-size control user** — 150 groups, 0 mapped, to isolate memberOf
   attribute cost from mapped-map cost.
7. **Interior points on the ON-side curve** — a user with ~750 matched groups
   at 1500 mappers. Currently the toggle-ON cost curve (∝ non-matching maps)
   has no interior points between 1 and ~500.
8. **Concurrency sweep at 500** (5/10/25) and sustained load (minutes, not 4
   bursts); the 25-browser point from PLAN is missing.
9. **A second full run** for between-run variance. Everything so far is n=1
   at the cell level.
10. **Toggle-flip measurement** — duration of the 1500-map PATCH and its
    partial-failure behavior.

## 5. Predictions (to check against results)

Let c = per-non-matching-map deny+reconcile cost. From scale-1/on, c is
undetectable (nomatch has 1 non-matching map and on ≈ off), so c ∈ [0,
~100 ms]. The 500/on cell will roughly bracket it.

1. **500/on, first phase**: few/nomatch have 495–500 non-matching maps; many
   has 350. If c ≈ 10–20 ms → few/nomatch first logins ≈ 6.5–11.5 s → likely
   503; many ≈ 5–9 s, borderline. If c ≈ 0 → all ≈ 1.3–1.9 s, no failures.
2. **500/on, steady**: either ≈ OFF steady (c ≈ 0) or 4–8 s p50 with
   scattered 503s (c ≈ 10–20 ms). Pool users are a bonus dataset here: 25
   users with ~490–499 non-matching maps each — expect pool-first 500/on to
   behave like nomatch.
3. **1500/off**: all `first` logins fast — no creation left for the three
   main users (pool users create 1–10 teams) — p50 ≈ 1.5–2.5 s, zero 503s.
   If this happens, **do not** read it as "cold start at 1500 is cheap".
   Steady ≈ 500/off + small delta (many ~2.3–2.5 s p50).
4. **1500/on (the decisive cell)**: few/nomatch ≈ 1495–1500 non-matching
   maps, many ≈ 1350. c ≈ 10–20 ms → 13.5–22 s per login → **all** logins for
   all three users 503; the cell may produce zero successes. c ≈ 5 ms →
   p50 7–9 s, mixed 503s. c ≈ 0 → ≈ OFF profile. **Falsifiable signature**:
   under ON, the user ranking must flip relative to OFF (nomatch ≈ few ≥
   many). If "many" is still the worst user under ON, the toggle's marginal
   cost is ~0 and matched-map processing dominates regardless of toggle.
5. **Concurrent 500/on and 1500/on**: if per-login > 10 s, 10-way concurrency
   queues on top — expect high 503 rates and inflated POST times for
   survivors.
6. **Failure-mode mechanics**: post-13:22-UTC code records 503s as http_503
   in ~0.5 s, so later cells will churn through failures quickly; the first
   three failures each burned 180 s. Don't compare per-cell wall-clock across
   the code change.

## 6. Verdicts on the interim conclusions

**a. "The toggle has no cost at 1 mapper." — Supported, but structurally
near-vacuous.** Toggle cost is proportional to non-matching maps; at 1 mapper
only perf-nomatch has any (exactly 1), and few/many have 0. n=20, no CIs, and
the ON cell ran on a warmer system (concurrent ON was ~11% faster than OFF at
the same scale — ordering noise of the same magnitude as the claim). Restate
as: "no measurable cost at 1 mapper, as expected by construction."

**b. "Mapper count alone barely affects users who match few or no groups." —
Supported so far (toggle OFF only).** few 1309→1414 ms p50 (+8%), nomatch
1322→1340 (+1.4%) from 1→500 mappers; first-login few 1398→1845 (partly cache/
map-creation noise). Hold until 1500/off. Note this says nothing about
toggle-ON behavior — under ON, these are the users with the *most*
non-matching maps.

**c. "Number of matched groups, not mapper count, drives login cost." —
Supported for revoke=OFF, premature as a general statement.** At 500 mappers,
many (150 matched) p50 2237 and the creation 503s, vs few/nomatch ~1.3–1.4 s.
But the claim is conditional and the toggle exists precisely to invert it: with
revoke=ON the work moves to non-matching maps, and the predicted ranking flips
(nomatch/few ≥ many). Also "drives" conflates creation (~60–70 ms/map) with
steady processing (~6 ms/map) — the same matched count costs very differently
depending on whether objects exist. Restate as: "with the toggle OFF, matched
group count drives cost; mapper count barely matters."

**d. "New users with many mapped groups cannot log in on first attempt." —
Partly supported.** One user, three consecutive 503s at 9.8–10.1 s POST before
a 6.86 s success; consistent with creation work exceeding the 10 s harakiri,
with progress persisting across attempts. But: (i) it's a property of this
environment (10 s harakiri, 1 gateway pod, external DB) — in production the
same user would more likely see a 10–20 s first login than a 503; (ii) it was
not one failed attempt but three, so "first attempt" understates the symptom;
(iii) the mechanism is unproven until the section-3 checks (harakiri log line,
DB timings, LDAP timings) are done. Supported as an environment finding;
unsupported as a general AAP claim until it is measured at production
sizing.

---

**Bottom line**: the design is directionally right and the data so far are
real, but the strongest current claims (c, d) are hostage to two unfixed
issues — creation work bleeding into "steady" cells, and zero server-side
evidence for what the 10 s is spent on. Before the 1500 cells finish: verify
the missing 124 records on the load node, add the A/B/A cell, and instrument
the gateway DB + LDAP path. Then re-run the interim table with
creation-purged steady cells and failures included in the tail statistics.
