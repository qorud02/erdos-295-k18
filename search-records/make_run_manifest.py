from pathlib import Path
import hashlib,json
from datetime import datetime, timezone

cpp_runs=[
('cpp-prefix-18-19-20-21-90s.jsonl','search-cpp',list(range(18,22)),90,False),
('frontier-next-33-joint.jsonl','search-cpp',list(range(18,29))+[33],90,True),
('frontier-next-32-joint.jsonl','search-cpp',list(range(18,29))+[32],90,True),
('frontier-next-31-joint.jsonl','search-cpp',list(range(18,29))+[31],90,True),
('frontier-next-31-nojoint.jsonl','search-cpp',list(range(18,29))+[31],30,False),
('frontier-next-30-joint.jsonl','search-cpp',list(range(18,29))+[30],90,True),
('frontier-next-30-nojoint.jsonl','search-cpp',list(range(18,29))+[30],180,False),
('checkpoint-validation-next31.jsonl','checkpoint-search',list(range(18,29))+[31],30,True),
('checkpoint-next30-60s.jsonl','checkpoint-search',list(range(18,29))+[30],60,True),
('quota-next30-180s.jsonl','quota-search',list(range(18,29))+[30],180,True),
('quota-next29-240s.jsonl','quota-search',list(range(18,30)),240,True),
('laminar-next30-90s.jsonl','laminar-search',list(range(18,29))+[30],90,True)]
runs=[]
for log,engine,prefix,seconds,joint in cpp_runs:
    rows=[json.loads(x) for x in Path(log).read_text().splitlines()]
    result=next(x for x in rows if x['event']=='result')
    command=f'{engine} --minimum 18 --terms 33 --prefix '+','.join(map(str,prefix))+f' --seconds {seconds}'+(' --joint' if joint else '')+f' --output {log}'
    runs.append({'command':command,'log':log,'result':result})
for log in sorted(Path('.').glob('surgery*.jsonl')):
    rows=[json.loads(x) for x in log.read_text().splitlines()]
    args=rows[0]['args'];result=rows[-1]
    command='python local_surgery.py '+' '.join(f'--{k.replace("_","-")} {v}' for k,v in args.items())
    runs.append({'command':command,'log':log.name,'result':result})
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('.').iterdir()
       if p.is_file() and p.suffix in ('.py','.cpp','.json','.jsonl','.md','.cmd','.txt')
       and p.name not in ('run-manifest.json','lower-n19-t34-60s.jsonl')}
out={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'minimum_resolved':False,
     'original_cpp_source_sha256':'63353f9010c84cec04662fd367befaeb089baf95f40eecbed73e27528df4790e',
     'original_executable_sha256':hashlib.sha256(Path('search-cpp.exe').read_bytes()).hexdigest(),
     'cpp_validation_captured_from_completed_tool_output':{'square_roots':10000,'reductions':10000,'two_oracles':1000,'valid_prime_covers':10000,'full_on_off':100,'status':'passed'},
     'runs':runs,'file_sha256':files}
Path('run-manifest.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'runs_recorded':len(runs),'files_hashed':len(files)}))
