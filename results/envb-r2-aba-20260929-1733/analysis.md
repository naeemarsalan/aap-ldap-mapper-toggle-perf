## Results - Environment B, 2 gateway replicas, drift and cold start - run envb-r2-aba-20260929-1733 (1167 logins)

### Phase first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 787 | 787 | 787 | 787 | 787 | 0.0% | 0.0% | 1231 |
| 1 | 1 | 1500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 801 | 801 | 801 | 801 | 801 | 0.0% | 0.0% | 1210 |
| 1 | 1 | 1500 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 1442 | 1442 | 1442 | 1442 | 1442 | 0.0% | 0.0% | 1862 |
| 1 | 1 | 1500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 736 | 736 | 736 | 736 | 736 | 0.0% | 0.0% | 1173 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 4295 | 4295 | 4295 | 4295 | 4295 | 0.0% | 0.0% | 4738 |
| 1 | 2 | 1500 | on | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 4057 | 4057 | 4057 | 4057 | 4057 | 0.0% | 0.0% | 4491 |
| 1 | 2 | 1500 | on | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 4268 | 4268 | 4268 | 4268 | 4268 | 0.0% | 0.0% | 5093 |
| 1 | 2 | 1500 | on | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 2414 | 2414 | 2414 | 2414 | 2414 | 0.0% | 0.0% | 2821 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 763 | 763 | 763 | 763 | 763 | 0.0% | 0.0% | 1176 |
| 1 | 3 | 1500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 750 | 750 | 750 | 750 | 750 | 0.0% | 0.0% | 1210 |
| 1 | 3 | 1500 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 1308 | 1308 | 1308 | 1308 | 1308 | 0.0% | 0.0% | 1726 |
| 1 | 3 | 1500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 731 | 731 | 731 | 731 | 731 | 0.0% | 0.0% | 1152 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase cold - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-cold-01 | 1 | 5 | 1 | 20.0% | 0 | 1435 | 9803 | 9803 | 9803 | 1228 | 20.0% | 0.0% | 14157 |
| 1 | 2 | 1500 | on | perf-cold-02 | 1 | 5 | 2 | 40.0% | 0 | 3873 | 10394 | 10394 | 10394 | 2658 | 40.0% | 20.0% | 15730 |
| 1 | 3 | 1500 | off | perf-cold-03 | 1 | 5 | 2 | 40.0% | 0 | 1861 | 10406 | 10406 | 10406 | 1014 | 40.0% | 20.0% | 13878 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase steady - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 712 | 803 | 877 | 877 | 712 | 0.0% | 0.0% | 1110 |
| 1 | 1 | 1500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 736 | 858 | 1032 | 1032 | 736 | 0.0% | 0.0% | 1164 |
| 1 | 1 | 1500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 1008 | 1355 | 1413 | 1413 | 1008 | 0.0% | 0.0% | 1406 |
| 1 | 1 | 1500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 706 | 805 | 853 | 853 | 706 | 0.0% | 0.0% | 1120 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 2459 | 4237 | 4343 | 4343 | 2459 | 0.0% | 0.0% | 2866 |
| 1 | 2 | 1500 | on | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 3284 | 4184 | 4214 | 4214 | 3284 | 0.0% | 0.0% | 3694 |
| 1 | 2 | 1500 | on | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 2679 | 4374 | 4390 | 4390 | 2679 | 0.0% | 0.0% | 3105 |
| 1 | 2 | 1500 | on | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 2360 | 4082 | 4378 | 4378 | 2360 | 0.0% | 0.0% | 2760 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 751 | 885 | 919 | 919 | 751 | 0.0% | 0.0% | 1174 |
| 1 | 3 | 1500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 719 | 791 | 843 | 843 | 719 | 0.0% | 0.0% | 1117 |
| 1 | 3 | 1500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 1050 | 1302 | 1358 | 1358 | 1050 | 0.0% | 0.0% | 1450 |
| 1 | 3 | 1500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 676 | 846 | 864 | 864 | 676 | 0.0% | 0.0% | 1071 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.
- Raw phase: includes convergence and warm-up logins. See the steady-state table.

### Phase pool-first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 767 | 894 | 907 | 983 | 767 | 0.0% | 0.0% | 1202 |
| 1 | 2 | 1500 | on | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 2394 | 4119 | 4189 | 4216 | 2394 | 0.0% | 0.0% | 2857 |
| 1 | 3 | 1500 | off | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 765 | 886 | 907 | 960 | 765 | 0.0% | 0.0% | 1199 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase concurrent - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 815 | 971 | 1077 | 1332 | 815 | 0.0% | 0.0% | 1400 |
| 1 | 2 | 1500 | on | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 2867 | 4652 | 4695 | 4982 | 2867 | 0.0% | 0.0% | 3422 |
| 1 | 3 | 1500 | off | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 820 | 945 | 1256 | 1471 | 820 | 0.0% | 0.0% | 1378 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Steady state - login POST ms

| rep | cell | mappers | toggle | user | dropped | n | fail | fail% | no POST | p50 | p50 95% CI | p95 | p99 | max | p50 ok | >5s | >10s |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 706 | 696..763 | 798 | 803 | 803 | 706 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 742 | 681..784 | 858 | 1032 | 1032 | 742 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 1010 | 989..1274 | 1336 | 1413 | 1413 | 1010 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 710 | 656..765 | 802 | 805 | 805 | 710 | 0.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 2456 | 2407..2526 | 4237 | 4343 | 4343 | 2456 | 0.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 4039 | 2362..4161 | 4184 | 4214 | 4214 | 4039 | 0.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 2684 | 2527..4296 | 4374 | 4390 | 4390 | 2684 | 0.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 2353 | 2326..4048 | 4075 | 4082 | 4082 | 2353 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 747 | 706..800 | 885 | 919 | 919 | 747 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 715 | 672..741 | 750 | 791 | 791 | 715 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 1046 | 971..1285 | 1294 | 1358 | 1358 | 1046 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 686 | 646..718 | 846 | 864 | 864 | 686 | 0.0% | 0.0% |

- Steady state = logins after the first successful login of the user in the cell and the 2 logins following it ('dropped').
- Failed logins are included in p50/p95/p99/max. CI: bootstrap, 2000 resamples, seed 20260929.
- A login killed at the gateway time limit is recorded with the time at which it was killed, so values with failures are lower bounds.

### Convergence - attempts until the first successful login

| rep | cell | mappers | toggle | user | 'first' phase | attempts to first success | attempt POST ms | following POST ms |
|---:|---:|---:|---|---|---|---:|---|---|
| 1 | 1 | 1500 | off | perf-ctl-150 | 787 | 1 | 690 | 877 748 |
| 1 | 1 | 1500 | off | perf-match-few | 801 | 1 | 690 | 748 695 |
| 1 | 1 | 1500 | off | perf-match-many | 1442 | 1 | 1355 | 961 970 |
| 1 | 1 | 1500 | off | perf-nomatch | 736 | 1 | 853 | 644 702 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 4295 | 1 | 2666 | 2502 2441 |
| 1 | 2 | 1500 | on | perf-match-few | 4057 | 1 | 2474 | 2538 2521 |
| 1 | 2 | 1500 | on | perf-match-many | 4268 | 1 | 2674 | 4268 2591 |
| 1 | 2 | 1500 | on | perf-nomatch | 2414 | 1 | 4378 | 2335 2368 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 763 | 1 | 766 | 753 749 |
| 1 | 3 | 1500 | off | perf-match-few | 750 | 1 | 843 | 712 753 |
| 1 | 3 | 1500 | off | perf-match-many | 1308 | 1 | 973 | 1302 1055 |
| 1 | 3 | 1500 | off | perf-nomatch | 731 | 1 | 643 | 652 779 |
| 1 | 1 | 1500 | off | perf-cold-01 (cold) | - | 2 | 9803(http_503) 4466 | 1021 1002 1435 |
| 1 | 2 | 1500 | on | perf-cold-02 (cold) | - | 3 | 9542(http_503) 10394(http_503) 3873 | 2648 2658 |
| 1 | 3 | 1500 | off | perf-cold-03 (cold) | - | 3 | 9920(http_503) 10406(http_503) 1861 | 976 1014 |

- Attempts are counted inside the steady phase (inside the cold phase for cold users); the 'first' phase login precedes them.
- 'following' = the warm-up logins dropped from steady state; for cold users, every login after the first success.

### Toggle effect - steady state, sequential logins

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | perf-ctl-150 | 1 | 1 | 2 | 0 | 1500 | 17 | 17 | 706 | 2456 | +1751 | 1676..1821 | 3.48 | 1.17 |
| 1 | 1500 | perf-match-few | 1 | 1 | 2 | 5 | 1495 | 17 | 17 | 742 | 4039 | +3298 | 1604..3420 | 5.45 | 2.21 |
| 1 | 1500 | perf-match-many | 1 | 1 | 2 | 150 | 1350 | 17 | 17 | 1010 | 2684 | +1674 | 1497..3289 | 2.66 | 1.24 |
| 1 | 1500 | perf-nomatch | 1 | 1 | 2 | 0 | 1500 | 17 | 17 | 710 | 2353 | +1643 | 1585..3338 | 3.32 | 1.10 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Drift (A/B/A) - steady state, sequential logins

| rep | mappers | user | conc | off cell before | off cell after | off p50 before | off p50 after | drift | 95% CI | drift % | on p50 | on - mean(off) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | perf-ctl-150 | 1 | 1 | 3 | 706 | 747 | +42 | -20..97 | +5.9% | 2456 | +1730 |
| 1 | 1500 | perf-match-few | 1 | 1 | 3 | 742 | 715 | -27 | -97..52 | -3.6% | 4039 | +3311 |
| 1 | 1500 | perf-match-many | 1 | 1 | 3 | 1010 | 1046 | +36 | -228..271 | +3.6% | 2684 | +1656 |
| 1 | 1500 | perf-nomatch | 1 | 1 | 3 | 710 | 686 | -24 | -84..35 | -3.3% | 2353 | +1655 |

- Same configuration measured before and after the toggle-on cell. Drift is what the system changed by without any change to the toggle.
- A toggle effect smaller than the drift is not evidence of a toggle effect.

### Toggle effect - concurrent logins, pool users

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | pool | 10 | 1 | 2 | 10 | 1490 | 200 | 200 | 815 | 2867 | +2052 | 2005..2148 | 3.52 | 1.38 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Drift (A/B/A) - concurrent logins, pool users

| rep | mappers | user | conc | off cell before | off cell after | off p50 before | off p50 after | drift | 95% CI | drift % | on p50 | on - mean(off) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | pool | 10 | 1 | 3 | 815 | 820 | +5 | -17..27 | +0.6% | 2867 | +2049 |

- Same configuration measured before and after the toggle-on cell. Drift is what the system changed by without any change to the toggle.
- A toggle effect smaller than the drift is not evidence of a toggle effect.

### Gateway access log - POST /login/ server time (s)

| rep | cell | mappers | toggle | pod | n | p50 | p95 | p99 | max | HTTP 5xx | harakiri lines |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | aap-gateway-9cd77b9cb-hnvvk | 174 | 0.78 | 0.99 | 1.36 | 1.38 | 0 | 0 |
| 1 | 1 | 1500 | off | aap-gateway-9cd77b9cb-pd2kh | 215 | 0.68 | 0.93 | 0.96 | 9.75 | 1 | 6 |
| 1 | 1 | 1500 | off | all 2 pods | 389 | 0.72 | 0.95 | 1.36 | 9.75 | 1 | 6 |
| 1 | 2 | 1500 | on | aap-gateway-9cd77b9cb-hnvvk | 5 | 4.51 | 4.55 | 4.55 | 4.55 | 0 | 0 |
| 1 | 2 | 1500 | on | aap-gateway-9cd77b9cb-pd2kh | 74 | 2.70 | 2.84 | 2.86 | 2.88 | 0 | 0 |
| 1 | 2 | 1500 | on | all 2 pods | 79 | 2.71 | 4.45 | 4.51 | 4.55 | 0 | 0 |
| 1 | 3 | 1500 | off | aap-gateway-9cd77b9cb-hnvvk | 177 | 0.78 | 0.93 | 1.31 | 10.32 | 2 | 12 |
| 1 | 3 | 1500 | off | aap-gateway-9cd77b9cb-pd2kh | 212 | 0.67 | 0.92 | 1.34 | 1.80 | 0 | 0 |
| 1 | 3 | 1500 | off | all 2 pods | 389 | 0.72 | 0.94 | 1.34 | 10.32 | 2 | 12 |

- One log file per gateway pod per cell. Requests killed by the gateway may have no access log line.

### Failed logins by outcome

| rep | cell | mappers | toggle | phase | conc | outcome | count |
|---:|---:|---:|---|---|---:|---|---:|
| 1 | 1 | 1500 | off | cold | 1 | http_503 | 1 |
| 1 | 2 | 1500 | on | cold | 1 | http_503 | 2 |
| 1 | 3 | 1500 | off | cold | 1 | http_503 | 2 |


