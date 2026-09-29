#!/usr/bin/env python3
"""Manage the isolated PERF - LDAP authenticator and its maps on AAP gateway.

usage:
  aap_setup.py status
  aap_setup.py authenticator            create PERF - LDAP if missing
  aap_setup.py maps <N>                 ensure exactly N team maps exist (plus the allow map)
  aap_setup.py toggle on|off            set revoke on all PERF team maps
  aap_setup.py verify <N> on|off        exit non-zero unless exactly N team maps exist, all with that revoke
  aap_setup.py teardown                 remove maps, authenticator, PERF org/teams, perf-* users

Only objects belonging to the PERF - LDAP authenticator are ever modified.
"""
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

AUTH_NAME = "PERF - LDAP"
ORG = "PERF"
BASE_DN = GROUPS_DN = USERS_DN = ""  # set from LDAP_BASE_DN in main
WORKERS = 8
RETRIES = 3
BACKOFF = 2.0  # seconds, doubled per retry


def load_env():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)


class Api:
    def __init__(self):
        self.base = os.environ["AAP_URL"].rstrip("/") + "/api/gateway/v1"
        tok = base64.b64encode(f"{os.environ['AAP_USER']}:{os.environ['AAP_PASS']}".encode()).decode()
        self.headers = {"Authorization": f"Basic {tok}", "Content-Type": "application/json", "Accept": "application/json"}
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.retried = 0

    def req(self, method, path, body=None):
        url = path if path.startswith("http") else self.base + path
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(url, data=data, method=method, headers=self.headers)
        try:
            with urllib.request.urlopen(r, context=self.ctx, timeout=120) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, raw[:500]
        except (OSError, ValueError) as e:
            # no HTTP response at all (connection error, timeout)
            return 0, f"{type(e).__name__}: {e}"

    def retry(self, method, path, body=None, done=None):
        """req() with up to RETRIES retries. done(): True if an earlier attempt took effect."""
        for attempt in range(RETRIES + 1):
            if attempt:
                time.sleep(BACKOFF * 2 ** (attempt - 1))
                self.retried += 1
                if done and done():
                    return 200, "applied by an earlier attempt"
            code, d = self.req(method, path, body)
            if 200 <= code < 300:
                return code, d
            if method == "DELETE" and code == 404 and attempt:
                return 204, "deleted by an earlier attempt"
            # other 4xx answers are deterministic, retrying cannot help
            if 400 <= code < 500 and code not in (408, 429):
                return code, d
        return code, d

    def list(self, path):
        out, url = [], path + ("&" if "?" in path else "?") + "page_size=200"
        while url:
            code, d = self.retry("GET", url)
            if code != 200:
                raise SystemExit(f"GET {url} -> {code} {d}")
            out += d["results"]
            url = d.get("next")
            if url and url.startswith("/"):
                url = os.environ["AAP_URL"].rstrip("/") + url
        return out


def get_auth(api):
    found = [a for a in api.list("/authenticators/") if a["name"] == AUTH_NAME]
    return found[0] if found else None


def perf_maps(api, auth):
    return api.list(f"/authenticator_maps/?authenticator={auth['id']}")


def team_maps(api, auth):
    return [m for m in perf_maps(api, auth) if m["map_type"] == "team"]


def parallel(fn, items, label):
    return not run_parallel(fn, items, label)


def run_parallel(fn, items, label):
    failed = []
    with ThreadPoolExecutor(WORKERS) as ex:
        for n, (item, (code, body)) in enumerate(zip(items, ex.map(fn, items)), 1):
            if not 200 <= code < 300:
                failed.append((item if isinstance(item, (str, int)) else item.get("name", item.get("id")), code, body))
            if n % 250 == 0 or n == len(items):
                print(f"  {label}: {n}/{len(items)}", flush=True)
    print(f"{label}: ok={len(items) - len(failed)} failed={len(failed)}")
    for f in failed[:5]:
        print("   ", f)
    return failed


def cmd_status(api):
    auths = api.list("/authenticators/")
    maps = api.list("/authenticator_maps/")
    for a in auths:
        mine = [m for m in maps if m["authenticator"] == a["id"]]
        by = {}
        for m in mine:
            key = f"{m['map_type']}/revoke={m['revoke']}"
            by[key] = by.get(key, 0) + 1
        print(f"authenticator id={a['id']} order={a['order']} enabled={a['enabled']} name={a['name']!r} maps={len(mine)} {by}")
    for ep in ("users", "teams", "organizations"):
        code, d = api.req("GET", f"/{ep}/?page_size=1")
        print(f"{ep}: {d['count']}")
    return True


def cmd_authenticator(api):
    auth = get_auth(api)
    if auth:
        print(f"exists: id={auth['id']} order={auth['order']}")
    else:
        body = {
            "name": AUTH_NAME,
            "type": "ansible_base.authentication.authenticator_plugins.ldap",
            "enabled": True,
            "create_objects": True,
            "remove_users": True,
            # tried before the live IdM authenticator so perf users never touch it
            "order": 1,
            "configuration": {
                "SERVER_URI": [os.environ["LDAP_URI"]],
                "BIND_DN": f"uid=perf-bind,{USERS_DN}",
                "BIND_PASSWORD": os.environ["PERF_PASS"],
                "START_TLS": False,
                "CONNECTION_OPTIONS": {"OPT_REFERRALS": 0, "OPT_NETWORK_TIMEOUT": 30},
                # only members of perf-all are visible to this authenticator
                "USER_SEARCH": [USERS_DN, "SCOPE_SUBTREE", f"(&(uid=%(user)s)(memberOf=cn=perf-all,{GROUPS_DN}))"],
                "GROUP_SEARCH": [GROUPS_DN, "SCOPE_SUBTREE", "(objectClass=ipausergroup)"],
                "GROUP_TYPE": "MemberDNGroupType",
                "GROUP_TYPE_PARAMS": {"name_attr": "cn", "member_attr": "member"},
                "USER_ATTR_MAP": {"email": "mail", "last_name": "sn", "first_name": "givenName"},
            },
        }
        code, d = api.req("POST", "/authenticators/", body)
        if code >= 300:
            print(f"create failed: {code} {d}")
            return False
        auth = d
        print(f"created: id={auth['id']} order={auth['order']}")
    if not [m for m in perf_maps(api, auth) if m["map_type"] == "allow"]:
        code, d = api.req(
            "POST",
            "/authenticator_maps/",
            {
                "name": "perf-allow",
                "authenticator": auth["id"],
                "map_type": "allow",
                "revoke": False,
                "order": 0,
                "triggers": {"groups": {"has_or": [f"cn=perf-all,{GROUPS_DN}"]}},
            },
        )
        print(f"allow map: {code}")
        return code < 300
    return True


def cmd_maps(api, n):
    auth = get_auth(api)
    if not auth:
        raise SystemExit("run 'authenticator' first")
    team = sorted((m for m in perf_maps(api, auth) if m["map_type"] == "team"), key=lambda m: m["name"])
    have = {m["name"] for m in team}
    revoke = team[0]["revoke"] if team else False
    want = [f"perf-map-{i:04d}" for i in range(1, n + 1)]
    good = True

    def exists(name):
        code, d = api.req("GET", f"/authenticator_maps/?authenticator={auth['id']}&name={name}")
        return code == 200 and any(m["name"] == name for m in d["results"])

    def create(name):
        i = int(name.rsplit("-", 1)[1])
        return api.retry(
            "POST",
            "/authenticator_maps/",
            {
                "name": name,
                "authenticator": auth["id"],
                "map_type": "team",
                "organization": ORG,
                "team": f"perf-team-{i:04d}",
                "role": "Team Member",
                "revoke": revoke,
                "order": i,
                "triggers": {"groups": {"has_or": [f"cn=perf-grp-{i:04d},{GROUPS_DN}"]}},
            },
            done=lambda: exists(name),
        )

    missing = [w for w in want if w not in have]
    if missing:
        good &= parallel(create, missing, "create maps")
    extra = [m for m in team if m["name"] not in set(want)]
    if extra:
        good &= parallel(lambda m: api.retry("DELETE", f"/authenticator_maps/{m['id']}/"), extra, "delete maps")
    now = len(team_maps(api, auth))
    print(f"team maps now: {now} retried={api.retried}")
    return good and now == n


def cmd_toggle(api, state):
    auth = get_auth(api)
    if not auth:
        raise SystemExit("run 'authenticator' first")
    revoke = state == "on"
    t0 = time.monotonic()
    team = team_maps(api, auth)
    todo = [m for m in team if m["revoke"] != revoke]
    failed = []
    if todo:
        failed = run_parallel(lambda m: api.retry("PATCH", f"/authenticator_maps/{m['id']}/", {"revoke": revoke}), todo, f"revoke={revoke}")
    else:
        print(f"all team maps already revoke={revoke}")
    # parsed by run_matrix.sh
    print(f"toggle-result state={state} maps={len(team)} patched={len(todo) - len(failed)} failed={len(failed)} retried={api.retried} elapsed_s={time.monotonic() - t0:.2f}")
    return not failed


def cmd_verify(api, n, state):
    auth = get_auth(api)
    if not auth:
        print(f"verify FAILED: authenticator {AUTH_NAME!r} not found")
        return False
    revoke = state == "on"
    team = team_maps(api, auth)
    wrong = [m["name"] for m in team if m["revoke"] != revoke]
    good = len(team) == n and not wrong
    print(f"verify {'ok' if good else 'FAILED'}: team maps={len(team)} expected={n} revoke!={revoke}: {len(wrong)} {wrong[:5] if wrong else ''}")
    return good


def cmd_teardown(api):
    good = True
    auth = get_auth(api)
    if auth:
        maps = perf_maps(api, auth)
        if maps:
            good &= parallel(lambda m: api.req("DELETE", f"/authenticator_maps/{m['id']}/"), maps, "delete maps")
    users = [u for u in api.list("/users/?username__startswith=perf-") if u["username"].startswith("perf-")]
    if users:
        good &= parallel(lambda u: api.req("DELETE", f"/users/{u['id']}/"), users, "delete users")
    teams = [t for t in api.list("/teams/?name__startswith=perf-team-") if t["name"].startswith("perf-team-")]
    if teams:
        good &= parallel(lambda t: api.req("DELETE", f"/teams/{t['id']}/"), teams, "delete teams")
    for o in [o for o in api.list(f"/organizations/?name={ORG}") if o["name"] == ORG]:
        code, d = api.req("DELETE", f"/organizations/{o['id']}/")
        print(f"delete org {ORG}: {code}")
        good &= code < 300
    if auth:
        code, d = api.req("DELETE", f"/authenticators/{auth['id']}/")
        print(f"delete authenticator: {code} {d if code >= 300 else ''}")
        good &= code < 300
    return good


if __name__ == "__main__":
    load_env()
    BASE_DN = os.environ["LDAP_BASE_DN"]
    GROUPS_DN = f"cn=groups,cn=accounts,{BASE_DN}"
    USERS_DN = f"cn=users,cn=accounts,{BASE_DN}"
    api = Api()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        ok = cmd_status(api)
    elif cmd == "authenticator":
        ok = cmd_authenticator(api)
    elif cmd == "maps":
        ok = cmd_maps(api, int(sys.argv[2]))
    elif cmd in ("toggle", "verify") and sys.argv[-1] not in ("on", "off"):
        raise SystemExit(__doc__)
    elif cmd == "toggle":
        ok = cmd_toggle(api, sys.argv[2])
    elif cmd == "verify":
        ok = cmd_verify(api, int(sys.argv[2]), sys.argv[3])
    elif cmd == "teardown":
        ok = cmd_teardown(api)
    else:
        raise SystemExit(__doc__)
    sys.exit(0 if ok else 1)
