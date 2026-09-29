# Environment B — AWS, managed database

A larger, dedicated environment on AWS with a managed database. Same AAP
build, same test, same load-generator software as Environment A.

## Infrastructure

| Layer | Detail |
|---|---|
| Platform | OpenShift 4.20.27 on AWS, installer-provisioned, us-east-2, three availability zones |
| Nodes | 3 control plane m6i.xlarge (4 vCPU / 16 GB); 3 workers m6i.2xlarge (8 vCPU / 32 GB), one per zone, dedicated to this test |
| AAP | 2.6, operator `aap-operator.v2.6.0-0.1789677985` (same build as Environment A), controller 4.7.17, gateway 2.6.20260923, django-ansible-base 2.7.0 |
| Gateway | **2 pods**, fixed. `api` container: request 2 CPU / 2 Gi, memory limit 4 Gi, no CPU limit |
| Gateway app server | uWSGI, **5 worker processes** per pod (not configurable), **`harakiri = 10`**, nginx `uwsgi_read_timeout 15s`: operator defaults, identical to Environment A |
| Gateway database | Amazon RDS for PostgreSQL 15.18, db.m6i.2xlarge, Multi-AZ, gp3 200 GB. `max_connections` 3,452, `shared_buffers` 7.7 GB. 0.2 to 0.8 ms per statement from the gateway, depending on the gateway pod's zone; 13 ms per new connection |
| Other components | Controller, EDA and hub enabled; hub on S3. Redis in cluster mode, 6 pods |
| LDAP | FreeIPA 4.12.2 (same version as Environment A) on c6i.4xlarge (16 vCPU), same VPC, plain LDAP. 1,656 groups. Search limits raised to 5,000 entries / 10 s (Environment A: 100 / 2 s) |
| Load generator | c6i.4xlarge (16 vCPU / 32 GB) in the same VPC, Playwright 1.55 Chromium 140 in podman: same image definition as Environment A |
| Network | Load generator → internet-facing classic load balancer → 2 router pods → gateway. About 50 ms for a health check |
| Autoscaling | None. See *Autoscaling* below |

Differences from Environment A that are **not** hardware: two gateway pods
instead of one; a pool of 100 concurrency users instead of 25; raised LDAP
search limits; the authenticator is the only LDAP authenticator on the
platform.

## Results — Environment B

Run `envb-r2-matrix-20260929-1733`: 4,704 browser logins, 2 gateway pods. One run per cell.
Full tables in [`results/envb-r2-matrix-20260929-1733/analysis.md`](../results/envb-r2-matrix-20260929-1733/analysis.md).

Login POST time in milliseconds. Sequential logins, steady state, 17 logins
per row. No login failed in steady state.

| Mappers | Toggle | User | Median | 95% CI of median | p95 | Max | Failed |
|---|---|---|---|---|---|---|---|
| 1 | off | 5 groups | 625 | 614–707 | 713 | 923 | 0 |
| 1 | off | 150 groups | 728 | 643–734 | 746 | 759 | 0 |
| 1 | off | no match | 605 | 597–686 | 694 | 696 | 0 |
| 1 | off | control: 150 LDAP groups, none mapped | 716 | 630–730 | 743 | 837 | 0 |
| 1 | on | 5 groups | 693 | 615–697 | 796 | 813 | 0 |
| 1 | on | 150 groups | 706 | 630–719 | 749 | 837 | 0 |
| 1 | on | no match | 637 | 612–682 | 696 | 697 | 0 |
| 1 | on | control: 150 LDAP groups, none mapped | 721 | 637–757 | 847 | 909 | 0 |
| 500 | off | 5 groups | 731 | 641–739 | 757 | 826 | 0 |
| 500 | off | 150 groups | 1,258 | 993–1,287 | 1,356 | 1,372 | 0 |
| 500 | off | no match | 642 | 612–702 | 809 | 832 | 0 |
| 500 | off | control: 150 LDAP groups, none mapped | 723 | 648–758 | 825 | 882 | 0 |
| 500 | on | 5 groups | 1,218 | 1,190–1,874 | 1,984 | 1,991 | 0 |
| 500 | on | 150 groups | 1,440 | 1,312–2,131 | 2,244 | 2,253 | 0 |
| 500 | on | no match | 1,195 | 1,177–1,272 | 1,932 | 2,019 | 0 |
| 500 | on | control: 150 LDAP groups, none mapped | 1,353 | 1,233–1,914 | 1,987 | 2,018 | 0 |
| 1,500 | off | 5 groups | 716 | 672–731 | 786 | 904 | 0 |
| 1,500 | off | 150 groups | 1,064 | 961–1,262 | 1,389 | 1,427 | 0 |
| 1,500 | off | no match | 696 | 684–747 | 786 | 823 | 0 |
| 1,500 | off | control: 150 LDAP groups, none mapped | 746 | 733–806 | 912 | 925 | 0 |
| 1,500 | on | 5 groups | 2,547 | 2,358–4,173 | 4,273 | 4,277 | 0 |
| 1,500 | on | 150 groups | 2,615 | 2,562–4,435 | 4,522 | 4,530 | 0 |
| 1,500 | on | no match | 2,410 | 2,346–4,168 | 4,190 | 4,337 | 0 |
| 1,500 | on | control: 150 LDAP groups, none mapped | 2,457 | 2,422–4,246 | 4,323 | 4,380 | 0 |

**Toggle effect**, sequential, steady state:

| Mappers | User | Off | On | Added | 95% CI of added | Ratio | ms per non-matching mapper |
|---|---|---|---|---|---|---|---|
| 500 | 5 groups | 731 | 1,218 | +487 | 456 to 1,143 | 1.67 | 1.0 |
| 500 | 150 groups | 1,258 | 1,440 | +182 | 54 to 878 | 1.14 | 0.5 |
| 500 | no match | 642 | 1,195 | +553 | 487 to 584 | 1.86 | 1.1 |
| 500 | control: 150 LDAP groups, none mapped | 723 | 1,353 | +630 | 509 to 1,223 | 1.87 | 1.3 |
| 1,500 | 5 groups | 716 | 2,547 | +1,831 | 1,650 to 3,483 | 3.56 | 1.2 |
| 1,500 | 150 groups | 1,064 | 2,615 | +1,552 | 1,321 to 3,429 | 2.46 | 1.1 |
| 1,500 | no match | 696 | 2,410 | +1,714 | 1,630 to 3,454 | 3.46 | 1.1 |
| 1,500 | control: 150 LDAP groups, none mapped | 746 | 2,457 | +1,712 | 1,652 to 3,500 | 3.29 | 1.1 |

**Concurrent browsers**, 200 logins per row, pool of 100 users:

| Mappers | Browsers | Toggle | Median | Median, time to first byte | p95 | Max | Over 5 s | Over 10 s | Failed |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | off | 714 | 643 | 824 | 1,298 | 0.0% | 0.0% | 0 |
| 1 | 10 | on | 732 | 651 | 882 | 1,217 | 0.0% | 0.0% | 0 |
| 1 | 25 | off | 888 | 689 | 1,663 | 2,413 | 0.0% | 0.0% | 0 |
| 1 | 25 | on | 926 | 747 | 1,928 | 2,354 | 0.0% | 0.0% | 0 |
| 1 | 50 ⚠ | off | 9,122 | 1,773 | 20,154 | 30,479 | 68.0% | 47.4% | 6 |
| 1 | 50 ⚠ | on | 3,368 | 1,457 | 25,798 | 31,307 | 47.2% | 46.7% | 3 |
| 500 | 10 | off | 723 | 652 | 874 | 1,333 | 0.0% | 0.0% | 0 |
| 500 | 10 | on | 1,468 | 1,387 | 2,222 | 3,526 | 0.0% | 0.0% | 0 |
| 500 | 25 | off | 930 | 745 | 1,939 | 2,624 | 0.0% | 0.0% | 0 |
| 500 | 25 | on | 2,254 | 2,019 | 4,316 | 6,191 | 1.5% | 0.0% | 0 |
| 500 | 50 ⚠ | off | 2,106 | 998 | 15,301 | 16,087 | 36.7% | 25.6% | 1 |
| 500 | 50 ⚠ | on | 6,567 | 2,828 | 23,865 | 32,825 | 52.0% | 37.9% | 2 |
| 1,500 | 10 | off | 828 | 761 | 988 | 1,430 | 0.0% | 0.0% | 0 |
| 1,500 | 10 | on | 2,961 | 2,838 | 5,052 | 7,876 | 6.5% | 0.0% | 0 |
| 1,500 | 25 | off | 969 | 812 | 2,103 | 2,782 | 0.0% | 0.0% | 0 |
| 1,500 | 25 | on | 4,913 | 3,982 | 9,303 | 14,219 | 46.7% | 0.5% | 1 |
| 1,500 | 50 ⚠ | off | 5,721 | 1,430 | 22,100 | 47,138 | 51.1% | 33.9% | 14 |
| 1,500 | 50 ⚠ | on | 12,296 | 8,472 | 44,995 | 48,083 | 79.8% | 60.7% | 36 |

⚠ **The 50-browser rows measure the load generator, not AAP, and must not be
used.** At that level the gateway's own access log shows logins taking at most
2.6 s (1 mapper, toggle off) while the browsers measured a median of 9.1 s;
the login page itself took 9.7 s to load against 0.7 s at 10 browsers;
throughput fell from 5.1 to 1.3 logins per second; and most failures were
browser socket errors before any request reached AAP. One Playwright driver
process could not service 50 busy browsers. The rows are shown so the problem
is visible. The 25-browser rows show early signs of the same effect (login
page 2.1 s) and should be read with care.

## Two kinds of login: the gateway pod's zone

The two gateway pods are in different availability zones, and the database's
primary is in one of them. With the option on at 1,500 mappers, a login makes
3,049 database statements, so the distance to the database decides the
result:

| Gateway pod | Time per statement | Login, measured in the pod | Browser logins |
|---|---|---|---|
| In the database's zone | 0.23 ms | 2.4 s | 45 of 80, median 2.4 s |
| In another zone | 0.77 ms | 4.1 s | 35 of 80, median 4.3 s |

**Medians for the option on in the tables above sit in the faster group, and
the p95 and maximum in the slower one.** They describe a mix of two
populations, which is also why the confidence intervals are wide. With the
option off the difference is about 30 ms and does not show.

## Run 2: drift check and cold start

Run `envb-r2-aba-20260929-1733`: 1,167 browser logins at 1,500 mappers, in the
order option off, on, off. Full tables in
[`results/envb-r2-aba-20260929-1733/analysis.md`](../results/envb-r2-aba-20260929-1733/analysis.md).

Sequential logins, steady state, login POST median in ms:

| User | Off, before | On | Off, after | Drift | 95% CI of drift |
|---|---|---|---|---|---|
| 5 groups | 742 | 4,039 | 715 | −3.6% | −97 to 52 |
| 150 groups | 1,010 | 2,684 | 1,046 | +3.6% | −228 to 271 |
| no match | 710 | 2,353 | 686 | −3.3% | −84 to 35 |
| control: 150 LDAP groups, none mapped | 706 | 2,456 | 747 | +5.9% | −20 to 97 |

Every drift interval contains zero. The "on" medians differ between users
because of the two zones above, not because of the users: a median lands in
whichever group holds more of that user's 17 logins.

Cold start, users in 150 mapped groups that no other user is in:

| Option | Failed attempts before the first success | First successful login |
|---|---|---|
| off | 1 | 4.5 s |
| on | 2 | 3.9 s |
| off | 2 | 1.9 s |

Each failure is *Service Unavailable* at about 10 s. After a successful
login, the landing page took 13–17 s to appear for these users, against about
1 s for others. The cause was not investigated.

## Findings — Environment B

1. **The toggle costs the same kind of penalty on much better infrastructure.**
   At 1,500 mappers a login goes from 0.7 s to 2.4 s through the gateway pod
   in the database's zone and to 4.1–4.3 s through the other: 3.5 and 6
   times slower. Environment A went from 1.5 s to 7 s.
2. **Hardware lowers the cost per mapper but does not remove it:** 1.1 ms
   per non-matching mapper in the database's zone and 2.3 ms from another
   zone, against 3.5–5 ms in Environment A.
3. **The kill limit is no longer reached by one login at a time,** because
   2.5 s is far from 10 s. With 25 browsers at once the median is 4.9 s and
   the slowest login took 14 s.
4. **With the toggle off, results match Environment A in shape:** mapper count
   is nearly free, matched groups cost, and LDAP group count alone costs
   nothing (control user 746 ms against 716 ms for the 5-group user).
5. **The directory server limited login throughput.** On 4 vCPU, FreeIPA
   served 15 binds per second at 100% CPU and logins were capped at 5.2 per
   second whatever the number of gateway pods, with the gateway at 5–27% of
   its CPU request. One bind costs about 130 ms, almost all password hashing.
   On 16 vCPU it serves 60 binds per second. The main run above was made after
   that change.

## Autoscaling

Tested on this environment.

| Test | Result |
|---|---|
| Manual scale of the gateway from 2 to 3 | Reverted by the operator after 35 s |
| HorizontalPodAutoscaler on the gateway | Flaps: 22 pods created and destroyed in 37 minutes |
| Replica count through `spec.api.replicas` | Holds. 77 s from the change to 4 pods Ready |
| CPU as a scaling signal | Did not move: 5–27% of request while logins slowed from 0.6 s to 7 s |
| Requests in flight on the route | Tracked the load from the first sample |

## Limitations — Environment B

- One run per cell.
- 50 concurrent browsers could not be measured; see the warning above. A
  load generator with one driver process per few browsers is in preparation.
- Pool users 1–60 had logged in before the run, during the autoscaling
  experiment, so their "first" login in this run is not a first login.
- One of the two gateway pods shares a node with the controller, EDA and hub.
- Whether the gateway's database connection is encrypted was not confirmed.
- The effect of more gateway pods has not been measured yet.


[Back to the report](../README.md)
