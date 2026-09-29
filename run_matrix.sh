#!/bin/bash
# Runs a sequence of (mapper scale, toggle) cells with real-browser logins.
# usage: run_matrix.sh <run-id> [scales...]
#   with scales:    cells are "<scale>:off <scale>:on" for each scale
#   without scales: cells come from CELLS, default is the full matrix
# All options are environment variables, see .env.example.
# Output in results/<run-id>/: logins.jsonl, phases.tsv, toggle-flip.tsv,
# replicas.tsv, run-meta.txt and per cell gwlog-*, restarts-*, status-*.
set -u
cd "$(dirname "$0")"
# .env supplies defaults, variables already in the environment win
preset=$(export -p)
set -a
[ -f ./.env ] && . ./.env
set +a
eval "$preset"

RUN=${1:?run id}
shift
if [ $# -gt 0 ]; then
    CELLS=$(for s in "$@"; do printf '%s:off %s:on ' "$s" "$s"; done)
fi
CELLS=${CELLS:-1:off 1:on 500:off 500:on 1500:off 1500:on}
REPEAT=${REPEAT:-1}
RAMP=${RAMP:-${CONC:-10}}
STEADY_ITER=${STEADY_ITER:-20}
CONC_ITER=${CONC_ITER:-4}
COLD_ITER=${COLD_ITER:-5}
COLD_PER_CELL=${COLD_PER_CELL:-1}
THINK_MIN=${THINK_MIN:-0.5}
THINK_MAX=${THINK_MAX:-2.0}
THINK_SEED=${THINK_SEED:-$RANDOM}
ON_PHASE_FAIL=${ON_PHASE_FAIL:-abort}
PUSH_LOADTEST=${PUSH_LOADTEST:-0}

NODE=${LOAD_NODE:?ssh target of the load generator}
LOAD_DIR=${LOAD_DIR:-aap-perf}
LOAD_IMAGE=${LOAD_IMAGE:-aap-perf-pw}
GRAFANA=${GRAFANA_HOST:-}
default_annotate='~/aap-perf-annotate.sh'
GRAFANA_ANNOTATE=${GRAFANA_ANNOTATE:-$default_annotate}
NS=${AAP_NAMESPACE:-aap}
export KUBECONFIG=${AAP_KUBECONFIG:-$HOME/.kube/config}
GW_SELECTOR=${GATEWAY_SELECTOR:-app.kubernetes.io/component=gateway}
GW_POD_REGEX=${GATEWAY_POD_REGEX:-gateway}
GW_CONTAINER=${GATEWAY_CONTAINER:-api}
GW_LOG_PATTERN='"POST /api/gateway/v1/login/|denied access|Exception|Traceback|timeout|[Hh][Aa][Rr][Aa][Kk][Ii][Rr][Ii]'
PYTHON=${PYTHON:-python3}
# extra ssh/scp options, e.g. "-F /path/to/ssh_config"
SSH_OPTS=${SSH_OPTS:-}
SSH="ssh -o BatchMode=yes $SSH_OPTS"
SCP="scp -q -o BatchMode=yes $SSH_OPTS"

POOL_SIZE=${PERF_POOL_SIZE:-25}
SINGLE=${SINGLE_USERS:-perf-match-few,perf-match-many,perf-nomatch,perf-ctl-150}
POOL=$(printf 'perf-user-%02d,' $(seq 1 "$POOL_SIZE") | sed 's/,$//')
N_SINGLE=$(echo "$SINGLE" | tr ',' '\n' | grep -c .)
read -r -a COLD <<< "$(echo "${COLD_USERS:-}" | tr ',' ' ')"
read -r -a CELL_LIST <<< "$CELLS"
cold_next=0

OUT=results/$RUN
REMOTE_JSONL=$LOAD_DIR/results/$RUN.jsonl
LOCAL_JSONL=$OUT/logins.jsonl
problems=0

utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(date -u +%H:%M:%S)] $*"; }
loud() {
    echo "##########################################################################" >&2
    echo "[$(date -u +%H:%M:%S)] $*" >&2
    echo "##########################################################################" >&2
}
is_int() { case "$1" in '' | *[!0-9]*) return 1 ;; esac; }
field() { echo "$1" | tr ' ' '\n' | sed -n "s/^$2=//p" | tail -1; }

annotate() {
    [ -n "$GRAFANA" ] || return 0
    $SSH "$GRAFANA" "$GRAFANA_ANNOTATE '$1'" </dev/null >/dev/null 2>&1 || log "warning: Grafana annotation failed"
}
browser() {
    $SSH "$NODE" "cd $LOAD_DIR && podman run --rm --ipc=host --env-file .env -v \$PWD:/work:Z -w /work $LOAD_IMAGE python3 loadtest.py --run $RUN $*" </dev/null
}
remote_count() {
    $SSH "$NODE" "cat $REMOTE_JSONL 2>/dev/null | wc -l" </dev/null 2>/dev/null | tr -d '[:space:]'
}
healthy() {
    local code
    code=$(curl -sk -m 60 -u "$AAP_USER:$AAP_PASS" -o /dev/null -w '%{http_code}' "$AAP_URL/api/gateway/v1/me/")
    [ "$code" = 200 ]
}
sync_results() {
    if $SCP "$NODE:$REMOTE_JSONL" "$LOCAL_JSONL.tmp" && mv "$LOCAL_JSONL.tmp" "$LOCAL_JSONL"; then
        log "synced $(wc -l < "$LOCAL_JSONL") login records to $LOCAL_JSONL"
    else
        rm -f "$LOCAL_JSONL.tmp"
        problems=$((problems + 1))
        loud "RESULT SYNC FAILED: could not copy $REMOTE_JSONL from the load node"
        return 1
    fi
}
abort() {
    local code=$1
    shift
    loud "ABORT: $* - leaving toggle OFF"
    $PYTHON aap_setup.py toggle off
    sync_results
    exit "$code"
}
gw_pods() {
    local pods
    pods=$(oc -n "$NS" get pod -l "$GW_SELECTOR" -o name 2>/dev/null | grep -E "$GW_POD_REGEX")
    [ -z "$pods" ] && pods=$(oc -n "$NS" get pod -o name 2>/dev/null | grep -E 'gateway-[a-z0-9]+-[a-z0-9]+$')
    echo "$pods" | sed 's#^pod/##' | grep . | sort
}
replicas() {
    # replicas <start|end> <pods>
    local n
    n=$(echo "$2" | grep -c .)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$rep" "$seq" "$cell" "$1" "$(utc)" "$n" "$(echo "$2" | tr '\n' ',' | sed 's/,$//')" >> "$OUT/replicas.tsv"
    [ "$n" -gt 0 ] || { problems=$((problems + 1)); loud "NO GATEWAY PODS FOUND at cell $1 ($cell): selector '$GW_SELECTOR' in namespace '$NS'"; }
    log "gateway replicas at cell $1: $n"
}

run_phase() {
    # run_phase <phase> <expected records> <loadtest.py arguments...>
    local phase=$1 expected=$2 before after actual rc start end
    shift 2
    before=$(remote_count)
    start=$(utc)
    browser --scale "$scale" --toggle "$toggle" --cell-seq "$seq" --rep "$rep" --phase "$phase" --think-seed "$THINK_SEED" "$@"
    rc=$?
    end=$(utc)
    after=$(remote_count)
    if is_int "$before" && is_int "$after"; then actual=$((after - before)); else actual=NA; fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$cell" "$phase" "$expected" "$actual" "$rc" "$start" "$end" >> "$OUT/phases.tsv"
    if [ "$rc" != 0 ] || [ "$actual" = 0 ] || [ "$actual" = NA ]; then
        problems=$((problems + 1))
        loud "PHASE FAILED: cell $cell phase $phase $* - exit code $rc, records $actual of $expected"
        [ "$ON_PHASE_FAIL" = continue ] || abort 3 "phase $phase failed in cell $cell"
    elif [ "$actual" != "$expected" ]; then
        problems=$((problems + 1))
        loud "PHASE SHORT: cell $cell phase $phase $* - records $actual of $expected"
    else
        log "phase $phase ok: $actual records"
    fi
}

flip() {
    local out rc res t0 t1 start
    start=$(utc)
    t0=$(date +%s.%N)
    out=$($PYTHON aap_setup.py toggle "$toggle" 2>&1)
    rc=$?
    t1=$(date +%s.%N)
    echo "$out"
    res=$(echo "$out" | grep '^toggle-result' | tail -1)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$rep" "$seq" "$cell" "$scale" "$toggle" \
        "$(field "$res" maps)" "$(field "$res" patched)" "$(field "$res" failed)" "$(field "$res" retried)" "$(field "$res" elapsed_s)" \
        "$(awk "BEGIN { printf \"%.2f\", $t1 - $t0 }")" "$rc" "$start" >> "$OUT/toggle-flip.tsv"
    log "toggle $toggle: ${res:-no result line} exit=$rc"
    return $rc
}

collect_gateway() {
    # collect_gateway <start time> <pods>
    local pod lines=0
    : > "$OUT/restarts-$cell.txt"
    for pod in $2; do
        { oc -n "$NS" logs "$pod" -c "$GW_CONTAINER" --previous --since-time="$1" 2>/dev/null
          oc -n "$NS" logs "$pod" -c "$GW_CONTAINER" --since-time="$1" 2>/dev/null; } | grep -E "$GW_LOG_PATTERN" > "$OUT/gwlog-$cell-$pod.log"
        printf '%s\t%s\n' "$pod" "$(oc -n "$NS" get pod "$pod" -o jsonpath='{.status.containerStatuses[*].restartCount}' 2>/dev/null)" >> "$OUT/restarts-$cell.txt"
        lines=$((lines + $(wc -l < "$OUT/gwlog-$cell-$pod.log")))
    done
    log "cell $cell done: $lines gateway log lines from $(echo "$2" | grep -c .) pods, restarts: $(tr '\t\n' '= ' < "$OUT/restarts-$cell.txt")"
}

# ---- checks that need no network
is_int "$REPEAT" && is_int "$POOL_SIZE" && is_int "$STEADY_ITER" && is_int "$CONC_ITER" && is_int "$COLD_ITER" && is_int "$COLD_PER_CELL" && is_int "$THINK_SEED" \
    || { echo "REPEAT, PERF_POOL_SIZE, STEADY_ITER, CONC_ITER, COLD_ITER, COLD_PER_CELL and THINK_SEED must be integers" >&2; exit 1; }
[ "$REPEAT" -ge 1 ] && [ "${#CELL_LIST[@]}" -ge 1 ] || { echo "nothing to run: REPEAT=$REPEAT CELLS='$CELLS'" >&2; exit 1; }
for c in "${CELL_LIST[@]}"; do
    [[ $c =~ ^[0-9]+:(on|off)$ ]] || { echo "bad cell '$c' in CELLS, expected <mappers>:<on|off>" >&2; exit 1; }
done
for level in $RAMP; do
    is_int "$level" && [ "$level" -ge 1 ] || { echo "bad concurrency '$level' in RAMP" >&2; exit 1; }
    [ "$level" -le "$POOL_SIZE" ] || echo "warning: concurrency $level exceeds the pool of $POOL_SIZE users, users will log in more than once at a time" >&2
done
cold_needed=$((${#CELL_LIST[@]} * REPEAT * COLD_PER_CELL))
if [ "${#COLD[@]}" -gt 0 ] && [ "${#COLD[@]}" -lt "$cold_needed" ]; then
    echo "COLD_USERS has ${#COLD[@]} users but ${#CELL_LIST[@]} cells x $REPEAT repeats x $COLD_PER_CELL per cell need $cold_needed" >&2
    exit 1
fi
if [ "${#COLD[@]}" -gt 0 ] && [ "$(printf '%s\n' "${COLD[@]}" | sort | uniq -d | wc -l)" != 0 ]; then
    echo "COLD_USERS contains duplicates, every cold user can be used once only" >&2
    exit 1
fi
if [ -e "$OUT/phases.tsv" ]; then
    echo "$OUT already holds a run, choose a new run id" >&2
    exit 1
fi

mkdir -p "$OUT"
printf 'cell\tphase\texpected_records\tactual_records\texit_code\tstart_utc\tend_utc\n' > "$OUT/phases.tsv"
printf 'rep\tcell_seq\tcell\tscale\ttoggle\tmaps\tpatched\tfailed\tretried\telapsed_s\twall_s\texit_code\tstart_utc\n' > "$OUT/toggle-flip.tsv"
printf 'rep\tcell_seq\tcell\twhen\tutc\treplicas\tpods\n' > "$OUT/replicas.tsv"
{
    echo "run=$RUN"
    echo "started_utc=$(utc)"
    echo "git_commit=$(git rev-parse HEAD 2>/dev/null)"
    echo "git_dirty_files=$(git status --porcelain 2>/dev/null | grep -vc '^??')"
    echo "sha256_loadtest=$(sha256sum loadtest.py | cut -d' ' -f1)"
    echo "sha256_aap_setup=$(sha256sum aap_setup.py | cut -d' ' -f1)"
    echo "sha256_run_matrix=$(sha256sum run_matrix.sh | cut -d' ' -f1)"
    echo "cells=${CELL_LIST[*]}"
    echo "repeat=$REPEAT"
    echo "ramp=$RAMP"
    echo "steady_iter=$STEADY_ITER conc_iter=$CONC_ITER cold_iter=$COLD_ITER cold_per_cell=$COLD_PER_CELL"
    echo "pool_size=$POOL_SIZE"
    echo "single_users=$SINGLE"
    echo "cold_users=${COLD[*]:-}"
    echo "think_min=$THINK_MIN think_max=$THINK_MAX think_seed=$THINK_SEED"
    echo "on_phase_fail=$ON_PHASE_FAIL"
} > "$OUT/run-meta.txt"

# ---- the load node must run the same loadtest.py as this checkout
if [ "$PUSH_LOADTEST" = 1 ]; then
    $SCP loadtest.py "$NODE:$LOAD_DIR/loadtest.py" || { loud "could not copy loadtest.py to the load node"; exit 1; }
fi
remote_sha=$($SSH "$NODE" "sha256sum $LOAD_DIR/loadtest.py" </dev/null 2>/dev/null | cut -d' ' -f1)
if [ "$remote_sha" != "$(sha256sum loadtest.py | cut -d' ' -f1)" ]; then
    loud "loadtest.py on the load node differs from this checkout (or cannot be read). Copy it, or run with PUSH_LOADTEST=1"
    exit 1
fi
if [ "$(remote_count)" != 0 ]; then
    loud "$REMOTE_JSONL on the load node is not empty (or cannot be read), choose a new run id"
    exit 1
fi

for rep in $(seq 1 "$REPEAT"); do
    seq=0
    for c in "${CELL_LIST[@]}"; do
        seq=$((seq + 1))
        scale=${c%%:*}
        toggle=${c##*:}
        cell=$(printf 'r%d-c%02d-scale%s-%s' "$rep" "$seq" "$scale" "$toggle")

        log "=== cell $cell (rep $rep of $REPEAT, cell $seq of ${#CELL_LIST[@]}): ensuring $scale mappers"
        $PYTHON aap_setup.py maps "$scale" || abort 1 "map setup failed before $cell"
        log "=== cell $cell: setting toggle $toggle"
        flip || abort 1 "toggle $toggle failed before $cell"
        $PYTHON aap_setup.py verify "$scale" "$toggle" || abort 1 "verify failed before $cell: mappers are not in the expected state"

        start=$(utc)
        pods_start=$(gw_pods)
        replicas start "$pods_start"
        annotate "$RUN rep=$rep cell=$seq mappers=$scale toggle=$toggle start"

        run_phase first "$N_SINGLE" --users "$SINGLE" --iterations 1 --think-min "$THINK_MIN" --think-max "$THINK_MAX"
        if [ "${#COLD[@]}" -gt 0 ]; then
            [ $((cold_next + COLD_PER_CELL)) -le "${#COLD[@]}" ] || abort 1 "COLD_USERS exhausted at cell $cell"
            cold=$(echo "${COLD[@]:cold_next:COLD_PER_CELL}" | tr ' ' ',')
            cold_next=$((cold_next + COLD_PER_CELL))
            log "cold users for $cell: $cold"
            run_phase cold $((COLD_PER_CELL * COLD_ITER)) --users "$cold" --iterations "$COLD_ITER" --think-min "$THINK_MIN" --think-max "$THINK_MAX"
        fi
        run_phase steady $((N_SINGLE * STEADY_ITER)) --users "$SINGLE" --iterations "$STEADY_ITER" --think-min "$THINK_MIN" --think-max "$THINK_MAX"
        run_phase pool-first "$POOL_SIZE" --users "$POOL" --iterations 1 --think-min "$THINK_MIN" --think-max "$THINK_MAX"
        for level in $RAMP; do
            run_phase concurrent $((POOL_SIZE * CONC_ITER)) --users "$POOL" --iterations "$CONC_ITER" --concurrency "$level" --think-min 0 --think-max 0
        done

        annotate "$RUN rep=$rep cell=$seq mappers=$scale toggle=$toggle end"
        pods_end=$(gw_pods)
        replicas end "$pods_end"
        collect_gateway "$start" "$(printf '%s\n%s\n' "$pods_start" "$pods_end" | grep . | sort -u)"
        $PYTHON aap_setup.py status > "$OUT/status-$cell.txt" || { problems=$((problems + 1)); loud "status call failed after $cell"; }
        sync_results

        if ! healthy; then
            abort 2 "admin login health check failed after $cell"
        fi
    done
done

log "=== restoring toggle off"
$PYTHON aap_setup.py toggle off || { problems=$((problems + 1)); loud "restoring toggle off FAILED"; }
sync_results
log "done: $(wc -l < "$LOCAL_JSONL" 2>/dev/null || echo 0) login records in $LOCAL_JSONL"
if [ "$problems" != 0 ]; then
    loud "$problems problem(s) during the run, see above and $OUT/phases.tsv"
    exit 4
fi
