"""Independent finite exhaustive oracle for the quota harmonic upper bound."""
from fractions import Fraction as F
from math import lcm
from random import Random
from pathlib import Path
import json
from local_surgery import BASE
from quota_tools import quota_harmonic_bound,intersection_quota,next_denominator_upper,prefix_quota_state

B=set(BASE)
def greedy(d,t,q):
    ds=[]
    while len(ds)<t:
        if d in B:
            if q==0:d+=1;continue
            q-=1
        ds.append(d);d+=1
    return sum((F(1,x) for x in ds),F())

cases=0
for d in range(2,81):
    # Any optimum of <=6 terms needs only the first six members of each group.
    # All later members of the same group are dominated by these candidates.
    base=[x for x in BASE if x>=d][:6]
    nonbase=[];x=d
    while len(nonbase)<6:
        if x not in B:nonbase.append(x)
        x+=1
    pool=sorted(base+nonbase);L=lcm(*pool);weights=[L//x for x in pool]
    count=[0]*(1<<len(pool));bcount=count.copy();sums=count.copy();best={}
    for mask in range(1,1<<len(pool)):
        bit=mask&-mask;i=bit.bit_length()-1;old=mask^bit
        count[mask]=count[old]+1;bcount[mask]=bcount[old]+(pool[i] in B);sums[mask]=sums[old]+weights[i]
        if count[mask]<=6:
            for q in range(bcount[mask],7):
                key=count[mask],q;best[key]=max(best.get(key,-1),sums[mask])
    for t in range(1,7):
        for q in range(7):
            assert greedy(d,t,q)==F(best[t,q],L)==quota_harmonic_bound(BASE,d,t,q)
            cases+=1

rng=Random(2953328);valid=0;general=0
for _ in range(200):
    A=sorted(rng.sample(range(2,101),rng.randrange(5,21)));d=rng.randrange(1,70);t=rng.randrange(1,6);q=rng.randrange(0,6)
    base=[x for x in A if x>=d][:5];nonbase=[];x=d
    while len(nonbase)<5:
        if x not in A:nonbase.append(x)
        x+=1
    from itertools import combinations
    expected=max(sum((F(1,x) for x in ds),F()) for ds in combinations(base+nonbase,t) if sum(x in A for x in ds)<=q)
    actual=quota_harmonic_bound(A,d,t,q);assert actual==expected
    residual=actual*rng.randrange(1,100)/100
    upper=next_denominator_upper(A,d,t,q,residual)
    assert upper>=d and quota_harmonic_bound(A,upper,t,q)>=residual and quota_harmonic_bound(A,upper+1,t,q)<residual
    general+=1
assert intersection_quota(34,5,1)==28
assert intersection_quota(20,7,3)==12
assert intersection_quota(10,10,2)==-1
assert quota_harmonic_bound(BASE,18,3,-1) is None
for _ in range(10000):
    d=rng.randrange(18,200);t=rng.randrange(1,34);ds=sorted(rng.sample(range(d,d+250),t))
    q=sum(x in B for x in ds)
    assert sum((F(1,x) for x in ds),F())<=greedy(d,t,q)
    valid+=1
out={'status':'passed','seed':2953328,'finite_exhaustive_quota_oracles':cases,'genuine_subset_upper_bound_controls':valid,
     'arbitrary_reference_subset_oracles_and_next_upper_checks':general,
     'method':'For each lower bound, enumerate every subset of the first six BASE and first six non-BASE denominators, using exact integer LCM weights. Compare every t<=6 and quota<=6 to the independently implemented greedy bound.'}
Path('quota-validation.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
