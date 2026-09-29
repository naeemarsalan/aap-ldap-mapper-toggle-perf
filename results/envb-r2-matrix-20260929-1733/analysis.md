## Results - Environment B, 2 gateway replicas - run envb-r2-matrix-20260929-1733 (4704 logins)

### Phase first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 651 | 651 | 651 | 651 | 651 | 0.0% | 0.0% | 1080 |
| 1 | 1 | 1 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 685 | 685 | 685 | 685 | 685 | 0.0% | 0.0% | 1134 |
| 1 | 1 | 1 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 641 | 641 | 641 | 641 | 641 | 0.0% | 0.0% | 1077 |
| 1 | 1 | 1 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 745 | 745 | 745 | 745 | 745 | 0.0% | 0.0% | 1234 |
| 1 | 2 | 1 | on | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 628 | 628 | 628 | 628 | 628 | 0.0% | 0.0% | 1052 |
| 1 | 2 | 1 | on | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 618 | 618 | 618 | 618 | 618 | 0.0% | 0.0% | 1013 |
| 1 | 2 | 1 | on | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 637 | 637 | 637 | 637 | 637 | 0.0% | 0.0% | 1054 |
| 1 | 2 | 1 | on | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 601 | 601 | 601 | 601 | 601 | 0.0% | 0.0% | 1003 |
| 1 | 3 | 500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 796 | 796 | 796 | 796 | 796 | 0.0% | 0.0% | 1256 |
| 1 | 3 | 500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 928 | 928 | 928 | 928 | 928 | 0.0% | 0.0% | 2300 |
| 1 | 3 | 500 | off | perf-match-many | 1 | 1 | 1 | 100.0% | 0 | 10184 | 10184 | 10184 | 10184 | - | 100.0% | 100.0% | - |
| 1 | 3 | 500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 737 | 737 | 737 | 737 | 737 | 0.0% | 0.0% | 1222 |
| 1 | 4 | 500 | on | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 1849 | 1849 | 1849 | 1849 | 1849 | 0.0% | 0.0% | 2278 |
| 1 | 4 | 500 | on | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 1970 | 1970 | 1970 | 1970 | 1970 | 0.0% | 0.0% | 2394 |
| 1 | 4 | 500 | on | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 1334 | 1334 | 1334 | 1334 | 1334 | 0.0% | 0.0% | 1748 |
| 1 | 4 | 500 | on | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 1179 | 1179 | 1179 | 1179 | 1179 | 0.0% | 0.0% | 1582 |
| 1 | 5 | 1500 | off | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 809 | 809 | 809 | 809 | 809 | 0.0% | 0.0% | 1246 |
| 1 | 5 | 1500 | off | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 816 | 816 | 816 | 816 | 816 | 0.0% | 0.0% | 1309 |
| 1 | 5 | 1500 | off | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 1263 | 1263 | 1263 | 1263 | 1263 | 0.0% | 0.0% | 1685 |
| 1 | 5 | 1500 | off | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 651 | 651 | 651 | 651 | 651 | 0.0% | 0.0% | 1107 |
| 1 | 6 | 1500 | on | perf-ctl-150 | 1 | 1 | 0 | 0.0% | 0 | 4266 | 4266 | 4266 | 4266 | 4266 | 0.0% | 0.0% | 4718 |
| 1 | 6 | 1500 | on | perf-match-few | 1 | 1 | 0 | 0.0% | 0 | 4210 | 4210 | 4210 | 4210 | 4210 | 0.0% | 0.0% | 4674 |
| 1 | 6 | 1500 | on | perf-match-many | 1 | 1 | 0 | 0.0% | 0 | 2486 | 2486 | 2486 | 2486 | 2486 | 0.0% | 0.0% | 2913 |
| 1 | 6 | 1500 | on | perf-nomatch | 1 | 1 | 0 | 0.0% | 0 | 4059 | 4059 | 4059 | 4059 | 4059 | 0.0% | 0.0% | 4490 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase steady - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 710 | 743 | 837 | 837 | 710 | 0.0% | 0.0% | 1138 |
| 1 | 1 | 1 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 625 | 724 | 923 | 923 | 625 | 0.0% | 0.0% | 1034 |
| 1 | 1 | 1 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 727 | 746 | 759 | 759 | 727 | 0.0% | 0.0% | 1149 |
| 1 | 1 | 1 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 606 | 694 | 696 | 696 | 606 | 0.0% | 0.0% | 1026 |
| 1 | 2 | 1 | on | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 719 | 887 | 909 | 909 | 719 | 0.0% | 0.0% | 1116 |
| 1 | 2 | 1 | on | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 693 | 798 | 813 | 813 | 693 | 0.0% | 0.0% | 1103 |
| 1 | 2 | 1 | on | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 689 | 749 | 837 | 837 | 689 | 0.0% | 0.0% | 1097 |
| 1 | 2 | 1 | on | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 669 | 698 | 716 | 716 | 669 | 0.0% | 0.0% | 1103 |
| 1 | 3 | 500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 724 | 825 | 882 | 882 | 724 | 0.0% | 0.0% | 1160 |
| 1 | 3 | 500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 731 | 757 | 826 | 826 | 731 | 0.0% | 0.0% | 1150 |
| 1 | 3 | 500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 1260 | 1471 | 5590 | 5590 | 1260 | 5.0% | 0.0% | 1720 |
| 1 | 3 | 500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 636 | 809 | 832 | 832 | 636 | 0.0% | 0.0% | 1030 |
| 1 | 4 | 500 | on | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 1386 | 1987 | 2018 | 2018 | 1386 | 0.0% | 0.0% | 1816 |
| 1 | 4 | 500 | on | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 1228 | 1984 | 1991 | 1991 | 1228 | 0.0% | 0.0% | 1652 |
| 1 | 4 | 500 | on | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 1745 | 2244 | 2253 | 2253 | 1745 | 0.0% | 0.0% | 2179 |
| 1 | 4 | 500 | on | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 1196 | 1932 | 2019 | 2019 | 1196 | 0.0% | 0.0% | 1605 |
| 1 | 5 | 1500 | off | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 745 | 912 | 925 | 925 | 745 | 0.0% | 0.0% | 1157 |
| 1 | 5 | 1500 | off | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 718 | 839 | 904 | 904 | 718 | 0.0% | 0.0% | 1129 |
| 1 | 5 | 1500 | off | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 1044 | 1389 | 1427 | 1427 | 1044 | 0.0% | 0.0% | 1441 |
| 1 | 5 | 1500 | off | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 698 | 786 | 823 | 823 | 698 | 0.0% | 0.0% | 1120 |
| 1 | 6 | 1500 | on | perf-ctl-150 | 1 | 20 | 0 | 0.0% | 0 | 2474 | 4323 | 4380 | 4380 | 2474 | 0.0% | 0.0% | 2878 |
| 1 | 6 | 1500 | on | perf-match-few | 1 | 20 | 0 | 0.0% | 0 | 2477 | 4273 | 4277 | 4277 | 2477 | 0.0% | 0.0% | 2885 |
| 1 | 6 | 1500 | on | perf-match-many | 1 | 20 | 0 | 0.0% | 0 | 2603 | 4522 | 4530 | 4530 | 2603 | 0.0% | 0.0% | 3013 |
| 1 | 6 | 1500 | on | perf-nomatch | 1 | 20 | 0 | 0.0% | 0 | 2417 | 4190 | 4337 | 4337 | 2417 | 0.0% | 0.0% | 2828 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.
- Raw phase: includes convergence and warm-up logins. See the steady-state table.

### Phase pool-first - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 635 | 736 | 809 | 863 | 635 | 0.0% | 0.0% | 1107 |
| 1 | 2 | 1 | on | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 666 | 790 | 806 | 926 | 666 | 0.0% | 0.0% | 1092 |
| 1 | 3 | 500 | off | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 743 | 1370 | 1804 | 1980 | 743 | 0.0% | 0.0% | 1207 |
| 1 | 4 | 500 | on | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 1229 | 1899 | 1936 | 1976 | 1229 | 0.0% | 0.0% | 1666 |
| 1 | 5 | 1500 | off | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 1129 | 1814 | 1853 | 1920 | 1129 | 0.0% | 0.0% | 2009 |
| 1 | 6 | 1500 | on | pool(100 users) | 1 | 100 | 0 | 0.0% | 0 | 2483 | 4263 | 4325 | 4385 | 2483 | 0.0% | 0.0% | 2961 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Phase concurrent - all attempts

| rep | cell | mappers | toggle | user | conc | n | fail | fail% | no POST | p50 | p95 | p99 | max | p50 ok | >5s | >10s | landing p50 |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 714 | 824 | 938 | 1298 | 714 | 0.0% | 0.0% | 1269 |
| 1 | 1 | 1 | off | pool(100 users) | 25 | 200 | 0 | 0.0% | 0 | 888 | 1663 | 2269 | 2413 | 888 | 0.0% | 0.0% | 2027 |
| 1 | 1 | 1 | off | pool(100 users) | 50 | 200 | 6 | 3.0% | 6 | 9122 | 20154 | 30447 | 30479 | 9122 | 68.0% | 47.4% | 13118 |
| 1 | 2 | 1 | on | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 732 | 882 | 995 | 1217 | 732 | 0.0% | 0.0% | 1305 |
| 1 | 2 | 1 | on | pool(100 users) | 25 | 200 | 0 | 0.0% | 0 | 926 | 1928 | 2256 | 2354 | 926 | 0.0% | 0.0% | 2166 |
| 1 | 2 | 1 | on | pool(100 users) | 50 | 200 | 3 | 1.5% | 3 | 3368 | 25798 | 31296 | 31307 | 3368 | 47.2% | 46.7% | 22042 |
| 1 | 3 | 500 | off | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 723 | 874 | 976 | 1333 | 723 | 0.0% | 0.0% | 1286 |
| 1 | 3 | 500 | off | pool(100 users) | 25 | 200 | 0 | 0.0% | 0 | 930 | 1939 | 2391 | 2624 | 930 | 0.0% | 0.0% | 2081 |
| 1 | 3 | 500 | off | pool(100 users) | 50 | 200 | 1 | 0.5% | 1 | 2106 | 15301 | 16073 | 16087 | 2106 | 36.7% | 25.6% | 5301 |
| 1 | 4 | 500 | on | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 1468 | 2222 | 2566 | 3526 | 1468 | 0.0% | 0.0% | 2093 |
| 1 | 4 | 500 | on | pool(100 users) | 25 | 200 | 0 | 0.0% | 0 | 2254 | 4316 | 5270 | 6191 | 2254 | 1.5% | 0.0% | 3633 |
| 1 | 4 | 500 | on | pool(100 users) | 50 | 200 | 2 | 1.0% | 2 | 6567 | 23865 | 29236 | 32825 | 6567 | 52.0% | 37.9% | 23298 |
| 1 | 5 | 1500 | off | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 828 | 988 | 1308 | 1430 | 828 | 0.0% | 0.0% | 1403 |
| 1 | 5 | 1500 | off | pool(100 users) | 25 | 200 | 0 | 0.0% | 0 | 969 | 2103 | 2727 | 2782 | 969 | 0.0% | 0.0% | 2495 |
| 1 | 5 | 1500 | off | pool(100 users) | 50 | 200 | 14 | 7.0% | 14 | 5721 | 22100 | 40550 | 47138 | 5721 | 51.1% | 33.9% | 26985 |
| 1 | 6 | 1500 | on | pool(100 users) | 10 | 200 | 0 | 0.0% | 0 | 2961 | 5052 | 6294 | 7876 | 2961 | 6.5% | 0.0% | 3543 |
| 1 | 6 | 1500 | on | pool(100 users) | 25 | 200 | 1 | 0.5% | 1 | 4913 | 9303 | 9557 | 14219 | 4913 | 46.7% | 0.5% | 6908 |
| 1 | 6 | 1500 | on | pool(100 users) | 50 | 200 | 36 | 18.0% | 32 | 12296 | 44995 | 45007 | 48083 | 12270 | 79.8% | 60.7% | 19061 |

- Login POST ms over all attempts that returned a response, failed ones included. 'p50 ok' and 'landing p50' are successful logins only.

### Steady state - login POST ms

| rep | cell | mappers | toggle | user | dropped | n | fail | fail% | no POST | p50 | p50 95% CI | p95 | p99 | max | p50 ok | >5s | >10s |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 716 | 630..730 | 743 | 837 | 837 | 716 | 0.0% | 0.0% |
| 1 | 1 | 1 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 625 | 614..707 | 713 | 923 | 923 | 625 | 0.0% | 0.0% |
| 1 | 1 | 1 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 728 | 643..734 | 746 | 759 | 759 | 728 | 0.0% | 0.0% |
| 1 | 1 | 1 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 605 | 597..686 | 694 | 696 | 696 | 605 | 0.0% | 0.0% |
| 1 | 2 | 1 | on | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 721 | 637..757 | 847 | 909 | 909 | 721 | 0.0% | 0.0% |
| 1 | 2 | 1 | on | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 693 | 615..697 | 796 | 813 | 813 | 693 | 0.0% | 0.0% |
| 1 | 2 | 1 | on | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 706 | 630..719 | 749 | 837 | 837 | 706 | 0.0% | 0.0% |
| 1 | 2 | 1 | on | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 637 | 612..682 | 696 | 697 | 697 | 637 | 0.0% | 0.0% |
| 1 | 3 | 500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 723 | 648..758 | 825 | 882 | 882 | 723 | 0.0% | 0.0% |
| 1 | 3 | 500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 731 | 641..739 | 757 | 826 | 826 | 731 | 0.0% | 0.0% |
| 1 | 3 | 500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 1258 | 993..1287 | 1356 | 1372 | 1372 | 1258 | 0.0% | 0.0% |
| 1 | 3 | 500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 642 | 612..702 | 809 | 832 | 832 | 642 | 0.0% | 0.0% |
| 1 | 4 | 500 | on | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 1353 | 1233..1914 | 1987 | 2018 | 2018 | 1353 | 0.0% | 0.0% |
| 1 | 4 | 500 | on | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 1218 | 1190..1874 | 1984 | 1991 | 1991 | 1218 | 0.0% | 0.0% |
| 1 | 4 | 500 | on | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 1440 | 1312..2131 | 2244 | 2253 | 2253 | 1440 | 0.0% | 0.0% |
| 1 | 4 | 500 | on | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 1195 | 1177..1272 | 1932 | 2019 | 2019 | 1195 | 0.0% | 0.0% |
| 1 | 5 | 1500 | off | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 746 | 733..806 | 912 | 925 | 925 | 746 | 0.0% | 0.0% |
| 1 | 5 | 1500 | off | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 716 | 672..731 | 786 | 904 | 904 | 716 | 0.0% | 0.0% |
| 1 | 5 | 1500 | off | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 1064 | 961..1262 | 1389 | 1427 | 1427 | 1064 | 0.0% | 0.0% |
| 1 | 5 | 1500 | off | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 696 | 684..747 | 786 | 823 | 823 | 696 | 0.0% | 0.0% |
| 1 | 6 | 1500 | on | perf-ctl-150 | 3 | 17 | 0 | 0.0% | 0 | 2457 | 2422..4246 | 4323 | 4380 | 4380 | 2457 | 0.0% | 0.0% |
| 1 | 6 | 1500 | on | perf-match-few | 3 | 17 | 0 | 0.0% | 0 | 2547 | 2358..4173 | 4273 | 4277 | 4277 | 2547 | 0.0% | 0.0% |
| 1 | 6 | 1500 | on | perf-match-many | 3 | 17 | 0 | 0.0% | 0 | 2615 | 2562..4435 | 4522 | 4530 | 4530 | 2615 | 0.0% | 0.0% |
| 1 | 6 | 1500 | on | perf-nomatch | 3 | 17 | 0 | 0.0% | 0 | 2410 | 2346..4168 | 4190 | 4337 | 4337 | 2410 | 0.0% | 0.0% |

- Steady state = logins after the first successful login of the user in the cell and the 2 logins following it ('dropped').
- Failed logins are included in p50/p95/p99/max. CI: bootstrap, 2000 resamples, seed 20260929.
- A login killed at the gateway time limit is recorded with the time at which it was killed, so values with failures are lower bounds.

### Convergence - attempts until the first successful login

| rep | cell | mappers | toggle | user | 'first' phase | attempts to first success | attempt POST ms | following POST ms |
|---:|---:|---:|---|---|---|---:|---|---|
| 1 | 1 | 1 | off | perf-ctl-150 | 651 | 1 | 708 | 625 614 |
| 1 | 1 | 1 | off | perf-match-few | 685 | 1 | 615 | 605 724 |
| 1 | 1 | 1 | off | perf-match-many | 641 | 1 | 627 | 622 633 |
| 1 | 1 | 1 | off | perf-nomatch | 745 | 1 | 690 | 691 685 |
| 1 | 2 | 1 | on | perf-ctl-150 | 628 | 1 | 628 | 887 634 |
| 1 | 2 | 1 | on | perf-match-few | 618 | 1 | 712 | 619 798 |
| 1 | 2 | 1 | on | perf-match-many | 637 | 1 | 672 | 714 642 |
| 1 | 2 | 1 | on | perf-nomatch | 601 | 1 | 671 | 698 716 |
| 1 | 3 | 500 | off | perf-ctl-150 | 796 | 1 | 737 | 776 643 |
| 1 | 3 | 500 | off | perf-match-few | 928 | 1 | 751 | 626 641 |
| 1 | 3 | 500 | off | perf-match-many | 10184(http_503) | 1 | 5590 | 1471 1044 |
| 1 | 3 | 500 | off | perf-nomatch | 737 | 1 | 626 | 630 737 |
| 1 | 4 | 500 | on | perf-ctl-150 | 1849 | 1 | 1275 | 1977 1867 |
| 1 | 4 | 500 | on | perf-match-few | 1970 | 1 | 1189 | 1850 1984 |
| 1 | 4 | 500 | on | perf-match-many | 1334 | 1 | 2050 | 2052 1325 |
| 1 | 4 | 500 | on | perf-nomatch | 1179 | 1 | 1848 | 1811 1831 |
| 1 | 5 | 1500 | off | perf-ctl-150 | 809 | 1 | 741 | 689 750 |
| 1 | 5 | 1500 | off | perf-match-few | 816 | 1 | 721 | 660 839 |
| 1 | 5 | 1500 | off | perf-match-many | 1263 | 1 | 952 | 961 1259 |
| 1 | 5 | 1500 | off | perf-nomatch | 651 | 1 | 776 | 703 649 |
| 1 | 6 | 1500 | on | perf-ctl-150 | 4266 | 1 | 4297 | 2442 2492 |
| 1 | 6 | 1500 | on | perf-match-few | 4210 | 1 | 4195 | 2356 2348 |
| 1 | 6 | 1500 | on | perf-match-many | 2486 | 1 | 4485 | 2557 2542 |
| 1 | 6 | 1500 | on | perf-nomatch | 4059 | 1 | 4155 | 4089 4154 |

- Attempts are counted inside the steady phase (inside the cold phase for cold users); the 'first' phase login precedes them.
- 'following' = the warm-up logins dropped from steady state; for cold users, every login after the first success.

### Toggle effect - steady state, sequential logins

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | perf-ctl-150 | 1 | 1 | 2 | 0 | 1 | 17 | 17 | 716 | 721 | +5 | -87..94 | 1.01 | 5.30 |
| 1 | 1 | perf-match-few | 1 | 1 | 2 | 1 | 0 | 17 | 17 | 625 | 693 | +68 | -24..79 | 1.11 | - |
| 1 | 1 | perf-match-many | 1 | 1 | 2 | 1 | 0 | 17 | 17 | 728 | 706 | -22 | -100..-2 | 0.97 | - |
| 1 | 1 | perf-nomatch | 1 | 1 | 2 | 0 | 1 | 17 | 17 | 605 | 637 | +32 | -20..83 | 1.05 | 32.10 |
| 1 | 500 | perf-ctl-150 | 1 | 3 | 4 | 0 | 500 | 17 | 17 | 723 | 1353 | +630 | 509..1223 | 1.87 | 1.26 |
| 1 | 500 | perf-match-few | 1 | 3 | 4 | 5 | 495 | 17 | 17 | 731 | 1218 | +487 | 456..1143 | 1.67 | 0.98 |
| 1 | 500 | perf-match-many | 1 | 3 | 4 | 150 | 350 | 17 | 17 | 1258 | 1440 | +182 | 54..878 | 1.14 | 0.52 |
| 1 | 500 | perf-nomatch | 1 | 3 | 4 | 0 | 500 | 17 | 17 | 642 | 1195 | +553 | 487..584 | 1.86 | 1.11 |
| 1 | 1500 | perf-ctl-150 | 1 | 5 | 6 | 0 | 1500 | 17 | 17 | 746 | 2457 | +1712 | 1652..3500 | 3.29 | 1.14 |
| 1 | 1500 | perf-match-few | 1 | 5 | 6 | 5 | 1495 | 17 | 17 | 716 | 2547 | +1831 | 1650..3483 | 3.56 | 1.22 |
| 1 | 1500 | perf-match-many | 1 | 5 | 6 | 150 | 1350 | 17 | 17 | 1064 | 2615 | +1552 | 1321..3429 | 2.46 | 1.15 |
| 1 | 1500 | perf-nomatch | 1 | 5 | 6 | 0 | 1500 | 17 | 17 | 696 | 2410 | +1714 | 1630..3454 | 3.46 | 1.14 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Toggle effect - concurrent logins, pool users

| rep | mappers | user | conc | off cell | on cell | matched | non-matching | n off | n on | off p50 | on p50 | on - off | 95% CI | ratio | ms per non-matching mapper |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | pool | 10 | 1 | 2 | 1 | 0 | 200 | 200 | 714 | 732 | +18 | -47..44 | 1.03 | - |
| 1 | 1 | pool | 25 | 1 | 2 | 1 | 0 | 200 | 200 | 888 | 926 | +38 | -18..96 | 1.04 | - |
| 1 | 1 | pool | 50 | 1 | 2 | 1 | 0 | 194 | 197 | 9122 | 3368 | -5753 | -7784..6135 | 0.37 | - |
| 1 | 500 | pool | 10 | 3 | 4 | 10 | 490 | 200 | 200 | 723 | 1468 | +746 | 683..1242 | 2.03 | 1.52 |
| 1 | 500 | pool | 25 | 3 | 4 | 10 | 490 | 200 | 200 | 930 | 2254 | +1324 | 1220..1497 | 2.42 | 2.70 |
| 1 | 500 | pool | 50 | 3 | 4 | 10 | 490 | 199 | 198 | 2106 | 6567 | +4460 | 1200..6757 | 3.12 | 9.10 |
| 1 | 1500 | pool | 10 | 5 | 6 | 10 | 1490 | 200 | 200 | 828 | 2961 | +2133 | 2032..3049 | 3.58 | 1.43 |
| 1 | 1500 | pool | 25 | 5 | 6 | 10 | 1490 | 200 | 199 | 969 | 4913 | +3944 | 3569..4234 | 5.07 | 2.65 |
| 1 | 1500 | pool | 50 | 5 | 6 | 10 | 1490 | 186 | 168 | 5721 | 12296 | +6576 | 3820..11271 | 2.15 | 4.41 |

- Medians of login POST ms over all attempts with a response. 'off' is the closest toggle-off cell of the same scale before the toggle-on cell, or after it when none ran before.
- CI: bootstrap of the difference of medians. An interval that contains 0 means no toggle effect was shown.
- non-matching = mappers - matched; ms per non-matching mapper = (on p50 - off p50) / non-matching.

### Gateway access log - POST /login/ server time (s)

| rep | cell | mappers | toggle | pod | n | p50 | p95 | p99 | max | HTTP 5xx | harakiri lines |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | off | aap-gateway-9cd77b9cb-hnvvk | 342 | 0.68 | 1.74 | 2.37 | 2.51 | 0 | 0 |
| 1 | 1 | 1 | off | aap-gateway-9cd77b9cb-pd2kh | 436 | 0.59 | 1.77 | 2.54 | 2.64 | 0 | 0 |
| 1 | 1 | 1 | off | all 2 pods | 778 | 0.66 | 1.75 | 2.48 | 2.64 | 0 | 0 |
| 1 | 2 | 1 | on | aap-gateway-9cd77b9cb-hnvvk | 347 | 0.75 | 1.72 | 2.77 | 2.89 | 0 | 0 |
| 1 | 2 | 1 | on | aap-gateway-9cd77b9cb-pd2kh | 434 | 0.60 | 1.63 | 2.53 | 3.02 | 0 | 0 |
| 1 | 2 | 1 | on | all 2 pods | 781 | 0.69 | 1.71 | 2.71 | 3.02 | 0 | 0 |
| 1 | 3 | 500 | off | aap-gateway-9cd77b9cb-hnvvk | 347 | 0.75 | 1.78 | 2.89 | 10.12 | 1 | 6 |
| 1 | 3 | 500 | off | aap-gateway-9cd77b9cb-pd2kh | 436 | 0.63 | 1.33 | 2.00 | 5.53 | 0 | 0 |
| 1 | 3 | 500 | off | all 2 pods | 783 | 0.70 | 1.60 | 2.41 | 10.12 | 1 | 6 |
| 1 | 4 | 500 | on | aap-gateway-9cd77b9cb-hnvvk | 9 | 2.01 | 2.03 | 2.03 | 2.03 | 0 | 0 |
| 1 | 4 | 500 | on | aap-gateway-9cd77b9cb-pd2kh | 167 | 1.43 | 3.95 | 5.37 | 5.46 | 0 | 0 |
| 1 | 4 | 500 | on | all 2 pods | 176 | 1.44 | 3.85 | 5.37 | 5.46 | 0 | 0 |
| 1 | 5 | 1500 | off | aap-gateway-9cd77b9cb-hnvvk | 353 | 0.85 | 1.80 | 2.51 | 2.73 | 0 | 0 |
| 1 | 5 | 1500 | off | aap-gateway-9cd77b9cb-pd2kh | 417 | 0.72 | 1.60 | 2.23 | 2.49 | 0 | 0 |
| 1 | 5 | 1500 | off | all 2 pods | 770 | 0.80 | 1.75 | 2.35 | 2.73 | 0 | 0 |
| 1 | 6 | 1500 | on | aap-gateway-9cd77b9cb-hnvvk | 32 | 7.12 | 15.00 | 15.00 | 15.00 | 4 | 0 |
| 1 | 6 | 1500 | on | aap-gateway-9cd77b9cb-pd2kh | 16 | 2.96 | 3.33 | 4.33 | 4.33 | 0 | 0 |
| 1 | 6 | 1500 | on | all 2 pods | 48 | 4.97 | 15.00 | 15.00 | 15.00 | 4 | 0 |

- One log file per gateway pod per cell. Requests killed by the gateway may have no access log line.

### Failed logins by outcome

| rep | cell | mappers | toggle | phase | conc | outcome | count |
|---:|---:|---:|---|---|---:|---|---:|
| 1 | 1 | 1 | off | concurrent | 50 | error | 6 |
| 1 | 2 | 1 | on | concurrent | 50 | error | 3 |
| 1 | 3 | 500 | off | concurrent | 50 | error | 1 |
| 1 | 3 | 500 | off | first | 1 | http_503 | 1 |
| 1 | 4 | 500 | on | concurrent | 50 | error | 2 |
| 1 | 5 | 1500 | off | concurrent | 50 | error | 14 |
| 1 | 6 | 1500 | on | concurrent | 25 | error | 1 |
| 1 | 6 | 1500 | on | concurrent | 50 | error | 32 |
| 1 | 6 | 1500 | on | concurrent | 50 | http_503 | 3 |
| 1 | 6 | 1500 | on | concurrent | 50 | http_504 | 1 |


