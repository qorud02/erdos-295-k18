"""Exact, no-denominator-cap local shortening of the published 34-term set.

Every accepted witness is verified twice (Fraction and integer LCM).
Exhaustion applies only to the specified removed-subset family.
Timeout never means nonexistence. Deadline is checked inside all loops.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import gcd, isqrt, lcm
from pathlib import Path
import argparse, json, time

BASE = (18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,43,44,45,46,48,50,52,54,63,275,14143068,10457416992)
assert len(BASE)==34 and sum((Fraction(1,x) for x in BASE),Fraction())==1

class Deadline(Exception): pass

class Search:
    def __init__(self, forbidden, seconds):
        self.forbidden=frozenset(forbidden)
        self.deadline=time.monotonic()+seconds
        self.nodes=0; self.two_prunes=0; self.two_candidates=0
    def tick(self):
        if time.monotonic()>=self.deadline: raise Deadline
    @lru_cache(maxsize=10000)
    def harmonic(self,d,t):
        out=Fraction();j=0
        while j<t:
            if d not in self.forbidden:out+=Fraction(1,d);j+=1
            d+=1
        return out
    def dfs(self,d,t,a,b):
        self.nodes+=1
        if self.nodes&255==0:self.tick()
        if a<=0:return None
        if t==1:
            if b%a==0 and b//a>=d and b//a not in self.forbidden:return (b//a,)
            return None
        lo=max(d,b//a+1)
        hi=(t*b-1)//a
        if t==2:
            if hi<lo or lo*lo-a*lo+b<0:
                self.two_prunes+=1;return None
            delta=a*a-4*b
            if delta>0:
                s=isqrt(delta);s+=int(s*s<delta)
                hi=min(hi,(a-s)//2)
            for x in range(lo,hi+1):
                self.two_candidates+=1
                if self.two_candidates&255==0:self.tick()
                if x in self.forbidden:continue
                y,rem=divmod(b*x,a*x-b)
                if rem==0 and y>x and y not in self.forbidden:return (x,y)
            return None
        # Necessary harmonic bound using the smallest permitted distinct terms.
        for x in range(lo,hi+1):
            if x in self.forbidden:continue
            h=self.harmonic(x,t)
            if h.numerator*b<a*h.denominator:break
            aa=a*x-b;bb=b*x;g=gcd(aa,bb)
            ans=self.dfs(x+1,t-1,aa//g,bb//g)
            if ans:return (x,)+ans
        return None

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--remove',type=int,default=4)
    p.add_argument('--required-large',type=int,choices=(0,1,2),default=2)
    p.add_argument('--seconds',type=float,default=120)
    p.add_argument('--per-case',type=float,default=2)
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    started=time.monotonic();deadline=started+args.seconds
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    complete=timed=nodes=two_prunes=two_candidates=0;witness=None;next_index=args.start
    required=BASE[-args.required_large:] if args.required_large else ()
    pool=tuple(x for x in BASE if x not in required)
    with path.open('w',encoding='utf-8') as log:
        def emit(r):log.write(json.dumps(r)+'\n');log.flush();print(json.dumps(r),flush=True)
        emit({'event':'start','args':vars(args),'scope':'local subset replacement; no denominator cap'})
        for index,extra in enumerate(combinations(pool,args.remove-len(required))):
            if index<args.start:continue
            next_index=index
            if time.monotonic()>=deadline:break
            removed=tuple(sorted(required+extra));kept=set(BASE)-set(removed)
            r=sum((Fraction(1,x) for x in removed),Fraction())
            s=Search(kept,min(args.per_case,deadline-time.monotonic()))
            case_started=time.monotonic();status='exhausted';answer=None
            try:answer=s.dfs(18,args.remove-1,r.numerator,r.denominator)
            except Deadline:status='timeout'
            if answer:
                status='witness';ds=sorted(kept|set(answer));total=sum((Fraction(1,x) for x in ds),Fraction())
                L=lcm(*ds);weighted=sum(L//x for x in ds)
                assert len(ds)==33 and min(ds)>=18 and total==1 and weighted==L
                witness={'denominators':ds,'removed':removed,'replacement':answer,'lcm':str(L),'weighted_sum':str(weighted)}
            timed+=status=='timeout';complete+=status=='exhausted'
            nodes+=s.nodes;two_prunes+=s.two_prunes;two_candidates+=s.two_candidates
            if status!='exhausted' or index%1000==0:
                emit({'event':'case','index':index,'removed':removed,'status':status,'nodes':s.nodes,'elapsed_seconds':time.monotonic()-case_started})
            next_index=index+1
            if witness:break
        emit({'event':'result','status':'witness' if witness else ('family_exhausted' if time.monotonic()<deadline and timed==0 else 'incomplete'),
              'elapsed_seconds':time.monotonic()-started,'cases_exhausted':complete,'cases_timed_out':timed,'next_index':next_index,
              'nodes':nodes,'quadratic_two_prunes':two_prunes,'two_candidates':two_candidates,'witness':witness})

if __name__=='__main__':main()
