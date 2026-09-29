## Results - Environment A, run 2 (drift and cold start) - run run2-abatest-20260929-1458 (642 logins)

### Phase first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 1556 | 1556 | 1556 | 1556 | 1556 | 0.0% | 0.0% | 2948 |
| 1 | 1 | 1500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 1782 | 1782 | 1782 | 1782 | 1782 | 0.0% | 0.0% | 2925 |
| 1 | 1 | 1500 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 2634 | 2634 | 2634 | 2634 | 2634 | 0.0% | 0.0% | 3650 |
| 1 | 1 | 1500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 1508 | 1508 | 1508 | 1508 | 1508 | 0.0% | 0.0% | 2597 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 8718 | 8718 | 8718 | 8718 | 8718 | 100.0% | 0.0% | 9813 |
| 1 | 2 | 1500 | on | perf-match-few | 1 | 1 | 1 | 100.0% | 0 | 9634 | 9634 | 9634 | 9634 | - | 100.0% | 0.0% | - |
| 1 | 2 | 1500 | on | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 7964 | 7964 | 7964 | 7964 | 7964 | 100.0% | 0.0% | 9114 |
| 1 | 2 | 1500 | on | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 8670 | 8670 | 8670 | 8670 | 8670 | 100.0% | 0.0% | 9775 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 1911 | 1911 | 1911 | 1911 | 1911 | 0.0% | 0.0% | 2971 |
| 1 | 3 | 1500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 1666 | 1666 | 1666 | 1666 | 1666 | 0.0% | 0.0% | 2767 |
| 1 | 3 | 1500 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 2358 | 2358 | 2358 | 2358 | 2358 | 0.0% | 0.0% | 3393 |
| 1 | 3 | 1500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 1524 | 1524 | 1524 | 1524 | 1524 | 0.0% | 0.0% | 2995 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase cold - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-cold-01 | 1 | 5 | 4 | 80.0% | 0 | 9999 | 10656 | 10656 | 10656 | 5631 | 100.0% | 40.0% | 6765 |
| 1 | 2 | 1500 | on | perf-cold-02 | 1 | 5 | 5 | 100.0% | 0 | 9997 | 10076 | 10076 | 10076 | - | 100.0% | 40.0% | - |
| 1 | 3 | 1500 | off | perf-cold-03 | 1 | 5 | 4 | 80.0% | 0 | 10597 | 10688 | 10688 | 10688 | 6922 | 100.0% | 80.0% | 8421 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase steady - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 1576 | 1854 | 1889 | 1889 | 1576 | 0.0% | 0.0% | 2626 |
| 1 | 1 | 1500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 1535 | 1655 | 1656 | 1656 | 1535 | 0.0% | 0.0% | 2560 |
| 1 | 1 | 1500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 2518 | 2936 | 2954 | 2954 | 2518 | 0.0% | 0.0% | 3524 |
| 1 | 1 | 1500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 1420 | 1631 | 1675 | 1675 | 1420 | 0.0% | 0.0% | 2482 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 7346 | 9290 | 9464 | 9464 | 7346 | 100.0% | 0.0% | 8451 |
| 1 | 2 | 1500 | on | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 7047 | 7624 | 8110 | 8110 | 7047 | 100.0% | 0.0% | 8084 |
| 1 | 2 | 1500 | on | perf-match-many | 1 | 20 | 1 | 5.0% | 0 | 7269 | 8238 | 10048 | 10048 | 7262 | 100.0% | 5.0% | 8278 |
| 1 | 2 | 1500 | on | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 6984 | 8160 | 8183 | 8183 | 6984 | 100.0% | 0.0% | 8057 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 1553 | 1686 | 1830 | 1830 | 1553 | 0.0% | 0.0% | 2659 |
| 1 | 3 | 1500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 1547 | 1778 | 1800 | 1800 | 1547 | 0.0% | 0.0% | 2578 |
| 1 | 3 | 1500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 2392 | 3107 | 3138 | 3138 | 2392 | 0.0% | 0.0% | 3407 |
| 1 | 3 | 1500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 1436 | 1633 | 1874 | 1874 | 1436 | 0.0% | 0.0% | 2478 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.
- Raw phase: includes convergence and warm-up logins. See the steady-state table.

### Phase pool-first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | pool(25 users) | 1 | 25 | 0 | 0.0% | 0 | 1583 | 1762 | 1959 | 1959 | 1583 | 0.0% | 0.0% | 2636 |
| 1 | 2 | 1500 | on | pool(25 users) | 1 | 25 | 0 | 0.0% | 0 | 6713 | 7935 | 8047 | 8047 | 6713 | 100.0% | 0.0% | 7789 |
| 1 | 3 | 1500 | off | pool(25 users) | 1 | 25 | 0 | 0.0% | 0 | 1664 | 1828 | 1847 | 1847 | 1664 | 0.0% | 0.0% | 2676 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase concurrent - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | pool(25 users) | 10 | 100 | 0 | 0.0% | 0 | 2827 | 3889 | 4872 | 4992 | 2827 | 0.0% | 0.0% | 5928 |
| 1 | 2 | 1500 | on | pool(25 users) | 10 | 100 | 16 | 16.0% | 0 | 12073 | 19810 | 21774 | 21935 | 11147 | 100.0% | 76.0% | 19564 |
| 1 | 3 | 1500 | off | pool(25 users) | 10 | 100 | 0 | 0.0% | 0 | 2836 | 3956 | 4720 | 4740 | 2836 | 0.0% | 0.0% | 5671 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Steady state - login POST ms

| rep | cell | mappers | toggle | user | dropped | n | fail | fail% | no POST | p50 | p50 95% CI | p95 | p99 | max | p50 ok | >5s | >10s |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 1532 | 1487..1648 | 1854 | 1889 | 1889 | 1532 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 1525 | 1442..1550 | 1593 | 1656 | 1656 | 1525 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 2501 | 2326..2585 | 2936 | 2954 | 2954 | 2501 | 0.0% | 0.0% |
| 1 | 1 | 1500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 1456 | 1385..1519 | 1631 | 1675 | 1675 | 1456 | 0.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 7347 | 6828..7425 | 9290 | 9464 | 9464 | 7347 | 100.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 7079 | 6683..7472 | 7624 | 8110 | 8110 | 7079 | 100.0% | 0.0% |
| 1 | 2 | 1500 | on | perf-match-many | 3 | 17 | 1 | 5.9% | 0 | 7262 | 6801..7911 | 8238 | 10048 | 10048 | 7239 | 100.0% | 5.9% |
| 1 | 2 | 1500 | on | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 6951 | 6685..7367 | 8034 | 8160 | 8160 | 6951 | 100.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 1539 | 1520..1612 | 1633 | 1686 | 1686 | 1539 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 1524 | 1443..1582 | 1711 | 1778 | 1778 | 1524 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 2369 | 2322..2516 | 2740 | 3138 | 3138 | 2369 | 0.0% | 0.0% |
| 1 | 3 | 1500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 1422 | 1382..1501 | 1584 | 1633 | 1633 | 1422 | 0.0% | 0.0% |

- Steady state = logins after the first successful login of the user in the cell and the 2 logins following it ('dropped').
- Failed logins are included in p50/p95/p99/max. CI: bootstrap, 2000 resamples, seed 20260929.
- A login killed at the gateway time limit is recorded with the time at which it was killed, so values with failures are lower bounds.

### Convergence - attempts until the first successful login

| rep | cell | mappers | toggle | user | 'first' phase | attempts to first success | attempt POST ms | following POST ms |
|---:|---:|---:|---|---|---|---:|---|---|
| 1 | 1 | 1500 | off | perf-ctl-150 | 1556 | 1 | 1582 | 1718 1572 |
| 1 | 1 | 1500 | off | perf-match-few | 1782 | 1 | 1655 | 1625 1562 |
| 1 | 1 | 1500 | off | perf-match-many | 2634 | 1 | 2686 | 2592 2344 |
| 1 | 1 | 1500 | off | perf-nomatch | 1508 | 1 | 1313 | 1422 1325 |
| 1 | 2 | 1500 | on | perf-ctl-150 | 8718 | 1 | 7104 | 7610 6881 |
| 1 | 2 | 1500 | on | perf-match-few | 9634(http_503) | 1 | 7146 | 6808 6595 |
| 1 | 2 | 1500 | on | perf-match-many | 7964 | 1 | 7419 | 7040 7276 |
| 1 | 2 | 1500 | on | perf-nomatch | 8670 | 1 | 7591 | 6117 8183 |
| 1 | 3 | 1500 | off | perf-ctl-150 | 1911 | 1 | 1575 | 1561 1830 |
| 1 | 3 | 1500 | off | perf-match-few | 1666 | 1 | 1800 | 1770 1596 |
| 1 | 3 | 1500 | off | perf-match-many | 2358 | 1 | 3107 | 2425 2710 |
| 1 | 3 | 1500 | off | perf-nomatch | 1524 | 1 | 1519 | 1361 1874 |
| 1 | 1 | 1500 | off | perf-cold-01 (cold) | - | 5 | 10434(http_503) 10656(http_503) 9172(http_503) 9999(http_503) 5631 | - |
| 1 | 2 | 1500 | on | perf-cold-02 (cold) | - | never (5 tried) | 9640(http_503) 9791(http_503) 10066(http_503) 9997(http_503) 10076(http_503) | - |
| 1 | 3 | 1500 | off | perf-cold-03 (cold) | - | 5 | 10602(http_503) 10240(http_503) 10597(http_503) 10688(http_503) 6922 | - |

- Attempts are counted inside the steady phase (inside the cold phase for cold users); the 'first' phase login precedes them.
- 'following' = the warm-up logins dropped from steady state; for cold users, every login after the first success.

### Toggle effect - steady state, sequential logins

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | perf-ctl-150 | 1 | 1 | 2 | 0 | 1500 | 17 | 17 | 1532 | 7347 | +5815 | 5297..5894 | 4.80 | 3.88 |
| 1 | 1500 | perf-match-few | 1 | 1 | 2 | 5 | 1495 | 17 | 17 | 1525 | 7079 | +5554 | 5157..5956 | 4.64 | 3.72 |
| 1 | 1500 | perf-match-many | 1 | 1 | 2 | 150 | 1350 | 17 | 17 | 2501 | 7262 | +4762 | 4407..5467 | 2.90 | 3.53 |
| 1 | 1500 | perf-nomatch | 1 | 1 | 2 | 0 | 1500 | 17 | 17 | 1456 | 6951 | +5495 | 5201..5883 | 4.77 | 3.66 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Drift (A/B/A) - steady state, sequential logins

| rep | mappers | user | conc | off cell before | off cell after | off p50 before | off p50 after | drift | 95% CI | drift % | on p50 | on - mean(off) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | perf-ctl-150 | 1 | 1 | 3 | 1532 | 1539 | +7 | -106..81 | +0.5% | 7347 | +5811 |
| 1 | 1500 | perf-match-few | 1 | 1 | 3 | 1525 | 1524 | -1 | -92..92 | -0.1% | 7079 | +5554 |
| 1 | 1500 | perf-match-many | 1 | 1 | 3 | 2501 | 2369 | -132 | -237..56 | -5.3% | 7262 | +4828 |
| 1 | 1500 | perf-nomatch | 1 | 1 | 3 | 1456 | 1422 | -35 | -104..74 | -2.4% | 6951 | +5512 |

- Same configuration measured before and after the toggle-on cell. Drift is what the system changed by without any change to the toggle.
- A toggle effect smaller than the drift is not evidence of a toggle effect.

### Toggle effect - concurrent logins, pool users

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | pool | 10 | 1 | 2 | 10 | 1490 | 100 | 100 | 2827 | 12073 | +9246 | 8063..10679 | 4.27 | 6.21 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Drift (A/B/A) - concurrent logins, pool users

| rep | mappers | user | conc | off cell before | off cell after | off p50 before | off p50 after | drift | 95% CI | drift % | on p50 | on - mean(off) |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1500 | pool | 10 | 1 | 3 | 2827 | 2836 | +9 | -162..209 | +0.3% | 12073 | +9241 |

- Same configuration measured before and after the toggle-on cell. Drift is what the system changed by without any change to the toggle.
- A toggle effect smaller than the drift is not evidence of a toggle effect.

### Gateway access log - POST /login/ server time (s)

| rep | cell | mappers | toggle | pod | n | p50 | p95 | p99 | max | HTTP 5xx | harakiri lines |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1500 | off | aap-26-gateway-7d68667f8-w2pcj | 0 | - | - | - | - | 0 | 0 |
| 1 | 2 | 1500 | on | aap-26-gateway-7d68667f8-w2pcj | 6 | 9.62 | 11.14 | 11.14 | 11.14 | 2 | 12 |
| 1 | 3 | 1500 | off | aap-26-gateway-7d68667f8-w2pcj | 214 | 2.04 | 2.96 | 10.35 | 10.59 | 4 | 24 |

- One log file per gateway pod per cell. Requests killed by the gateway may have no access log line.

### Failed logins by outcome

| rep | cell | mappers | toggle | phase | conc | outcome | count |
|---:|---:|---:|---|---|---:|---|---:|
| 1 | 1 | 1500 | off | cold | 1 | http_503 | 4 |
| 1 | 2 | 1500 | on | cold | 1 | http_503 | 5 |
| 1 | 2 | 1500 | on | concurrent | 10 | http_503 | 14 |
| 1 | 2 | 1500 | on | concurrent | 10 | http_504 | 2 |
| 1 | 2 | 1500 | on | first | 1 | http_503 | 1 |
| 1 | 2 | 1500 | on | steady | 1 | http_503 | 1 |
| 1 | 3 | 1500 | off | cold | 1 | http_503 | 4 |


