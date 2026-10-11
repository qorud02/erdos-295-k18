from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
from random import Random
import json
from local_surgery import BASE
from quota_tools import exclusion_group,laminar_quota_bound
A=set(BASE);S=set(BASE[:-2]);assert exclusion_group(BASE,BASE[-2:],6,1)==(tuple(sorted(S)),27)
cpp=0
p=Path('laminar-probe-bounds.txt')
if p.exists():
    for row in p.read_text().splitlines():
        d,t,q,qs,a,b=map(int,row.split());assert F(a,b)==laminar_quota_bound((A,S),d,t,(q,qs));cpp+=1
rng=Random(2953327);cases=0
for _ in range(300):
    # Three atoms: inner group, outer-only group, and complement.
    pool=sorted(rng.sample(range(2,80),10));outer=set(rng.sample(pool,rng.randrange(3,9)));inner=set(rng.sample(sorted(outer),rng.randrange(1,len(outer)+1)))
    d=pool[0];t=rng.randrange(1,5);q=rng.randrange(0,5);qs=rng.randrange(0,5)
    # Include the first t candidates of every atom so all optima are present.
    atoms=[sorted(x for x in inner if x>=d)[:t],sorted(x for x in outer-inner if x>=d)[:t],[]]
    x=d
    while len(atoms[2])<t:
        if x not in outer:atoms[2].append(x)
        x+=1
    candidates=sum(atoms,[])
    expected=max(sum((F(1,x) for x in ds),F()) for ds in combinations(candidates,t) if sum(x in outer for x in ds)<=q and sum(x in inner for x in ds)<=qs)
    assert expected==laminar_quota_bound((outer,inner),d,t,(q,qs));cases+=1
try:laminar_quota_bound(({2,3},{3,4}),2,2,(1,1));raise AssertionError('crossing groups accepted')
except ValueError:pass
out={'status':'passed','seed':2953327,'arbitrary_nested_group_exhaustive_oracles':cases,'cpp_vs_generic_api_exact_bounds':cpp,
     'crossing_groups_rejected':True,'core_fixed_certificate_group_size':len(S),'core_fixed_certificate_quota':27}
Path('laminar-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
