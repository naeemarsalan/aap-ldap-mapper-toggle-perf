#!/usr/bin/env python3
"""Seed / tear down perf test objects in FreeIPA. All objects are prefixed perf-.

usage: seed_idm.py [--pool N] seed | teardown | status
       seed_idm.py cold <count> <groups_per_user> [fresh]
         fresh: each cold user gets groups of its own that nobody else is in,
         so the first login also creates the teams
env:   IPA_URL, IPA_USER, IPA_PASS, PERF_PASS, PERF_POOL_SIZE (from .env)
"""
import http.cookiejar
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

IPA = ""  # set from IPA_URL in main
API_VERSION = "2.251"
N_GROUPS = 1500
N_POOL = 25  # default, overridden by PERF_POOL_SIZE / --pool
N_UNMAPPED = 150
CHUNK = 100
DESC = "AAP perf test - safe to delete"

GROUPS = [f"perf-grp-{i:04d}" for i in range(1, N_GROUPS + 1)]
# groups that never get a mapper: LDAP-size control
UNMAPPED = [f"perf-unmapped-{i:04d}" for i in range(1, N_UNMAPPED + 1)]
EXTRA_GROUPS = ["perf-all", "perf-unmapped"]
CONTROL = f"perf-ctl-{N_UNMAPPED}"
SINGLE = ["perf-match-few", "perf-match-many", "perf-nomatch", CONTROL]


def pool(n):
    return [f"perf-user-{i:02d}" for i in range(1, n + 1)]


def cold_users(n):
    return [f"perf-cold-{i:02d}" for i in range(1, n + 1)]


def load_env():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)


class Ipa:
    def __init__(self):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            urllib.request.HTTPSHandler(context=ctx),
        )
        data = urllib.parse.urlencode({"user": os.environ["IPA_USER"], "password": os.environ["IPA_PASS"]}).encode()
        req = urllib.request.Request(
            f"{IPA}/session/login_password",
            data=data,
            headers={"Referer": IPA, "Content-Type": "application/x-www-form-urlencoded", "Accept": "text/plain"},
        )
        self.opener.open(req, timeout=60)

    def call(self, method, args=None, opts=None):
        opts = dict(opts or {})
        opts.setdefault("version", API_VERSION)
        body = json.dumps({"method": method, "params": [args or [], opts], "id": 0}).encode()
        req = urllib.request.Request(
            f"{IPA}/session/json",
            data=body,
            headers={"Referer": IPA, "Content-Type": "application/json", "Accept": "application/json"},
        )
        return json.load(self.opener.open(req, timeout=600))

    def batch(self, calls, label):
        """calls: list of (method, args, opts). Returns (ok, errors)."""
        ok, errors = 0, []
        for i in range(0, len(calls), CHUNK):
            chunk = [{"method": m, "params": [a, o]} for m, a, o in calls[i : i + CHUNK]]
            res = self.call("batch", chunk)
            if res.get("error"):
                raise SystemExit(f"{label}: batch failed: {res['error']}")
            for c, r in zip(calls[i : i + CHUNK], res["result"]["results"]):
                if r.get("error"):
                    errors.append((c[1], r.get("error_name"), r["error"]))
                else:
                    ok += 1
            print(f"  {label}: {min(i + CHUNK, len(calls))}/{len(calls)}", flush=True)
        return ok, errors

    def find(self, kind, prefix):
        key = "cn" if kind == "group" else "uid"
        res = self.call(f"{kind}_find", [prefix], {"pkey_only": True, "sizelimit": 0})
        if res.get("error"):
            raise SystemExit(f"{kind}_find failed: {res['error']}")
        return sorted(n for r in res["result"]["result"] for n in r.get(key, []) if n.startswith(prefix))


def report(label, ok, errors, ignore=()):
    real = [e for e in errors if e[1] not in ignore]
    print(f"{label}: ok={ok} skipped={len(errors) - len(real)} failed={len(real)}")
    for e in real[:10]:
        print("   ", e)
    return not real


def user_add(name):
    return (
        "user_add",
        [name],
        {"givenname": "Perf", "sn": name, "userpassword": os.environ["PERF_PASS"], "krbpasswordexpiration": "20301231235959Z", "mail": f"{name}@perf.invalid"},
    )


def group_add(name):
    return ("group_add", [name], {"nonposix": True, "description": DESC})


def memberships(pool_users):
    m = {g: [] for g in GROUPS}
    for g in GROUPS[:5]:
        m[g].append("perf-match-few")
    for g in GROUPS[:150]:
        m[g].append("perf-match-many")
    # pool users: 10 groups each, spread over the whole range
    for n, u in enumerate(pool_users):
        for k in range(10):
            m[GROUPS[(n * 60 + k * 7) % N_GROUPS]].append(u)
    for g in UNMAPPED:
        m[g] = [CONTROL]
    return {g: u for g, u in m.items() if u}


def seed(ipa, n_pool):
    users = ["perf-bind"] + SINGLE + pool(n_pool)
    ok, err = ipa.batch([group_add(g) for g in GROUPS + UNMAPPED + EXTRA_GROUPS], "groups")
    good = report("groups", ok, err, ignore=("DuplicateEntry",))

    ok, err = ipa.batch([user_add(u) for u in users], "users")
    good &= report("users", ok, err, ignore=("DuplicateEntry",))

    m = memberships(pool(n_pool))
    m["perf-all"] = [u for u in users if u != "perf-bind"]
    m["perf-unmapped"] = ["perf-nomatch"]
    ok, err = ipa.batch([("group_add_member", [g], {"user": u}) for g, u in m.items()], "members")
    good &= report("members", ok, err)
    return good


def cold_groups(count, per_user, fresh, n_pool):
    """Groups of each cold user: shared low-end groups, or a block of its own."""
    if not fresh:
        # Mappers are created as perf-map-0001..N, so the lowest-numbered groups are
        # the ones that have a mapper at every scale >= groups_per_user.
        return [GROUPS[:per_user]] * count
    # Groups nobody else is in, so their teams do not exist before the cold login.
    # Taken from the high end: they only have a mapper at the largest scale.
    used = set(memberships(pool(n_pool)))
    free = [g for g in reversed(GROUPS) if g not in used]
    if count * per_user > len(free):
        raise SystemExit(f"cold fresh: {count} x {per_user} groups needed, {len(free)} unused groups exist")
    return [free[i * per_user : (i + 1) * per_user] for i in range(count)]


def cold(ipa, count, per_user, fresh=False, n_pool=25):
    if not 0 <= per_user <= N_GROUPS or count < 1:
        raise SystemExit(f"cold: count >= 1 and 0 <= groups_per_user <= {N_GROUPS}")
    users = cold_users(count)
    blocks = cold_groups(count, per_user, fresh, n_pool)
    ok, err = ipa.batch([user_add(u) for u in users], "cold users")
    good = report("cold users", ok, err, ignore=("DuplicateEntry",))
    m = {}
    for u, block in zip(users, blocks):
        for g in block:
            m.setdefault(g, []).append(u)
    m["perf-all"] = list(users)
    ok, err = ipa.batch([("group_add_member", [g], {"user": u}) for g, u in m.items()], "cold members")
    good &= report("cold members", ok, err)
    if fresh:
        print(f"lowest group used: {min(g for b in blocks for g in b)} - cold users match all their groups only at scales that include it")
    print("COLD_USERS=" + ",".join(users))
    return good


def teardown(ipa, n_pool):
    users = sorted(set(["perf-bind"] + SINGLE + pool(n_pool)) | set(ipa.find("user", "perf-")))
    ok, err = ipa.batch([("user_del", [u], {}) for u in users], "users")
    good = report("users", ok, err, ignore=("NotFound",))
    groups = sorted(set(GROUPS + UNMAPPED + EXTRA_GROUPS) | set(ipa.find("group", "perf-")))
    ok, err = ipa.batch([("group_del", [g], {}) for g in groups], "groups")
    return good & report("groups", ok, err, ignore=("NotFound",))


def status(ipa, n_pool):
    g = ipa.find("group", "perf-")
    u = ipa.find("user", "perf-")
    allg = ipa.call("group_find", [""], {"pkey_only": True, "sizelimit": 0})["result"]
    print(f"perf groups={len(g)} perf users={len(u)} total groups={allg['count']}")
    count = lambda names, prefix: len([n for n in names if n.startswith(prefix)])
    print(f"  mapped groups (perf-grp-):        {count(g, 'perf-grp-')} of {N_GROUPS}")
    print(f"  unmapped groups (perf-unmapped-): {count(g, 'perf-unmapped-')} of {N_UNMAPPED}")
    print(f"  pool users (perf-user-):          {count(u, 'perf-user-')} (configured pool size {n_pool})")
    print(f"  cold users (perf-cold-):          {count(u, 'perf-cold-')}")
    print(f"  control users (perf-ctl-):        {count(u, 'perf-ctl-')}")
    cold_seen = [n for n in u if n.startswith("perf-cold-")]
    for name in SINGLE + ["perf-user-01"] + cold_seen[:1]:
        r = ipa.call("user_show", [name], {})
        if r.get("error"):
            print(f"  {name}: {r['error']['message']}")
        else:
            print(f"  {name}: member of {len(r['result']['result'].get('memberof_group', []))} groups")
    return True


if __name__ == "__main__":
    load_env()
    args = sys.argv[1:]
    n_pool = int(os.environ.get("PERF_POOL_SIZE") or N_POOL)
    if args[:1] == ["--pool"]:
        n_pool, args = int(args[1]), args[2:]
    if n_pool < 1:
        raise SystemExit("pool size must be >= 1")
    action = args[0] if args else "status"
    if action not in ("seed", "teardown", "status", "cold") or (action == "cold" and (len(args) not in (3, 4) or args[3:] not in ([], ["fresh"]))):
        raise SystemExit(__doc__)
    IPA = os.environ["IPA_URL"].rstrip("/")
    if action == "cold":
        good = cold(Ipa(), int(args[1]), int(args[2]), fresh=args[3:] == ["fresh"], n_pool=n_pool)
    else:
        good = {"seed": seed, "teardown": teardown, "status": status}[action](Ipa(), n_pool)
    sys.exit(0 if good else 1)
