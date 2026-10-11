#!/usr/bin/env python3
from __future__ import annotations
import argparse,collections,hashlib,importlib.machinery,importlib.util,json,os,platform,subprocess,time
from pathlib import Path
import run_benchmark as matched
loader=importlib.machinery.SourceFileLoader('upstream_wrapper',str(Path(__file__).with_name('run_upstream.sage')))
spec=importlib.util.spec_from_loader(loader.name,loader)
upstream=importlib.util.module_from_spec(spec);loader.exec_module(upstream)
def dump(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args):
    _,cases,manifest_sha=upstream.read_manifest(args.manifest,'pilot')
    out=args.out_dir.resolve();out.mkdir(parents=True,exist_ok=False);(out/'logs').mkdir()
    affinity=None
    if hasattr(os,'sched_getaffinity'):
        affinity=sorted(os.sched_getaffinity(0));os.sched_setaffinity(0,{min(affinity)});affinity=sorted(os.sched_getaffinity(0))
    binary=args.binary.resolve();source=Path(__file__).with_name('matched-search.cpp')
    dump(out/'metadata.json',{'manifest_sha256':manifest_sha,'source_sha256':sha(source),'binary_sha256':sha(binary),'cpu_affinity':affinity,'platform':platform.platform(),'python':platform.python_version(),'repetitions':1,'suite':'pilot53','preprocessing':'Exact local-exclusion premise costs and compilation excluded. Source hashes and historical premise costs reported separately.','timing':'Solver internal seconds plus separate process wall time. Completed answers after declared solver limit are retained as late/censored.'})
    rows=[]
    with (out/'runs.jsonl').open('w',encoding='utf-8',buffering=1) as stream:
        for ordinal,case in enumerate(cases):
            order=matched.MODES[ordinal%3:]+matched.MODES[:ordinal%3]
            for mode in order:
                limit=args.control_seconds if case['family']=='control' else args.seconds
                command=[str(binary),'--minimum','18','--terms','33','--prefix',','.join(map(str,case['prefix'])),'--seconds',str(limit),'--quota-mode',mode,'--joint']
                row={'instance_id':case['id'],'family':case['family'],'mode':mode,'seconds_limit':limit,'complete':False,'censored':False,'command':command}
                start=time.perf_counter();stdout='';stderr=''
                try:
                    p=subprocess.run(command,cwd=binary.parent,capture_output=True,text=True,timeout=max(10,limit*3+5))
                    stdout,stderr=p.stdout,p.stderr
                    values=[json.loads(x) for x in stdout.splitlines() if x.startswith('{')]
                    result=next(x for x in reversed(values) if x.get('event')=='result')
                    if p.returncode:raise ValueError('nonzero solver exit')
                    status=matched.validate_result(case,mode,result)
                    row.update(result=result,answer_status=status,status=status)
                    if status=='timeout':row.update(censored=True)
                    elif result['elapsed_seconds']>=limit:row.update(status='late-result',censored=True)
                    else:row.update(complete=True)
                except subprocess.TimeoutExpired as exc:
                    row.update(status='external-timeout',censored=True);stdout=exc.stdout or '';stderr=exc.stderr or ''
                    if isinstance(stdout,bytes):stdout=stdout.decode('utf-8','replace')
                    if isinstance(stderr,bytes):stderr=stderr.decode('utf-8','replace')
                except (OSError,ValueError,KeyError,StopIteration) as exc:row.update(status='error',error=str(exc))
                row['wall_seconds']=time.perf_counter()-start
                raw=out/'logs'/(case['id']+'-'+mode+'.jsonl');raw.write_text(stdout,encoding='utf-8');row['stdout_sha256']=sha(raw)
                if stderr:(out/'logs'/(case['id']+'-'+mode+'.stderr.txt')).write_text(stderr,encoding='utf-8')
                rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(json.dumps({'event':'matched-pilot-progress','instance_id':case['id'],'runs':len(rows)}),flush=True)
    summary={'cases':len(cases),'runs':len(rows),'per_mode':{mode:dict(collections.Counter(x['status'] for x in rows if x['mode']==mode)) for mode in matched.MODES},'errors':sum(x['status']=='error' for x in rows),'source_unchanged':sha(source)==json.loads((out/'metadata.json').read_text())['source_sha256'],'binary_unchanged':sha(binary)==json.loads((out/'metadata.json').read_text())['binary_sha256']}
    dump(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    return int(summary['errors']>0 or not summary['source_unchanged'] or not summary['binary_unchanged'])
def compare(args):
    from math import isfinite

    def require(value,message):
        if not value:raise ValueError(message)

    def read_rows(path):
        rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
        require(all(isinstance(x,dict) for x in rows),'execution rows must be JSON objects')
        return rows

    def budget(value,label):
        require(isinstance(value,(int,float)) and not isinstance(value,bool) and isfinite(value) and value>0,'invalid positive finite time budget: '+label)
        return value

    cpp=read_rows(args.cpp_dir/'runs.jsonl')
    sage_all=read_rows(args.sage_dir/'runs.jsonl')
    controls=[x for x in sage_all if x.get('family')=='api-control']
    expected_controls={x['id'] for x in upstream.api_controls()}
    require(len(controls)==6 and {x.get('instance_id') for x in controls}==expected_controls and all(x.get('status')=='control-passed' and x.get('complete') is True and x.get('censored') is False for x in controls),'Sage API controls did not all pass')
    require(not any(x.get('status') in ('error','invalid-result','not-run-control-failure') for x in cpp+sage_all),'invalid or failed execution records')
    sage=[x for x in sage_all if x.get('family')!='api-control']
    require(len(cpp)==159 and len(sage)==53 and len(sage_all)==59,'incorrect raw execution row counts')

    expected={};broad_index=0
    for case in matched.generate_instances():
        keep=case['family']!='broad' or broad_index%10==0
        if case['family']=='broad':broad_index+=1
        if keep:expected[case['id']]=case
    require(len(expected)==53,'unexpected fixed pilot definition')
    expected_cpp={(case_id,mode) for case_id in expected for mode in matched.MODES}
    cpp_keys=[(x.get('instance_id'),x.get('mode')) for x in cpp]
    sage_keys=[x.get('instance_id') for x in sage]
    require(len(set(cpp_keys))==len(cpp_keys),'duplicate C++ instance/mode rows')
    require(len(set(sage_keys))==len(sage_keys),'duplicate Sage instance rows')
    require(set(cpp_keys)==expected_cpp,'C++ instance/mode coverage differs from fixed 53-case pilot')
    require(set(sage_keys)==set(expected),'Sage instance coverage differs from fixed 53-case pilot')
    cg=dict(zip(cpp_keys,cpp));sg=dict(zip(sage_keys,sage))
    cm=json.loads((args.cpp_dir/'metadata.json').read_text(encoding='utf-8'))
    sm=json.loads((args.sage_dir/'metadata.json').read_text(encoding='utf-8'))
    require(isinstance(cm,dict) and isinstance(sm,dict),'metadata must be JSON objects')
    require(isinstance(cm.get('manifest_sha256'),str) and len(cm['manifest_sha256'])==64 and cm['manifest_sha256']==sm.get('manifest_sha256'),'manifest digest mismatch')
    affinity=cm.get('cpu_affinity')
    require(isinstance(affinity,list) and len(affinity)==1 and isinstance(affinity[0],int) and not isinstance(affinity[0],bool) and affinity[0]>=0 and affinity==sm.get('cpu_affinity'),'execution must use the same single CPU affinity')
    require(cm.get('suite')=='pilot53' and cm.get('repetitions')==1 and sm.get('suite')=='pilot','metadata pilot scope mismatch')
    require(sm.get('sage_map_reduce_workers')==1,'Sage baseline must declare one map-reduce worker')
    regular_limit=budget(sm.get('seconds_limit'),'Sage ordinary cases')
    control_limit=budget(sm.get('control_seconds_limit'),'Sage control cases')
    for control in controls:
        require(budget(control.get('seconds_limit'),'Sage API control')==control_limit,'Sage API-control time budget mismatch')

    proof_statuses=('exhausted','witness')
    def check_row(row,case,solver):
        require(row.get('family')==case['family'],'case family mismatch: '+case['id']+'/'+solver)
        expected_limit=control_limit if case['family']=='control' else regular_limit
        require(budget(row.get('seconds_limit'),case['id']+'/'+solver)==expected_limit,'case time budget mismatch: '+case['id']+'/'+solver)
        require(type(row.get('complete')) is bool and type(row.get('censored')) is bool,'invalid completion/censor flags: '+case['id']+'/'+solver)
        allowed=proof_statuses+('late-result','timeout','external-timeout') if solver!='sage' else proof_statuses+('late-result','timeout','startup-timeout')
        status=row.get('status');answer=row.get('answer_status')
        require(status in allowed,'unexpected execution status: '+case['id']+'/'+solver)
        if status in proof_statuses or status=='late-result':
            require(answer in proof_statuses and (status=='late-result' or answer==status),'invalid proof-answer status: '+case['id']+'/'+solver)
            result=row.get('result',{}) if solver!='sage' else row
            require(isinstance(result,dict),'missing solver result: '+case['id']+'/'+solver)
            elapsed=result.get('elapsed_seconds') if solver!='sage' else result.get('solver_seconds')
            require(isinstance(elapsed,(int,float)) and not isinstance(elapsed,bool) and isfinite(elapsed) and elapsed>=0,'invalid solver elapsed time: '+case['id']+'/'+solver)
            if status=='late-result':
                require(row['complete'] is False and row['censored'] is True,'late result must remain censored: '+case['id']+'/'+solver)
                require(elapsed>=expected_limit if solver!='sage' else elapsed>expected_limit,'incorrect late-result time: '+case['id']+'/'+solver)
            else:
                require(row['complete'] is True and row['censored'] is False,'completed result flags disagree: '+case['id']+'/'+solver)
                require(elapsed<expected_limit if solver!='sage' else elapsed<=expected_limit,'completed result exceeds conservative time budget: '+case['id']+'/'+solver)
                if solver!='sage':
                    require(isinstance(result.get('nodes'),int) and not isinstance(result.get('nodes'),bool) and result['nodes']>=0,'invalid solver node count: '+case['id']+'/'+solver)
        else:
            require(row['complete'] is False and row['censored'] is True and answer not in proof_statuses,'timeout flags or answer disagree: '+case['id']+'/'+solver)

    paired=[];mismatches=[]
    for case_id,case in expected.items():
        s=sg[case_id];rs=[cg[case_id,m] for m in matched.MODES]
        check_row(s,case,'sage')
        for mode,row in zip(matched.MODES,rs):check_row(row,case,mode)
        proof_rows=[(solver,row) for solver,row in [('sage',s)]+list(zip(matched.MODES,rs)) if row.get('answer_status') in proof_statuses]
        proof_answers=[row['answer_status'] for solver,row in proof_rows]
        if len(set(proof_answers))>1:
            mismatches.append({'id':case_id,'answers':proof_answers,'sources':[{'solver':solver,'answer_status':row['answer_status'],'complete':row['complete'],'censored':row['censored']} for solver,row in proof_rows]})
        if s['complete'] and all(r['complete'] for r in rs):
            paired.append({'id':case_id,'family':s['family'],'sage_seconds':s['solver_seconds'],'cpp':{m:{'seconds':r['result']['elapsed_seconds'],'nodes':r['result']['nodes']} for m,r in zip(matched.MODES,rs)}})
    report={'manifest_sha256':cm['manifest_sha256'],'pilot_cases':53,'same_cpu_affinity':cm['cpu_affinity'],'single_repetition':True,'all_four_complete_cases':len(paired),'answer_mismatches':mismatches,'matched_complete_counts':{m:sum(x['complete'] for x in cpp if x['mode']==m) for m in matched.MODES},'sage_complete_count':sum(x['complete'] for x in sage),'complete_paired_cases':paired,'interpretation':'Single-run controlled pilot on fixed subtrees. Correctness and timing evidence for these cases; broader general speedup and global33-term exclusion remain unestablished.'}
    dump(args.output,report);print(json.dumps({k:v for k,v in report.items() if k!='complete_paired_cases'}),flush=True)
    return int(bool(mismatches))
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('run');r.add_argument('--manifest',type=Path,required=True);r.add_argument('--binary',type=Path,required=True);r.add_argument('--out-dir',type=Path,required=True);r.add_argument('--seconds',type=float,default=5);r.add_argument('--control-seconds',type=float,default=30)
    c=sub.add_parser('compare');c.add_argument('--cpp-dir',type=Path,required=True);c.add_argument('--sage-dir',type=Path,required=True);c.add_argument('--output',type=Path,required=True)
    a=p.parse_args();return run(a) if a.action=='run' else compare(a)
if __name__=='__main__':raise SystemExit(main())
