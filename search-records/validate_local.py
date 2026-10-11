from fractions import Fraction as F
from math import gcd
from random import Random
from pathlib import Path
import json
from local_surgery import Search

rng=Random(2953312)
valid=oracle=0
for _ in range(1000):
    t=rng.randrange(2,5);ds=sorted(rng.sample(range(18,90),t));forbid=set(rng.sample([x for x in range(18,90) if x not in ds],rng.randrange(0,15)))
    r=sum((F(1,x) for x in ds),F());s=Search(forbid,5)
    got=s.dfs(18,t,r.numerator,r.denominator)
    assert got and len(set(got))==t and all(x>=18 and x not in forbid for x in got) and sum((F(1,x) for x in got),F())==r
    valid+=1
for _ in range(2000):
    a=rng.randrange(1,90);b=rng.randrange(2,150);g=gcd(a,b);a//=g;b//=g;d=rng.randrange(2,30)
    forbid=set(rng.sample(range(2,80),rng.randrange(0,20)))
    expected=None
    for x in range(max(d,b//a+1),(2*b-1)//a+1):
        if x in forbid:continue
        y,rem=divmod(b*x,a*x-b)
        if rem==0 and y>x and y not in forbid:expected=(x,y);break
    s=Search(forbid,5);got=s.dfs(d,2,a,b)
    assert bool(got)==bool(expected)
    oracle+=1
r={'status':'passed','seed':2953312,'genuine_witness_controls':valid,'two_term_direct_scan_oracles':oracle}
Path('local-validation.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
