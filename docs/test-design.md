# The option and the test

## What the option is

| Where | Name |
|---|---|
| UI | Access Management → Authentication Methods → *authenticator* → Mapping → *mapper* → Options → **Block non-matching users** |
| API | `revoke` (boolean) on `/api/gateway/v1/authenticator_maps/` |

Behaviour in `ansible_base.authentication.utils.claims.create_claims()`:

- **off** — a mapper whose trigger the user does not match is skipped.
- **on** — a non-matching mapper becomes an explicit deny, which is then
  handled like a mapper that matched: its role is validated against the
  database before anything else happens. Every non-matching mapper produces
  that work on every login.

This is a property of the product code and applies to every environment.

## Test design, common to both environments

- Isolated authenticator `PERF - LDAP`, tried before any live authenticator,
  with `USER_SEARCH` restricted to members of `perf-all`.
- 1,500 LDAP groups `perf-grp-0001..1500`, one `team` mapper per group.
- Matrix: mappers {1, 500, 1500} × toggle {off, on}.
- Per cell: one first login per user, 20 sequential logins per user, then 100
  logins at 10 concurrent browsers. Fresh browser context for every login.
- Measured in a real browser (Playwright, Chromium):
  - **login POST** — click *Log in* → response to `POST /api/gateway/v1/login/`
  - **submit → landing** — click *Log in* → navigation rendered

| Test user | LDAP groups that have a mapper |
|---|---|
| `perf-match-few` | 5 |
| `perf-match-many` | 150 |
| `perf-nomatch` | 0 |
| `perf-user-01..25` (concurrency pool) | 10 each |


[Back to the report](../README.md)
