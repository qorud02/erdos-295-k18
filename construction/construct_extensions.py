"""Reusable divisor-based two-term completion; standard library only.
Default execution regenerates the N=19,20,21 upper-bound certificates.
The factorization identity is classical; see David Eppstein's Egyptian-fraction algorithms.
"""
from fractions import Fraction
from math import prod,isqrt
from pathlib import Path
import bisect,json
HERE=Path(__file__).resolve().parent
FACTORS={
20:[(2,5),(3,2),(5,2),(7,1),(11,1),(17,1),(19,1),(23,1),(29,1),(37,1),(41,1),(43,1),(53,1),(137999,1)],
21:[(2,6),(3,2),(5,2),(7,2),(11,1),(17,1),(19,1),(23,1),(29,1),(31,1),(37,1),(41,1),(53,1),(113,1)]}

def prime(n):
    if n<2:return False
    if n%2==0:return n==2
    return all(n%d for d in range(3,isqrt(n)+1,2))

def complete_two(residual,minimum,factorization):
    """Return an ordered exact pair or None after complete divisor enumeration.
    factorization must be a complete prime factorization of residual.denominator.
    No denominator cap is imposed. Work depends on the divisor count.
    """
    r=Fraction(residual);a,b=r.numerator,r.denominator
    assert r>0 and minimum>=1
    factors=list(factorization)
    assert len({p for p,e in factors})==len(factors)
    assert all(e>=1 and prime(p) for p,e in factors)
    assert prod(p**e for p,e in factors)==b
    low=max(1,a*minimum-b);high=b-1
    if low>high:return None
    halves=[[],[]];counts=[1,1]
    for p,e in sorted(((p,2*e) for p,e in factors),key=lambda pe:pe[1],reverse=True):
        i=0 if counts[0]<=counts[1] else 1
        halves[i].append((p,e));counts[i]*=e+1
    def divisors(fs):
        out=[1]
        for p,e in fs:
            nxt=[]
            for u in out:
                for _ in range(e+1):
                    if u>high:break
                    nxt.append(u);u*=p
            out=nxt
        return out
    left,right=divisors(halves[0]),divisors(halves[1]);buckets={}
    for v in right:buckets.setdefault(v%a,[]).append(v)
    for bucket in buckets.values():bucket.sort()
    for u in left:
        wanted=(-b*pow(u,-1,a))%a if a>1 else 0
        bucket=buckets.get(wanted,())
        lo=(low+u-1)//u;hi=high//u
        idx=bisect.bisect_left(bucket,lo)
        if idx<len(bucket) and bucket[idx]<=hi:
            q=u*bucket[idx];x=(b+q)//a;yn=b+b*b//q
            assert yn%a==0
            y=yn//a
            assert x>=minimum and x<y and Fraction(1,x)+Fraction(1,y)==r
            return x,y
    return None

def complete_prefix(prefix,factorization):
    """Construct a distinct completion above every denominator in prefix."""
    prefix=tuple(prefix);assert prefix and len(prefix)==len(set(prefix))
    r=1-sum((Fraction(1,d) for d in prefix),Fraction())
    pair=complete_two(r,max(prefix)+1,factorization)
    return tuple(sorted(prefix+pair)) if pair else None

def main():
    cert=json.loads((HERE/'extension-certificates.json').read_text());output=[]
    for c in cert['results']:
        N=c['N'];source=tuple(map(int,c['source_denominators']))
        if N==19:
            ds=tuple(sorted((set(source)-{18,63})|{42,55,66,70}))
        else:
            prefix=source[:-3]
            ds=complete_prefix(prefix,FACTORS[N])
            assert ds is not None
        assert len(ds)==c['upper_bound'] and min(ds)==N and len(ds)==len(set(ds))
        assert sum((Fraction(1,d) for d in ds),Fraction())==1
        assert list(map(str,ds))==c['denominators']
        output.append({'N':N,'terms':len(ds),'denominators':[str(d) for d in ds],'regenerated':True})
    (HERE/'constructed-extensions.json').write_text(json.dumps({'all_regenerated':True,'results':output},indent=2))
    print(json.dumps([{'N':c['N'],'terms':c['terms'],'regenerated':True} for c in output],indent=2))
if __name__=='__main__':main()
