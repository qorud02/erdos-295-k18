from pathlib import Path
import importlib.util,json,time
from fractions import Fraction
HERE=Path(__file__).resolve().parent
OLD=HERE/'search-deps'
spec=importlib.util.spec_from_file_location('engine',OLD/'search-earlyterminal.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
base=e.terminal.strong._base
prior=json.loads((HERE/'search-inputs/prior_botnet_verification.json').read_text())
new=json.loads((HERE/'lift-results.json').read_text())
seeds={c['N']:c['denominators'] for c in prior['checks'] if c['N']>=19}
for c in new['records']:
    if c['minimum']>=19 and len(c['denominators'])<len(seeds.get(c['minimum'],range(10000))):seeds[c['minimum']]=c['denominators']
records=[]
for N in [19,20,21,22]:
    ds=seeds[N];target=len(ds)-1
    for t in range(2,7):
        fixed=ds[:target-t]
        r=1-sum((Fraction(1,d) for d in fixed),Fraction(0))
        s=e.Search(seconds=25,cap=None,memo_size=10000,prime_prune=True)
        try:
            ans=s.dfs(fixed[-1]+1,t,r.numerator,r.denominator,base.small_prime_factors(r.denominator),())
            status='found' if ans else 'exhausted_for_fixed_prefix'
        except base.SearchTimeout:ans=None;status='timeout'
        rec={'minimum':N,'target':target,'tail_terms':t,'fixed_prefix':fixed,'residual':str(r),'status':status,'counters':s.stats,'elapsed_seconds':time.monotonic()-s.start}
        if ans:
            full=fixed+list(ans);assert len(full)==target and len(full)==len(set(full)) and min(full)>=N and sum((Fraction(1,d) for d in full),Fraction(0))==1
            rec['denominators']=full;ds=full;seeds[N]=ds
        records.append(rec);print(json.dumps(rec),flush=True)
        (HERE/'tail-refinement-results.json').write_text(json.dumps({'records':records,'best':seeds},indent=2))
        if ans:break
