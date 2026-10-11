"""Independent finite oracle checks for the optimized exact tail loop."""
from pathlib import Path
import importlib.util,random,json
from fractions import Fraction
root=Path(__file__).resolve().parent
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,root/file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
fast=module('fast','search-fasttail.py')
rng=random.Random(20261011)
counts={'two_oracles':0,'three_oracles':0,'known_two':0}
for j in range(2000):
    d=rng.randint(2,40);cap=rng.randint(d+1,150)
    r=Fraction(rng.randint(1,50),rng.randint(2,2000))
    expected=next(((x,y) for x in range(d,cap) for y in range(x+1,cap+1) if Fraction(1,x)+Fraction(1,y)==r),None)
    s=fast.Search(120,cap,0,False)
    actual=s.dfs(d,2,r.numerator,r.denominator,(),())
    assert bool(actual)==bool(expected),(d,cap,r,actual,expected)
    if actual:assert sum((Fraction(1,x) for x in actual),Fraction())==r
    counts['two_oracles']+=1
for j in range(300):
    d=rng.randint(2,20);cap=rng.randint(d+2,45)
    r=Fraction(rng.randint(1,20),rng.randint(2,300))
    expected=next(((x,y,z) for x in range(d,cap-1) for y in range(x+1,cap) for z in range(y+1,cap+1) if Fraction(1,x)+Fraction(1,y)+Fraction(1,z)==r),None)
    s=fast.Search(120,cap,0,False)
    actual=s.dfs(d,3,r.numerator,r.denominator,(),())
    assert bool(actual)==bool(expected),(d,cap,r,actual,expected)
    if actual:assert sum((Fraction(1,x) for x in actual),Fraction())==r
    counts['three_oracles']+=1
for j in range(5000):
    x=rng.randint(2,500);y=rng.randint(x+1,1000000)
    r=Fraction(1,x)+Fraction(1,y)
    s=fast.Search(120,None,0,False)
    actual=s.dfs(x,2,r.numerator,r.denominator,(),())
    assert actual and sum((Fraction(1,v) for v in actual),Fraction())==r
    counts['known_two']+=1
result={'status':'passed','seed':20261011,'checks':counts}
(root/'verify-fasttail.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result),flush=True)
