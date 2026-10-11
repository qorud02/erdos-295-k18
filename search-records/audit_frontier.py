"""Audit the prefix coverage in completed old and new no-cap exact runs."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json

OLD=Path(__file__).with_name('prior-completed-prefixes.jsonl')
records=[]
for line in OLD.read_text().splitlines():
    if line.startswith('{'):
        row=json.loads(line)
        if row.get('event')=='result' and row.get('terms')==33 and row.get('status')=='exhausted' and row.get('max_denominator') is None:records.append(row)
for p in Path('.').glob('frontier-next-*-joint.jsonl'):
    for line in p.read_text().splitlines():
        row=json.loads(line)
        if row.get('event')=='result' and row.get('status')=='exhausted':records.append(row)

exclusions={tuple(r['prefix']):r for r in records if r.get('minimum')==18}
first19=next(r for r in records if r.get('minimum')==19 and not r['prefix'])
steps=[];prefix=[]
for next_d in range(18,45):
    r=1-sum((F(1,x) for x in prefix),F());t=33-len(prefix)
    hi=next_d
    while sum((F(1,hi+1+j) for j in range(t)),F())>=r:hi+=1
    needed=list(range(next_d+1,hi+1));missing=[];used=[]
    for x in needed:
        if not prefix and x>=19:used.append(first19);continue
        row=exclusions.get(tuple(prefix+[x]))
        if row is None:missing.append(x)
        else:used.append(row)
    steps.append({'prefix':prefix.copy(),'required_next_if_previous_steps_hold':next_d,'harmonic_next_upper':hi,
                  'excluded_next_values':[x for x in needed if x not in missing], 'unresolved_next_values':missing,
                  'boundary_residual':str(r),'harmonic_at_upper_plus_one':str(sum((F(1,hi+1+j) for j in range(t)),F())),
                  'completed_run_records':used})
    if missing:break
    prefix.append(next_d)
out={'scope':'Conditional on mathematical correctness of preserved exact search engines and proofs; audit verifies logical prefix coverage and exact harmonic bounds.',
     'previous_log':OLD.name,'previous_log_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),
     'forced_initial_denominators':prefix,'steps':steps,'exact_minimum_resolved':False}
Path('frontier-manifest.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'forced_initial_denominators':prefix,'remaining_next_choices': [steps[-1]['required_next_if_previous_steps_hold']]+steps[-1]['unresolved_next_values']}))
