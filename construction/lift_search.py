"""Exact bounded local lifting of distinct Egyptian fraction certificates.
Positive outputs are globally valid; failed local searches prove nothing global.
The complete two-term solver uses mathematical bounds and integer arithmetic.
"""
from fractions import Fraction
from math import gcd,isqrt,lcm
from itertools import combinations
from pathlib import Path
import argparse,json,time
D18=(18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,63,275,14143068,10457416992)
HERE=Path(__file__).resolve().parent
START=time.monotonic()
COUNTS={'nodes':0,'two':0,'two_candidates':0}
class Limit(Exception): pass
DEADLINE=float('inf')
def checktime():
    if time.monotonic()>DEADLINE: raise Limit

def two(a,b,lo,forbidden,limit=None):
    COUNTS['two']+=1
    lo=max(lo,b//a+1); hi=(2*b-1)//a
    if a*a>4*b:
        disc=a*a-4*b; s=isqrt(disc); s+=s*s<disc
        hi=min(hi,(a-s)//2)
    if lo>hi:return
    # A wide range is not silently truncated: use exact divisor enumeration.
    if hi-lo>20000:
        import sympy
        fs=sympy.factorint(b)
        qmax=min(b-1,a*hi-b); qmin=max(1,a*lo-b)
        divisors=[1]
        for pp,ee in fs.items():
            old=divisors; divisors=[]; power=1
            for _ in range(2*int(ee)+1):
                divisors.extend(v*power for v in old if v*power<=qmax)
                power*=int(pp)
        cand=((b+q)//a for q in divisors if qmin<=q<=qmax and (b+q)%a==0)
    else: cand=range(lo,hi+1)
    found=0
    for x in cand:
        COUNTS['two_candidates']+=1
        if COUNTS['two_candidates']%8192==0:checktime()
        if x in forbidden:continue
        z=a*x-b
        if (b*x)%z:continue
        y=b*x//z
        if y>x and y not in forbidden:
            yield (x,y);found+=1
            if limit and found>=limit:return

def solve(r,t,lo,forbidden,limit=None):
    COUNTS['nodes']+=1
    if COUNTS['nodes']%4096==0:checktime()
    a,b=r.numerator,r.denominator
    if t==1:
        if a==1 and b>=lo and b not in forbidden:yield(b,)
        return
    if t==2:
        yield from two(a,b,lo,forbidden,limit);return
    low=max(lo,b//a+1);high=(t*b-1)//a
    found=0
    for x in range(low,high+1):
        if x in forbidden:continue
        yy=x;maximum=Fraction(0)
        for _ in range(t):
            while yy in forbidden:yy+=1
            maximum+=Fraction(1,yy);yy+=1
        if maximum<r:break
        for tail in solve(r-Fraction(1,x),t-1,x+1,forbidden,limit):
            yield (x,)+tail;found+=1
            if limit and found>=limit:return

def validate(ds,N):
    assert len(ds)==len(set(ds)) and min(ds)>=N
    assert sum((Fraction(1,d) for d in ds),Fraction(0))==1
    L=lcm(*ds);S=sum(L//d for d in ds);assert S==L
    return {'minimum':N,'terms':len(ds),'denominators':list(ds),'lcm':str(L),'scaled_sum':str(S),'valid':True}

def lift(ds,N,max_removed=3,max_added=4,variants=5):
    required=tuple(d for d in ds if d<N); optional=tuple(d for d in ds if d>=N)
    if not required:return [(ds,None)]
    candidates=[]
    for delta in range(0,max_added):
        for nr in range(len(required),max_removed+1):
            na=nr+delta
            if na<1 or na>max_added:continue
            for extra in combinations(optional,nr-len(required)):
                checktime();removed=required+extra;fixed=set(ds)-set(removed)
                r=sum((Fraction(1,d) for d in removed),Fraction(0))
                for added in solve(r,na,N,fixed,limit=variants):
                    full=tuple(sorted(fixed|set(added)));validate(full,N)
                    candidates.append((full,{'removed':removed,'added':added}))
        if candidates:
            candidates.sort(key=lambda c:(len(c[0]),max(c[0]),sum(c[0]),c[0]))
            seen=set();unique=[]
            for c in candidates:
                if c[0] not in seen:unique.append(c);seen.add(c[0])
                if len(unique)>=variants:return unique
            return unique
    return []

def main():
    global DEADLINE
    ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=22);ap.add_argument('--seconds',type=int,default=300);ap.add_argument('--max-removed',type=int,default=3);ap.add_argument('--max-added',type=int,default=4);ap.add_argument('--variants',type=int,default=3);ap.add_argument('--out',default='lift-results.json');args=ap.parse_args()
    DEADLINE=time.monotonic()+args.seconds
    records=[validate(D18,18)];beam=[(D18,None)];status='completed'
    try:
        for N in range(19,args.max_n+1):
            choices=[]
            for ds,_ in beam:choices.extend(lift(ds,N,args.max_removed,args.max_added,args.variants))
            if not choices:status='no_witness_in_configured_local_scope';break
            choices.sort(key=lambda c:(len(c[0]),max(c[0]),sum(c[0]),c[0]));seen=set();beam=[]
            for c in choices:
                if c[0] not in seen:beam.append(c);seen.add(c[0])
                if len(beam)>=args.variants:break
            rec=validate(beam[0][0],N);rec['replacement']=beam[0][1];records.append(rec)
            print(json.dumps(rec),flush=True)
            (HERE/args.out).write_text(json.dumps({'status':'running','records':records,'counters':COUNTS,'elapsed_seconds':time.monotonic()-START},indent=2))
    except Limit:status='timeout'
    result={'status':status,'records':records,'counters':COUNTS,'elapsed_seconds':time.monotonic()-START,'scope':'Exact certificates from bounded-size local replacement; unsuccessful search is not global exclusion.'}
    (HERE/args.out).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)
if __name__=='__main__':main()
