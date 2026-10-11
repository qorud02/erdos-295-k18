from pathlib import Path
import importlib.util,json,time
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lift',HERE/'lift_search.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
records=[]
for N in range(19,27):
    m.DEADLINE=time.monotonic()+240
    required=sum(d<N for d in m.D18)
    try:
        answers=m.lift(m.D18,N,max_removed=required+1,max_added=required+4,variants=4)
        if answers:
            ds,step=answers[0];rec=m.validate(ds,N);rec['replacement']=step
        else:rec={'minimum':N,'status':'no_witness_in_local_scope'}
    except m.Limit:rec={'minimum':N,'status':'timeout'}
    records.append(rec);print(json.dumps(rec),flush=True)
    (HERE/'direct-lift-results.json').write_text(json.dumps({'records':records,'counters':m.COUNTS},indent=2))
