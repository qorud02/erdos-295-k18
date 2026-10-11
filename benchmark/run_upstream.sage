#!/usr/bin/env sage -python
"""Run the author's pinned Sage solver; Linux/POSIX, no redistributed source.

Invocation: sage -python benchmark/run_upstream.sage --manifest PATH --out-dir PATH
The wrapper is ordinary Python so --check-only also works without Sage installed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import select
import signal
import sys
import time
import traceback
import urllib.request

COMMIT = "8680599e77683a9057ee55871a0893bb319300e8"
SOURCE_SHA256 = "4febfdbee3710f05775f41bc15a9046984c69da1f7a53f105116579a663ad480"
SOURCE_URL = "https://raw.githubusercontent.com/maxale/egyptian-fractions/" + COMMIT + "/egypt_rep.sage"
IMAGE = "sagemath/sagemath:10.8@sha256:e2e4747b0e1ea8753a9cb5a399314a8b2c25fcefaf69ba85b22ee075829d09ea"
FOUR = ((2, 3, 7, 42), (2, 3, 8, 24), (2, 3, 9, 18),
        (2, 3, 10, 15), (2, 4, 5, 20), (2, 4, 6, 12))


def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def expected_instance_ids():
    return ([f"broad-{u:03d}-{v:03d}" for u in range(45, 65) for v in range(u+1, 65)]
            + [f"structural-{z:03d}" for z in range(49, 80)]
            + [f"control-next-{z}" for z in (31, 32, 33)])


def read_manifest(path, suite):
    raw = Path(path).read_bytes()
    obj = json.loads(raw)
    instances = obj["instances"] if isinstance(obj, dict) else obj
    if [x["id"] for x in instances] != expected_instance_ids():
        raise ValueError("manifest must contain the frozen 224 cases in the declared order")
    for case in instances:
        prefix = [int(x) for x in case["prefix"]]
        if prefix != sorted(set(prefix)) or not prefix or prefix[0] < 18:
            raise ValueError("invalid strictly increasing prefix")
        if int(case["minimum"]) != 18 or int(case["terms"]) != 33:
            raise ValueError("manifest problem identity mismatch")
        residual = Fraction(1) - sum((Fraction(1, x) for x in prefix), Fraction())
        if residual <= 0 or int(case["terms_remaining"]) != 33-len(prefix):
            raise ValueError("invalid residual/remaining count")
        if residual != Fraction(int(case["residual_numerator"]), int(case["residual_denominator"])):
            raise ValueError("manifest residual disagrees with exact prefix arithmetic")
        # Check the actual frozen prefixes as well as their identities.
        if case["family"] == "broad":
            _, u, v = case["id"].split("-")
            expected = list(range(18, 29)) + list(range(30, 45)) + [int(u), int(v)]
        elif case["family"] == "structural":
            z = int(case["id"].split("-")[-1])
            expected = [18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,
                        34,35,36,38,39,40,43,44,45,46,48,z]
        elif case["family"] == "control":
            expected = list(range(18, 29)) + [int(case["id"].split("-")[-1])]
        else:
            raise ValueError("unknown frozen family")
        if prefix != expected:
            raise ValueError("prefix differs from frozen selection rule")
    selected = []
    broad_index = 0
    for case in instances:
        if case["family"] == "broad":
            keep = suite == "all" or broad_index % 10 == 0
            broad_index += 1
        else:
            keep = True
        if keep:
            selected.append(case)
    if len(selected) != (224 if suite == "all" else 53):
        raise ValueError("unexpected suite selection count")
    return instances, selected, hashlib.sha256(raw).hexdigest()


def api_controls():
    return [
        {"id":"api-one-1-2-min2", "api":"one_rep", "target":"1", "terms":2, "minimum":2, "expected":[]},
        {"id":"api-one-1-3-min2", "api":"one_rep", "target":"1", "terms":3, "minimum":2, "expected":[[2,3,6]]},
        {"id":"api-one-1-4-min2", "api":"one_rep", "target":"1", "terms":4, "minimum":2, "expected":[list(x) for x in FOUR]},
        {"id":"api-one-1-4-min3", "api":"one_rep", "target":"1", "terms":4, "minimum":3, "expected":[]},
        {"id":"api-one-half-2-min3", "api":"one_rep", "target":"1/2", "terms":2, "minimum":3, "expected":[[3,6]]},
        {"id":"api-all-1-4-min2", "api":"all_rep", "target":"1", "terms":4, "minimum":2, "expected":[list(x) for x in FOUR]},
    ]


def verify_denominators(ds, target, terms, minimum, prefix=()):
    if len(ds) != terms or ds != sorted(set(ds)) or (ds and ds[0] < minimum):
        raise ValueError("invalid count/order/distinctness/minimum in returned witness")
    if ds[:len(prefix)] != list(prefix):
        raise ValueError("returned witness fails to extend prefix")
    if sum((Fraction(1, x) for x in ds), Fraction()) != target:
        raise ValueError("returned witness fails exact reciprocal sum")


def load_upstream():
    # Set all controls before importing Sage's parallel runtime.
    for name in ("SAGE_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"
    with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("upstream SHA-256 mismatch; source will not be executed")
    import sage.all as sage_all
    from sage.repl.preparse import preparse
    from sage.parallel.map_reduce import proc_number
    from sage.env import SAGE_VERSION
    if int(proc_number()) != 1:
        raise RuntimeError("Sage map-reduce did not honor single-worker setting")
    namespace = dict(vars(sage_all))
    namespace["__name__"] = "upstream_egypt_rep"
    exec(compile(preparse(raw.decode("utf-8")), SOURCE_URL, "exec"), namespace)
    if namespace["BERTRAM"] is not False:
        raise ValueError("unexpected upstream BERTRAM restriction")
    return namespace, sage_all.QQ, str(SAGE_VERSION), int(proc_number())


def send_pipe(fd, obj):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    while data:
        count = os.write(fd, data)
        data = data[count:]


def child_job(fd, log_path, api, target, terms, minimum, namespace, QQ):
    started = None
    try:
        # A distinct process group contains this case and all Sage fork workers.
        os.setsid()
        log_fd = os.open(str(log_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        os.dup2(log_fd, 1)
        os.dup2(log_fd, 2)
        os.close(log_fd)
        rational = QQ(target.numerator) / QQ(target.denominator)
        send_pipe(fd, {"event":"ready", "pid":os.getpid()})
        started = time.perf_counter()
        value = namespace[api](rational, terms, min_denom=minimum, distinct=True)
        elapsed = time.perf_counter() - started
        if api == "all_rep":
            result = sorted([list(map(int, row)) for row in value])
        else:
            result = None if value is None else list(map(int, value))
        send_pipe(fd, {"event":"answer", "solver_seconds":elapsed, "value":result})
        os.close(fd)
        os._exit(0)
    except BaseException as exc:
        elapsed = None if started is None else time.perf_counter() - started
        try:
            send_pipe(fd, {"event":"error", "solver_seconds":elapsed,
                           "error":type(exc).__name__ + ": " + str(exc),
                           "traceback":traceback.format_exc()[-4000:]})
        except BaseException:
            pass
        os._exit(1)


def kill_case(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def run_case(api, target, terms, minimum, namespace, QQ, seconds, log_path):
    read_fd, write_fd = os.pipe()
    sys.stdout.flush()
    sys.stderr.flush()
    wall_started = time.perf_counter()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        child_job(write_fd, log_path, api, target, terms, minimum, namespace, QQ)
    os.close(write_fd)
    buffer = b""
    ready = None
    answer = None
    deadline = wall_started + 15.0  # fork/setup watchdog, outside solver timing
    timed_out = False
    try:
        while answer is None:
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                timed_out = True
                break
            readable, _, _ = select.select([read_fd], [], [], min(remaining, 0.05))
            if not readable:
                continue
            block = os.read(read_fd, 65536)
            if not block:
                break
            buffer += block
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                message = json.loads(line)
                if message.get("event") == "ready":
                    ready = time.perf_counter()
                    # Small cleanup grace does not make late completions uncensored.
                    deadline = ready + seconds + 0.25
                else:
                    answer = message
    finally:
        os.close(read_fd)
        # Always remove the case's process group, including any leftover Sage worker.
        kill_case(pid)
    wall = time.perf_counter() - wall_started
    if timed_out:
        return {"status":"timeout" if ready is not None else "startup-timeout",
                "complete":False, "censored":True, "wall_seconds":wall,
                "solver_seconds":None, "solver_seconds_lower_bound":seconds if ready is not None else None}
    if answer is None:
        return {"status":"error", "complete":False, "censored":False,
                "wall_seconds":wall, "error":"case process exited without an answer"}
    if answer["event"] == "error":
        return dict(answer, status="error", complete=False, censored=False, wall_seconds=wall)
    elapsed = answer["solver_seconds"]
    if elapsed > seconds:
        return dict(answer, status="late-result", complete=False, censored=True,
                    wall_seconds=wall, solver_seconds_lower_bound=seconds)
    return dict(answer, status="answered", complete=True, censored=False, wall_seconds=wall)


def main():
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("benchmark/upstream-results"))
    parser.add_argument("--suite", choices=("pilot", "all"), default="pilot")
    parser.add_argument("--seconds", type=float, default=5.0)
    parser.add_argument("--control-seconds", type=float, default=30.0)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--no-pin-cpu", action="store_true")
    args = parser.parse_args()
    if any(not math.isfinite(x) or x <= 0 for x in (args.seconds, args.control_seconds)):
        parser.error("time budgets must be positive")
    instances, selected, manifest_sha = read_manifest(args.manifest, args.suite)
    selection = {"suite":args.suite, "full_manifest_sha256":manifest_sha,
                 "full_manifest_instances":len(instances), "selected_instances":len(selected),
                 "selection_rule":"all control and structural cases; broad zero-based ordinal divisible by10" if args.suite=="pilot" else "all224 frozen cases",
                 "instance_ids":[x["id"] for x in selected], "api_controls":api_controls()}
    if args.check_only:
        print(json.dumps(dict(selection, status="manifest-validated-no-Sage-execution")))
        return 0
    if not hasattr(os, "fork") or not hasattr(os, "setsid"):
        parser.error("real execution requires Linux/POSIX Sage; use official Docker image")
    out = args.out_dir.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error("output directory must be new/empty to preserve previous evidence")
    out.mkdir(parents=True, exist_ok=True)
    (out/"logs").mkdir()
    dump(out/"selection.json", selection)
    affinity = None
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        if not args.no_pin_cpu:
            os.sched_setaffinity(0, {min(affinity)})
            affinity = sorted(os.sched_getaffinity(0))
    load_started = time.perf_counter()
    namespace, QQ, sage_version, workers = load_upstream()
    metadata = {"created_utc":utcnow(), "upstream_commit":COMMIT,
                "upstream_source_url":SOURCE_URL, "upstream_sha256":SOURCE_SHA256,
                "wrapper_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "official_image_recommendation":IMAGE, "sage_version":sage_version,
                "python":sys.version, "platform":platform.platform(),
                "cpu_affinity":affinity, "sage_map_reduce_workers":workers,
                "manifest_sha256":manifest_sha, "suite":args.suite,
                "seconds_limit":args.seconds, "control_seconds_limit":args.control_seconds,
                "source_fetch_and_Sage_load_seconds":time.perf_counter()-load_started,
                "timing":"solver timer surrounds unchanged original API; excludes Sage startup/source fetch/load/fork; includes API parallel setup and cleanup; wall_seconds includes case fork and watchdog cleanup",
                "semantics":"exact rational sum, distinct increasing denominators, no maximum denominator, no overlap-quota pruning in upstream",
                "watchdog":"separate POSIX session per case; parent kills entire case process group; late answers remain censored",
                "preprocessing":"local exclusion-premise derivation is excluded from these upstream timings and must be charged separately for cold-start comparisons"}
    dump(out/"metadata.json", metadata)
    rows = []
    fatal_controls = False
    with (out/"runs.jsonl").open("w", encoding="utf-8", buffering=1) as stream:
        def save(row):
            rows.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print(json.dumps({"event":"upstream-progress", "id":row["instance_id"], "status":row["status"], "recorded":len(rows)}), flush=True)

        for control in api_controls():
            row = {"instance_id":control["id"], "family":"api-control", "api":control["api"],
                   "expected_solution_set":control["expected"], "started_utc":utcnow(),
                   "seconds_limit":args.control_seconds}
            result = run_case(control["api"], Fraction(control["target"]), control["terms"], control["minimum"],
                              namespace, QQ, args.control_seconds, out/"logs"/(control["id"]+".txt"))
            row.update(result)
            if result["status"] == "answered":
                try:
                    value = result["value"]
                    expected = {tuple(x) for x in control["expected"]}
                    if control["api"] == "all_rep":
                        actual = {tuple(x) for x in value}
                        for ds in value:
                            verify_denominators(ds, Fraction(control["target"]), control["terms"], control["minimum"])
                        if actual != expected:
                            raise ValueError("all_rep did not return the exact declared solution set")
                    else:
                        if value is not None:
                            verify_denominators(value, Fraction(control["target"]), control["terms"], control["minimum"])
                        if (value is None) != (not expected) or (value is not None and tuple(value) not in expected):
                            raise ValueError("one_rep control outcome disagrees with exact expected set")
                    row["status"] = "control-passed"
                except (ValueError, TypeError) as exc:
                    row.update(status="invalid-result", complete=False, error=str(exc))
            if row["status"] != "control-passed":
                fatal_controls = True
            save(row)
        # Preserve all declared cases even when a control failed: mark them not run.
        for case in selected:
            row = {"instance_id":case["id"], "family":case["family"], "api":"one_rep",
                   "prefix":case["prefix"], "minimum":18, "terms":33,
                   "residual_numerator":case["residual_numerator"],
                   "residual_denominator":case["residual_denominator"],
                   "terms_remaining":case["terms_remaining"], "max_denominator":None,
                   "seconds_limit":args.control_seconds if case["family"]=="control" else args.seconds,
                   "started_utc":utcnow()}
            if fatal_controls:
                row.update(status="not-run-control-failure", complete=False, censored=False)
                save(row)
                continue
            prefix = [int(x) for x in case["prefix"]]
            target = Fraction(int(case["residual_numerator"]), int(case["residual_denominator"]))
            result = run_case("one_rep", target, int(case["terms_remaining"]), prefix[-1]+1,
                              namespace, QQ, row["seconds_limit"], out/"logs"/(case["id"]+".txt"))
            row.update(result)
            if result["status"] in ("answered", "late-result"):
                try:
                    ds = None if result["value"] is None else prefix + result["value"]
                    if ds is not None:
                        verify_denominators(ds, Fraction(1), 33, 18, prefix)
                    row["denominators"] = None if ds is None else list(map(str, ds))
                    row["answer_status"] = "exhausted" if ds is None else "witness"
                    if result["status"] == "answered":
                        row["status"] = row["answer_status"]
                except (ValueError, TypeError) as exc:
                    row.update(status="invalid-result", complete=False, error=str(exc))
            save(row)
    case_rows = [x for x in rows if x["family"] != "api-control"]
    summary = {"created_utc":utcnow(), "upstream_commit":COMMIT, "manifest_sha256":manifest_sha,
               "suite":args.suite, "expected_case_rows":len(selected), "recorded_case_rows":len(case_rows),
               "api_controls_passed":not fatal_controls, "status_counts":dict(Counter(x["status"] for x in case_rows)),
               "complete_cases":sum(x["complete"] for x in case_rows),
               "censored_cases":sum(x["censored"] for x in case_rows),
               "errors":sum(x["status"] in ("error", "invalid-result", "not-run-control-failure") for x in case_rows),
               "interpretation":"bounded original-Sage pilot, not a general speedup or global33-term exclusion"}
    dump(out/"summary.json", summary)
    print(json.dumps(dict(summary, event="upstream-complete")), flush=True)
    return 1 if fatal_controls or summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
