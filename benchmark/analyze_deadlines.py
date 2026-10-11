#!/usr/bin/env python3
"""Audit the preserved benchmark's soft budgets without changing raw evidence."""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results",type=Path)
    parser.add_argument("--common-seconds",type=float,default=5.0)
    args=parser.parse_args()
    folder=args.results.resolve()
    receipt=json.loads((folder/"runner-source-receipt.json").read_text(encoding="utf-8"))
    runner=folder/"run_benchmark.executed.py"
    if sha(runner)!=receipt["sha256"]:
        raise ValueError("executed runner source hash mismatch")
    spec=importlib.util.spec_from_file_location("executed_benchmark",runner)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    manifest=json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    metadata=json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    records=[json.loads(x) for x in (folder/"runs.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    strict=copy.deepcopy(records)
    late=[]
    after_common=[]
    earlier_censored=[]
    for original,row in zip(records,strict):
        elapsed=original.get("result",{}).get("elapsed_seconds")
        if original["complete"] and elapsed>original["seconds_limit"]:
            late.append({"run_id":original["run_id"],"instance_id":original["instance_id"],"mode":original["mode"],"declared_seconds":original["seconds_limit"],"actual_elapsed_seconds":elapsed,"actual_status":original["status"]})
            row.update(complete=False,censored=True,status="late-complete")
        if original["complete"] and elapsed>args.common_seconds:
            after_common.append({"run_id":original["run_id"],"elapsed_seconds":elapsed})
        if original["censored"] and original["seconds_limit"]<args.common_seconds:
            earlier_censored.append({"run_id":original["run_id"],"declared_seconds":original["seconds_limit"],"elapsed_seconds":elapsed,"status":original["status"]})
    summary=module.summarize(strict,manifest["instances"],metadata["repeats"],metadata)
    summary.update({"deadline_basis":"solver internal elapsed_seconds, excluding process startup", "strict_policy":"An answer counts as complete only if elapsed_seconds <= that run's declared budget. Raw completed answers remain preserved separately.","late_complete_excluded":len(late),"raw_runs_sha256":sha(folder/"runs.jsonl")})
    write(folder/"strict-deadline-summary.json",summary)
    result={"raw_runs_sha256":sha(folder/"runs.jsonl"),"executed_runner_sha256":receipt["sha256"],"analysis_source_sha256":sha(__file__),"recorded_runs":len(records),"late_complete_count":len(late),"late_complete":late,"strict_answer_mismatches":summary["answer_mismatches"],"strict_triple_complete_instances":summary["all_repetitions_triple_complete_instances"],"common_cutoff_seconds":args.common_seconds,"complete_after_common_cutoff_count":len(after_common),"complete_after_common_cutoff":after_common,"censored_before_common_cutoff_count":len(earlier_censored),"censored_before_common_cutoff":earlier_censored,"common_cutoff_inference":"A timeout before the common cutoff stays censored; it does not establish that the case would remain unresolved at the longer common cutoff. Cross-system comparison needs identical cases and equal enforced budgets.","clock_policy":"The C++ watchdog polls each1024 DFS states and two-term candidate tests, so budgets are soft; actual elapsed times are retained. External process wall time is reported separately."}
    write(folder/"deadline-audit.json",result)
    print(json.dumps({k:result[k] for k in ("recorded_runs","late_complete_count","strict_triple_complete_instances","complete_after_common_cutoff_count","censored_before_common_cutoff_count")}))

if __name__=="__main__":
    main()
