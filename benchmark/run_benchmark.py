#!/usr/bin/env python3
"""Serial, fixed-manifest OFF/single/nested benchmark; Python standard library only."""
from __future__ import annotations
import argparse
import datetime as dt
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

MODES = ("off", "single", "nested")
BASE = (18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,63,275,14143068,10457416992)
SMALL = set(BASE[:-2])

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def generate_instances():
    instances = []
    p0 = list(range(18,29)) + list(range(30,45))
    for u in range(45,65):
        for v in range(u+1,65):
            instances.append({"id":f"broad-{u:03d}-{v:03d}", "family":"broad", "prefix":p0+[u,v]})
    p1 = list(BASE[:27])
    for z in range(49,80):
        instances.append({"id":f"structural-{z:03d}", "family":"structural", "prefix":p1+[z]})
    for z in (31,32,33):
        instances.append({"id":f"control-next-{z}", "family":"control", "prefix":list(range(18,29))+[z]})
    assert len(instances) == 224
    for instance in instances:
        prefix = instance["prefix"]
        assert len(prefix) <= 33 and prefix == sorted(set(prefix)) and prefix[0] >= 18
        residual = 1 - sum((Fraction(1,d) for d in prefix), Fraction())
        assert residual > 0
        remaining = 33-len(prefix)
        harmonic = sum((Fraction(1,d) for d in range(prefix[-1]+1,prefix[-1]+1+remaining)), Fraction())
        instance.update({"minimum":18, "terms":33, "terms_remaining":remaining,
                         "residual_numerator":str(residual.numerator),
                         "residual_denominator":str(residual.denominator),
                         "selected_reference":len(set(prefix)&set(BASE)),
                         "selected_small_reference":len(set(prefix)&SMALL),
                         "root_harmonic_feasible":harmonic>=residual})
    return instances

def validate_result(instance, mode, result, require_mode=True):
    if result.get("minimum") != 18 or result.get("terms") != 33:
        raise ValueError("solver instance identity mismatch")
    if result.get("prefix") != instance["prefix"]:
        raise ValueError("solver prefix mismatch")
    if require_mode and result.get("quota_mode") != MODES.index(mode):
        raise ValueError("solver mode mismatch")
    status = result.get("status")
    if status not in ("exhausted", "witness", "timeout"):
        raise ValueError("unknown solver status")
    if status == "witness":
        ds = [int(x) for x in result["denominators"]]
        if len(ds) != 33 or ds != sorted(set(ds)) or ds[0] < 18:
            raise ValueError("invalid witness denominators")
        if ds[:len(instance["prefix"])] != instance["prefix"]:
            raise ValueError("witness does not extend fixed prefix")
        if sum((Fraction(1,d) for d in ds), Fraction()) != 1:
            raise ValueError("invalid exact witness sum")
        lcm = 1
        for d in ds:
            lcm = math.lcm(lcm, d)
        if sum(lcm//d for d in ds) != lcm:
            raise ValueError("invalid scaled LCM witness sum")
        if len(set(ds)&set(BASE)) > 28 or len(set(ds)&SMALL) > 27:
            raise ValueError("witness contradicts certified quota premise")
    return status

def summarize(records, instances, repeats, metadata):
    grouped = {}
    for row in records:
        grouped[(row["instance_id"],row["repetition"]) , row["mode"]] = row
    paired = []
    mismatches = []
    for instance in instances:
        for repetition in range(repeats):
            rows = [grouped.get(((instance["id"],repetition),mode)) for mode in MODES]
            if not all(rows):
                continue
            if all(row["complete"] for row in rows):
                answers = [(row["status"],row.get("result",{}).get("denominators")) for row in rows]
                if answers[1:] != answers[:-1]:
                    mismatches.append({"instance_id":instance["id"], "repetition":repetition, "answers":answers})
                paired.append({"instance_id":instance["id"], "family":instance["family"],
                               "repetition":repetition,
                               "answers_agree":answers[1:]==answers[:-1],
                               "runs":{mode:{"seconds":row["result"]["elapsed_seconds"],
                                             "wall_seconds":row["wall_seconds"],
                                             "nodes":row["result"]["nodes"],
                                             "two_candidates":row["result"].get("two_candidates",0),
                                             "quota_prunes":row["result"].get("base_quota_prunes",0)}
                                       for mode,row in zip(MODES,rows)}})
    per_mode = {}
    for mode in MODES:
        rows = [r for r in records if r["mode"]==mode]
        per_mode[mode] = {"runs":len(rows), "complete":sum(r["complete"] for r in rows),
                          "censored":sum(r["censored"] for r in rows),
                          "errors":sum(r["status"] in ("error","invalid-result") for r in rows),
                          "all_run_wall_seconds":sum(r["wall_seconds"] for r in rows),
                          "statuses":{s:sum(r["status"]==s for r in rows) for s in sorted({r["status"] for r in rows})}}
    # Only instances completed in all modes in all declared repetitions enter the median paired table.
    complete_instances = []
    for instance in instances:
        rows = [p for p in paired if p["instance_id"]==instance["id"]]
        if len(rows) != repeats or not all(p["answers_agree"] for p in rows):
            continue
        mode_stats = {}
        for mode in MODES:
            node_values = [p["runs"][mode]["nodes"] for p in rows]
            candidate_values = [p["runs"][mode]["two_candidates"] for p in rows]
            mode_stats[mode] = {
                "median_solver_seconds":statistics.median(p["runs"][mode]["seconds"] for p in rows),
                "median_wall_seconds":statistics.median(p["runs"][mode]["wall_seconds"] for p in rows),
                "nodes":node_values[0], "nodes_deterministic":len(set(node_values))==1,
                "two_candidates":candidate_values[0], "two_candidates_deterministic":len(set(candidate_values))==1,
                "quota_prunes":rows[0]["runs"][mode]["quota_prunes"]}
        complete_instances.append({"instance_id":instance["id"], "family":instance["family"], "modes":mode_stats})
    family_stats = {}
    for family in ("broad","structural","control","all"):
        selected = [x for x in complete_instances if family=="all" or x["family"]==family]
        counts = len([x for x in instances if family=="all" or x["family"]==family])
        totals = {mode:{"sum_median_solver_seconds":sum(x["modes"][mode]["median_solver_seconds"] for x in selected),
                       "sum_median_wall_seconds":sum(x["modes"][mode]["median_wall_seconds"] for x in selected),
                       "nodes":sum(x["modes"][mode]["nodes"] for x in selected),
                       "two_candidates":sum(x["modes"][mode]["two_candidates"] for x in selected),
                       "quota_prunes":sum(x["modes"][mode]["quota_prunes"] for x in selected)} for mode in MODES}
        ratios = {}
        for mode in ("single","nested"):
            den = totals[mode]["sum_median_solver_seconds"]
            ratios[mode] = None if den<=0 else totals["off"]["sum_median_solver_seconds"]/den
        family_stats[family] = {"declared_instances":counts, "all_repetitions_triple_complete_instances":len(selected),
                                "selection":"fixed input suite; this table is restricted to all-repetition triple-complete instances",
                                "totals":totals, "conditional_online_solver_time_ratio_off_over_mode":ratios,
                                "whole_suite_speedup_supported":False if len(selected)!=counts else "evaluate absolute times and preprocessing separately"}
    return {"created_utc":utcnow(), "manifest_sha256":metadata["manifest_sha256"],
            "source_sha256":metadata["source_sha256"], "binary_sha256":metadata["binary_sha256"],
            "expected_runs":len(instances)*repeats*3, "recorded_runs":len(records),
            "per_mode":per_mode, "triple_complete_pairs":len(paired),
            "all_repetitions_triple_complete_instances":len(complete_instances),
            "answer_mismatches":mismatches, "family_stats":family_stats,
            "completed_instance_medians":complete_instances,
            "cost_scope":metadata["preprocessing"],
            "interpretation":"Censored runs remain recorded. Complete-subset ratios are conditional online measurements, not a whole-suite or cold-start speedup. Special structural cases exercise the lemma and do not establish general search performance."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    engine_group=parser.add_mutually_exclusive_group(required=True)
    engine_group.add_argument("--binary", type=Path)
    engine_group.add_argument("--engine-dir", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent/"results")
    parser.add_argument("--seconds", type=float, default=2.0)
    parser.add_argument("--control-seconds", type=float, default=30.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--mode-flag", default="--quota-mode")
    parser.add_argument("--no-joint", action="store_true")
    parser.add_argument("--compiler-note", default="See build-matched.cmd; compiler/GMP version must be recorded separately.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.seconds <= 0 or args.control_seconds <= 0 or args.repeats < 1:
        parser.error("positive time limits and repetitions required")
    if args.engine_dir:
        engine_dir=args.engine_dir.resolve()
        names={"off":"checkpoint-search","single":"quota-search","nested":"laminar-search"}
        engines={mode:{"binary":engine_dir/(name+(".exe" if os.name=="nt" else "")), "source":engine_dir/(name+".cpp")} for mode,name in names.items()}
        engine_kind="three-preserved-executables"
    else:
        binary=args.binary.resolve()
        source=args.source.resolve() if args.source else Path(__file__).resolve().parent/"matched-search.cpp"
        engines={mode:{"binary":binary,"source":source} for mode in MODES}
        engine_kind="single-matched-executable"
    if any(not e["source"].is_file() or (not args.dry_run and not e["binary"].is_file()) for e in engines.values()):
        parser.error("all sources and compiled binaries must exist")
    out = args.out_dir.resolve()
    if (out/"runs.jsonl").exists() or (out/"manifest.json").exists():
        parser.error("output already contains a run; choose a fresh --out-dir to preserve evidence")
    out.mkdir(parents=True, exist_ok=True)
    (out/"logs").mkdir(exist_ok=True)
    instances = generate_instances()
    manifest = {"created_utc":utcnow(), "minimum":18, "terms":33,
                "selection":"all 190 P0 pairs; all 31 P1 final values; controls next31/32/33, fixed before timing",
                "families":{"broad":190,"structural":31,"control":3}, "instances":instances}
    dump(out/"manifest.json", manifest)
    metadata = {"created_utc":utcnow(), "python":sys.version, "platform":platform.platform(),
                "machine":platform.machine(), "processor":os.environ.get("PROCESSOR_IDENTIFIER",platform.processor()), "logical_cpus":os.cpu_count(),
                "runtime_dependency_sha256":{str(p):sha_file(p) for directory in sorted({e["binary"].parent for e in engines.values()}) for p in sorted(directory.glob("*.dll"))},
                "engine_kind":engine_kind,
                "single_binary_comparison":engine_kind=="single-matched-executable",
                "engines":{mode:{"source_path":str(e["source"]),"source_sha256":sha_file(e["source"]),"binary_path":str(e["binary"]),"binary_sha256":sha_file(e["binary"]) if e["binary"].is_file() else None} for mode,e in engines.items()},
                "source_sha256":{mode:sha_file(e["source"]) for mode,e in engines.items()},
                "binary_sha256":{mode:sha_file(e["binary"]) if e["binary"].is_file() else None for mode,e in engines.items()},
                "instrumentation_note":"Preserved engines have distinct quota instrumentation, cache keys and quota bound calls; coherent direct comparison, not a single-binary ablation." if args.engine_dir else "Matched source with explicit quota modes; frozen checkpoint comparison remains separate.",
                "manifest_sha256":sha_file(out/"manifest.json"), "compiler_note":args.compiler_note,
                "repeats":args.repeats, "seconds":args.seconds, "control_seconds":args.control_seconds,
                "joint_pruning":not args.no_joint, "prime_pruning":True,
                "execution":"serial fresh subprocess per mode and case; no cache reuse; rotating mode order by repetition",
                "preprocessing":{
                    "included":"solver internal time includes prefix reduction, factor setup and quota checks; external wall time also includes process startup",
                    "excluded":"compilation and deriving the local exclusion premises; cold-start speedup not measured",
                    "historical_premise_cost_seconds":{"all_5_to_4":95.781,"fixed_core_6_to_5_including_replay":257.625},
                    "historical_machine_normalized":False,
                    "premise_verification":"verify_local_premises.py and local exact search reproduction remain separate from online benchmark"}}
    dump(out/"metadata.json", metadata)
    if args.dry_run:
        print(json.dumps({"status":"dry-run", "instances":len(instances), "expected_runs":len(instances)*args.repeats*3, "output":str(out)}),flush=True)
        return 0
    records = []
    with (out/"runs.jsonl").open("w",encoding="utf-8",buffering=1) as log:
        for repetition in range(args.repeats):
            order = MODES[repetition%3:]+MODES[:repetition%3]
            for instance in instances:
                limit = args.control_seconds if instance["family"]=="control" else args.seconds
                for mode in order:
                    run_id = f"r{repetition+1}-{instance['id']}-{mode}"
                    binary=engines[mode]["binary"]
                    command = [str(binary),"--minimum","18","--terms","33","--prefix",",".join(map(str,instance["prefix"])),"--seconds",str(limit)]
                    if not args.engine_dir:
                        command.extend([args.mode_flag,mode])
                    if not args.no_joint:
                        command.append("--joint")
                    row = {"run_id":run_id,"started_utc":utcnow(),"instance_id":instance["id"],
                           "family":instance["family"],"repetition":repetition,"mode":mode,
                           "seconds_limit":limit,"command":command,"complete":False,"censored":False}
                    started = time.perf_counter()
                    stdout, stderr = "", ""
                    try:
                        proc = subprocess.run(command,cwd=binary.parent,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=max(10.0,limit*3+5))
                        stdout,stderr=proc.stdout,proc.stderr
                        row["returncode"] = proc.returncode
                        results = [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]
                        result = next((x for x in reversed(results) if x.get("event")=="result"),None)
                        if proc.returncode != 0 or result is None:
                            row.update(status="error",error=stderr[-4000:] or "missing result")
                        else:
                            row["result"] = result
                            try:
                                status = validate_result(instance,mode,result,require_mode=not args.engine_dir)
                                row.update(status=status,complete=status in ("exhausted","witness"),censored=status=="timeout")
                            except (ValueError,KeyError,TypeError) as exc:
                                row.update(status="invalid-result",error=str(exc))
                    except subprocess.TimeoutExpired as exc:
                        stdout = exc.stdout.decode("utf-8",errors="replace") if isinstance(exc.stdout,bytes) else exc.stdout or ""
                        stderr = exc.stderr.decode("utf-8",errors="replace") if isinstance(exc.stderr,bytes) else exc.stderr or ""
                        row.update(status="external-timeout",censored=True,error="external watchdog terminated subprocess")
                    except (OSError,ValueError,json.JSONDecodeError) as exc:
                        row.update(status="error",error=str(exc))
                    row["wall_seconds"] = time.perf_counter()-started
                    raw = out/"logs"/(run_id+".stdout.jsonl")
                    raw.write_text(stdout,encoding="utf-8")
                    row["stdout_file"] = str(raw.relative_to(out))
                    row["stdout_sha256"] = sha_file(raw)
                    if stderr:
                        errpath = out/"logs"/(run_id+".stderr.txt")
                        errpath.write_text(stderr,encoding="utf-8")
                        row["stderr_file"] = str(errpath.relative_to(out))
                    records.append(row)
                    log.write(json.dumps(row,ensure_ascii=False)+"\n")
                    log.flush()
                if (len(records)//3)%20==0 or instance["family"]=="control":
                    print(json.dumps({"event":"benchmark-progress","repetition":repetition+1,"instance_id":instance["id"],"recorded_runs":len(records),"censored":sum(r["censored"] for r in records),"errors":sum(r["status"] in ("error","invalid-result") for r in records)}),flush=True)
            dump(out/"summary.json",summarize(records,instances,args.repeats,metadata))
    summary = summarize(records,instances,args.repeats,metadata)
    summary["source_unchanged"] = all(sha_file(e["source"])==metadata["source_sha256"][mode] for mode,e in engines.items())
    summary["binary_unchanged"] = all(sha_file(e["binary"])==metadata["binary_sha256"][mode] for mode,e in engines.items())
    summary["engine_kind"] = engine_kind
    summary["single_binary_comparison"] = metadata["single_binary_comparison"]
    summary["instrumentation_note"] = metadata["instrumentation_note"]
    dump(out/"summary.json",summary)
    print(json.dumps({"event":"benchmark-complete","output":str(out),"recorded_runs":len(records),"triple_complete_pairs":summary["triple_complete_pairs"],"all_repetitions_triple_complete_instances":summary["all_repetitions_triple_complete_instances"],"answer_mismatches":len(summary["answer_mismatches"]),"per_mode":summary["per_mode"]}),flush=True)
    return 1 if summary["answer_mismatches"] or any(x["errors"] for x in summary["per_mode"].values()) or not summary["source_unchanged"] or not summary["binary_unchanged"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
