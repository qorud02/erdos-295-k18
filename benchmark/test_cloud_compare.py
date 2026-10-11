#!/usr/bin/env python3
"""Lightweight synthetic-record tests; no solver execution or timing evidence."""
from __future__ import annotations
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'benchmark'))
spec=importlib.util.spec_from_file_location('cloud_pilot_under_test',ROOT/'benchmark'/'cloud_pilot.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def fixture():
    selected=[];broad=0
    for case in module.matched.generate_instances():
        keep=case['family']!='broad' or broad%10==0
        if case['family']=='broad':broad+=1
        if keep:selected.append(case)
    cpp=[];sage=[]
    for control in module.upstream.api_controls():
        sage.append(dict(instance_id=control['id'],family='api-control',status='control-passed',complete=True,censored=False,seconds_limit=30))
    for case in selected:
        limit=30 if case['family']=='control' else 5
        for mode in module.matched.MODES:
            cpp.append(dict(instance_id=case['id'],family=case['family'],mode=mode,seconds_limit=limit,status='exhausted',answer_status='exhausted',complete=True,censored=False,result=dict(elapsed_seconds=0.1,nodes=1)))
        sage.append(dict(instance_id=case['id'],family=case['family'],seconds_limit=limit,status='exhausted',answer_status='exhausted',complete=True,censored=False,solver_seconds=0.2))
    cm=dict(manifest_sha256='0'*64,cpu_affinity=[0],suite='pilot53',repetitions=1)
    sm=dict(manifest_sha256='0'*64,cpu_affinity=[0],suite='pilot',sage_map_reduce_workers=1,seconds_limit=5,control_seconds_limit=30)
    return dict(cpp=cpp,sage=sage,cm=cm,sm=sm)


def evaluate(value):
    with tempfile.TemporaryDirectory(prefix='matched-compare-test-') as folder:
        folder=Path(folder);cpp=folder/'cpp';sage=folder/'sage';cpp.mkdir();sage.mkdir()
        for name,path in (('cpp',cpp),('sage',sage)):
            (path/'runs.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in value[name]),encoding='utf-8')
            (path/'metadata.json').write_text(json.dumps(value['cm' if name=='cpp' else 'sm']),encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            result=module.compare(SimpleNamespace(cpp_dir=cpp,sage_dir=sage,output=folder/'comparison.json'))
        report=json.loads((folder/'comparison.json').read_text(encoding='utf-8'))
        return result,report


def replace_row(state,side,index,**changes):
    state[side][index].update(changes)


def timeout_cpp(row):
    row.update(status='timeout',answer_status='timeout',complete=False,censored=True)


def main():
    baseline=fixture();results=[]
    rc,report=evaluate(baseline)
    assert rc==0 and report['all_four_complete_cases']==53
    results.append('normal-53-complete')
    tests=[
        ('missing-cpp-row',lambda s:s['cpp'].pop()),
        ('extra-cpp-row',lambda s:s['cpp'].append(copy.deepcopy(s['cpp'][0]))),
        ('duplicate-cpp-key',lambda s:s['cpp'].__setitem__(1,copy.deepcopy(s['cpp'][0]))),
        ('duplicate-sage-key',lambda s:s['sage'].__setitem__(7,copy.deepcopy(s['sage'][6]))),
        ('unexpected-case-id',lambda s:replace_row(s,'sage',6,instance_id='unknown-case')),
        ('wrong-mode',lambda s:replace_row(s,'cpp',0,mode='unknown-mode')),
        ('wrong-family',lambda s:replace_row(s,'cpp',0,family='control')),
        ('cpp-budget-mismatch',lambda s:replace_row(s,'cpp',0,seconds_limit=4)),
        ('sage-budget-mismatch',lambda s:replace_row(s,'sage',6,seconds_limit=4)),
        ('invalid-nan-budget',lambda s:replace_row(s,'cpp',0,seconds_limit=float('nan'))),
        ('failed-api-control',lambda s:replace_row(s,'sage',0,status='timeout',complete=False,censored=True)),
        ('duplicate-api-control',lambda s:s['sage'].__setitem__(1,copy.deepcopy(s['sage'][0]))),
        ('api-control-budget-mismatch',lambda s:replace_row(s,'sage',0,seconds_limit=20)),
        ('failed-case-execution',lambda s:replace_row(s,'cpp',0,status='error')),
        ('manifest-mismatch',lambda s:s['cm'].__setitem__('manifest_sha256','1'*64)),
        ('cpu-affinity-mismatch',lambda s:s['sm'].__setitem__('cpu_affinity',[1])),
        ('multi-cpu-affinity',lambda s:(s['sm'].__setitem__('cpu_affinity',[0,1]),s['cm'].__setitem__('cpu_affinity',[0,1]))),
        ('wrong-pilot-scope',lambda s:s['cm'].__setitem__('repetitions',2)),
        ('multiple-sage-workers',lambda s:s['sm'].__setitem__('sage_map_reduce_workers',2)),
        ('cpp-rounded-time-boundary',lambda s:s['cpp'][0]['result'].__setitem__('elapsed_seconds',5)),
        ('sage-completion-over-budget',lambda s:replace_row(s,'sage',6,solver_seconds=5.1)),
        ('unknown-status',lambda s:replace_row(s,'cpp',0,status='unknown')),
        ('invalid-completion-flags',lambda s:replace_row(s,'cpp',0,censored=True)),
        ('late-result-without-proof',lambda s:replace_row(s,'cpp',0,status='late-result',answer_status='timeout',complete=False,censored=True)),
    ]
    for name,mutate in tests:
        state=copy.deepcopy(baseline);mutate(state)
        try:evaluate(state)
        except ValueError:results.append(name)
        else:raise AssertionError(name+' did not fail')
    # Synthetic contradictory statuses test comparison acceptance logic only.
    # They are not genuine mathematical witnesses or solver timing measurements.
    for name,side,late in (('partial-proof-mismatch','cpp',False),('late-cpp-proof-mismatch','cpp',True),('late-sage-proof-mismatch','sage',True)):
        state=copy.deepcopy(baseline)
        timeout_cpp(state['cpp'][1]);timeout_cpp(state['cpp'][2])
        if side=='cpp':
            row=state['cpp'][0];row.update(status='late-result' if late else 'witness',answer_status='witness',complete=not late,censored=late)
            row['result']['elapsed_seconds']=5 if late else 0.1
        else:
            state['sage'][6].update(status='late-result',answer_status='witness',complete=False,censored=True,solver_seconds=5.1)
        rc,report=evaluate(state)
        assert rc==1 and len(report['answer_mismatches'])==1 and report['all_four_complete_cases']==52,name
        results.append(name)
    state=copy.deepcopy(baseline)
    for row in state['cpp']:timeout_cpp(row)
    for row in state['sage'][6:]:
        row.update(status='timeout',complete=False,censored=True);row.pop('answer_status',None)
    rc,report=evaluate(state)
    assert rc==0 and report['all_four_complete_cases']==0 and not report['answer_mismatches']
    results.append('all-censored-no-timing-pairs')
    payload=dict(status='passed',checks=len(results),names=results,scope='synthetic comparison acceptance tests only; no solvers or timing workloads executed')
    Path(__file__).with_name('cloud-compare-tests.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload))

if __name__=='__main__':main()
