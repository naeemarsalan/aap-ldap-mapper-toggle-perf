"""Time what one login spends in the database, in LDAP and in the gateway's own code.

Runs INSIDE the gateway 'api' container, fed to `aap-gateway-manage shell` on stdin.
It performs real logins through the same authentication backends the login view
uses, and times every database statement and every LDAP call made on the way.
What is left of the total is time in the gateway's Python code.

Replace the three placeholders before use, for example:

  sed -e 's/__USERS__/["perf-nomatch"]/' -e 's/__N__/4/' -e "s/__PASSWORD__/'...'/" probe_login.py \\
    | oc -n <namespace> exec -i <gateway pod> -c api -- aap-gateway-manage shell | grep '^PROBE_JSON '

Keep the password off command lines and out of files that are committed.
"""
import collections, json, re, statistics, time
import ldap.ldapobject
from django.contrib.auth import authenticate
from django.db import connection
from django.test import RequestFactory

USERS = __USERS__
PASSWORD = __PASSWORD__
N = __N__

class DbTimer:
    def __init__(self): self.calls = []
    def __call__(self, execute, sql, params, many, context):
        t = time.perf_counter()
        try:
            return execute(sql, params, many, context)
        finally:
            self.calls.append((time.perf_counter() - t, sql))

ldap_calls = []
_orig = ldap.ldapobject.SimpleLDAPObject._ldap_call
def _timed(self, func, *a, **kw):
    t = time.perf_counter()
    try:
        return _orig(self, func, *a, **kw)
    finally:
        ldap_calls.append((time.perf_counter() - t, getattr(func, "__name__", str(func))))
ldap.ldapobject.SimpleLDAPObject._ldap_call = _timed

def table(sql):
    m = re.search(r'\b(?:FROM|INTO|UPDATE)\s+"?([a-zA-Z0-9_]+)"?', sql)
    return m.group(1) if m else "?"

out = []
for user in USERS:
    for i in range(N):
        db = DbTimer(); del ldap_calls[:]
        request = RequestFactory().post("/api/gateway/v1/login/")
        with connection.execute_wrapper(db):
            t = time.perf_counter()
            u = authenticate(request, username=user, password=PASSWORD)
            total = time.perf_counter() - t
        kinds = collections.Counter(s.split(None, 1)[0].upper() for _, s in db.calls)
        by_table = collections.defaultdict(lambda: [0, 0.0])
        for d, s in db.calls:
            k = f"{s.split(None, 1)[0].upper()} {table(s)}"
            by_table[k][0] += 1; by_table[k][1] += d
        lk = collections.defaultdict(lambda: [0, 0.0])
        for d, n in ldap_calls:
            lk[n][0] += 1; lk[n][1] += d
        dbt = sum(d for d, _ in db.calls); lt = sum(d for d, _ in ldap_calls)
        out.append({
            "user": user, "iter": i, "ok": bool(u), "total_ms": round(total * 1000, 1),
            "db_ms": round(dbt * 1000, 1), "db_statements": len(db.calls),
            "db_median_statement_ms": round(statistics.median([d for d, _ in db.calls]) * 1000, 3) if db.calls else None,
            "ldap_ms": round(lt * 1000, 1), "ldap_calls": len(ldap_calls),
            "other_ms": round((total - dbt - lt) * 1000, 1),
            "db_kinds": dict(kinds),
            "db_top": sorted(([k, v[0], round(v[1] * 1000, 1)] for k, v in by_table.items()), key=lambda x: -x[2])[:8],
            "ldap_by_call": {k: [v[0], round(v[1] * 1000, 1)] for k, v in lk.items()},
        })
print("PROBE_JSON " + json.dumps(out))
