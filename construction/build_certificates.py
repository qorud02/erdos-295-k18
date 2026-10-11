from pathlib import Path
import json
from fractions import Fraction
from math import lcm
HERE=Path(__file__).resolve().parent
prior=json.loads((HERE/'search-inputs/prior_botnet_verification.json').read_text())
source={r['N']:r for r in prior['checks']}
lift=json.loads((HERE/'lift-results.json').read_text())
refine=json.loads((HERE/'tail-refinement-results.json').read_text())
new={19:next(r['denominators'] for r in lift['records'] if r['minimum']==19)}
for r in refine['records']:
    if r.get('denominators'):new[r['minimum']]=r['denominators']
D18=lift['records'][0]['denominators']
results=[]
for N in (19,20,21):
    ds=new[N];old=D18 if N==19 else source[N]['denominators']
    removed=sorted(set(old)-set(ds));added=sorted(set(ds)-set(old));common=sorted(set(old)&set(ds))
    assert sum((Fraction(1,d) for d in removed),Fraction())==sum((Fraction(1,d) for d in added),Fraction())
    assert len(ds)==len(set(ds)) and min(ds)==N and sum((Fraction(1,d) for d in ds),Fraction())==1
    L=lcm(*ds);S=sum(L//d for d in ds);assert L==S
    r=sum((Fraction(1,d) for d in added),Fraction())
    result={'N':N,'upper_bound':len(ds),'prior_compared_upper':source[N]['upper'],'prior_source':prior['source'],'denominators':[str(d) for d in ds],'lcm':str(L),'scaled_sum':str(S),'sum':'1','source_denominators':[str(d) for d in old],'removed':[str(d) for d in removed],'added':[str(d) for d in added],'replacement_sum':str(r),'prior_largest_denominator':str(max(source[N]['denominators'])),'new_largest_denominator':str(max(ds)),'prior_max_bit_length':max(source[N]['denominators']).bit_length(),'new_max_bit_length':max(ds).bit_length()}
    results.append(result)
(HERE/'extension-certificates.json').write_text(json.dumps({'definition':'k(N) is the minimum number of distinct unit fractions summing to 1 with every denominator at least N.','comparison_source_date':'2026-09-24','results':results},indent=2))
print(json.dumps([{k:r[k] for k in ('N','upper_bound','prior_compared_upper','replacement_sum','new_max_bit_length','prior_max_bit_length')} for r in results]))
