"""Tests for run_matrix.sh. ssh, scp, oc, curl and aap_setup.py are replaced by
local stubs, nothing leaves this machine."""
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STUBS = {
    "ssh": r"""#!/bin/bash
echo "ssh $*" >> "$STUB_DIR/calls.log"
cmd="${@: -1}"
case "$cmd" in
*sha256sum*) sha256sum "${STUB_REMOTE_LOADTEST:-loadtest.py}" ;;
*"wc -l"*) cat "$STUB_DIR/remote.jsonl" 2>/dev/null | wc -l ;;
*loadtest.py*)
    set -- $cmd
    iterations=1
    while [ $# -gt 0 ]; do
        case "$1" in
        --phase) phase=$2 ;;
        --users) users=$2 ;;
        --iterations) iterations=$2 ;;
        --concurrency) conc=$2 ;;
        esac
        shift
    done
    [ "$phase${conc:+-$conc}" = "${STUB_FAIL_PHASE:-}" ] && exit 1
    [ "$phase${conc:+-$conc}" = "${STUB_EMPTY_PHASE:-}" ] && exit 0
    n=$(($(echo "$users" | tr ',' '\n' | wc -l) * iterations))
    [ "$phase" = "${STUB_SHORT_PHASE:-}" ] && n=$((n - 1))
    for i in $(seq 1 $n); do echo "{\"phase\": \"$phase\"}" >> "$STUB_DIR/remote.jsonl"; done
    ;;
esac
""",
    "scp": r"""#!/bin/bash
echo "scp $*" >> "$STUB_DIR/calls.log"
[ -n "${STUB_SCP_FAIL:-}" ] && exit 1
cp "$STUB_DIR/remote.jsonl" "${@: -1}"
""",
    "oc": r"""#!/bin/bash
echo "oc $*" >> "$STUB_DIR/calls.log"
case "$*" in
*"get pod -l"*) printf 'pod/aap-gateway-abc-1\npod/aap-gateway-abc-2\n' ;;
*logs*--previous*) exit 1 ;;
*logs*) echo 'client - - [x] "POST /api/gateway/v1/login/ HTTP/1.1" 302 0 (1.234) "-"' ;;
*jsonpath*) printf '0 0' ;;
esac
""",
    "curl": r"""#!/bin/bash
echo "curl" >> "$STUB_DIR/calls.log"
printf '%s' "${STUB_HEALTH:-200}"
""",
    "python3-stub": r"""#!/bin/bash
echo "python $*" >> "$STUB_DIR/calls.log"
case "$2" in
toggle)
    echo "toggle-result state=$3 maps=7 patched=7 failed=${STUB_TOGGLE_FAILED:-0} retried=0 elapsed_s=1.50"
    [ "${STUB_TOGGLE_FAILED:-0}" = 0 ] || [ "$3" = off ] || exit 1
    ;;
verify) exit "${STUB_VERIFY_RC:-0}" ;;
esac
exit 0
""",
}


class RunMatrix(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.work = os.path.join(self.tmp, "work")
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.work)
        os.makedirs(self.bin)
        for name in ("run_matrix.sh", "loadtest.py", "aap_setup.py"):
            shutil.copy(os.path.join(ROOT, name), self.work)
        for name, body in STUBS.items():
            path = os.path.join(self.bin, name)
            with open(path, "w") as f:
                f.write(body)
            os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)

    def run_matrix(self, *args, **env):
        base = {
            "PATH": self.bin + ":/usr/bin:/bin",
            "HOME": self.tmp,
            "STUB_DIR": self.tmp,
            "PYTHON": os.path.join(self.bin, "python3-stub"),
            "LOAD_NODE": "stub-node",
            "AAP_URL": "https://aap.invalid",
            "AAP_USER": "stub",
            "AAP_PASS": "stub",
            "PERF_POOL_SIZE": "3",
            "STEADY_ITER": "2",
            "CONC_ITER": "2",
            "SINGLE_USERS": "perf-match-few,perf-nomatch",
        }
        base.update(env)
        p = subprocess.run(["bash", "run_matrix.sh", "t1"] + list(args), cwd=self.work, env=base, capture_output=True, text=True, timeout=120)
        self.out, self.err = p.stdout, p.stderr
        return p.returncode

    def read(self, name):
        path = os.path.join(self.work, "results", "t1", name)
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [l.rstrip("\n").split("\t") for l in f]

    def calls(self, prefix=""):
        path = os.path.join(self.tmp, "calls.log")
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return [l.strip() for l in f if l.startswith(prefix)]

    def logins(self):
        return [" ".join(c.split("loadtest.py", 1)[1].split()) for c in self.calls("ssh") if "loadtest.py --run" in c]

    def test_default_matrix(self):
        self.assertEqual(self.run_matrix(), 0, self.err)
        phases = self.read("phases.tsv")
        self.assertEqual(phases[0], ["cell", "phase", "expected_records", "actual_records", "exit_code", "start_utc", "end_utc"])
        self.assertEqual([r[0] for r in phases[1::4]], ["r1-c01-scale1-off", "r1-c02-scale1-on", "r1-c03-scale500-off", "r1-c04-scale500-on", "r1-c05-scale1500-off", "r1-c06-scale1500-on"])
        self.assertEqual([r[1:5] for r in phases[1:5]], [["first", "2", "2", "0"], ["steady", "4", "4", "0"], ["pool-first", "3", "3", "0"], ["concurrent", "6", "6", "0"]])
        self.assertEqual(len(phases), 1 + 6 * 4)
        self.assertEqual(len(self.read("logins.jsonl")), 6 * 15)
        flips = self.read("toggle-flip.tsv")
        self.assertEqual(flips[0][:8], ["rep", "cell_seq", "cell", "scale", "toggle", "maps", "patched", "failed"])
        self.assertEqual([r[:8] for r in flips[1:3]], [["1", "1", "r1-c01-scale1-off", "1", "off", "7", "7", "0"], ["1", "2", "r1-c02-scale1-on", "1", "on", "7", "7", "0"]])
        self.assertEqual(len(flips), 7)
        self.assertGreaterEqual(float(flips[1][10]), 0)

    def test_results_are_copied_after_every_cell(self):
        self.assertEqual(self.run_matrix(CELLS="1:off 1:on 500:off"), 0, self.err)
        self.assertEqual(len(self.calls("scp")), 3 + 1)

    def test_verify_runs_before_each_cell(self):
        self.assertEqual(self.run_matrix(CELLS="500:off 500:on"), 0, self.err)
        calls = [c for c in self.calls() if c.startswith("python") or "loadtest.py --run" in c]
        self.assertEqual([c.split("aap_setup.py ")[1] for c in calls[:3]], ["maps 500", "toggle off", "verify 500 off"])
        self.assertIn("--phase first", calls[3])
        second = calls.index("python aap_setup.py verify 500 on")
        self.assertEqual(calls[second - 1], "python aap_setup.py toggle on")
        self.assertIn("--phase first", calls[second + 1])

    def test_gateway_logs_of_every_pod(self):
        self.assertEqual(self.run_matrix(CELLS="500:off 500:on"), 0, self.err)
        files = sorted(f for f in os.listdir(os.path.join(self.work, "results", "t1")) if f.startswith("gwlog-"))
        self.assertEqual(files, [f"gwlog-r1-c0{n}-scale500-{t}-aap-gateway-abc-{p}.log" for n, t in ((1, "off"), (2, "on")) for p in (1, 2)])
        self.assertEqual(self.read(files[0])[0][0][:6], "client")
        replicas = self.read("replicas.tsv")
        self.assertEqual([(r[2], r[3], r[5], r[6]) for r in replicas[1:3]], [("r1-c01-scale500-off", w, "2", "aap-gateway-abc-1,aap-gateway-abc-2") for w in ("start", "end")])
        self.assertEqual(len(replicas), 5)
        self.assertEqual(self.read("restarts-r1-c02-scale500-on.txt"), [["aap-gateway-abc-1", "0 0"], ["aap-gateway-abc-2", "0 0"]])

    def test_aba_repeat_ramp_and_cold(self):
        cold = ",".join(f"perf-cold-{i:02d}" for i in range(1, 8))
        rc = self.run_matrix(CELLS="1500:off 1500:on 1500:off", REPEAT="2", RAMP="2 3", COLD_USERS=cold, COLD_ITER="2", THINK_SEED="42", THINK_MIN="0.1", THINK_MAX="0.2")
        self.assertEqual(rc, 0, self.err)
        logins = self.logins()
        self.assertEqual(len(logins), 6 * 6)
        self.assertEqual(logins[0], "--run t1 --scale 1500 --toggle off --cell-seq 1 --rep 1 --phase first --think-seed 42 --users perf-match-few,perf-nomatch --iterations 1 --think-min 0.1 --think-max 0.2")
        self.assertEqual([l.split("--phase ")[1].split()[0] for l in logins[:6]], ["first", "cold", "steady", "pool-first", "concurrent", "concurrent"])
        self.assertEqual([l.split("--concurrency ")[1] for l in logins[4:6]], ["2 --think-min 0 --think-max 0", "3 --think-min 0 --think-max 0"])
        seen = [(l.split("--rep ")[1].split()[0], l.split("--cell-seq ")[1].split()[0], l.split("--toggle ")[1].split()[0]) for l in logins[::6]]
        self.assertEqual(seen, [("1", "1", "off"), ("1", "2", "on"), ("1", "3", "off"), ("2", "1", "off"), ("2", "2", "on"), ("2", "3", "off")])
        used = [l.split("--users ")[1].split()[0] for l in logins if "--phase cold" in l]
        self.assertEqual(used, [f"perf-cold-{i:02d}" for i in range(1, 7)])
        cells = [r[0] for r in self.read("phases.tsv")[1::6]]
        self.assertEqual(cells, ["r1-c01-scale1500-off", "r1-c02-scale1500-on", "r1-c03-scale1500-off", "r2-c01-scale1500-off", "r2-c02-scale1500-on", "r2-c03-scale1500-off"])

    def test_no_cold_phase_without_cold_users(self):
        self.assertEqual(self.run_matrix(CELLS="1:off", COLD_USERS=""), 0, self.err)
        self.assertFalse([l for l in self.logins() if "cold" in l])

    def test_too_few_cold_users(self):
        rc = self.run_matrix(CELLS="1500:off 1500:on 1500:off", COLD_USERS="perf-cold-01,perf-cold-02")
        self.assertEqual(rc, 1)
        self.assertIn("COLD_USERS has 2 users", self.err)
        self.assertEqual(self.calls(), [])

    def test_duplicate_cold_users(self):
        self.assertEqual(self.run_matrix(CELLS="1:off 1:on", COLD_USERS="perf-cold-01 perf-cold-01"), 1)
        self.assertEqual(self.calls(), [])

    def test_bad_cell(self):
        self.assertEqual(self.run_matrix(CELLS="1500:maybe"), 1)
        self.assertEqual(self.calls(), [])

    def test_scales_as_arguments(self):
        self.assertEqual(self.run_matrix("1", "500"), 0, self.err)
        self.assertEqual([r[2] for r in self.read("toggle-flip.tsv")[1:]], ["r1-c01-scale1-off", "r1-c02-scale1-on", "r1-c03-scale500-off", "r1-c04-scale500-on"])

    def test_phase_without_records_aborts(self):
        rc = self.run_matrix(CELLS="500:off 500:on", STUB_EMPTY_PHASE="pool-first")
        self.assertEqual(rc, 3)
        self.assertIn("PHASE FAILED: cell r1-c01-scale500-off phase pool-first", self.err)
        self.assertEqual([r[1:5] for r in self.read("phases.tsv")[1:]], [["first", "2", "2", "0"], ["steady", "4", "4", "0"], ["pool-first", "3", "0", "0"]])
        self.assertEqual(self.calls("python")[-1], "python aap_setup.py toggle off")
        self.assertEqual(len(self.read("logins.jsonl")), 6)

    def test_phase_exit_status_is_checked(self):
        rc = self.run_matrix(CELLS="500:off", STUB_FAIL_PHASE="concurrent-10")
        self.assertEqual(rc, 3)
        self.assertEqual(self.read("phases.tsv")[-1][1:5], ["concurrent", "6", "0", "1"])

    def test_continue_after_failed_phase(self):
        rc = self.run_matrix(CELLS="500:off 500:on", STUB_FAIL_PHASE="steady", ON_PHASE_FAIL="continue")
        self.assertEqual(rc, 4)
        self.assertEqual(self.err.count("PHASE FAILED"), 2)
        self.assertEqual(len(self.read("phases.tsv")), 1 + 8)

    def test_short_phase_is_reported(self):
        rc = self.run_matrix(CELLS="500:off", STUB_SHORT_PHASE="steady")
        self.assertEqual(rc, 4)
        self.assertIn("PHASE SHORT: cell r1-c01-scale500-off phase steady", self.err)
        self.assertEqual(self.read("phases.tsv")[2][1:5], ["steady", "4", "3", "0"])

    def test_verify_failure_aborts_before_any_login(self):
        self.assertEqual(self.run_matrix(CELLS="500:off", STUB_VERIFY_RC="1"), 1)
        self.assertIn("verify failed", self.err)
        self.assertEqual(self.logins(), [])

    def test_failed_patches_abort_and_are_recorded(self):
        self.assertEqual(self.run_matrix(CELLS="500:on", STUB_TOGGLE_FAILED="3"), 1)
        self.assertEqual(self.read("toggle-flip.tsv")[1][4:8] + self.read("toggle-flip.tsv")[1][11:12], ["on", "7", "7", "3", "1"])
        self.assertEqual(self.logins(), [])

    def test_health_check_aborts(self):
        self.assertEqual(self.run_matrix(CELLS="500:off 500:on", STUB_HEALTH="503"), 2)
        self.assertEqual(len(self.read("phases.tsv")), 1 + 4)
        self.assertEqual(self.calls("python")[-1], "python aap_setup.py toggle off")

    def test_different_loadtest_on_load_node(self):
        other = os.path.join(self.tmp, "other.py")
        with open(other, "w") as f:
            f.write("# older version\n")
        self.assertEqual(self.run_matrix(CELLS="500:off", STUB_REMOTE_LOADTEST=other), 1)
        self.assertIn("loadtest.py on the load node differs", self.err)
        self.assertEqual(self.calls("python"), [])

    def test_failed_copy_is_reported(self):
        self.assertEqual(self.run_matrix(CELLS="500:off", STUB_SCP_FAIL="1"), 4)
        self.assertIn("RESULT SYNC FAILED", self.err)

    def test_environment_wins_over_dot_env(self):
        with open(os.path.join(self.work, ".env"), "w") as f:
            f.write('CELLS="1:off 1:on"\nRAMP="2 3"\nGRAFANA_HOST=\n')
        self.assertEqual(self.run_matrix(CELLS="500:on"), 0, self.err)
        phases = self.read("phases.tsv")[1:]
        self.assertEqual({r[0] for r in phases}, {"r1-c01-scale500-on"})
        self.assertEqual([r[1] for r in phases], ["first", "steady", "pool-first", "concurrent", "concurrent"])

    def test_run_id_is_not_reused(self):
        self.assertEqual(self.run_matrix(CELLS="1:off"), 0, self.err)
        self.assertEqual(self.run_matrix(CELLS="1:off"), 1)


if __name__ == "__main__":
    unittest.main()
