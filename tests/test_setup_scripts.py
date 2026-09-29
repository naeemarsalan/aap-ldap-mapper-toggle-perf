"""Tests for aap_setup.py and seed_idm.py. HTTP is replaced by fakes, nothing is contacted."""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.update(AAP_URL="https://aap.invalid", AAP_USER="stub", AAP_PASS="stub")
import aap_setup  # noqa: E402
import seed_idm  # noqa: E402

aap_setup.BACKOFF = 0


class FakeApi(aap_setup.Api):
    """Gateway with one authenticator and n team maps; fail maps request path -> list of codes to answer first."""

    def __init__(self, n, revoke=False, fail=None):
        super().__init__()
        self.maps = {i: {"id": i, "name": f"perf-map-{i:04d}", "map_type": "team", "revoke": revoke, "authenticator": 3} for i in range(1, n + 1)}
        self.maps[0] = {"id": 0, "name": "perf-allow", "map_type": "allow", "revoke": False, "authenticator": 3}
        self.fail = fail or {}
        self.seen = []

    def req(self, method, path, body=None):
        self.seen.append((method, path))
        if self.fail.get((method, path)):
            return self.fail[(method, path)].pop(0), "stub failure"
        if path.startswith("/authenticators/"):
            return 200, {"results": [{"id": 3, "name": aap_setup.AUTH_NAME}], "next": None}
        if method == "GET":
            return 200, {"results": list(self.maps.values()), "next": None}
        if method == "PATCH":
            self.maps[int(path.split("/")[2])].update(body)
            return 200, {}
        return 405, "unexpected"


def quiet(fn, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        return fn(*args), out.getvalue()


class Toggle(unittest.TestCase):
    def test_reports_time_and_failures(self):
        api = FakeApi(5)
        good, out = quiet(aap_setup.cmd_toggle, api, "on")
        self.assertTrue(good)
        self.assertRegex(out, r"toggle-result state=on maps=5 patched=5 failed=0 retried=0 elapsed_s=\d+\.\d\d\n$")
        self.assertTrue(all(m["revoke"] for m in api.maps.values() if m["map_type"] == "team"))
        self.assertFalse(api.maps[0]["revoke"])

    def test_retries_three_times_before_failing(self):
        path = "/authenticator_maps/2/"
        api = FakeApi(3, fail={("PATCH", path): [503, 0, 502], ("PATCH", "/authenticator_maps/3/"): [503, 503, 503, 503]})
        good, out = quiet(aap_setup.cmd_toggle, api, "on")
        self.assertFalse(good)
        self.assertIn("patched=2 failed=1 retried=6", out)
        self.assertEqual(api.seen.count(("PATCH", path)), 4)
        self.assertEqual(api.seen.count(("PATCH", "/authenticator_maps/3/")), 4)
        self.assertEqual([api.maps[i]["revoke"] for i in (1, 2, 3)], [True, True, False])

    def test_client_errors_are_not_retried(self):
        api = FakeApi(1, fail={("PATCH", "/authenticator_maps/1/"): [403]})
        good, out = quiet(aap_setup.cmd_toggle, api, "on")
        self.assertFalse(good)
        self.assertIn("failed=1 retried=0", out)

    def test_nothing_to_do(self):
        good, out = quiet(aap_setup.cmd_toggle, FakeApi(4), "off")
        self.assertTrue(good)
        self.assertIn("patched=0 failed=0", out)


class Verify(unittest.TestCase):
    def test_verify(self):
        self.assertTrue(quiet(aap_setup.cmd_verify, FakeApi(4), 4, "off")[0])
        self.assertTrue(quiet(aap_setup.cmd_verify, FakeApi(4, revoke=True), 4, "on")[0])
        self.assertFalse(quiet(aap_setup.cmd_verify, FakeApi(4), 4, "on")[0])
        self.assertFalse(quiet(aap_setup.cmd_verify, FakeApi(4), 5, "off")[0])
        self.assertFalse(quiet(aap_setup.cmd_verify, FakeApi(4), 3, "off")[0])

    def test_one_map_in_the_wrong_state(self):
        api = FakeApi(4, revoke=True)
        api.maps[2]["revoke"] = False
        good, out = quiet(aap_setup.cmd_verify, api, 4, "on")
        self.assertFalse(good)
        self.assertIn("perf-map-0002", out)


class Seed(unittest.TestCase):
    def test_pool_of_100(self):
        users = seed_idm.pool(100)
        self.assertEqual((len(set(users)), users[0], users[24], users[99]), (100, "perf-user-01", "perf-user-25", "perf-user-100"))
        m = seed_idm.memberships(users)
        per_user = {u: len([g for g in m if u in m[g]]) for u in users}
        self.assertEqual(set(per_user.values()), {10})

    def test_default_pool_memberships_unchanged(self):
        m = seed_idm.memberships(seed_idm.pool(25))
        self.assertEqual([g for g in m if "perf-user-02" in m[g]], [f"perf-grp-{60 + 7 * k + 1:04d}" for k in range(10)])
        self.assertEqual(len([g for g in m if "perf-match-many" in m[g]]), 150)
        self.assertEqual(len([g for g in m if "perf-match-few" in m[g]]), 5)

    def test_control_user_is_only_in_unmapped_groups(self):
        m = seed_idm.memberships(seed_idm.pool(25))
        groups = [g for g in m if seed_idm.CONTROL in m[g]]
        self.assertEqual(seed_idm.CONTROL, "perf-ctl-150")
        self.assertEqual(groups, [f"perf-unmapped-{i:04d}" for i in range(1, 151)])
        self.assertFalse(set(groups) & set(seed_idm.GROUPS))

    def test_cold_users_fresh_groups(self):
        blocks = seed_idm.cold_groups(4, 150, True, 25)
        flat = [g for block in blocks for g in block]
        self.assertEqual(len(set(flat)), 600)
        self.assertFalse(set(flat) & set(seed_idm.memberships(seed_idm.pool(25))))
        self.assertEqual(seed_idm.cold_groups(2, 5, False, 25), [seed_idm.GROUPS[:5]] * 2)
        with self.assertRaises(SystemExit):
            seed_idm.cold_groups(9, 150, True, 25)

    def test_cold_users(self):
        calls = []

        class Ipa:
            def batch(self, c, label):
                calls.extend(c)
                return len(c), []

        os.environ["PERF_PASS"] = "stub"
        good, out = quiet(seed_idm.cold, Ipa(), 3, 150)
        self.assertTrue(good)
        self.assertEqual([c[1][0] for c in calls if c[0] == "user_add"], ["perf-cold-01", "perf-cold-02", "perf-cold-03"])
        members = [c for c in calls if c[0] == "group_add_member"]
        self.assertEqual([c[1][0] for c in members], [f"perf-grp-{i:04d}" for i in range(1, 151)] + ["perf-all"])
        self.assertEqual(members[0][2], {"user": ["perf-cold-01", "perf-cold-02", "perf-cold-03"]})
        self.assertIn("COLD_USERS=perf-cold-01,perf-cold-02,perf-cold-03", out)


if __name__ == "__main__":
    unittest.main()
